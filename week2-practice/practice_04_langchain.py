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


# --- 题目 1: PromptTemplate 翻译器 ---

# TODO 1.1: 用 PromptTemplate 写一个翻译器
# - 创建模板：把 {text} 翻译成 {target_lang}
# - 用 LCEL 串联：template | llm | StrOutputParser()
# - 测试：翻译 "今天天气真好" 到英语和日语
# 测试:
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


# --- 题目 3: LCEL 组合 Chain ---

# TODO 3.1: 用 LCEL 写一个 "文本 → 关键词 → 标题" 的两步 chain
# - 第一步 chain: 从文本中提取 3 个关键词
# - 第二步 chain: 根据关键词生成一个吸引眼球的标题
# - 串起来执行
# 测试:
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
