# ===========================================
# config.py — 配置管理
# ===========================================
# 类比前端: 把 .env 变量收集到一个 config 对象里
# 这里用 dataclass，类似 TypeScript 的 interface

import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
# 1. 从代码所在目录的上一级找（本地开发时: week1-python-ai-basics/.env）
# 2. 从当前工作目录找（打包安装后: 用户运行 ai-chatbot 的目录）
# override=False 表示不覆盖已有的环境变量
_code_env = Path(__file__).resolve().parent.parent / ".env"
if _code_env.exists():
    load_dotenv(_code_env)
load_dotenv()  # 当前工作目录的 .env


@dataclass
class Config:
    """
    应用配置 — 用 dataclass 定义，类似 TypeScript 的 interface

    @dataclass 是装饰器（Day 4 提过），它会自动生成 __init__、__repr__ 等方法
    相当于 TS 里写了 interface + class 的组合
    """
    api_key: str
    base_url: str
    model_name: str
    max_tokens: int = 500

    @classmethod
    def from_env(cls) -> "Config":
        """
        从环境变量创建配置 — 类方法
        类比前端: Config.fromEnv() 这种静态工厂方法
        """
        api_key = os.getenv("MINIMAX_API_KEY", "")
        if not api_key:
            raise ValueError("未找到 MINIMAX_API_KEY，请检查 .env 文件")

        return cls(
            api_key=api_key,
            base_url=os.getenv("MINIMAX_API_BASE", "https://api.modelverse.cn"),
            model_name=os.getenv("MINIMAX_MODEL_NAME", "claude-opus-4-6"),
            max_tokens=int(os.getenv("MAX_TOKENS", "500")),
        )
