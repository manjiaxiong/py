# ===========================================
# 公共工具函数
# ===========================================
# 把多个文件中重复使用的代码提取到这里
# 用法：from utils import get_client, clean_markdown, ask
# ===========================================

import os
from dotenv import load_dotenv
from anthropic import Anthropic


def get_client(env_path=None):
    """
    初始化 Anthropic 客户端

    参数:
        env_path: .env 文件路径，默认为调用方所在目录的 .env

    返回:
        (client, MODEL) 元组

    用法:
        from utils import get_client
        client, MODEL = get_client(Path(__file__).parent / ".env")
    """
    if env_path:
        load_dotenv(env_path)
    else:
        load_dotenv()

    client = Anthropic(
        api_key=os.getenv("MINIMAX_API_KEY"),
        base_url=os.getenv("MINIMAX_API_BASE"),
    )
    model = os.getenv("MINIMAX_MODEL_NAME")
    return client, model


def clean_markdown(text):
    """
    清理 AI 回复中的 markdown 代码块标记

    AI 经常返回这种格式：
        ```json
        {"name": "xxx"}
        ```
    这个函数把 ``` 标记去掉，只保留中间的内容

    参数:
        text: AI 的原始回复文本

    返回:
        清理后的文本
    """
    raw = text.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        raw = raw.rsplit("```", 1)[0].strip()
    return raw


def ask(client, model, prompt, system="", max_tokens=500):
    """
    封装 API 调用

    参数:
        client: Anthropic 客户端
        model: 模型名称
        prompt: 用户消息
        system: 系统提示词（可选）
        max_tokens: 最大回复长度

    返回:
        AI 回复文本

    用法:
        from utils import get_client, ask
        client, MODEL = get_client(Path(__file__).parent / ".env")
        result = ask(client, MODEL, "你好")
    """
    kwargs = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        kwargs["system"] = system

    response = client.messages.create(**kwargs)
    # 模型可能返回 ThinkingBlock + TextBlock，取第一个有 .text 的 block
    for block in response.content:
        if hasattr(block, "text"):
            return block.text.strip()
    return ""
