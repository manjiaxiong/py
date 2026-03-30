# 前端工程师转型大模型应用开发 — 4周学习计划

## 第1周：Python 基础 + AI 基本概念

### 目标
补齐 Python 基础，理解大模型核心概念。

### 学习内容

| 天数 | 主题 | 具体内容 |
|------|------|----------|
| Day 1-2 | Python 基础 | 数据类型、函数、类、模块、虚拟环境（venv/conda） |
| Day 3 | Python 进阶 | 异步编程（async/await）、装饰器、类型提示 |
| Day 4 | AI 基本概念 | LLM 原理概述、Token、Prompt、Temperature 等核心概念 |
| Day 5 | API 调用实践 | 注册并调用 OpenAI / Claude API，理解请求/响应结构 |
| Day 6-7 | 动手项目 | 用 Python 写一个命令行聊天机器人 |

### 推荐资源
- [Python 官方教程](https://docs.python.org/zh-cn/3/tutorial/)
- [Anthropic API 文档](https://docs.anthropic.com/)
- [OpenAI API 文档](https://platform.openai.com/docs)

---

## 第2周：Prompt Engineering + LangChain/LlamaIndex

### 目标
掌握 Prompt 工程核心技巧，学会使用主流 LLM 开发框架。

### 学习内容

| 天数 | 主题 | 具体内容 |
|------|------|----------|
| Day 1 | Prompt Engineering | Few-shot、Chain-of-Thought、System Prompt 设计原则 |
| Day 2 | 结构化输出 | JSON Mode、Function Calling / Tool Use |
| Day 3-4 | LangChain 入门 | Chain、Agent、Memory、Tool 核心概念与实践 |
| Day 5 | RAG 概念 | 检索增强生成原理、Embedding、向量数据库概述 |
| Day 6-7 | 动手项目 | 用 LangChain 构建一个带上下文记忆的多轮对话应用 |

### 推荐资源
- [Prompt Engineering Guide](https://www.promptingguide.ai/zh)
- [LangChain 官方文档](https://python.langchain.com/)
- [Anthropic Prompt Engineering 指南](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering)

---

## 第3周：RAG 应用 + 向量数据库 + Web 开发整合

### 目标
构建完整的 RAG 应用，结合前端技能打造全栈 AI 应用。

### 学习内容

| 天数 | 主题 | 具体内容 |
|------|------|----------|
| Day 1 | 文本处理 | 文档加载、文本分割（Chunking 策略） |
| Day 2 | 向量数据库 | Chroma / Pinecone / Milvus 选型与使用 |
| Day 3 | RAG 实战 | 构建端到端的文档问答系统 |
| Day 4 | FastAPI | 用 FastAPI 构建 AI 应用后端 API |
| Day 5 | 流式输出 | SSE 流式响应、前端流式渲染（发挥前端优势） |
| Day 6-7 | 动手项目 | 全栈 RAG 应用：FastAPI 后端 + React/Next.js 前端 |

### 推荐资源
- [FastAPI 官方文档](https://fastapi.tiangolo.com/zh/)
- [ChromaDB 文档](https://docs.trychroma.com/)
- [Vercel AI SDK](https://sdk.vercel.ai/docs)（前端友好的 AI 工具包）

---

## 第4周：Agent 开发 + MCP + 部署上线

### 目标
掌握 AI Agent 开发范式，了解 MCP 协议，完成项目部署。

### 学习内容

| 天数 | 主题 | 具体内容 |
|------|------|----------|
| Day 1 | Agent 基础 | ReAct 模式、Tool Use、多步推理 |
| Day 2 | Agent 框架 | Claude Agent SDK / LangGraph / CrewAI |
| Day 3 | MCP 协议 | Model Context Protocol 概念、编写 MCP Server |
| Day 4 | 评估与优化 | Prompt 评估、成本优化、延迟优化 |
| Day 5 | 部署 | Docker 容器化、云平台部署（Vercel/Railway/AWS） |
| Day 6-7 | 毕业项目 | 构建一个完整的 AI Agent 应用并部署上线 |

### 推荐资源
- [Claude Agent SDK 文档](https://docs.anthropic.com/en/docs/agents)
- [MCP 官方文档](https://modelcontextprotocol.io/)
- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)

---

## 你的前端优势

作为前端工程师，你在转型过程中拥有以下优势：

- **TypeScript/JavaScript 能力**：Anthropic SDK、Vercel AI SDK 都提供 JS/TS 版本，可以快速上手
- **Web 开发经验**：流式渲染、SSE、WebSocket 等前端技术在 AI 应用中非常重要
- **UI/UX 理解**：AI 应用的用户体验设计是核心竞争力
- **React/Next.js**：目前最主流的 AI 应用前端技术栈

## 学习建议

1. **边学边做**：每周都有动手项目，确保理论与实践结合
2. **先用 API 再学原理**：先会用，再深入理解模型原理
3. **利用前端优势**：用 TypeScript + Vercel AI SDK 也能快速构建 AI 应用
4. **关注社区**：GitHub、Twitter、掘金上关注 AI 应用开发的最新动态
5. **建立作品集**：每周的项目整理成 GitHub 仓库，作为转型的证明
