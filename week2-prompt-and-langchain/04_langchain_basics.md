# Day 4：LangChain 基础 — 从原生 SDK 到框架

## 学习目标

掌握 LangChain 的核心概念和基本用法，理解它和原生 SDK 的区别。

## 为什么要学 LangChain？

Day 1-3 你用原生 Anthropic SDK 写了不少东西，完全够用。那为什么还要学 LangChain？

1. **岗位要求** — 国内几乎所有 AI 应用开发岗都要求 LangChain
2. **生态丰富** — Prompt 模板、记忆、Agent、RAG、向量库，全家桶
3. **统一接口** — 换模型（OpenAI → Claude → 国产模型）不用改业务代码
4. **社区活跃** — 遇到问题好搜索，第三方集成多

JS 类比：
- 原生 SDK = 原生 `fetch` API
- LangChain = Axios + React Query + Redux 全家桶

你可以不用它，但你得知道它。就像你可以不用 React，但面试不能说不会。

## 学习内容

### 1. 初始化 — ChatOpenAI

LangChain 用 `ChatOpenAI` 连接 OpenAI 兼容 API：

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="模型名",
    api_key="你的key",
    base_url="API地址",
)

response = llm.invoke("你好")
print(response.content)  # 注意：不是纯文本，是 AIMessage 对象
```

JS 类比：
```js
// 原生 SDK
const client = new Anthropic({ apiKey, baseURL })
const response = await client.messages.create({ model, messages })
response.content[0].text  // 取文本

// LangChain 等价物
const llm = new ChatOpenAI({ model, apiKey, baseUrl })
const response = await llm.invoke("你好")
response.content  // 取文本
```

### 2. PromptTemplate — 模板化 Prompt

把 Prompt 模板和变量分离，方便管理和复用：

```python
from langchain_core.prompts import PromptTemplate

template = PromptTemplate.from_template(
    "把以下文本翻译成{target_lang}：\n{text}"
)

# 填充变量
prompt = template.format(target_lang="英语", text="你好")
# → "把以下文本翻译成英语：\n你好"
```

JS 类比：
```js
// f-string = 模板字符串
const prompt = `把以下文本翻译成${targetLang}：\n${text}`

// PromptTemplate = Handlebars 模板
const template = Handlebars.compile("翻译成{{target_lang}}：\n{{text}}")
const prompt = template({ target_lang: "英语", text: "你好" })
```

**为什么不直接用 f-string？** 模板可以序列化保存、版本管理、和 Chain 组合。小项目无所谓，大项目有用。

### 3. ChatPromptTemplate — 多角色消息模板

生成 `[system, human, ai]` 消息列表，对应原生 SDK 的 messages 数组：

```python
from langchain_core.prompts import ChatPromptTemplate

template = ChatPromptTemplate.from_messages([
    ("system", "你是{role}，用{style}语气回答。"),
    ("human", "{question}"),
])
```

JS 类比：
```js
// 原生 SDK 手动构建 messages
const messages = [
    { role: "system", content: `你是${role}` },
    { role: "user", content: question },
]
```

### 4. Output Parser — 解析输出

自动把 AI 的回复解析成你要的格式：

| Parser | 输入 | 输出 | 用途 |
|--------|------|------|------|
| `StrOutputParser` | AIMessage | str | 拿纯文本 |
| `JsonOutputParser` | AIMessage | dict | 拿 JSON |

```python
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser

# AIMessage → str
str_parser = StrOutputParser()

# AIMessage → dict（自动 json.loads）
json_parser = JsonOutputParser()
```

JS 类比：
```js
// 没有 parser
const response = await llm.invoke("你好")  // AIMessage 对象
response.content  // 手动取

// 有 parser（自动取）
const chain = llm.pipe(new StrOutputParser())
const text = await chain.invoke("你好")  // 直接是 string
```

### 5. LCEL — 管道语法（核心）

LCEL = LangChain Expression Language，用 `|` 把组件串起来：

```python
chain = prompt | model | parser
result = chain.invoke({"question": "你好"})
```

数据流向：
```
输入变量 → PromptTemplate → ChatOpenAI → OutputParser → 最终结果
         (生成消息)       (调 API)     (解析输出)
```

JS 类比：
```js
// RxJS pipe
of(data).pipe(map(fn1), map(fn2), map(fn3))

// Lodash chain
_.chain(data).map(fn1).filter(fn2).value()

// Linux pipe
cat file | grep pattern | sort | uniq
```

**这是 LangChain 最重要的概念** — 所有组件都可以用 `|` 串联。

### 6. 对话记忆

让 AI 记住之前聊过什么：

```python
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# 创建带记忆的 chain
chain_with_memory = RunnableWithMessageHistory(
    chat_chain,
    get_session_history,  # 根据 session_id 获取历史
    input_messages_key="input",
    history_messages_key="history",
)

# 调用时带 session_id
config = {"configurable": {"session_id": "user_001"}}
chain_with_memory.invoke({"input": "我叫张三"}, config=config)
chain_with_memory.invoke({"input": "我叫什么？"}, config=config)  # AI 记得
```

JS 类比：
```js
// 原生 SDK = 手动维护 state
const [messages, setMessages] = useState([])

// LangChain = 框架帮你管理
// 类似 Redux：dispatch(action) 自动更新 store
```

## 原生 SDK vs LangChain 对比

| 操作 | 原生 SDK | LangChain |
|------|---------|-----------|
| 初始化 | `Anthropic(api_key=...)` | `ChatOpenAI(api_key=...)` |
| 调用 | `client.messages.create(messages=[...])` | `llm.invoke("你好")` |
| 取文本 | `response.content[0].text` | `response.content` 或 `StrOutputParser` |
| 拼 Prompt | f-string 手动拼 | `PromptTemplate` |
| 解析 JSON | `json.loads()` 手动 | `JsonOutputParser` 自动 |
| 对话记忆 | 手动维护 messages 列表 | `RunnableWithMessageHistory` |
| 串联流程 | 手动写函数调用链 | `prompt \| model \| parser` |
| 换模型 | 改代码 | 换 LLM 对象 |

## 什么时候用原生 SDK，什么时候用 LangChain？

| 场景 | 推荐 |
|------|------|
| 快速原型 / 简单脚本 | 原生 SDK |
| 正式项目 / 多人协作 | LangChain |
| 需要 Agent / RAG | LangChain |
| 追求最小依赖 | 原生 SDK |
| 面试 / 求职 | 两个都要会 |

## 关键要点

1. **LCEL 是核心** — `prompt | model | parser` 管道语法，所有组件都能串
2. **PromptTemplate 分离关注点** — 模板归模板，数据归数据
3. **OutputParser 省心** — 不用手动 `json.loads` 了
4. **记忆靠 session_id** — 不同用户不同 session，互不干扰
5. **LangChain 不是银弹** — 简单场景原生 SDK 更直接，复杂场景 LangChain 更省事

## 推荐资源

- [LangChain 官方文档](https://python.langchain.com/docs/introduction/)
- [LCEL 概念讲解](https://python.langchain.com/docs/concepts/lcel/)
- [LangChain + OpenAI 兼容 API](https://python.langchain.com/docs/integrations/chat/openai/)
