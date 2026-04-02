# ===========================================
# 配置管理模块
# ===========================================
# 集中管理环境变量和项目配置
# JS 类比: 类似于 config.js，把所有配置项放在一个地方
# ===========================================

import os
from pathlib import Path
from dotenv import load_dotenv


class Config:
    """
    项目配置类 — 集中管理所有配置项

    为什么用 class 而不是直接写变量？
    - 把相关的配置聚合在一起，方便管理
    - 可以加验证逻辑（比如 API key 不能为空）
    - 传参方便：传一个 config 对象就行，不用传一堆变量

    JS 类比:
    class Config {
      constructor() {
        this.apiKey = process.env.MINIMAX_API_KEY
        this.apiBase = process.env.MINIMAX_API_BASE
      }
    }
    """

    def __init__(self):
        # 加载 .env 文件（从 week1-practice/ 目录找）
        # Path(__file__).parent.parent = note_generator/ 的上一级 = week1-practice/
        env_path = Path(__file__).parent.parent / ".env"
        load_dotenv(env_path)

        # 读取环境变量
        self.api_key = os.getenv("MINIMAX_API_KEY")
        self.api_base = os.getenv("MINIMAX_API_BASE")
        self.model_name = os.getenv("MINIMAX_MODEL_NAME")

        # 验证：API key 不能为空，否则后面调用必崩
        if not self.api_key:
            raise ValueError("MINIMAX_API_KEY 未设置，请检查 .env 文件")

        # 项目相关配置
        self.max_tokens = 1000          # AI 回复最大 token 数
        self.output_dir = Path(__file__).parent.parent / "output"  # 报告输出目录

        # 确保输出目录存在（= JS: fs.mkdirSync(dir, { recursive: true })）
        self.output_dir.mkdir(exist_ok=True)

    def __str__(self):
        """打印配置信息（隐藏 API key，防止泄露）"""
        return (
            f"Config(\n"
            f"  api_base={self.api_base}\n"
            f"  model={self.model_name}\n"
            f"  api_key={self.api_key[:8]}...（已隐藏）\n"
            f")"
        )
