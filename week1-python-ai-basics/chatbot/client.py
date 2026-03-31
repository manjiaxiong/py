# ===========================================
# client.py — AI 客户端封装
# ===========================================
# 把 API 调用封装成类，外部只需要调 chat() 和 stream_chat()
# 类比前端: 封装一个 apiClient 模块，统一处理请求

import anthropic
from .config import Config


class ChatClient:
    """
    AI 聊天客户端

    封装了:
    - 对话历史管理
    - 普通调用和流式调用
    - system prompt 设置
    """

    def __init__(self, config: Config):
        self.config = config
        self.client = anthropic.Anthropic(
            api_key=config.api_key,
            base_url=config.base_url,
        )
        self.messages: list[dict] = []  # 对话历史
        self.system_prompt = "你是一个友好的 AI 助手，擅长帮助前端工程师学习 Python 和 AI 开发。回答简洁清晰。"

    def set_system_prompt(self, prompt: str):
        """设置 system prompt"""
        self.system_prompt = prompt
        print("System Prompt 已更新")

    def clear_history(self):
        """清空对话历史"""
        self.messages = []
        print("对话历史已清空")

    def get_history(self) -> list[dict]:
        """获取对话历史"""
        return self.messages.copy()

    def chat(self, user_input: str) -> str:
        """
        普通对话 — 等全部生成完再返回
        类比前端: await fetch(...).then(r => r.json())
        """
        self.messages.append({"role": "user", "content": user_input})

        try:
            message = self.client.messages.create(
                model=self.config.model_name,
                max_tokens=self.config.max_tokens,
                system=self.system_prompt,
                messages=self.messages,
            )

            # 提取 text 内容
            reply = ""
            for block in message.content:
                if block.type == "text":
                    reply += block.text

            self.messages.append({"role": "assistant", "content": reply})
            return reply

        except Exception as e:
            self.messages.pop()  # 请求失败，移除刚添加的 user 消息
            raise e

    def stream_chat(self, user_input: str):
        """
        流式对话 — 逐字输出，返回完整回复
        类比前端: EventSource / ReadableStream 逐块读取
        """
        self.messages.append({"role": "user", "content": user_input})

        try:
            full_reply = ""

            with self.client.messages.stream(
                model=self.config.model_name,
                max_tokens=self.config.max_tokens,
                system=self.system_prompt,
                messages=self.messages,
            ) as stream:
                for text in stream.text_stream:
                    print(text, end="", flush=True)
                    full_reply += text

            print()  # 换行
            self.messages.append({"role": "assistant", "content": full_reply})
            return full_reply

        except Exception as e:
            self.messages.pop()
            raise e
