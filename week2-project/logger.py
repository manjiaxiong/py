# ===========================================
# logger.py — API 请求日志记录
# ===========================================
# 记录每次 API 调用的 prompt / response / token / 耗时
# 写入 JSONL 文件（每行一条 JSON，方便追加和逐行读取）
#
# JS 类比：
# 就像 Express 的 morgan 日志中间件，记录每个请求
# JSONL = JSON Lines，每行一条独立的 JSON
# ===========================================

import json
import time
from pathlib import Path
from datetime import datetime


LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)


def get_log_path():
    """获取当天的日志文件路径（按天分文件）"""
    today = datetime.now().strftime("%Y-%m-%d")
    return LOG_DIR / f"api_log_{today}.jsonl"


def log_request(prompt, response, tokens=None, duration=None, extra=None):
    """
    记录一次 API 调用

    参数:
        prompt: 发送给 AI 的内容
        response: AI 的回复
        tokens: token 用量 dict，如 {"input": 100, "output": 50}
        duration: 耗时（秒）
        extra: 额外信息 dict
    """
    record = {
        "timestamp": datetime.now().isoformat(),
        "prompt": prompt,
        "response": response,
        "tokens": tokens,
        "duration_seconds": round(duration, 3) if duration else None,
    }
    if extra:
        record.update(extra)

    log_path = get_log_path()
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return record


def timed_ask(client, model, prompt, system="", max_tokens=500):
    """
    带日志的 API 调用 — 封装 client.messages.create + 自动记录日志

    返回:
        (response_text, log_record) 元组
    """
    start = time.time()

    kwargs = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        kwargs["system"] = system

    response = client.messages.create(**kwargs)
    duration = time.time() - start

    text = response.content[0].text.strip()
    tokens = {
        "input": response.usage.input_tokens,
        "output": response.usage.output_tokens,
    }

    record = log_request(
        prompt=prompt,
        response=text,
        tokens=tokens,
        duration=duration,
        extra={"model": model, "system": system},
    )

    return text, record


def read_logs(log_path=None):
    """读取日志文件，返回 record 列表"""
    if log_path is None:
        log_path = get_log_path()
    if not Path(log_path).exists():
        return []
    with open(log_path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]
