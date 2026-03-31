# ===========================================
# Day 6-7: 综合项目 — 实用 AI 工具集
# ===========================================
#
# 本课整合第一周所有知识，构建几个实用的 AI 小工具：
# 1. 代码解释器 — 读取本地文件让 AI 解释代码
# 2. 装饰器实战 — 给 API 调用加计时和重试
# 3. 并发翻译器 — 异步并行调用，同时翻译多段文本
# 4. 结构化输出 — 让 AI 返回 JSON 而非纯文本
#
# ===========================================

import os
import json
import time
import asyncio
import functools
from pathlib import Path
from dotenv import load_dotenv
import anthropic

load_dotenv()

api_key = os.getenv("MINIMAX_API_KEY")
base_url = os.getenv("MINIMAX_API_BASE", "https://api.modelverse.cn")
model_name = os.getenv("MINIMAX_MODEL_NAME", "claude-opus-4-6")

if not api_key:
    print("⚠ 未找到 MINIMAX_API_KEY")
    exit(1)

client = anthropic.Anthropic(api_key=api_key, base_url=base_url)


# ===========================================
# 工具一：装饰器实战
# ===========================================
# 装饰器 = 高阶函数，接收函数返回新函数
# 类比前端:
#   - React 的 HOC: withAuth(Component) → 增强版 Component
#   - JS: const timed = (fn) => (...args) => { console.time(); fn(...args); console.timeEnd() }

# --- 计时装饰器 ---
def timer(func):
    """
    给函数加上耗时统计

    类比 JS:
    const timer = (fn) => (...args) => {
        const start = Date.now()
        const result = fn(...args)
        console.log(`耗时: ${Date.now() - start}ms`)
        return result
    }
    """
    @functools.wraps(func)  # 保留原函数的名字和文档
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"  ⏱ {func.__name__} 耗时: {elapsed:.2f}s")
        return result
    return wrapper


# --- 重试装饰器 ---
def retry(max_retries=3, delay=1):
    """
    自动重试装饰器 — API 调用必备

    类比前端: axios-retry 插件
    注意这是一个"装饰器工厂" — 返回装饰器的函数
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries:
                        print(f"  ❌ {func.__name__} 失败 {max_retries} 次，放弃: {e}")
                        raise
                    print(f"  ⚠ 第 {attempt} 次失败: {e}，{delay}s 后重试...")
                    time.sleep(delay)
        return wrapper
    return decorator


# 使用装饰器 — 直接加 @ 就行
@timer
@retry(max_retries=2, delay=1)
def ask_ai(question: str, system: str = "") -> str:
    """被装饰的 AI 调用函数 — 自动计时 + 自动重试"""
    message = client.messages.create(
        model=model_name,
        max_tokens=300,
        system=system or "用中文简洁回答。",
        messages=[{"role": "user", "content": question}]
    )
    for block in message.content:
        if block.type == "text":
            return block.text
    return ""


def demo_decorators():
    """演示装饰器效果"""
    print("=== 装饰器实战 ===\n")
    result = ask_ai("Python 的 with 语句是什么？一句话解释。")
    print(f"  回答: {result}\n")

# demo_decorators()


# ===========================================
# 工具二：代码解释器 — 读取本地文件让 AI 解释
# ===========================================
@timer
def explain_code(file_path: str) -> str:
    """
    读取一个代码文件，让 AI 解释它的功能

    类比前端: 读取文件内容 → 发给 API → 展示结果
    """
    path = Path(file_path)

    if not path.exists():
        print(f"文件不存在: {file_path}")
        return ""

    # 读取文件 — 注意指定 encoding，Windows 默认不是 utf-8
    code = path.read_text(encoding="utf-8")
    suffix = path.suffix  # 获取文件扩展名，如 .py .js

    print(f"=== 代码解释器 ===")
    print(f"文件: {path.name} ({len(code)} 字符)\n")

    system_prompt = """你是一个代码导师，用户是前端工程师正在学习 Python。
请解释这段代码的功能，要求：
1. 先用一句话总结整体功能
2. 逐段解释关键逻辑
3. 如果有 Python 特有的语法，用 JavaScript 类比解释
4. 回答控制在 300 字以内"""

    message = client.messages.create(
        model=model_name,
        max_tokens=500,
        system=system_prompt,
        messages=[{"role": "user", "content": f"请解释这段 {suffix} 代码:\n\n```{suffix}\n{code}\n```"}]
    )

    result = ""
    for block in message.content:
        if block.type == "text":
            result += block.text

    print(result)
    return result


# 解释 Day 1 的代码
explain_code("week1-python-ai-basics/chatbot/config.py")


# ===========================================
# 工具三：并发翻译器 — asyncio 并行调用
# ===========================================

async def translate_one(async_client, text: str, target_lang: str = "English") -> dict:
    """翻译单条文本（异步版本）"""
    message = await async_client.messages.create(
        model=model_name,
        max_tokens=200,
        system=f"你是翻译器，将输入翻译成{target_lang}，只返回翻译结果，不要解释。",
        messages=[{"role": "user", "content": text}]
    )
    result = ""
    for block in message.content:
        if block.type == "text":
            result += block.text
    return {"original": text, "translated": result}


async def batch_translate(texts: list[str], target_lang: str = "English"):
    """
    并行翻译多条文本

    类比前端:
    const results = await Promise.all(
        texts.map(text => translateOne(text))
    )
    """
    # 异步客户端 — 注意是 AsyncAnthropic
    async_client = anthropic.AsyncAnthropic(api_key=api_key, base_url=base_url)

    print(f"\n=== 并发翻译器 ({len(texts)} 条文本) ===\n")
    start = time.time()

    # asyncio.gather = Promise.all
    tasks = [translate_one(async_client, text, target_lang) for text in texts]
    results = await asyncio.gather(*tasks)

    elapsed = time.time() - start
    print(f"  总耗时: {elapsed:.2f}s（并行执行，不是串行！）\n")

    for r in results:
        print(f"  原文: {r['original']}")
        print(f"  译文: {r['translated']}\n")

    return results


# 运行并发翻译
# asyncio.run(batch_translate([
#     "这个组件需要支持响应式布局",
#     "请修复暗黑模式下按钮颜色异常的问题",
#     "新增用户权限管理模块",
# ]))


# ===========================================
# 工具四：结构化输出 — 让 AI 返回 JSON
# ===========================================

def analyze_code_structure(code: str) -> dict:
    """
    让 AI 分析代码并返回结构化 JSON

    这是 AI 应用开发的核心技巧：
    不要让 AI 返回自然语言，而是返回结构化数据，方便程序处理
    """
    print("\n=== 结构化输出 ===\n")

    system_prompt = """分析用户提供的代码，以 JSON 格式返回分析结果。
只返回 JSON，不要返回其他内容。格式如下：
{
    "language": "编程语言",
    "summary": "一句话功能总结",
    "functions": ["函数名列表"],
    "classes": ["类名列表"],
    "imports": ["导入的模块列表"],
    "complexity": "simple/medium/complex",
    "suggestions": ["改进建议，最多3条"]
}"""

    message = client.messages.create(
        model=model_name,
        max_tokens=500,
        system=system_prompt,
        messages=[{"role": "user", "content": code}]
    )

    text = ""
    for block in message.content:
        if block.type == "text":
            text += block.text

    # 尝试解析 JSON — AI 返回的不一定是合法 JSON，要 try/except
    try:
        # 有时 AI 会在 JSON 外面包 ```json ... ```，需要清理
        cleaned = text.strip()
        if cleaned.startswith("```"):
            # 去掉 markdown 代码块标记
            lines = cleaned.split("\n")
            cleaned = "\n".join(lines[1:-1])

        result = json.loads(cleaned)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return result
    except json.JSONDecodeError:
        print(f"  AI 返回的不是合法 JSON，原始回复:\n  {text}")
        return {}


# 分析一段代码
sample_code = '''
import os
from pathlib import Path

class FileManager:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)

    def list_files(self, pattern="*"):
        return list(self.base_dir.glob(pattern))

    def read_file(self, name: str) -> str:
        return (self.base_dir / name).read_text(encoding="utf-8")

def get_project_files(directory: str) -> list:
    fm = FileManager(directory)
    return fm.list_files("*.py")
'''

# analyze_code_structure(sample_code)


# ===========================================
# 练习
# ===========================================

# TODO 1: 写一个 @cache 装饰器
# - 缓存函数调用结果，相同参数不重复调用
# - 类比前端: useMemo / React.memo
# - 提示: 用 dict 存储 {参数: 结果}
def cache(func):
    pass  # 替换为你的代码


# TODO 2: 写一个 code_reviewer 函数
# - 读取一个 .py 文件
# - 让 AI 以 JSON 格式返回 code review 结果:
#   { "score": 1-10, "issues": [...], "good_parts": [...] }
def code_reviewer(file_path: str) -> dict:
    pass  # 替换为你的代码


# TODO 3: 写一个异步批量摘要函数
# - 接收多段长文本
# - 并行调用 AI 生成每段的摘要
# - 返回 [{"original": "...", "summary": "..."}]
async def batch_summarize(texts: list[str]) -> list[dict]:
    pass  # 替换为你的代码


# 取消注释测试:
# code_reviewer("week1-python-ai-basics/chatbot/client.py")
# asyncio.run(batch_summarize(["长文本1...", "长文本2..."]))
