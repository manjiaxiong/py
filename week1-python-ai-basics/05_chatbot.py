# ===========================================
# Day 5: 实战项目 — 命令行 AI 聊天机器人
# ===========================================
#
# 这是第一周的综合项目，把前 4 天学的知识串起来：
# - Python 基础语法（Day 1）
# - 类、模块、异步（Day 2）
# - API 调用、环境变量（Day 3）
# - Prompt 设计、流式输出（Day 4）
#
# 运行: python week1-python-ai-basics/05_chatbot.py
#
# ===========================================

# 注意这里的导入方式:
# 从 chatbot 包（文件夹）导入各个模块的内容
# 类比前端: import { Config } from './chatbot/config'
from chatbot.config import Config
from chatbot.client import ChatClient
from chatbot.commands import handle_command


def main():
    """聊天机器人主程序"""

    # 1. 加载配置
    try:
        config = Config.from_env()
    except ValueError as e:
        print(e)
        return

    print(f"模型: {config.model_name}")
    print(f"接口: {config.base_url}")

    # 2. 创建客户端
    chat_client = ChatClient(config)

    # 3. 欢迎信息
    print()
    print("╭──────────────────────────────────────╮")
    print("│       AI Chatbot — Day 5 实战项目     │")
    print("│    输入 /help 查看命令，quit 退出      │")
    print("╰──────────────────────────────────────╯")
    print()

    # 4. 主循环
    while True:
        try:
            user_input = input("你: ").strip()
        except (KeyboardInterrupt, EOFError):
            # Ctrl+C 或 Ctrl+D 退出
            print("\n再见！")
            break

        # 空输入跳过
        if not user_input:
            continue

        # 退出
        if user_input.lower() == "quit":
            print("再见！")
            break

        # 斜杠命令
        if user_input.startswith("/"):
            handle_command(user_input, chat_client)
            continue

        # 正常对话 — 流式输出
        try:
            print("AI: ", end="", flush=True)
            chat_client.stream_chat(user_input)
        except Exception as e:
            print(f"\n请求出错: {e}")
            print("   可以输入 /clear 清空历史后重试")


# Python 的入口判断
# 类比 Node.js: if (require.main === module)
# 只有直接运行这个文件时才执行 main()，被 import 时不执行
if __name__ == "__main__":
    main()
