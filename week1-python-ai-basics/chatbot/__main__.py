from chatbot.config import Config
from chatbot.client import ChatClient
from chatbot.commands import handle_command


def main():
    """聊天机器人主程序"""

    try:
        config = Config.from_env()
    except ValueError as e:
        print(e)
        return

    print(f"模型: {config.model_name}")
    print(f"接口: {config.base_url}")

    chat_client = ChatClient(config)

    print()
    print("╭──────────────────────────────────────╮")
    print("│       AI Chatbot                      │")
    print("│    输入 /help 查看命令，quit 退出      │")
    print("╰──────────────────────────────────────╯")
    print()

    while True:
        try:
            user_input = input("你: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n再见！")
            break

        if not user_input:
            continue

        if user_input.lower() == "quit":
            print("再见！")
            break

        if user_input.startswith("/"):
            handle_command(user_input, chat_client)
            continue

        try:
            print("AI: ", end="", flush=True)
            chat_client.stream_chat(user_input)
        except Exception as e:
            print(f"\n请求出错: {e}")
            print("   可以输入 /clear 清空历史后重试")


if __name__ == "__main__":
    main()
