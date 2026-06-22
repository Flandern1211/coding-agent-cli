"""
从 agent run 的 messages 中提取 API 调用元数据。

pydantic-ai 0.8.1 移除了 Hooks API，改为从 all_messages() 中解析 ModelResponse 来获取调用信息。
"""
from dataclasses import dataclass, field
from typing import Any

from pydantic_ai.messages import ModelRequest, ModelResponse


@dataclass
class ApiCall:
    """
    一次 model API 调用的元数据，从 ModelResponse 消息中提取。
    """
    model: str
    messages_count: int
    last_part: Any
    tools: list
    finish_reason: str = ""
    parts_kinds: list = field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0


# 主循环在每轮 run_sync 之前清空它
api_call_log: list[ApiCall] = []


def extract_api_calls(messages: list) -> list[ApiCall]:
    """
    从 agent run 的完整消息列表中提取 API 调用元数据。
    每个 ModelResponse 对应一次 API 调用。
    """
    calls = []
    request_count = 0

    for i, msg in enumerate(messages):
        if isinstance(msg, ModelRequest):
            request_count += 1
            # 找到这条 request 之后的 response
            if i + 1 < len(messages) and isinstance(messages[i + 1], ModelResponse):
                resp = messages[i + 1]
                # 提取最后一个 part 作为 last_part
                last_part = msg.parts[-1] if msg.parts else None
                # 提取工具名（从 request 的 parts 中找 tool-call）
                tool_names = []
                for p in msg.parts:
                    if hasattr(p, 'tool_name'):
                        tool_names.append(p.tool_name)

                calls.append(ApiCall(
                    model=resp.model_name or "unknown",
                    messages_count=request_count,
                    last_part=last_part,
                    tools=tool_names,
                    finish_reason=resp.provider_details.get('finish_reason', 'unknown') if resp.provider_details else 'unknown',
                    parts_kinds=[p.part_kind for p in resp.parts],
                    input_tokens=resp.usage.input_tokens,
                    output_tokens=resp.usage.output_tokens,
                ))

    return calls
