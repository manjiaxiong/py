# 前端工程师转型 LLM 应用开发：更贴近实战的 4 周学习计划

## 这份计划适合谁

适合已经有前端开发经验，熟悉 `JavaScript / TypeScript`、`React / Next.js`，希望尽快转向大模型应用开发的人。

这版计划的核心思路不是“先学一堆框架”，而是：

- 先用原生 API 和 SDK，把模型能力真正用明白
- 先把你已有的前端优势用起来，而不是强行把自己变成纯后端
- 尽早建立评估、日志、调试意识，而不是最后才补
- 把 Agent 和 MCP 放到后面，避免一开始被概念和抽象层压住

---

## 总目标

4 周结束后，你应该能做到：

- 独立调用大模型 API，处理流式输出、结构化输出、工具调用
- 用 `Next.js + TypeScript` 做一个像样的 AI Web 应用
- 用 `Python + FastAPI` 补齐后端接口、脚本处理、简单 RAG 能力
- 理解 RAG、Agent、MCP 的边界，不会把所有问题都做成 Agent
- 做出 2 到 3 个可展示的项目，足够放进 GitHub 和简历

---

## 建议主栈

优先主栈：

- 前端：`TypeScript`、`Next.js`、`React`
- AI 前端集成：`Vercel AI SDK`
- 模型平台：`OpenAI API`
- 数据与存储：`Postgres / Supabase`
- 部署：`Vercel`

补强副栈：

- 后端：`Python`、`FastAPI`
- 数据处理：`Pydantic`
- RAG 实验：`Python` 脚本 + 向量库或托管检索

一句话理解：

你的“求职主武器”应该是 `TS + Next.js + AI SDK`，`Python` 负责补工程短板和扩展能力，而不是反过来。

---

## 学习原则

1. 少框架，先原生

先用官方 SDK 把 `prompt`、`structured outputs`、`tool use`、`streaming`、`file search` 这些基本功跑通，再决定要不要引入 LangChain、LangGraph 之类的抽象层。

2. 先能做产品，再补模型原理

对转岗来说，先把 API 调用、上下文设计、UI 交互、错误处理、部署上线做出来，比先啃大量 Transformer 细节更值。

3. 评估前置

从第 2 周开始，你写的每一个 demo 都应该有最基本的：

- 输入样例
- 期望输出
- 失败案例
- 调试日志
- 成本和延迟观察

4. 把前端优势变成作品优势

前端工程师最大的差异化不是“也会调 API”，而是你能把 AI 应用做得更顺滑、更快、更像一个真实产品。

---

## 第 1 周：打基础，但直接进入 LLM 应用开发

### 目标

- 补齐 Python 必需基础
- 用 TypeScript 和 Python 都能调用模型
- 理解聊天、流式输出、提示词、上下文这些最核心概念

### 这一周的重点

不是“学完整门 Python”，而是只学 LLM 开发立刻会用到的部分。

### Day 1

环境准备与全景认识：

- 配置 `Python`、`venv`、`.env`
- 配置 `Node.js`、`pnpm` 或 `npm`
- 注册并配置 `OpenAI API`
- 理解 `model`、`input`、`output`、`token`、`temperature`

产出：

- 一个最小 `Python` 调用脚本
- 一个最小 `TypeScript` 调用脚本

### Day 2

Python 最小必需知识：

- 数据类型、函数、模块、异常处理
- `list / dict`
- 文件读取与 JSON 处理
- `requests` 或官方 SDK 的基础调用

产出：

- 一个命令行聊天脚本
- 一个把模型输出保存为 JSON 的小脚本

### Day 3

TypeScript 路线接入：

- 在 `Next.js` 中接模型
- 理解服务端调用和浏览器端调用的边界
- 做一个最小聊天页

产出：

- 一个可输入、可返回结果的 Web 聊天页

### Day 4

Prompt 基础：

- system prompt
- few-shot
- 输出格式约束
- 限制模型胡说八道的写法

产出：

- 一个“商品信息提取器”
- 一个“代码解释器”

### Day 5

流式输出：

- 什么是 streaming
- 为什么 AI 产品几乎都要流式输出
- 前端如何渲染 token-by-token 输出

产出：

- Web 聊天页支持流式响应

### Day 6-7

周项目：`AI Chat Playground`

功能要求：

- 支持普通问答
- 支持系统提示词切换
- 支持流式输出
- 支持保存最近几轮消息
- 页面做得像产品，不要只是一个输入框和按钮

### 第 1 周完成标准

- 你能解释清楚 `prompt`、`system prompt`、`temperature`、`streaming`
- 你能分别用 `Python` 和 `TypeScript` 调一次模型
- 你有一个能跑的 Web 聊天 demo

---

## 第 2 周：结构化输出、工具调用、评估与调试

### 目标

- 掌握真实业务最常用的 LLM 能力
- 建立“可测试、可观测、可调试”的开发习惯
- 暂时不急着沉进复杂 Agent 框架

### 为什么第 2 周先学这些

大多数公司真正落地的大模型需求，并不是“先做 Agent”，而是：

- 抽取结构化信息
- 让模型调用工具
- 让输出稳定可控
- 评估 prompt 和结果质量

### Day 1

结构化输出：

- JSON Schema 思维
- `Pydantic` 基础
- 让模型返回稳定字段
- 处理字段缺失、类型错误、脏数据

产出：

- 一个“简历信息抽取器”
- 一个“商品参数抽取器”

### Day 2

工具调用：

- 什么情况下该用 tool use
- 模型何时生成文本，何时调用函数
- 用工具连接天气、搜索、数据库或内部函数

产出：

- 一个“帮你查天气/查汇率/查库存”的问答 demo

### Day 3

评估入门：

- 什么叫 prompt eval
- 什么叫 regression case
- 如何保留一组固定输入用于回归测试
- 如何衡量正确率、稳定性、成本、延迟

产出：

- 给你前两天的 demo 补一个最小评估集

### Day 4

调试与日志：

- 记录请求和响应
- 记录 token 消耗和耗时
- 保存失败样本
- 观察哪些 prompt 容易出错

产出：

- 一个简单的日志面板或控制台调试脚本

### Day 5

文件与知识输入：

- 文件上传
- 文件解析
- 什么时候应该自己做 RAG
- 什么时候直接用托管检索能力更省事

产出：

- 一个“上传文档并提问”的最小功能

### Day 6-7

周项目：`AI Data Assistant`

功能要求：

- 上传一份文本或简历
- 提取结构化字段
- 对字段做基础校验
- 支持一个工具调用场景
- 有日志和最小评估样例

### 第 2 周完成标准

- 你会做结构化抽取
- 你会做工具调用
- 你知道如何复现一次 prompt 退化
- 你不再把“大模型调不准”当成玄学

---

## 第 3 周：RAG、全栈整合、把应用做得更像产品

### 目标

- 理解 RAG 的真正用途和局限
- 完成一个前后端完整 AI 应用
- 开始做作品集级别的项目

### 第 3 周的关键原则

不要把 RAG 学成“切块 + embedding + 向量库”的背诵题。

你真正要搞懂的是：

- 什么问题适合 RAG
- 为什么检索不到
- 为什么召回了但回答仍然差
- chunk、embedding、retrieval、rerank 分别会在哪一步出问题

### Day 1

RAG 基础概念：

- chunking
- embedding
- retrieval
- top-k
- 上下文拼接

产出：

- 一个离线文档切块脚本

### Day 2

最小 RAG 跑通：

- 先用最简单方案完成一条链路
- 不先纠结复杂框架
- 文档少时优先简单和可解释

产出：

- 一个本地知识库问答 demo

### Day 3

优化 RAG：

- chunk 大小调整
- 检索数量调整
- 引用片段展示
- “没找到就明确说没找到”

产出：

- 一个能显示引用来源的回答页

### Day 4

后端补强：

- 用 `FastAPI` 暴露检索和问答接口
- 理解前后端分层
- 理解什么时候逻辑应该放前端，什么时候要下沉到服务端

产出：

- 一个 `FastAPI` 后端接口

### Day 5

前端体验优化：

- SSE 或 streaming UI
- 加载态与中断生成
- 历史会话
- 错误提示与重试
- 引用来源展示

产出：

- 一个更完整的知识库问答前端

### Day 6-7

周项目：`Docs Copilot`

推荐做法：

- 前端：`Next.js`
- 后端：`FastAPI`
- 数据：本地文件或托管数据库
- 能力：上传文档、检索、回答、引用来源、流式输出

如果你想更贴近前端背景，可以把项目主题做成：

- 组件库文档助手
- 公司内部前端规范问答助手
- React/Next.js 学习资料助手

### 第 3 周完成标准

- 你理解 RAG 不是“万能记忆外挂”
- 你能解释一个回答差，到底是检索问题还是生成问题
- 你做出了一个能展示的全栈项目

---

## 第 4 周：Agent、MCP、部署上线与作品集包装

### 目标

- 理解 Agent 什么时候该用，什么时候不该用
- 学会让模型与外部工具协作
- 把项目部署出去，形成可展示作品

### 第 4 周的原则

不要一口气学 3 个 Agent 框架。

这周建议只选一个主方向：

- 如果你偏产品快速落地：优先官方 SDK + tool use
- 如果你偏复杂工作流：再看 `LangGraph`

### Day 1

Agent 基础：

- 什么是 agent loop
- 什么是 plan-act-observe
- ReAct 在实战里解决什么问题
- 为什么不是所有任务都适合 Agent

产出：

- 一个多步骤任务 demo

### Day 2

工具型 Agent：

- 查询天气、日历、数据库、内部 API
- 处理多工具协作
- 限制无意义循环
- 给 Agent 设置停止条件和失败回退

产出：

- 一个“任务助手” demo

### Day 3

MCP：

- 理解 MCP 的定位
- 理解 MCP 和普通函数调用的区别
- 跑通一个现成 MCP server
- 如果时间够，再自己写一个最小 MCP server

产出：

- 一个接入外部工具的最小实验

### Day 4

评估与优化：

- 为你的项目补回归样例
- 记录失败任务
- 调整 prompt
- 调整工具描述
- 观察延迟和成本

产出：

- 一份项目调优记录

### Day 5

部署：

- 前端部署到 `Vercel`
- Python 服务部署到 `Railway` 或其他平台
- 环境变量配置
- 错误日志检查

产出：

- 一个线上可访问版本

### Day 6-7

毕业项目：从下面选一个

1. 前端开发知识助手

- 上传项目规范文档
- 支持问答、引用、结构化抽取
- 支持工具调用

2. AI PR Review Assistant

- 分析 diff
- 给出代码审查建议
- 输出结构化 review 结果

3. AI Workflow Assistant

- 用户输入任务
- Agent 调用多个工具完成子步骤
- 展示执行过程和最终结果

### 第 4 周完成标准

- 你能说清楚 Agent 适用边界
- 你能跑通一个 MCP 相关实验
- 你有至少 1 个线上可访问项目

---

## 4 周后的能力判断标准

如果学完以后你能做到下面这些，就说明这条路线基本走对了：

- 能独立完成一个 AI Web 应用的前端交互
- 能独立接模型 API，处理 streaming 和结构化输出
- 能做一个最小 RAG
- 能做一个最小工具调用或 Agent 应用
- 能把项目部署出去，并能向别人清楚解释架构

如果还做不到，就优先补这三项：

- 结构化输出
- 工具调用
- 评估与调试

这三项比“再学一个新框架”更值钱。

---

## 作品集建议

建议你最终整理出 3 个项目放进 GitHub：

1. `ai-chat-playground`

- 展示聊天、流式输出、提示词控制、UI 体验

2. `ai-data-assistant`

- 展示结构化输出、工具调用、基础评估

3. `docs-copilot` 或 `agent-assistant`

- 展示 RAG 或 Agent、全栈整合、部署能力

每个项目 README 至少写清楚：

- 项目解决什么问题
- 用了什么模型能力
- 技术栈是什么
- 遇到什么坑，怎么调试
- 还有什么可以继续优化

---

## 推荐学习资源

优先看官方文档：

- [OpenAI API Docs](https://platform.openai.com/docs)
- [OpenAI Developers Docs](https://developers.openai.com/)
- [Vercel AI SDK Docs](https://sdk.vercel.ai/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Pydantic Docs](https://docs.pydantic.dev/)
- [Model Context Protocol Docs](https://modelcontextprotocol.io/)

按需再看：

- [LangChain Docs](https://python.langchain.com/docs/introduction/)
- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)

建议顺序：

- 官方 SDK 文档优先
- 实战项目第二
- 框架文档第三

---

## 最后一句建议

你的目标不是“会很多 AI 名词”，而是“能做出一个真实、稳定、可展示的 AI 应用”。

对前端工程师来说，最短路径通常不是先变成算法工程师，而是先成为一个很强的 `AI 应用工程师`。
