# ===========================================
# Day 4: LangChain 基础 — 从原生 SDK 到框架
# ===========================================
# Day 1-3 你用原生 Anthropic SDK 直接调 API
# 现在学 LangChain — AI 应用开发的"React"
#
# 为什么要学？
# 1. 岗位高频要求（几乎所有 AI 应用岗都要求）
# 2. 生态丰富（Prompt 模板、记忆、Agent、RAG 全套）
# 3. 统一接口（换模型不用改业务代码）
#
# 类比：
# 原生 SDK = 原生 JS fetch API
# LangChain = Axios + React Query + Redux 全家桶
# ===========================================

# 安装（如果还没装）：
# pip install langchain langchain-openai

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).resolve().parent.parent))

# 加载环境变量
load_dotenv(Path(__file__).parent / ".env")


# ===========================================
# 1. 初始化 — 用 LangChain 连接模型
# ===========================================
# LangChain 用 ChatOpenAI 连接 OpenAI 兼容 API
# 我们的代理 API 兼容 OpenAI 协议，所以用 ChatOpenAI 就行
#
# JS 类比：
# 原生 SDK = new Anthropic({ apiKey, baseURL })
# LangChain = 像换了一个统一的 HTTP client，底层帮你封装好了

print("=== 1. 初始化 LangChain ===\n")

from langchain_openai import ChatOpenAI

# ChatOpenAI 支持任何 OpenAI 兼容的 API
llm = ChatOpenAI(
    model=os.getenv("MINIMAX_MODEL_NAME"),
    api_key=os.getenv("MINIMAX_API_KEY"),
    base_url=os.getenv("MINIMAX_API_BASE"),
    max_tokens=500,
)

# 最简单的调用 — 直接传字符串
# response = llm.invoke("你好，用一句话介绍你自己")
# print(f"回复: {response.content}")
# print(f"类型: {type(response)}")  # <class 'langchain_core.messages.ai.AIMessage'>

# 注意：LangChain 返回的不是纯文本，而是 AIMessage 对象
# response.content 才是文本内容
# 类比：axios 返回的是 response 对象，response.data 才是数据


# ===========================================
# 2. PromptTemplate — 模板化 Prompt
# ===========================================
# 原生 SDK: f"分析{language}代码：{code}" — 用 f-string 拼接
# LangChain: PromptTemplate — 把模板和变量分离，更好管理
#
# JS 类比：
# f-string = 模板字符串 `分析${language}代码：${code}`
# PromptTemplate = Handlebars/Mustache 模板引擎

print(f"\n{'='*50}")
print("=== 2. PromptTemplate ===\n")

from langchain_core.prompts import PromptTemplate

# 定义模板（{变量名} 是占位符）
translate_template = PromptTemplate.from_template(
    "把以下文本翻译成{target_lang}，只返回翻译结果：\n\n{text}"
)

# 格式化 — 填充变量生成最终 prompt
# prompt = translate_template.format(target_lang="英语", text="今天天气真好")
# print(f"生成的 Prompt: {prompt}")
# response =  llm.invoke(prompt)  # 直接传给模型
# print(f"翻译结果: {response.content}\n {response}")
# 也可以直接传给模型（invoke 时传变量）
# result = (translate_template | llm).invoke({"target_lang": "日语", "text": "你好世界"})
# print(f"翻译结果: {result.content}")

# PromptTemplate 的好处：
# 1. 模板和数据分离，方便管理和测试
# 2. 可以复用同一个模板处理不同输入
# 3. 可以和 Chain 组合使用（后面会讲）


# ===========================================
# 3. ChatPromptTemplate — 多角色消息模板
# ===========================================
# 之前的 PromptTemplate 生成的是一个字符串
# ChatPromptTemplate 生成的是 [system, human, ai] 消息列表
# 对应原生 SDK 里 messages 数组的结构
#
# JS 类比：
# PromptTemplate = 生成一个 string
# ChatPromptTemplate = 生成一个 messages[] 数组

print(f"\n{'='*50}")
print("=== 3. ChatPromptTemplate ===\n")

from langchain_core.prompts import ChatPromptTemplate

# 方式一：用元组列表定义（推荐，简洁）
chat_template = ChatPromptTemplate.from_messages([
    ("system", "你是一个{role}，用{style}的语气回答问题。"),
    ("human", "{question}"),
])

# 看看生成了什么
# messages = chat_template.format_messages(
#     role="资深前端工程师",
#     style="简洁专业",
#     question="React 和 Vue 怎么选？"
# )
# for msg in messages:
#     print(f"  [{msg.type}] {msg.content}")

# 方式二：直接传给模型
# result = (chat_template | llm).invoke({
#     "role": "资深前端工程师",
#     "style": "简洁专业",
#     "question": "React 和 Vue 怎么选？",
# })
# print(f"\n回复: {result.content}")


# ===========================================
# 4. Output Parser — 解析 AI 的输出
# ===========================================
# 原生 SDK: response.content[0].text → 手动 json.loads
# LangChain: OutputParser → 自动帮你解析成想要的格式
#
# JS 类比：
# 手动解析 = JSON.parse(response.data)
# OutputParser = zod + 自动 parse，还能生成格式说明给 AI

print(f"\n{'='*50}")
print("=== 4. Output Parser ===\n")

from langchain_core.output_parsers import StrOutputParser, JsonOutputParser

# --- 4.1 StrOutputParser：直接拿文本 ---
# 最常用，把 AIMessage 对象变成纯字符串
str_parser = StrOutputParser()

# 没有 parser: llm.invoke("你好") → AIMessage(content="你好呀")
# 有 parser:   (llm | str_parser).invoke("你好") → "你好呀"

# chain = llm | str_parser
# result = chain.invoke("1+1等于几？直接回答数字")
# print(f"StrOutputParser 结果: {result}")
# print(f"类型: {type(result)}")  # <class 'str'>

# --- 4.2 JsonOutputParser：解析 JSON ---
# 自动把 AI 的 JSON 文本解析成 Python dict
#
# 关键：配合 Pydantic 模型才真正有用
# 它会自动生成字段说明（名称、类型），省得你在 prompt 里手写格式要求
# 如果不传 Pydantic 模型，它只会说 "Return a JSON object"，没什么用

from pydantic import BaseModel

class ProductInfo(BaseModel):
    """商品信息"""
    name: str       # 商品名称
    price: float    # 价格
    color: str      # 颜色
    storage: str    # 存储容量

json_parser = JsonOutputParser(pydantic_object=ProductInfo)

# 看看自动生成的格式说明 — 包含了每个字段的名称和类型
# print(f"格式说明:\n{json_parser.get_format_instructions()}")
# 输出类似：
# Return a JSON object with the following schema:
# {"name": string, "price": number, "color": string, "storage": string}
#
# 这段文字会被塞进 prompt，AI 就知道该返回什么结构了
# 不用你手动写 {{"name": "商品名", "price": 数字, ...}} 了

extract_template = ChatPromptTemplate.from_messages([
    ("system", "从用户描述中提取商品信息。\n{format_instructions}"),
    ("human", "{text}"),
])

print(json_parser.get_format_instructions(), "pppppppp")
# chain = extract_template | llm | json_parser
# result = chain.invoke({
#     "text": "iPhone 15 Pro 256GB 黑色 8999元",
#     "format_instructions": json_parser.get_format_instructions(),
# })
# print(f"JsonOutputParser 结果: {result}")
# print(f"类型: {type(result)}")  # <class 'dict'>


# ===========================================
# 5. LCEL — LangChain 的管道语法（⭐ 核心）
# ===========================================
# LCEL = LangChain Expression Language
# 用 | (pipe) 把组件串起来，数据从左到右流过每个组件
#
# prompt | model | parser
#   ↓       ↓       ↓
# 生成消息 → 调 API → 解析结果
#
# JS 类比：
# RxJS:   of(data).pipe(map(fn1), map(fn2), map(fn3))
# Lodash: _.chain(data).map(fn1).filter(fn2).value()
# Linux:  cat file | grep pattern | sort | uniq

print(f"\n{'='*50}")
print("=== 5. LCEL 管道语法 ===\n")

# --- 5.1 基础 Chain ---
# prompt → model → parser 三件套
basic_chain = (
    ChatPromptTemplate.from_messages([
        ("system", "你是一个代码助手，用简洁的中文回答。"),
        ("human", "{question}"),
    ])
    | llm
    | StrOutputParser()
)

# result = basic_chain.invoke({"question": "Python 的 list 和 tuple 有什么区别？"})
# print(f"基础 Chain 结果: {result}")

# --- 5.2 带变量的 Chain ---
# 复用同一个 chain，传不同参数
translator_chain = (
    PromptTemplate.from_template(
        "把以下文本翻译成{target_lang}，只返回翻译结果：\n{text}"
    )
    | llm
    | StrOutputParser()
)

# result_en = translator_chain.invoke({"target_lang": "英语", "text": "今天天气真好"})
# result_ja = translator_chain.invoke({"target_lang": "日语", "text": "今天天气真好"})
# print(f"英语: {result_en}")
# print(f"日语: {result_ja}")

# --- 5.3 Chain 组合 — 把多个 Chain 串起来 ---
# 场景：先提取关键词，再根据关键词写文章

from langchain_core.runnables import RunnableLambda

# 第一步：提取关键词
keyword_chain = (
    PromptTemplate.from_template("从以下文本中提取3个关键词，用逗号分隔：\n{text}")
    | llm
    | StrOutputParser()
)

# 第二步：根据关键词生成摘要
summary_chain = (
    PromptTemplate.from_template("根据以下关键词写一段50字的摘要：\n关键词：{keywords}")
    | llm
    | StrOutputParser()
)

# 串起来：text → 关键词 → 摘要
# RunnableLambda 就是一个普通函数，把上一步的结果转成下一步需要的格式
# 类比 JS: .then(keywords => ({ keywords }))
combined_chain = (
    keyword_chain
    | RunnableLambda(lambda keywords: {"keywords": keywords})
    | summary_chain
)

# result = combined_chain.invoke({"text": "人工智能正在改变软件开发方式，从代码补全到自动测试"})
# print(f"组合 Chain 结果: {result}")


# ===========================================
# 6. 对话记忆 — 让 AI 记住上下文
# ===========================================
# 原生 SDK: 手动维护 messages 列表
# LangChain: 内置记忆组件，自动管理
#
# JS 类比：
# 原生 = 自己维护 state（useState 管理聊天记录）
# LangChain = 用 Redux/Zustand 管理，自动同步

print(f"\n{'='*50}")
print("=== 6. 对话记忆 ===\n")

from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# 存储每个 session 的聊天记录
store = {}


def get_session_history(session_id: str):
    """根据 session_id 获取或创建聊天历史"""
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]


# 创建带记忆的 chain
chat_chain = (
    ChatPromptTemplate.from_messages([
        ("system", "你是一个友好的助手，用简洁的中文回答。"),
        ("placeholder", "{history}"),  # 这里会自动插入历史消息
        ("human", "{input}"),
    ])
    | llm
    | StrOutputParser()
)

chain_with_memory = RunnableWithMessageHistory(
    chat_chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)

# 测试对话记忆
# config = {"configurable": {"session_id": "user_001"}}
#
# r1 = chain_with_memory.invoke({"input": "我叫张三"}, config=config)
# print(f"第一轮: {r1}")
#
# r2 = chain_with_memory.invoke({"input": "我叫什么名字？"}, config=config)
# print(f"第二轮: {r2}")  # AI 应该记得你叫张三
#
# r3 = chain_with_memory.invoke({"input": "我叫什么？"}, config={"configurable": {"session_id": "user_002"}})
# print(f"新 session: {r3}")  # 新 session 不知道你叫什么


# ===========================================
# 7. 实战：用 LangChain 重写 Day 1 的对话应用
# ===========================================
# Day 1 用原生 SDK 写了代码审查器
# 现在用 LangChain 重写，对比差异

print(f"\n{'='*50}")
print("=== 7. 用 LangChain 重写 Day 1 应用 ===\n")

# --- 7.1 代码审查器 (原生 SDK 版回忆) ---
# def review_code(code, language="Python"):
#     response = client.messages.create(
#         model=MODEL, max_tokens=500,
#         system="你是代码审查员...",
#         messages=[{"role": "user", "content": f"审查这段{language}代码：\n{code}"}]
#     )
#     return response.content[0].text

# --- 7.2 代码审查器 (LangChain 版) ---
code_review_chain = (
    ChatPromptTemplate.from_messages([
        ("system", """你是一个资深代码审查员。
审查规则：
1. 找出代码问题（bug、性能、安全）
2. 每个问题给出：问题描述 → 影响 → 修复建议
3. 如果没问题就说"代码看起来不错"
4. 用中文回答，简洁明了"""),
        ("human", "审查这段 {language} 代码：\n```{language}\n{code}\n```"),
    ])
    | llm
    | StrOutputParser()
)

# 测试
# result = code_review_chain.invoke({
#     "language": "Python",
#     "code": """
# def get_user(id):
#     query = f"SELECT * FROM users WHERE id = {id}"
#     return db.execute(query)
# """
# })
# print(f"审查结果:\n{result}")

# --- 7.3 带记忆的多轮代码审查 ---
review_with_memory = RunnableWithMessageHistory(
    ChatPromptTemplate.from_messages([
        ("system", "你是一个资深代码审查员，帮助用户改进代码。用中文简洁回答。"),
        ("placeholder", "{history}"),
        ("human", "{input}"),
    ]) | llm | StrOutputParser(),
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)

# config = {"configurable": {"session_id": "review_session"}}
# r1 = review_with_memory.invoke({"input": "帮我审查这段代码：\ndef add(a, b): return a + b"}, config=config)
# print(f"第一轮: {r1}\n")
# r2 = review_with_memory.invoke({"input": "怎么加上类型提示？"}, config=config)
# print(f"第二轮: {r2}")


# ===========================================
# 总结
# ===========================================

print(f"\n{'='*50}")
print("=== 总结 ===")
print("""
LangChain 核心概念：

1. ChatOpenAI       — 统一的模型接口，换模型不改代码
2. PromptTemplate   — 模板化 Prompt，分离模板和数据
3. OutputParser     — 自动解析 AI 输出（文本/JSON/Pydantic）
4. LCEL (|管道)     — prompt | model | parser 串联组件
5. MessageHistory   — 对话记忆，AI 记住上下文

原生 SDK vs LangChain：
| 原生 SDK          | LangChain                  |
|-------------------|----------------------------|
| 手动拼 messages   | PromptTemplate 自动生成    |
| 手动 json.loads   | OutputParser 自动解析      |
| 手动维护历史      | MessageHistory 自动管理    |
| 换模型改代码      | 换 LLM 对象即可           |

下一课：Day 5 LangChain Agent + Tool
""")
