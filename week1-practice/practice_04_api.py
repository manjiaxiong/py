# ===========================================
# 练习 4：AI API 调用（对应 Day 3 + Day 4）
# ===========================================
# 不看教程，自己写！
# 你需要自己完成: 加载 .env、创建客户端、调用 API、处理返回
# ===========================================


# TODO 0: 自己写出完整的初始化代码
# - 导入需要的库 (os, dotenv, anthropic)
# - 加载 .env
# - 读取 MINIMAX_API_KEY, MINIMAX_API_BASE, MINIMAX_MODEL_NAME
# - 创建 anthropic 客户端
# 不要复制粘贴！自己写！
import os
from dotenv import load_dotenv
from anthropic import Client

# 加载 .env 文件
load_dotenv()

# 读取环境变量
api_key = os.getenv("MINIMAX_API_KEY")
api_base = os.getenv("MINIMAX_API_BASE")
model_name = os.getenv("MINIMAX_MODEL_NAME")
print(f"API Key: {api_key}")
print(f"API Base: {api_base}") 
print(f"Model Name: {model_name}")
# 创建 anthropic 客户端
client = Client(
    api_key=api_key,
    base_url=api_base
)
# --- 题目 1: 多角色对话 ---

# TODO 1.1: 写一个函数 role_play(role_description, question)
# - 用 system prompt 设定角色
# - 调用 API 获取回答
# - 返回回答文本
# 测试:
# print(role_play("你是一个严格的代码审查员", "帮我看看 for i in range(len(arr)) 这行代码"))
# print(role_play("你是一个鼓励型的编程导师", "我总是记不住 Python 语法怎么办"))
# --- 题目 2: 流式输出封装 ---
def role_play(role_description, question):
    messages = [
        {"role": "system", "content": role_description},
        {"role": "user", "content": question}
    ]
    response = client.messages.create(
        max_tokens=200,
        model=model_name,
        messages=messages
    )
    result = ""
    for block in response.content:
        if block.type == "text":
            text = block.text.strip()
            print(text, end="", flush=True)  # 逐字打印
            result += text
    print()  # 打印完成后换行
    return result
role_play("你是一个严格的代码审查员", "帮我看看 for i in range(len(arr)) 这行代码")
role_play("你是一个鼓励型的编程导师", "我总是记不住 Python 语法怎么办")
# TODO 2.1: 写一个函数 stream_ask(question, system="")
# - 流式调用 API
# - 逐字打印回复
# - 返回完整回复文本
# - 要有异常处理
def stream_ask(question, system=""):
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": question})
    try:
        response = client.messages.create(
            max_tokens=200,
            model=model_name,
            messages=messages
        )
        result = ""
        for block in response.content:
            if block.type == "text":
                text = block.text.strip()
                print(text, end="", flush=True)  # 逐字打印
                result += text
        print()  # 打印完成后换行
        return result
    except Exception as e:
        print(f"API 调用失败: {e}")
        return ""

# stream_ask("用一句话总结一下人工智能的定义", system="你是一个简洁明了的解释者")
# --- 题目 3: 带重试的 API 调用 ---

# TODO 3.1: 自己写一个 retry 装饰器（不看 Day 6 的代码）
# - 参数: max_retries, delay
# - 失败时打印错误信息并等待后重试
# - 超过次数后抛出异常

import time
import functools

def retry(max_retries=3, delay=2):
    """
    重试装饰器
    JS 类比: 就像一个高阶函数包装 fetch，失败了自动重试
    const retry = (maxRetries, delay) => (fn) => async (...args) => { ... }
    """
    def decorator(func):                    # 接收被装饰的函数
        @functools.wraps(func)              # 保留原函数的名字和文档
        def wrapper(*args, **kwargs):       # 接收任意参数
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)  # 调用原函数
                except Exception as e:
                    if attempt == max_retries:
                        print(f"❌ 已重试 {max_retries} 次，全部失败")
                        raise                     # 超过次数，抛出异常
                    print(f"⚠️ 第 {attempt + 1} 次失败: {e}，{delay}秒后重试...")
                    time.sleep(delay)
        return wrapper
    return decorator

# TODO 3.2: 用你写的 retry 装饰器装饰 stream_ask 函数

@retry(max_retries=3, delay=2)
def stream_ask_with_retry(question, system=""):
    return stream_ask(question, system)

# 测试:
# stream_ask_with_retry("你好，用一句话介绍Python")


# --- 题目 4: Few-shot 格式化器 ---

# TODO 4.1: 写一个函数 format_commit(description)
# - 用 few-shot prompting 把中文描述转成规范的 git commit message
# - 在 messages 中提供 2-3 个示例
# - 返回格式化后的 commit message
# 测试:
# print(format_commit("把用户列表从一次全部加载改成了分页加载"))
# print(format_commit("修复了 iOS 上日期选择器显示英文的问题"))
def format_commit(description):
    system = "你是一个 Git commit 信息生成器。根据用户描述的需求，生成规范的 commit message。"
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": "把这个需求转换成 Git commit 信息: 修复了登录页面在手机端输入框无法获取焦点的问题"},
        {"role": "assistant", "content": "fix: 修复登录页面在手机端输入框无法获取焦点的问题"},
        {"role": "user", "content": "把这个需求转换成 Git commit 信息: 优化了数据处理逻辑，提升了性能"},
        {"role": "assistant", "content": "perf: 优化数据处理逻辑，提升性能"},
    ]
    messages.append({"role": "user", "content": f"把这个需求转换成 Git commit 信息: {description}"})
    response = client.messages.create(
        max_tokens=100,
        model=model_name,
        messages=messages
    )
    result = ""
    for block in response.content:
        if block.type == "text":
            text = block.text.strip()
            print(text, end="", flush=True)  # 逐字打印
            result += text
    print()  # 打印完成后换行
    return result