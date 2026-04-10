# ===========================================
# 练习 4：LangChain 基础（对应 Day 4）
# ===========================================
# 不看教程，自己写！
# 卡住了再回去看 04_langchain_basics.py
# ===========================================

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

# TODO 0: 初始化 ChatOpenAI（自己写）
# - 导入 ChatOpenAI
# - 用 .env 里的 MINIMAX_API_KEY / MINIMAX_API_BASE / MINIMAX_MODEL_NAME
# - 创建 llm 对象

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.runnables import RunnableLambda
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from pydantic import BaseModel, Field
from typing import List

llm = ChatOpenAI(
    model=os.getenv("MINIMAX_MODEL_NAME"),
    api_key=os.getenv("MINIMAX_API_KEY"),
    base_url=os.getenv("MINIMAX_API_BASE"),
    max_tokens=500,
)


# --- 题目 1: PromptTemplate 翻译器 ---

# TODO 1.1: 用 PromptTemplate 写一个翻译器
# - 创建模板：把 {text} 翻译成 {target_lang}
# - 用 LCEL 串联：template | llm | StrOutputParser()
# - 测试：翻译 "今天天气真好" 到英语和日语
# 测试:
# print(translate("今天天气真好", "英语"))
# print(translate("今天天气真好", "日语"))

translate_template = PromptTemplate.from_template(
    "把以下文本翻译成{target_lang}，只返回翻译结果，不要加解释：\n\n{text}"
)

translate_chain = translate_template | llm | StrOutputParser()


def translate(text, target_lang):
    return translate_chain.invoke({"text": text, "target_lang": target_lang})


# print("=== 题目 1: 翻译器 ===")
# print(translate("今天天气真好", "英语"))
# print(translate("今天天气真好", "日语"))


# --- 题目 2: ChatPromptTemplate + JsonOutputParser ---

# TODO 2.1: 用 ChatPromptTemplate + JsonOutputParser 做结构化提取
# - system: "你是数据提取助手，从文本中提取人物信息，返回 JSON"
# - human: "{text}"
# - 用 JsonOutputParser 自动解析
# - 串成 chain: template | llm | json_parser
# 测试:
# print(extract_person("张三，28岁，在深圳做前端开发"))
# print(extract_person("李四，35岁，北京的产品经理，清华毕业"))


class PersonInfo(BaseModel):
    """人物信息"""
    name: str = Field(description="姓名")
    age: int = Field(description="年龄")
    city: str = Field(description="所在城市")
    job: str = Field(description="职业")


json_parser = JsonOutputParser(pydantic_object=PersonInfo)

extract_template = ChatPromptTemplate.from_messages([
    ("system", "你是数据提取助手，从文本中提取人物信息。\n{format_instructions}"),
    ("human", "{text}"),
])

extract_chain = extract_template | llm | json_parser


def extract_person(text):
    return extract_chain.invoke({
        "text": text,
        "format_instructions": json_parser.get_format_instructions(),
    })


# print("\n=== 题目 2: 结构化提取 ===")
# print(extract_person("张三，28岁，在深圳做前端开发"))
# print(extract_person("李四，35岁，北京的产品经理，清华毕业"))


# --- 题目 3: LCEL 组合 Chain ---

# TODO 3.1: 用 LCEL 写一个 "文本 → 关键词 → 标题" 的两步 chain
# - 第一步 chain: 从文本中提取 3 个关键词
# - 第二步 chain: 根据关键词生成一个吸引眼球的标题
# - 串起来执行
# 测试:
# print(generate_title("人工智能正在改变前端开发方式，越来越多的公司开始用 AI 辅助编程"))

keyword_template = PromptTemplate.from_template(
    "从以下文本中提取 3 个关键词，用逗号分隔，只返回关键词：\n\n{text}"
)

title_template = PromptTemplate.from_template(
    "根据以下关键词生成一个吸引眼球的文章标题，只返回标题：\n\n关键词：{keywords}"
)

keyword_chain = keyword_template | llm | StrOutputParser()
title_chain = title_template | llm | StrOutputParser()

# 组合：keyword_chain 输出字符串 → 转成 dict → 传给 title_chain
combined_chain = (
    keyword_chain
    | RunnableLambda(lambda keywords: {"keywords": keywords})
    | title_chain
)


def generate_title(text):
    return combined_chain.invoke({"text": text})


# print("\n=== 题目 3: LCEL 组合 Chain ===")
# print(generate_title("人工智能正在改变前端开发方式，越来越多的公司开始用 AI 辅助编程"))


# --- 题目 4: 对话记忆 ---

# TODO 4.1: 实现一个带记忆的多轮对话
# - 用 InMemoryChatMessageHistory 存储历史
# - 用 RunnableWithMessageHistory 包装 chain
# - 支持 session_id 区分不同用户
# 测试:
# chat("我叫小明，我是前端工程师", session_id="user1")
# chat("我叫什么？做什么的？", session_id="user1")      # 应该记得
# chat("我叫什么？", session_id="user2")                # 新 session，不知道

chat_template = ChatPromptTemplate.from_messages([
    ("system", "你是一个友好的助手，记住用户告诉你的信息。"),
    ("placeholder", "{history}"),
    ("human", "{input}"),
])

chat_chain = chat_template | llm | StrOutputParser()

# 用 dict 存储每个 session 的历史
session_store = {}


def get_session_history(session_id):
    if session_id not in session_store:
        session_store[session_id] = InMemoryChatMessageHistory()
    return session_store[session_id]


chain_with_history = RunnableWithMessageHistory(
    chat_chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)


def chat(message, session_id="default"):
    result = chain_with_history.invoke(
        {"input": message},
        config={"configurable": {"session_id": session_id}},
    )
    print(f"[{session_id}] 用户: {message}")
    print(f"[{session_id}] AI: {result}\n")
    return result


# print("\n=== 题目 4: 对话记忆 ===")
# chat("我叫小明，我是前端工程师", session_id="user1")
# chat("我叫什么？做什么的？", session_id="user1")
# chat("我叫什么？", session_id="user2")


# --- 题目 5: 用 LangChain 重写 Day 1 的 demo ---

# TODO 5.1: 选 Day 1 的一个 demo，用 LangChain 重写
# 推荐选择：
# - commit message 生成器（输入 diff，输出 commit message）
# - 代码审查器（输入代码，输出审查建议）
# - 商品信息提取器（输入描述，输出 JSON）
#
# 要求：
# - 用 ChatPromptTemplate 定义 prompt
# - 用 LCEL 串联
# - 用合适的 OutputParser

# 选择：商品信息提取器（用 LangChain 重写）

class ProductInfo(BaseModel):
    """商品信息"""
    name: str = Field(description="商品名称")
    storage: str = Field(description="存储容量，如 256GB")
    color: str = Field(description="颜色")
    price: int = Field(description="价格（数字）")


product_parser = JsonOutputParser(pydantic_object=ProductInfo)

product_template = ChatPromptTemplate.from_messages([
    ("system", "你是一个商品信息提取器。从商品描述中提取结构化信息。\n{format_instructions}"),
    ("human", "{text}"),
])

product_chain = product_template | llm | product_parser


def extract_product(text):
    return product_chain.invoke({
        "text": text,
        "format_instructions": product_parser.get_format_instructions(),
    })


# print("\n=== 题目 5: 商品信息提取器（LangChain 版）===")
# print(extract_product("iPhone 15 Pro Max 256GB 钛金属色 官方价 9999 元"))
# print(extract_product("华为 Mate 60 Pro 512GB 雅丹黑 售价 6999 元"))
