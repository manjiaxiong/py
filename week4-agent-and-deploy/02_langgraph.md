# Day 2: LangGraph — 图结构 Agent 编排

## 学习目标

- 理解 LangGraph 为什么比 LangChain Agent 更可控
- 掌握 State / Node / Edge / Conditional Edge 四个核心概念
- 能用 LangGraph 构建线性和带分支的工作流
- 了解人工介入节点（Human-in-the-loop）

## 为什么需要 LangGraph

### LangChain Agent 的问题

| 问题 | 表现 |
|------|------|
| 流程不可控 | Agent 自己决定调用什么，可能跑偏 |
| 无法暂停 | 不能在中间加人工审核 |
| 调试困难 | 黑盒执行，不知道哪一步出了问题 |
| 状态不透明 | 难以追踪 Agent 做了什么 |

### LangGraph 的解决方案

| 解决 | 方式 |
|------|------|
| 可控流程 | 图结构，每个节点和边都显式定义 |
| 可暂停 | interrupt_before / interrupt_after |
| 易调试 | 每个节点输入输出都可观察 |
| 状态透明 | State 对象记录所有数据 |

## 核心概念

### 1. State — 共享数据

```python
from typing import TypedDict

class WorkflowState(TypedDict):
    topic: str        # 主题
    research: str     # 研究结果
    draft: str        # 草稿
    status: str       # 当前状态
```

```javascript
// JS 类比：React useState 或 Redux store
const [state, setState] = useState({
  topic: '',
  research: '',
  draft: '',
  status: 'idle',
});
```

### 2. Node — 执行单元

```python
def research_node(state: WorkflowState) -> dict:
    result = ask(client, MODEL, f"研究：{state['topic']}")
    return {"research": result, "status": "researched"}
```

```javascript
// JS 类比：reducer 函数
const researchNode = async (state) => {
  const research = await llm.ask(`研究：${state.topic}`);
  return { ...state, research, status: 'researched' };
};
```

### 3. Edge — 固定连接

```python
graph.add_edge("research", "outline")  # research 完成后一定去 outline
```

```javascript
// JS 类比：直接函数调用
const result = await research();
return outline(result);  // 无条件跳转
```

### 4. Conditional Edge — 条件分支

```python
def should_continue(state):
    if "7/10" in state["review"]:
        return "end"
    return "revise"

graph.add_conditional_edges("review", should_continue, {
    "end": END,
    "revise": "draft",
})
```

```javascript
// JS 类比：switch/if 路由
const nextStep = (state) => {
  if (state.review.score >= 7) return 'end';
  return 'revise';
};
```

## 构建流程图

### 线性工作流

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ research  │───→│ outline  │───→│  draft   │───→│  review  │───→ END
└──────────┘    └──────────┘    └──────────┘    └──────────┘
```

```python
from langgraph.graph import StateGraph, END

workflow = StateGraph(WritingState)
workflow.add_node("research", research_node)
workflow.add_node("outline", outline_node)
workflow.add_node("draft", draft_node)
workflow.add_node("review", review_node)

workflow.set_entry_point("research")
workflow.add_edge("research", "outline")
workflow.add_edge("outline", "draft")
workflow.add_edge("draft", "review")
workflow.add_edge("review", END)

app = workflow.compile()
result = app.invoke(initial_state)
```

### 带条件的工作流

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ research  │───→│ outline  │───→│  draft   │───→│  review  │
└──────────┘    └──────────┘    └──────────┘    └────┬─────┘
                                     ↑               │
                                     │         ┌─────┴─────┐
                                     │         │ 分数>=7？  │
                                     │         └─────┬─────┘
                                     │          Yes   │  No
                                     └────────────────┘  ↓
                                                        END
```

## 人工介入（Human-in-the-loop）

### 概念

在关键节点前暂停，等待人工审核后继续。

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
app = workflow.compile(
    checkpointer=checkpointer,
    interrupt_before=["review"],  # review 前暂停
)

config = {"configurable": {"thread_id": "demo-1"}}

# 第一次调用 — 在 review 前暂停
result = app.invoke(initial_state, config)

# 第二次调用 — 恢复执行
from langgraph.types import Command
final = app.invoke(Command(resume="approved"), config)
```

```javascript
// JS 类比
const result = await workflow.runUntil('review');
// 暂停，等用户输入
const feedback = await getUserInput();
await workflow.resume(feedback);
```

### MemorySaver（检查点）

| 概念 | 作用 | JS 类比 |
|------|------|---------|
| MemorySaver | 内存中保存状态快照 | localStorage.setItem |
| thread_id | 区分不同对话 | session ID |
| interrupt_before | 节点执行前暂停 | await confirm() |
| Command(resume=) | 恢复并传入数据 | callback(userInput) |

## JS 类比总览

| LangGraph 概念 | JS 类比 |
|----------------|---------|
| `StateGraph` | XState `createMachine` |
| `State (TypedDict)` | React `useState` / Redux store |
| `Node (函数)` | Reducer `(state) => newState` |
| `Edge` | 直接函数调用 / `return next()` |
| `Conditional Edge` | `switch/case` 路由 |
| `compile()` | `createMachine(config)` |
| `invoke()` | `machine.send(event)` |
| `MemorySaver` | `localStorage` |
| `interrupt_before` | `await confirm()` |
| `END` | 终止状态 / `return` |

## 关键要点

1. **LangGraph = 图结构编排** — 节点做事，边控制流程，比 Agent 黑盒更可控
2. **State 是核心** — 所有节点共享一个 State 对象，就像全局 store
3. **条件边** — 根据 state 决定下一步走哪，实现分支和循环
4. **人工介入** — interrupt_before + MemorySaver 让工作流可以暂停等人
5. **compile() 才能运行** — 定义完图结构后必须 compile 才能 invoke

## 推荐资源

- [LangGraph 官方文档](https://langchain-ai.github.io/langgraph/)
- [LangGraph 快速入门](https://langchain-ai.github.io/langgraph/tutorials/introduction/)
- [LangGraph Human-in-the-loop](https://langchain-ai.github.io/langgraph/how-tos/human_in_the_loop/)
