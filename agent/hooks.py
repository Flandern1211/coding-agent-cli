"""
挂在 Agent 上的 event_stream_handler：
1. API 调用元数据记录（/api-detail 命令用）
2. 工具执行异常的兜底处理

pydantic-ai 0.8.x 使用 event_stream_handler 替代旧版 Hooks API。
重试由 Agent(retries=N) 内置支持，不再需要手动 wrap。
"""
from dataclasses import dataclass, field
from typing import Any

from pydantic_ai.messages import (
    FunctionToolCallEvent,
    FunctionToolResultEvent,
    FinalResultEvent,
    PartStartEvent,
)
from pydantic_ai._run_context import RunContext

from render import console


@dataclass
class ApiCall:
    """
    一次 model API 调用的元数据。
    event_stream_handler 在事件流中逐步填充。
    """
    # request 侧
    model: str = ""
    messages_count: int = 0
    # 这次发送给模型的 messages 中最后一条消息的最后一个 part
    last_part: Any = None
    tools: list = field(default_factory=list)
    # response 侧（handler 从事件流中填充）
    finish_reason: str = ""
    parts_kinds: list = field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0


# 主循环在每轮 agent.iter() 之前清空它
api_call_log: list[ApiCall] = []


async def api_event_handler(ctx: RunContext, event_stream) -> None:
    """
    event_stream_handler 回调，在 Agent 构造时传入。

    每次 model 调用产生一轮事件流，我们据此填充 api_call_log。
    """
    current_call = ApiCall(
        model=ctx.model.model_name if hasattr(ctx.model, 'model_name') else str(ctx.model),
        messages_count=len(ctx.messages) if ctx.messages else 0,
    )
    api_call_log.append(current_call)

    try:
        tool_names: list[str] = []
        async for event in event_stream:
            if isinstance(event, PartStartEvent):
                current_call.parts_kinds.append(event.part.part_kind)
            elif isinstance(event, FunctionToolCallEvent):
                tool_names.append(event.part.tool_name)
            elif isinstance(event, FunctionToolResultEvent):
                pass  # tool result 已记录
            elif isinstance(event, FinalResultEvent):
                current_call.finish_reason = "stop"
    except Exception as e:
        current_call.finish_reason = f"error: {e}"
        console.print(f"[bold red]✗ 事件流处理出错：{e}[/]")
        raise

    # 填充 token 用量（来自 RunContext 的累计值）
    if ctx.usage:
        current_call.input_tokens = ctx.usage.input_tokens
        current_call.output_tokens = ctx.usage.output_tokens

    current_call.tools = tool_names
    if not current_call.finish_reason:
        current_call.finish_reason = "unknown"


def extract_api_calls(messages: list) -> list[ApiCall]:
    """
    从消息列表中提取 API 调用元数据。
    当 api_call_log 为空时，作为降级方案从历史消息中重建。
    """
    calls: list[ApiCall] = []
    for msg in messages:
        if not hasattr(msg, 'parts'):
            continue
        for part in msg.parts:
            if hasattr(part, 'part_kind') and part.part_kind == 'tool-call':
                call = ApiCall(
                    tools=[getattr(part, 'tool_name', '')],
                    parts_kinds=[part.part_kind],
                )
                calls.append(call)
    return calls
