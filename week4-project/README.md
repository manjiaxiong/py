# AI Workflow Assistant

第 4 周毕业项目 — 基于 LangGraph 的多步骤工作流助手。

## 项目解决什么问题

用户输入一个复杂任务描述（如"查一下 Python 版本然后计算..."），系统自动：
1. 规划执行步骤（plan）
2. 逐步调用工具执行（execute）
3. 汇总结果返回（summarize）

## 用了什么模型能力

- **Agent 自主决策** — LLM 自动规划步骤和选择工具
- **工具调用** — 搜索、计算、文件读取、摘要、时间查询
- **LangGraph 编排** — 图结构控制流程（plan → execute loop → summarize）
- **SSE 流式输出** — 前端实时看到执行进度

## 技术架构

```
用户 → 前端(HTML/JS) → FastAPI → LangGraph Workflow
                                       ↓
                              plan_node (LLM 规划)
                                       ↓
                              execute_node (调用工具) ←→ tools.py
                                       ↓ (循环)
                              summarize_node (LLM 总结)
                                       ↓
                                  返回结果
```

## 快速开始

```bash
# 安装依赖
pip install fastapi uvicorn langgraph langchain-core sse-starlette python-dotenv anthropic

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入 API Key

# 启动服务
uvicorn week4-project.main:app --reload

# 访问
open http://localhost:8000
```

## 项目结构

```
week4-project/
├── main.py          # FastAPI 入口 + SSE
├── workflow.py      # LangGraph 工作流定义
├── tools.py         # 5 个工具
├── models.py        # Pydantic 模型
├── templates/
│   └── index.html   # 前端页面
├── eval_cases.json  # 评估集（8 条）
├── eval_runner.py   # 评估脚本
└── README.md
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | / | 前端页面 |
| GET | /api/health | 健康检查 |
| POST | /api/submit | 提交任务 |
| GET | /api/status/{id} | 查询任务状态 |
| GET | /api/stream/{id} | SSE 流式进度 |

## 评估

```bash
python week4-project/eval_runner.py
```

## 还可以优化

- 接入真实搜索 API（Tavily / Bing）
- 工具执行并行化
- 加入人工介入节点（Human-in-the-loop）
- 用 SQLite checkpointer 持久化状态
- Docker 部署
