# 前端工程师转型大模型应用开发：4 周学习计划 v2

## 适合谁

有前端开发经验（JS/TS、React/Next.js），想转向大模型应用开发的工程师。

## 核心理念

1. **先原生 SDK，再框架** — 先用 API 把 prompt、streaming、tool use、structured output 跑通，再引入 LangChain
2. **评估前置** — 从第 2 周开始，每个 demo 都要有输入样例、期望输出、失败案例
3. **每周一个可展示项目** — 不是零散 demo，而是完整作品
4. **Python 为主栈** — 国内岗位要求，TS/Next.js 作为加分项放后面
5. **先能做产品，再补原理** — API 调用、上下文设计、错误处理优先，Transformer 细节后补

---

## 主栈

| 层级 | 技术 |
|------|------|
| 语言 | Python 3.11+ |
| 后端框架 | FastAPI |
| 数据验证 | Pydantic |
| AI 框架 | LangChain / LangGraph |
| 向量库 | Chroma / FAISS |
| 模型 API | OpenAI / Anthropic / 国产模型 |
| 部署 | Railway / Vercel / Docker |

加分项（你已有的前端优势）：

| 层级 | 技术 |
|------|------|
| 前端 | TypeScript + Next.js + React |
| AI 前端 | Vercel AI SDK |
| 部署 | Vercel |

一句话：Python 拿 offer，TS 做差异化。

---

## 第 1 周：Python 基础 + LLM 初体验

### 目标

- 补齐 Python 必需基础（只学 LLM 开发用得到的）
- 用 Python 调通模型 API
- 理解 prompt、streaming、token、temperature

### Day 1：环境 + 第一次调用

- 配置 Python、venv、.env
- 注册模型 API（OpenAI / Anthropic / 国产）
- 理解 model、input、output、token、temperature
- 产出：一个最小 Python 调用脚本

### Day 2：Python 数据类型与函数

- 数据类型：str、int、float、bool、None
- 容器：list、dict、tuple、set
- 函数定义、默认参数、*args / **kwargs
- 产出：用 Python 处理一组数据并格式化输出

### Day 3：文件 IO + JSON + 异常处理

- 文件读写：open / with / pathlib
- JSON：json.loads / json.dumps / json.load / json.dump
- 异常处理：try / except / finally
- 产出：读取文件 → 调用模型 → 保存 JSON 结果

### Day 4：模块、类、包

- import / from...import / 相对导入
- class 基础（__init__、方法、属性）
- 包结构（__init__.py）
- 产出：把前几天的代码重构成模块化结构

### Day 5：异步 + 流式输出

- async / await 基础（对比 JS 的 Promise）
- asyncio.gather（= Promise.all）
- 流式输出：为什么 AI 产品几乎都要 streaming
- 产出：一个支持流式输出的命令行聊天脚本

### Day 6-7：周项目 — AI 笔记生成器

- 扫描指定目录的代码文件
- 异步调用模型分析每个文件
- 生成结构化 JSON + Markdown 报告
- 展示：文件扫描、异步并发、JSON 处理、错误处理

### 第 1 周完成标准

- [ ] 能解释 list / dict / class / async 的用法
- [ ] 能独立用 Python 调用模型 API
- [ ] 有一个能跑的命令行 AI 工具

---

## 第 2 周：Prompt Engineering + 结构化输出 + 评估入门

### 目标

- 掌握 Prompt 设计的核心技巧
- 掌握结构化输出（Tool Use、Pydantic）
- 建立"可测试、可观测"的开发习惯

### Day 1：Prompt Engineering

- Few-shot prompting（给示例让 AI 照格式回答）
- Chain-of-Thought（让 AI 分步推理）
- System Prompt 设计（角色、约束、输出格式）
- Prompt 模板与变量替换
- 产出：商品信息提取器、代码分析器、多角色审查器

### Day 2：结构化输出

- Prompt 约束法（最简单，不够稳定）
- Tool Use / Function Calling（生产环境首选）
- Pydantic 模型验证（运行时类型校验）
- 多工具路由（AI 自动选择调用哪个工具）
- 产出：简历抽取器、智能客服路由器、带工具执行的完整对话

### Day 3：评估与调试

- 什么是 prompt eval / regression case
- 保留固定输入用于回归测试
- 衡量正确率、稳定性、成本、延迟
- 记录请求响应日志、token 消耗、失败样本
- 产出：给 Day 1-2 的 demo 补评估集 + 调试日志

### Day 4：LangChain 基础

- 为什么要学 LangChain（岗位要求 + 生态）
- 核心概念：Chain、Prompt Template、Output Parser
- LCEL（LangChain Expression Language）
- 对话记忆（ConversationBufferMemory）
- 产出：用 LangChain 重写 Day 1 的对话应用

### Day 5：LangChain Agent + Tool

- Agent 概念：让 AI 自主决定调用什么工具
- 内置工具 + 自定义工具
- Agent 执行流程观察（verbose=True）
- Agent 的局限性和常见踩坑
- 产出：一个能查天气 + 做计算 + 搜索的 Agent

### Day 6-7：周项目 — AI 数据助手

功能要求：
- 上传文本 / 简历 / 商品描述
- 提取结构化字段（用 Tool Use）
- 对字段做 Pydantic 校验
- 支持一个工具调用场景（计算 / 查询）
- 有日志记录和最小评估样例（5 条以上）

### 第 2 周完成标准

- [ ] 能写 Few-shot、CoT、System Prompt
- [ ] 会用 Tool Use 做结构化抽取
- [ ] 能复现一次 prompt 退化并修复
- [ ] 能用 LangChain 搭建基础 Chain 和 Agent
- [ ] 项目有评估集和调试日志

---

## 第 3 周：RAG + FastAPI + 全栈整合

### 目标

- 理解 RAG 的真正用途和局限
- 用 FastAPI 暴露后端接口
- 完成一个前后端完整的 AI 应用

### 关键原则

不要把 RAG 学成"切块 + embedding + 向量库"的背诵题。搞懂：
- 什么问题适合 RAG
- 为什么检索不到
- 为什么召回了但回答仍然差
- chunk、embedding、retrieval、rerank 分别在哪一步出问题

### Day 1：RAG 基础概念

- chunking（文档分块策略）
- embedding（文本向量化）
- retrieval（相似度检索）
- top-k 与上下文拼接
- 产出：一个离线文档切块 + embedding 脚本

### Day 2：最小 RAG 跑通

- 用 Chroma / FAISS 存储向量
- 实现：加载文档 → 分块 → embedding → 存储 → 检索 → 生成
- 先用最简单方案跑通，不纠结框架
- 产出：一个本地知识库问答 demo

### Day 3：RAG 优化

- chunk 大小调整实验
- 检索数量（top-k）调整
- 引用片段展示（让用户看到依据）
- "没找到就明确说没找到"（减少幻觉）
- rerank 概念介绍
- 产出：能显示引用来源的问答页

### Day 4：FastAPI 后端

- FastAPI 基础（路由、请求体、响应模型）
- 用 Pydantic 定义接口 schema
- 暴露检索和问答接口
- 理解前后端分层（什么逻辑放前端，什么下沉到服务端）
- 产出：一个 FastAPI 后端 API

### Day 5：前端对接（用你的前端优势）

- 用 Next.js / React 做前端（或简单 HTML）
- SSE / streaming UI
- 加载态、中断生成、错误重试
- 历史会话、引用来源展示
- 产出：一个完整的知识库问答前端

### Day 6-7：周项目 — Docs Copilot

推荐方向（选一个）：
- 组件库文档助手
- 公司内部规范问答助手
- 技术文档搜索助手

技术要求：
- 后端：FastAPI + RAG pipeline
- 前端：Next.js 或 React
- 能力：上传文档、检索、回答、引用来源、流式输出
- 有评估集（至少 10 条 QA 对）

### 第 3 周完成标准

- [ ] 能解释 RAG 不是"万能记忆外挂"
- [ ] 能判断一个差回答是检索问题还是生成问题
- [ ] 有一个前后端完整的 AI 应用
- [ ] FastAPI 接口能正常工作

---

## 第 4 周：Agent 深入 + MCP + LangGraph + 部署

### 目标

- 理解 Agent 的适用边界
- 学会 LangGraph 构建复杂工作流
- 了解 MCP 协议
- 把项目部署上线，形成作品集

### 原则

不要一口气学 3 个 Agent 框架。这周只聚焦：
- LangGraph（岗位要求 + 比原始 LangChain Agent 更可控）
- MCP（新兴标准，了解即可）

### Day 1：Agent 深入

- Agent Loop：plan → act → observe → repeat
- ReAct 模式实战
- 为什么不是所有任务都适合 Agent
- Agent 的停止条件、失败回退、循环限制
- 产出：一个多步骤任务 Agent

### Day 2：LangGraph

- 为什么需要 LangGraph（LangChain Agent 的局限）
- 核心概念：State、Node、Edge、Conditional Edge
- 构建一个简单的工作流图
- 人工介入节点（Human-in-the-loop）
- 产出：一个 LangGraph 工作流 demo

### Day 3：MCP（Model Context Protocol）

- MCP 的定位和价值
- MCP 和普通 function calling 的区别
- 跑通一个现成 MCP server
- （可选）写一个最小 MCP server
- 产出：一个接入外部工具的 MCP 实验

### Day 4：评估与优化（项目级）

- 为整个项目补回归测试集
- 记录失败任务并分析原因
- 调整 prompt / 工具描述 / 检索参数
- 观察延迟和成本，做基础优化
- 产出：一份项目调优记录

### Day 5：部署上线

- Python 服务部署（Railway / Render / Docker）
- 前端部署（Vercel）
- 环境变量配置与安全
- 错误日志与监控
- 产出：一个线上可访问的项目

### Day 6-7：毕业项目（选一个）

**选项 A：技术文档知识助手**
- 上传项目规范文档
- RAG 检索 + 问答 + 引用
- 结构化抽取 + 工具调用
- 部署上线

**选项 B：AI Code Review Assistant**
- 分析 git diff
- 给出代码审查建议
- 输出结构化 review 结果
- 部署上线

**选项 C：AI Workflow Assistant**
- 用户输入任务描述
- LangGraph 编排多步骤工作流
- Agent 调用工具完成子步骤
- 展示执行过程和最终结果

### 第 4 周完成标准

- [ ] 能说清楚 Agent 适用边界（什么该用 Agent，什么不该）
- [ ] 能用 LangGraph 构建一个工作流
- [ ] 了解 MCP 是什么，跑通过一个实验
- [ ] 至少 1 个项目部署上线

---

## 4 周后的能力自检

全部达标 = 可以开始投简历：

- [ ] 能独立用 Python 调用模型 API，处理 streaming 和结构化输出
- [ ] 能写有效的 Prompt 并做基础评估
- [ ] 能用 LangChain / LangGraph 构建 Chain 和 Agent
- [ ] 能做一个最小 RAG（知道哪一步出问题怎么调）
- [ ] 能用 FastAPI 写后端接口
- [ ] 能把项目部署出去，向别人清楚解释架构
- [ ] 有 2-3 个可展示的 GitHub 项目

如果还差，优先补这三项（比学新框架更值）：
1. 结构化输出 + 工具调用
2. 评估与调试
3. RAG 调优

---

## 作品集建议

最终整理 3 个项目放进 GitHub：

### 1. ai-data-assistant（第 2 周项目）
- 展示：结构化输出、Tool Use、Pydantic 校验、评估日志
- 关键词：Prompt Engineering、Function Calling、数据抽取

### 2. docs-copilot（第 3 周项目）
- 展示：RAG pipeline、FastAPI、前端交互、引用来源
- 关键词：RAG、Embedding、向量检索、全栈

### 3. agent-assistant（第 4 周项目）
- 展示：LangGraph 工作流、Agent、MCP、部署
- 关键词：Agent、LangGraph、工作流编排

每个项目 README 必须写清楚：
- 项目解决什么问题
- 用了什么模型能力（不是框架名，而是能力：结构化输出、工具调用、RAG 等）
- 技术架构图（简单的就行）
- 遇到什么坑，怎么调试的
- 还有什么可以继续优化

---

## 推荐学习资源

优先级从高到低：

1. **官方 SDK 文档**（必看）
   - [OpenAI API Docs](https://platform.openai.com/docs)
   - [Anthropic Docs](https://docs.anthropic.com/)
   - [FastAPI Docs](https://fastapi.tiangolo.com/)
   - [Pydantic Docs](https://docs.pydantic.dev/)

2. **框架文档**（第 2 周开始看）
   - [LangChain Docs](https://python.langchain.com/docs/introduction/)
   - [LangGraph Docs](https://langchain-ai.github.io/langgraph/)

3. **协议与标准**（第 4 周看）
   - [Model Context Protocol](https://modelcontextprotocol.io/)

4. **前端 AI 集成**（加分项）
   - [Vercel AI SDK](https://sdk.vercel.ai/docs)

---

## 和原计划的差异说明

| 改动 | 原因 |
|------|------|
| 评估从第 2 周开始 | GPT 计划的建议，确实应该早学 |
| 每周有完整项目 | GPT 计划的建议，出作品更快 |
| 加入部署环节 | GPT 计划的建议，线上项目求职加分 |
| 加入 LangGraph | 岗位高频要求，比纯 LangChain Agent 更实用 |
| 加入 MCP | 新兴标准，了解即可 |
| Python 仍为主栈 | 国内岗位要求，TS 作为加分项 |
| 保留 LangChain | 岗位高频要求，不能跳过 |
| 加入作品集包装 | GPT 计划的建议，实用 |
