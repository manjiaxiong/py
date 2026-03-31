# ===========================================
# Day 3: 虚拟环境 + pip + 第一次调用 AI API (Claude Anthropic 兼容)
# ===========================================
#
# 运行本文件前，请先完成以下步骤：
#
# 【第一步：创建并激活虚拟环境】
#
#   Windows Git Bash / MSYS2:
#     python -m venv venv
#     source venv/Scripts/activate
#
#   Windows CMD:
#     python -m venv venv
#     venv\Scripts\activate
#
#   Windows PowerShell:
#     python -m venv venv
#     venv\Scripts\Activate.ps1
#
#   激活成功后，终端提示符前面会出现 (venv)
#
# 【第二步：安装依赖】
#
#   pip install httpx python-dotenv anthropic
#
# 【第三步：创建 .env 文件】
#
#   在 week1-python-ai-basics 文件夹下创建 .env 文件，写入：
#   MINIMAX_API_KEY=你的 Claude Key
#
# ===========================================


# ----- 1. 环境变量管理 -----
# 类比前端: process.env.API_KEY
# Python: os.environ["API_KEY"] 或用 python-dotenv 加载 .env

import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")
base_url = os.getenv("ANTHROPIC_BASE_URL")
model_name = os.getenv("MODEL_NAME", "claude-opus-4-6")
if not api_key:
    print("⚠ 未找到 ANTHROPIC_API_KEY，请检查 .env 文件")
    exit(1)

# 安全地打印 key（只显示前10位）
print(f"API Key 已加载: {api_key[:10]}...")
print(f"API 接口: {base_url}")


# ----- 2. 用 httpx 直接调用 API（理解 HTTP 层） -----
# 类比前端: fetch() 或 axios
# Python: httpx（比 requests 更现代，支持 async）

import httpx
import anthropic

def call_claude_raw():
    """用 httpx 直接发 HTTP 请求调用 API — 理解底层原理"""

    url = f"{base_url}/v1/messages"

    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }

    # 请求体 — 类似前端发 POST 请求
    body = {
        "model": model_name,
        "max_tokens": 200,
        "system": "你是一个帮助前端工程师学习 Python 的助手，回答简洁。",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "用一句话解释什么是 Python 的虚拟环境，用前端开发者能理解的比喻。"
                    }
                ]
            }
        ]
    }

    print("=== 方式一：httpx 直接调用 ===")
    print("发送请求中...")

    response = httpx.post(url, headers=headers, json=body, timeout=30)

    if response.status_code == 200:
        data = response.json()
        print_message_blocks(data["content"], "Claude")
        print(f"\nToken 使用: 输入 {data['usage']['input_tokens']}, 输出 {data['usage']['output_tokens']}")
    else:
        print(f"请求失败: {response.status_code}")
        print(response.text)

# ----- 3. 用官方 SDK 调用（推荐方式） -----
# 类比: 直接用 fetch 调 API vs 用封装好的 SDK
# SDK 帮你处理了认证、重试、类型等

def create_client():
    """创建 Anthropic 客户端（通过 UCloud 中转）"""
    return anthropic.Anthropic(
        api_key=api_key,
        base_url=base_url
    )

def print_message_blocks(blocks, label="Claude"):
    """处理 httpx 返回的内容块"""
    for block in blocks:
        if block["type"] == "thinking":
            print(f"{label} Thinking:\n{block['thinking']}\n")
        elif block["type"] == "text":
            print(f"{label} Text:\n{block['text']}\n")

def print_sdk_message(message, label="Claude"):
    """处理 Anthropic SDK 返回的内容块"""
    for block in message.content:
        if block.type == "thinking":
            print(f"{label} Thinking:\n{block.thinking}\n")
        elif block.type == "text":
            print(f"{label} Text:\n{block.text}\n")

# call_claude_raw()

def call_claude_sdk():
    """用 Anthropic 官方 SDK 调用 — 实际开发中推荐"""

    client = create_client()

    print("\n=== 方式二：官方 SDK 调用 ===")

    message = client.messages.create(
        model=model_name,
        max_tokens=200,
        system="You are a helpful assistant.",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "用 3 个要点总结 Python 和 JavaScript 的主要区别。"
                    }
                ]
            }
        ]
    )

    print_sdk_message(message)
    print(f"\nToken: 输入 {message.usage.input_tokens}, 输出 {message.usage.output_tokens}")
    print(f"停止原因: {message.stop_reason}")  # end_turn 表示正常结束

# call_claude_sdk()


# ----- 4. System Prompt — 设定 AI 的角色 -----

def call_with_system_prompt():
    """System Prompt 相当于给 AI 一个角色设定"""

    client = create_client()

    print("\n=== System Prompt 示例 ===")

    message = client.messages.create(
        model=model_name,
        max_tokens=300,
        system="你是一个专门帮助前端工程师学习 Python 的导师。回答要简洁，多用 JS 对比。",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Python 的装饰器是什么？"
                    }
                ]
            }
        ]
    )

    print_sdk_message(message)

# call_with_system_prompt()


# ----- 5. 多轮对话 -----

def multi_turn_chat():
    """多轮对话 — messages 数组中交替放 user 和 assistant 消息"""

    client = create_client()

    print("\n=== 多轮对话 ===")

    # 类比前端: 维护一个消息数组，每次发送时带上历史
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "我正在学 Python，之前写 JavaScript。"}
            ]
        },
        {
            "role": "assistant",
            "content": [
                {"type": "text", "text": "很好！JS 转 Python 很顺畅，语法有不少相似之处。有什么具体想了解的吗？"}
            ]
        },
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Python 的 list 和 JS 的 Array 有什么区别？"}
            ]
        }
    ]

    message = client.messages.create(
        model=model_name,
        max_tokens=300,
        messages=messages
    )

    print_sdk_message(message)

# multi_turn_chat()


# ----- 6. 流式输出（重要！） -----

def stream_chat():
    """
    流式输出 — AI 应用的核心体验
    类比前端: SSE (Server-Sent Events) 或 ReadableStream
    不用等全部生成完，逐字输出给用户
    """

    client = create_client()
    messages = []

    print("\n=== 流式对话（输入 q 退出） ===")

    while True:
        user_input = input("\n你: ").strip()
        if user_input.lower() == "q":
            print("再见！")
            break
        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})

        try:
            print("Claude: ", end="", flush=True)

            # stream=True 开启流式
            with client.messages.stream(
                model=model_name,
                max_tokens=200,
                messages=messages
            ) as stream:
                full_reply = ""
                for text in stream.text_stream:
                    print(text, end="", flush=True)  # 逐字打印，flush 确保立即显示
                    full_reply += text

            print()  # 换行

            # 把 AI 回复加入历史，实现多轮对话
            messages.append({"role": "assistant", "content": full_reply})
        except Exception as e:
            print(f"\n请求出错: {e}")
            messages.pop()  # 移除刚才添加的 user 消息，避免污染对话历史

# stream_chat()


# ===========================================
# 练习
# ===========================================

# TODO 1: 写一个函数 ask_claude(question: str) -> str
# - 用 SDK 调用 Claude
# - 设置 system prompt 为 "用中文简洁回答，50字以内"
# - 返回回复文本
def ask_claude(question: str) -> str:
    client = create_client()
    
    message = client.messages.create(
        model=model_name,
        max_tokens=100,
        system="用中文简洁回答，50字以内。",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": question
                    }
                ]
            }
        ]
    )
    # print(f"Token 使用: 输入 {message}")
    print_sdk_message(message)

# ask_claude("Python 的 GIL 是什么？")

# TODO 2: 写一个简单的命令行聊天机器人
# - 用 while 循环不断接收用户输入（input() 函数）
# - 输入 "quit" 退出
# - 维护 messages 列表实现多轮对话
# - 用流式输出显示回复
def chat_bot():
    client = create_client()
    messages = []
    print("=== Claude 聊天机器人 ===")
    print("输入 'quit' 退出\n")
    while True:
        user_input = input("你: ").strip()
        if user_input.lower() == "quit":
            print("再见！")
            break
        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})

        try:
            print("Claude: ", end="", flush=True)
            with client.messages.stream(
                model=model_name,
                max_tokens=200,
                messages=messages
            ) as stream:
                full_reply = ""
                for text in stream.text_stream:
                    print(text, end="", flush=True)
                    full_reply += text

            print()  # 换行
            messages.append({"role": "assistant", "content": full_reply})
        except Exception as e:
            print(f"\n请求出错: {e}")
            messages.pop()  # 移除刚才添加的 user 消息，避免污染对话历史


# 取消注释测试:
# print(ask_claude("Python 的 GIL 是什么？"))
chat_bot()
