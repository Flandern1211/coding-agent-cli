# Coding Agent CLI

一个基于 [pydantic-ai](https://github.com/pydantic/pydantic-ai) 的终端 AI 编程助手，支持实时流式输出、工具调用和多轮对话。

## 功能特点

- **实时流式输出** — 逐节点驱动 Agent 循环，每一步（thinking、文本、工具调用、工具返回）即时打印
- **工具调用** — 内置文件读写、代码执行等工具，Agent 可直接操作项目文件
- **多轮对话** — 自动维护对话历史，支持上下文连续交互
- **Rich 终端渲染** — Markdown 回答自动渲染，thinking / tool_call 等角色用不同颜色区分
- **会话管理** — 支持 `/new` 重置会话、`/status` 查看 token 用量、`/api-detail` 查看 API 调用详情

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

在项目根目录创建 `.env` 文件，填入你的 API Key（具体变量名参考 `agent/` 下的配置）。

### 3. 运行

```bash
python main.py
```

## 可用命令

| 命令 | 说明 |
|------|------|
| `/help` | 显示可用命令 |
| `/new` | 开启新会话 |
| `/status` | 显示当前会话状态（模型、消息数、token 用量） |
| `/api-detail` | 显示最近一轮 API 调用详情 |
| `/exit` | 退出程序 |

## 项目结构

```
coding-agent-cli/
├── main.py          # 程序入口，主循环
├── commands.py      # 命令定义、会话状态、终端渲染逻辑
├── render.py        # 共享的终端渲染原语（Console、print_step）
├── agent/           # Agent 核心
│   ├── core.py      # Agent 定义与配置
│   ├── tools.py     # 工具函数
│   └── hooks.py     # 钩子函数
└── requirements.txt # Python 依赖
```

## 技术栈

- **pydantic-ai** — AI Agent 框架
- **Rich** — 终端富文本渲染
- **prompt_toolkit** — 命令行输入（支持光标移动、历史记录）
