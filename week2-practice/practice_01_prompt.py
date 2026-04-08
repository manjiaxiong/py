# ===========================================
# 练习 1：Prompt Engineering（对应 Day 1）
# ===========================================
# 不看教程，自己写！
# 卡住了再回去看 01_prompt_engineering.py
# ===========================================

import os
from pathlib import Path
from dotenv import load_dotenv
from anthropic import Anthropic

# TODO 0: 初始化（自己写，别复制）
# - 加载 .env
# - 创建 client
# - 定义 MODEL

load_dotenv(Path(__file__).parent / ".env")
minimax_api_key = os.getenv("MINIMAX_API_KEY")
minimax_api_base = os.getenv("MINIMAX_API_BASE")
minimax_model_name = os.getenv("MINIMAX_MODEL_NAME")
client = Anthropic(
    api_key=minimax_api_key,
    base_url=minimax_api_base,
)


def ask(prompt, system=""):
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    if isinstance(prompt, list):
        messages.extend(prompt)
    else:
        messages.append({"role": "user", "content": prompt})

    response = client.messages.create(
        model=minimax_model_name,
        max_tokens=500,
        messages=messages,
    )
    # return response.content[0].text.strip()
    for block in response.content:
        if block.type == "text":
            return block.text.strip()
    raise Exception("No text block in response")


# --- 题目 1: Few-shot 数据提取器 ---

# TODO 1.1: 写一个函数 extract_product(text)
# - 用 Few-shot prompting 从商品描述中提取结构化信息
# - 输入: "iPhone 15 Pro Max 256GB 钛金属色 官方价 9999 元"
# - 输出: {"name": "iPhone 15 Pro Max", "storage": "256GB", "color": "钛金属色", "price": 9999}
# - 至少给 2 个 few-shot 示例
# 测试:
# print(extract_product("MacBook Air M3 16GB+512GB 星光色 售价 10499 元"))
# print(extract_product("华为 Mate 60 Pro 512GB 雅丹黑 售价 6999 元"))
message = [
    {
        "role": "system",
        "content": "你是一个商品信息提取器，专门从商品描述中提取结构化信息。",
    },
    {"role": "user", "content": "iPhone 15 Pro Max 256GB 钛金属色 官方价 9999 元"},
    {
        "role": "assistant",
        "content": '{"name": "iPhone 15 Pro Max", "storage": "256GB", "color": "钛金属色", "price": 9999}',
    },
]
# print(ask([*message, {"role": "user", "content": "小米 14 Pro 512GB 陶瓷白 官方价 5999 元"}]))
# print(ask([*message, {"role": "user", "content": "华为 Mate 60 Pro 512GB 雅丹黑 售价 6999 元"}]))
# --- 题目 2: Chain-of-Thought 代码分析 ---

# TODO 2.1: 写一个函数 analyze_complexity(code)
# - 让 AI 分步分析代码的时间复杂度和空间复杂度
# - 要求 AI 展示推理过程，不是直接给结论
# - System Prompt 要求 AI 按步骤回答
# 测试:
# analyze_complexity("""
# def two_sum(nums, target):
#     seen = {}
#     for i, num in enumerate(nums):
#         complement = target - num
#         if complement in seen:
#             return [seen[complement], i]
#         seen[num] = i
#     return []
# """)


def analyze_complexity(code):
    system_prompt = "你是一个算法分析专家，专门分析代码的时间复杂度和空间复杂度。请按步骤推理，展示你的分析过程。"
    user_prompt = (
        f"请分析以下 Python 代码的时间复杂度和空间复杂度:\n```python\n{code}\n```"
    )
    response = ask(user_prompt, system=system_prompt)
    print(response)


# analyze_complexity("""
# def two_sum(nums, target):
#     seen = {}
#     for i, num in enumerate(nums):
#         complement = target - num
#         if complement in seen:
#             return [seen[complement], i]
#         seen[num] = i
#     return []
# """)
# --- 题目 3: System Prompt 角色扮演 ---


# TODO 3.1: 写一个函数 multi_role_review(code)
# - 让 3 个不同角色审查同一段代码:
#   1. 安全专家（关注安全漏洞）
#   2. 性能专家（关注性能瓶颈）
#   3. 可读性专家（关注代码风格和命名）
# - 每个角色用不同的 System Prompt
# - 打印每个角色的审查意见
# 测试:
# multi_role_review("""
# def get_user_data(user_id):
#     query = f"SELECT * FROM users WHERE id = {user_id}"
#     result = db.execute(query)
#     data = []
#     for row in result:
#         data.append({"id": row[0], "name": row[1], "email": row[2]})
#     return data
# """)
def multi_role_review(raw_code):
    roles = {
        "安全专家": "你是一个安全专家，专门审查代码中的安全漏洞。请指出代码中可能存在的安全问题，并给出修复建议。",
        "性能专家": "你是一个性能专家，专门分析代码的性能瓶颈。请指出代码中可能存在的性能问题，并给出优化建议。",
        "可读性专家": "你是一个可读性专家，专门评审代码的风格和命名。请指出代码中可能存在的可读性问题，并给出改进建议。",
    }
    for role, system_prompt in roles.items():
        print(f"--- {role} 的审查意见 ---")
        response = ask(raw_code, system=system_prompt)
        print(response, end="\n\n")


# --- 异步版本对比 ---
# 同步版: 3 个角色串行调用，总耗时 = t1 + t2 + t3
# 异步版: 3 个角色并行调用，总耗时 = max(t1, t2, t3)

import asyncio
import time
from anthropic import AsyncAnthropic

# 创建异步客户端（和同步的 Anthropic 参数一样，只是类名不同）
async_client = AsyncAnthropic(
    api_key=minimax_api_key,
    base_url=minimax_api_base,
)


async def async_ask(prompt, system=""):
    """异步版的 ask — 和同步版逻辑一样，只是加了 async/await"""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    # await = 等待 API 响应，但不阻塞其他任务
    # 同步版用 client.messages.create()，阻塞整个程序
    # 异步版用 await async_client.messages.create()，只阻塞当前任务，其他任务继续跑
    response = await async_client.messages.create(
        model=minimax_model_name,
        max_tokens=500,
        messages=messages,
    )
    return response.content[0].text.strip()


async def multi_role_review_async(raw_code):
    """
    异步版多角色审查 — 3 个角色并行调用

    JS 类比:
    // 同步版（你现在的）
    for (const [role, prompt] of roles) {
        const res = await ask(code, prompt)   // 串行，一个一个等
    }

    // 异步版（这个函数）
    const results = await Promise.all(        // 并行，同时发出
        roles.map(([role, prompt]) => ask(code, prompt))
    )
    """
    roles = {
        "安全专家": "你是一个安全专家，专门审查代码中的安全漏洞。请指出代码中可能存在的安全问题，并给出修复建议。",
        "性能专家": "你是一个性能专家，专门分析代码的性能瓶颈。请指出代码中可能存在的性能问题，并给出优化建议。",
        "可读性专家": "你是一个可读性专家，专门评审代码的风格和命名。请指出代码中可能存在的可读性问题，并给出改进建议。",
    }

    # 创建所有任务（还没执行，只是注册）
    # 列表推导式 + async_ask 生成 3 个协程（coroutine）
    role_names = list(roles.keys())
    tasks = [async_ask(raw_code, system=prompt) for prompt in roles.values()]

    # asyncio.gather() = Promise.all()
    # 3 个 API 调用同时发出，等全部返回
    results = await asyncio.gather(*tasks)

    # 打印结果（gather 返回的顺序和传入的顺序一致）
    for role, response in zip(role_names, results):
        print(f"--- {role} 的审查意见 ---")
        print(response, end="\n\n")


# 对比测试（取消注释运行）:
# test_code = """
# def get_user_data(user_id):
#     query = f"SELECT * FROM users WHERE id = {user_id}"
#     result = db.execute(query)
#     data = []
#     for row in result:
#         data.append({"id": row[0], "name": row[1], "email": row[2]})
#     return data
# """
#
# # 同步版
# start = time.time()
# multi_role_review(test_code)
# print(f"同步耗时: {time.time() - start:.2f}秒\n")
#
# # 异步版
# start = time.time()
# asyncio.run(multi_role_review_async(test_code))
# print(f"异步耗时: {time.time() - start:.2f}秒")

# --- 题目 4: Prompt 模板引擎 ---


# TODO 4.1: 写一个 PromptTemplate 类
# - __init__(self, template): 接收模板字符串
# - render(**kwargs): 填充变量，返回完整 prompt
# - 支持默认值（如果变量没传，用默认值）
# 测试:
# tpl = PromptTemplate("把以下 {source_lang} 代码翻译成 {target_lang}:\n{code}")
# prompt = tpl.render(source_lang="JavaScript", target_lang="Python", code="const x = 1")
# print(prompt)
class PromptTemplate:
    """
    Prompt 模板引擎 — 集中管理和复用 prompt

    支持:
    - 变量占位符: {variable_name}
    - 默认值: 没传的变量用默认值填充
    - render() 渲染完整 prompt

    JS 类比:
    class PromptTemplate {
      constructor(template, defaults = {}) {
        this.template = template
        this.defaults = defaults
      }
      render(kwargs) {
        const merged = { ...this.defaults, ...kwargs }
        return this.template.replace(/{(\w+)}/g, (_, k) => merged[k])
      }
    }
    """

    def __init__(self, template, defaults=None):
        self.template = template
        # defaults 存默认值，没传就是空字典
        # or {} 的作用: None or {} → {}（短路求值，和 JS 的 ?? {} 一样）
        self.defaults = defaults or {}

    def render(self, **kwargs):
        # 先用 defaults 打底，再用 kwargs 覆盖（后面的优先级更高）
        # = JS: { ...this.defaults, ...kwargs }
        merged = {**self.defaults, **kwargs}
        return self.template.format(**merged)


# 测试 PromptTemplate:
# tpl = PromptTemplate("把以下 {source_lang} 代码翻译成 {target_lang}:\n{code}")
# prompt = tpl.render(source_lang="JavaScript", target_lang="Python", code="const x = 1")
# print(prompt)


# TODO 4.2: 用你的 PromptTemplate 类做一个 "错误诊断器"
# - 模板包含: 错误信息、代码、语言
# - 让 AI 诊断错误原因并给出修复代码

# 错误诊断模板 — language 有默认值 "Python"，不传就用默认的
error_tpl = PromptTemplate(
    "我在写 {language} 代码时遇到了以下错误:\n\n"
    "错误信息: {error}\n\n"
    "出错代码:\n```{language}\n{code}\n```\n\n"
    "请分析错误原因，并给出修复后的代码。",
    defaults={"language": "Python"},
)

# 测试:
# prompt = error_tpl.render(
#     error="TypeError: 'NoneType' object is not subscriptable",
#     code="result = get_user()['name']"
# )
# print(ask(prompt))


# --- 题目 5: 综合挑战 — Prompt 优化器 ---

# TODO 5.1: 写一个函数 optimize_prompt(original_prompt)
# - 把用户写的"懒 Prompt"用 AI 优化成结构化的好 Prompt
# - System Prompt: 你是 Prompt 优化专家，把模糊的提示词变成结构清晰的
# - 优化后的 Prompt 要包含：角色、任务、格式要求、约束


def optimize_prompt(original_prompt):
    """
    Prompt 优化器 — 把模糊的 prompt 优化成结构化的好 prompt

    原理: 用 AI 来优化 prompt（用 AI 优化和 AI 的沟通方式）
    这就是 "meta-prompting"（元提示）：用 prompt 生成更好的 prompt
    """
    # 版本 1: 纯文本拼接
    system_v1 = (
        "你是一位 Prompt Engineering 专家。\n"
        "用户会给你一个模糊、简短的提示词，请你将其优化为结构清晰、效果更好的 Prompt。\n\n"
        "优化后的 Prompt 必须包含以下部分:\n"
        "1. 角色设定: 明确 AI 应该扮演什么角色\n"
        "2. 任务描述: 具体要做什么，输入和输出是什么\n"
        "3. 格式要求: 输出应该是什么格式（列表、JSON、代码等）\n"
        "4. 约束条件: 有什么限制或注意事项\n\n"
        "直接输出优化后的 Prompt，不要解释你做了什么改动。"
    )

    # 版本 2: XML 标签版（结构更清晰，Claude 对 XML 理解更好）
    system_v2 = """
<role>你是一位 Prompt Engineering 专家</role>

<task>
用户会给你一个模糊、简短的提示词，请你将其优化为结构清晰、效果更好的 Prompt。
</task>

<output_format>
优化后的 Prompt 必须包含以下部分:
<section name="角色设定">明确 AI 应该扮演什么角色</section>
<section name="任务描述">具体要做什么，输入和输出是什么</section>
<section name="格式要求">输出应该是什么格式（列表、JSON、代码等）</section>
<section name="约束条件">有什么限制或注意事项</section>
</output_format>

<constraints>
直接输出优化后的 Prompt，不要解释你做了什么改动。
</constraints>"""

    result = ask(original_prompt, system=system_v2)
    return result


# 测试:
# print(optimize_prompt("帮我写个爬虫"))
# print("=" * 50)
# print(optimize_prompt("优化我的代码"))
