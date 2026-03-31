# ===========================================
# commands.py — 斜杠命令处理
# ===========================================
# 实现 /help、/clear、/save 等命令
# 类比前端: 像 Discord bot 的斜杠命令

import json
import os
from datetime import datetime
from .client import ChatClient


def handle_command(command: str, chat_client: ChatClient) -> bool:
    """
    处理斜杠命令，返回 True 表示已处理

    类比前端: switch(command) 路由分发
    """
    parts = command.strip().split(maxsplit=1)  # 分割命令和参数
    cmd = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else ""

    if cmd == "/help":
        show_help()
    elif cmd == "/clear":
        chat_client.clear_history()
    elif cmd == "/history":
        show_history(chat_client)
    elif cmd == "/save":
        save_chat(chat_client, arg)
    elif cmd == "/system":
        if arg:
            chat_client.set_system_prompt(arg)
        else:
            print(f"当前 System Prompt: {chat_client.system_prompt}")
    elif cmd == "/tokens":
        show_token_count(chat_client)
    else:
        print(f"未知命令: {cmd}，输入 /help 查看可用命令")

    return True


def show_help():
    """显示帮助信息"""
    print("""
╭─────────────────────────────────────╮
│         AI Chatbot 命令列表          │
├─────────────────────────────────────┤
│  /help          显示此帮助信息       │
│  /clear         清空对话历史         │
│  /history       查看对话历史         │
│  /save [文件名]  保存对话到 JSON     │
│  /system [内容]  查看/设置 System    │
│  /tokens        查看当前消息数       │
│  quit           退出程序             │
╰─────────────────────────────────────╯
""")


def show_history(chat_client: ChatClient):
    """显示对话历史"""
    history = chat_client.get_history()
    if not history:
        print("（暂无对话历史）")
        return

    print(f"\n=== 对话历史 ({len(history)} 条消息) ===\n")
    for i, msg in enumerate(history):
        role = "[你]" if msg["role"] == "user" else "[AI]"
        content = msg["content"]
        # 太长的消息截断显示
        if len(content) > 100:
            content = content[:100] + "..."
        print(f"  [{i+1}] {role}: {content}")
    print()


def save_chat(chat_client: ChatClient, filename: str = ""):
    """
    保存对话到 JSON 文件
    类比前端: localStorage.setItem() 持久化数据
    """
    history = chat_client.get_history()
    if not history:
        print("没有对话可保存")
        return

    if not filename:
        # 用时间戳生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chat_{timestamp}.json"

    if not filename.endswith(".json"):
        filename += ".json"

    save_data = {
        "saved_at": datetime.now().isoformat(),
        "message_count": len(history),
        "system_prompt": chat_client.system_prompt,
        "messages": history,
    }

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)

    print(f"对话已保存到: {filename}")


def show_token_count(chat_client: ChatClient):
    """粗略统计当前对话的消息数和字数"""
    history = chat_client.get_history()
    total_chars = sum(len(msg["content"]) for msg in history)
    # 粗略估算: 中文约 1-2 字/token
    estimated_tokens = total_chars // 2

    print(f"  消息数: {len(history)}")
    print(f"  总字数: {total_chars}")
    print(f"  估算 tokens: ~{estimated_tokens}")
    print(f"  注意: 消息越多，每次请求消耗的 token 越大")
