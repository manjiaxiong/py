# Day 1: Agent 深入 — 从手写循环到 ReAct 模式

## 学习目标

- 理解 Agent 和 Chain 的本质区别
- 掌握 ReAct（Reasoning + Acting）模式
- 学会判断什么任务适合用 Agent
- 实现一个带停止条件和错误回退的 Agent

## 核心概念

### Agent vs Chain

| 维度 | Chain | Agent |
|------|-------|-------|
| 流程 | 固定步骤 A → B → C | 动态决策，每步都可能不同 |
| 控制 | 开发者写死流程 | LLM 自己决定下一步 |
| 灵活性 | 低 — 改流程要改代码 | 高 — 同一个 Agent 处理不同任务 |
| 可预测性 | 高 — 每次走同样路径 | 低 — 可能每次走不同路径 |
| 延迟 | 低 — 步骤固定 | 高 — 多轮 LLM 调用 |
| 适合场景 | 翻译、摘要、格式化 | 研究、规划、多工具协作 |

### JS 类比

```javascript
// Chain = Promise chain，固定顺序
const result = await translate(text)
  .then(summarize)
  .then(format);

// Agent = while loop，动态决策
let done = false;
let attempts = 0;
while (!done && attempts < MAX) {
  const { action, input } = await llm.decide(context);
  if (action === 'final_answer') { done = true; break; }
  const result = await tools[action](input);
  context.push({ action, result });
  attempts++;
}
```

## ReAct 模式

### 流程图

```
┌──────────────┐
│  用户任务     │
└──────┬───────┘
       ↓
┌──────────────┐     ┌──────────────┐
│  Thought     │────→│  有最终答案？  │──→ Yes → Final Answer
│  (推理分析)   │     └──────┬───────┘
└──────────────┘            │ No
                            ↓
                   ┌──────────────┐
                   │  Action      │
                   │  (选择工具)   │
                   └──────┬───────┘
                          ↓
                   ┌──────────────┐
                   │  Observation  │
                   │  (工具返回)   │
                   └──────┬───────┘
                          ↓
                   ┌──────────────┐
                   │  回到 Thought │ ←── 循环
                   └──────────────┘
```

### ReAct Prompt 模板

```
你是一个推理助手。你可以使用以下工具：
- calculator: 计算数学表达式
- search: 搜索信息
- get_current_time: 获取当前时间

请严格按照以下格式回答：

Thought: 分析当前情况
Action: 工具名
Action Input: 工具输入

当你有最终答案时：

Thought: 我已经有足够的信息了
Final Answer: 你的最终答案
```

### 解析 LLM 输出

```python
import re

def parse_react_response(response):
    # 检查 Final Answer
    final_match = re.search(r"Final Answer:\s*(.+)", response, re.DOTALL)
    if final_match:
        return {"type": "final", "answer": final_match.group(1).strip()}

    # 解析 Action
    action_match = re.search(r"Action:\s*(.+)", response)
    input_match = re.search(r"Action Input:\s*(.+)", response)
    if action_match:
        return {
            "type": "action",
            "name": action_match.group(1).strip(),
            "input": input_match.group(1).strip() if input_match else "",
        }

    return {"type": "unknown"}
```

## Agent 适用场景

### 什么时候用 Agent

| 场景 | 用 Agent？ | 原因 |
|------|-----------|------|
| 查信息 → 计算 → 整合 | ✅ | 多步骤，需要工具 |
| 不确定需要几步 | ✅ | 让 AI 自己规划 |
| 翻译一段文字 | ❌ | 一次调用就够 |
| 固定格式报告 | ❌ | Chain 更稳定 |
| 实时聊天 | ❌ | 延迟太高 |

### 一句话判断法

> 如果任务需要「先查再算再整合」→ Agent
> 如果任务一句话就能说清楚 → 直接调用

## 停止条件

Agent **必须**有停止条件，否则会无限循环。

| 停止条件 | 说明 |
|---------|------|
| Final Answer | LLM 判断已有足够信息，正常结束 |
| max_iterations | 迭代次数上限（通常 5-10 次） |
| 工具失败 | 重试 N 次后放弃 |
| 超时 | 总耗时超过阈值 |

### JS 类比

```javascript
// 停止条件 = break conditions
while (attempts < MAX_ITERATIONS) {
  try {
    const result = await step();
    if (result.isFinal) break;     // Final Answer
  } catch (e) {
    retries++;
    if (retries >= MAX_RETRIES) break; // 重试耗尽
  }
  attempts++;
}
// 循环结束 → max_iterations
```

## SimpleAgent 类

```python
class SimpleAgent:
    def __init__(self, client, model, tools, max_iterations=5, max_retries=2):
        self.client = client
        self.model = model
        self.tools = tools
        self.max_iterations = max_iterations
        self.max_retries = max_retries

    def run(self, task):
        history = ""
        steps = []
        for i in range(self.max_iterations):
            response = ask(...)
            parsed = parse_react_response(response)
            if parsed["type"] == "final":
                return {"answer": parsed["answer"], "steps": steps}
            elif parsed["type"] == "action":
                observation = self._execute_tool(parsed["name"], parsed["input"])
                history += f"Action: ...\nObservation: {observation}\n"
        return {"answer": "达到最大迭代次数"}
```

## JS 类比总览

| Python / Agent 概念 | JS 类比 |
|---------------------|---------|
| `class Agent` | `class Agent { constructor() {} async run() {} }` |
| `while i < max` | `while (attempts < MAX)` |
| `TOOLS = {"calc": fn}` | `const tools = { calc: fn }` |
| `re.search(pattern, text)` | `text.match(/pattern/)` |
| `try/except + retry` | `try/catch + for loop` |
| `parse_react_response` | `parseResponse(text)` 正则提取 |
| `history += observation` | `context.push(observation)` |

## 关键要点

1. **Agent = LLM + 工具 + 循环** — 让 AI 自主决策调用什么工具
2. **ReAct 模式** — Thought → Action → Observation 交替进行
3. **停止条件** — Final Answer / max_iterations / 工具失败，缺一不可
4. **不是万能的** — 简单任务直接调用更快更稳定
5. **工具注册表** — dict 映射工具名到函数，就像路由表

## 推荐资源

- [ReAct 论文](https://arxiv.org/abs/2210.03629)
- [Anthropic Tool Use 文档](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
- [LangChain Agent 概念](https://python.langchain.com/docs/concepts/agents/)
