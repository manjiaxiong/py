# Day 5：LangChain Agent + Tool — 让 AI 自主行动

## 学习目标

理解 Agent 的工作原理，学会用 LangChain 创建能调用工具的 Agent。

## Agent 是什么？

Day 4 你学了 Chain — 流程是固定的：`prompt → model → parser`。
Agent 不一样 — **AI 自己决定调什么工具、调几次、什么时候停**。

```
Chain：  输入 → 步骤1 → 步骤2 → 步骤3 → 输出（固定流水线）
Agent：  输入 → AI思考 → 调工具？→ 观察结果 → 够了吗？→ 不够再来 → 输出
```

JS 类比：
- Chain = Express 中间件链，按顺序执行
- Agent = 一个 while 循环，AI 自己控制什么时候 break

## 学习内容

### 1. ReAct 模式 — Agent 的工作循环

Agent 用 ReAct（Reasoning + Acting）模式工作：

```
用户: "北京天气怎么样？"

AI 思考(Reasoning): 用户问天气，我需要调 get_weather 工具
AI 行动(Acting):    调用 get_weather("北京")
观察(Observation):  返回 "晴，25°C"
AI 判断:            信息够了，可以回答了
AI 回答:            "北京今天晴，25°C"
```

如果一个问题需要多步：

```
用户: "北京天气怎么样？365天有多少小时？"

第一轮: 调 get_weather("北京") → "晴，25°C"
第二轮: 调 calculate("365*24") → "8760"
第三轮: 信息够了 → 最终回答
```

JS 类比：
```js
while (!done) {
  const action = ai.decide(question, previousResults)  // 思考
  const result = executeTool(action)                     // 行动
  if (ai.isSatisfied(result)) done = true               // 判断
}
```

### 2. 定义工具 — @tool 装饰器

LangChain 用 `@tool` 装饰器把普通函数变成工具：

```python
from langchain_core.tools import tool

@tool
def get_weather(city: str) -> str:
    """查询城市天气。当用户问天气相关问题时使用。

    Args:
        city: 城市名称，如 北京、上海
    """
    return f"{city}：晴，25°C"
```

对比 Day 2 原生写法：

| 原生 Tool Use | LangChain @tool |
|---------------|-----------------|
| 手动写 JSON Schema | 自动从函数签名生成 |
| `"name": "get_weather"` | 取函数名 |
| `"description": "..."` | 取 docstring |
| `"input_schema": {...}` | 取类型注解 |

**docstring 非常重要** — AI 根据它决定什么时候调用这个工具。写不清楚，AI 就会选错工具。

### 3. 创建 Agent

用 LangGraph 的 `create_react_agent`：

```python
from langgraph.prebuilt import create_react_agent

tools = [get_weather, calculate, search_product]

agent = create_react_agent(
    model=llm,
    tools=tools,
)

result = agent.invoke({
    "messages": [HumanMessage(content="北京天气怎么样？")]
})
print(result["messages"][-1].content)
```

### 4. 观察执行过程

用 `agent.stream()` 看 Agent 每一步在做什么：

```python
for step in agent.stream({"messages": [HumanMessage(content="...")]}):
    for node_name, node_output in step.items():
        if node_name == "agent":
            # AI 的决策（调工具 or 直接回答）
        elif node_name == "tools":
            # 工具执行结果
```

JS 类比：Redux DevTools 能看到每个 action 的派发过程。

### 5. Agent 的局限性

| 问题 | 表现 | 解决方法 |
|------|------|---------|
| 死循环 | 反复调同一个工具 | 设 max_iterations |
| 选错工具 | 用了不该用的工具 | description 写清楚 |
| 参数填错 | 传了错误参数 | Args docstring 写格式示例 |
| 幻觉 | 不调工具自己编答案 | system prompt 要求必须用工具 |
| 成本高 | 每轮循环都消耗 token | 简单任务用 Chain 不用 Agent |

## Chain vs Agent 怎么选？

| 场景 | 推荐 |
|------|------|
| 流程固定（翻译、提取、格式化） | Chain |
| 需要判断用哪个工具 | Agent |
| 多步骤、需要循环 | Agent |
| 追求稳定和低成本 | Chain |
| 开放式对话 + 工具 | Agent |

**原则：能用 Chain 解决的，别用 Agent。Agent 更灵活但更贵、更不稳定。**

## 原生 Tool Use vs LangChain Agent 对比

| 维度 | Day 2 原生 Tool Use | Day 5 LangChain Agent |
|------|---------------------|----------------------|
| 工具定义 | 手写 JSON Schema | @tool 自动生成 |
| 调用循环 | 手动写 if/while | Agent 自动循环 |
| 消息管理 | 手动拼 messages | 框架自动管理 |
| 多工具选择 | 手动路由 | AI 自动选择 |
| 控制力 | 高（什么都你定） | 中（框架有封装） |
| 代码量 | 多 | 少 |
| 适用场景 | 需要精确控制 | 快速搭建 |

## 关键要点

1. **Agent = AI 自主决策循环** — 不是固定流程，是 AI 判断做什么
2. **@tool 的 docstring 是关键** — AI 靠它选工具，写不好就选错
3. **能用 Chain 就别用 Agent** — Agent 更强但更贵更不稳定
4. **观察执行过程** — 用 stream 看 Agent 每步在干嘛，方便调试
5. **设置安全限制** — 防止死循环、防止幻觉

## 推荐资源

- [LangGraph Agent 文档](https://langchain-ai.github.io/langgraph/agents/)
- [LangChain Tools 文档](https://python.langchain.com/docs/concepts/tools/)
- [ReAct 论文](https://arxiv.org/abs/2210.03629)
