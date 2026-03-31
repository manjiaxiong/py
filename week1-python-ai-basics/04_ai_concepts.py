# ===========================================
# Day 4: 大模型核心概念 — Token、Temperature、Prompt 设计
# ===========================================
#
# 本课通过实际调参实验，帮你理解大模型的核心概念。
# 确保你已经完成 Day 3 的环境配置（venv、.env、依赖安装）。
# 使用 MiniMax Anthropic 兼容接口 + anthropic SDK
#
# ===========================================

import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

api_key = os.getenv("MINIMAX_API_KEY")
base_url = os.getenv("MINIMAX_API_BASE", "https://api.modelverse.cn")
model_name = os.getenv("MINIMAX_MODEL_NAME", "claude-opus-4-6")
if not api_key:
    print("⚠ 未找到 MINIMAX_API_KEY，请先完成 Day 3 的环境配置")
    exit(1)


def create_client():
    """创建 MiniMax Anthropic 兼容客户端"""
    return anthropic.Anthropic(api_key=api_key, base_url=base_url)


client = create_client()


# ----- 1. 理解 Token -----
# Token 是大模型的"最小处理单位"
# - 英文: 大约 1 个单词 = 1 token（"hello" = 1 token）
# - 中文: 大约 1-2 个字 = 1 token（"你好" ≈ 1 token）
# - 费用按 token 计算: 输入 token + 输出 token
#
# 类比前端: 就像网络请求按字节计费，大模型按 token 计费

def token_demo():
    """观察不同输入的 token 消耗"""

    print("=== Token 消耗对比 ===\n")

    prompts = [
        "Hi",
        "Hello, how are you today?",
        "你好",
        "请用100字介绍一下Python编程语言的特点和优势。",
    ]

    for prompt in prompts:
        message = client.messages.create(
            model=model_name,
            max_tokens=50,  # 限制输出，专注观察输入 token
            messages=[{"role": "user", "content": prompt}]
        )

        usage = message.usage
        print(f"输入: \"{prompt}\"")
        print(f"  → 输入 token: {usage.input_tokens}, 输出 token: {usage.output_tokens}, 回复了{message}")
        print()

# token_demo()


# ----- 2. Temperature — 控制随机性 -----
# temperature 是最重要的参数之一
#
# temperature = 0: 每次回答都一样（确定性），适合代码、数据提取
# temperature = 0.7: 有一定随机性，适合日常对话
# temperature = 1.0: 很随机，适合创意写作、头脑风暴
#
# 类比: 像 Math.random() 的种子
#   - temperature=0 就像固定种子，结果不变
#   - temperature=1 就像真随机，每次不同

def temperature_experiment():
    """实验: 同一个问题，不同 temperature 的效果"""

    print("=== Temperature 对比实验 ===\n")
    question = "随机写一句话，主题不限，风格不限，越意想不到越好"

    for temp in [0, 0.5, 1.0]:
        print(f"--- temperature = {temp} ---")

        # 同样的问题问 3 次，观察回答是否变化
        for i in range(3):
            message = client.messages.create(
                model=model_name,
                max_tokens=60,
                temperature=temp,
                messages=[{"role": "user", "content": question}]
            )
            # 取 text 类型的 content block
            text = ""
            for block in message.content:
                if block.type == "text":
                    text += block.text.strip()
            print(f"  第{i+1}次: {text}")

        print()

# temperature_experiment()


# ----- 3. max_tokens — 控制输出长度 -----
# max_tokens 限制模型最多输出多少 token
#
# 重要: 如果回答被截断，stop_reason 会是 "max_tokens" 而不是 "end_turn"
# 这在实际开发中很重要 — 你需要判断回答是否完整

def max_tokens_experiment():
    """实验: max_tokens 太小会截断回答"""

    print("=== max_tokens 截断实验 ===\n")
    question = "列出 Python 最常用的 10 个内置函数并简要说明用途"

    for max_t in [30, 100, 500]:
        message = client.messages.create(
            model=model_name,
            max_tokens=max_t,
            messages=[{"role": "user", "content": question}]
        )

        text = ""
        for block in message.content:
            if block.type == "text":
                text += block.text

        print(f"--- max_tokens = {max_t} ---")
        print(f"  停止原因: {message.stop_reason}")  # "end_turn"=正常结束, "max_tokens"=被截断
        print(f"  输出 token: {message.usage.output_tokens}")
        print(f"  回答: {text[:100]}{'...' if len(text) > 100 else ''}")
        print()

# max_tokens_experiment()


# ----- 4. System Prompt 设计技巧 -----
# System Prompt 是控制 AI 行为的最重要手段
# 好的 System Prompt = 好的 AI 应用

def system_prompt_comparison():
    """对比: 有无 System Prompt 的效果差异"""

    print("=== System Prompt 对比 ===\n")
    question = "解释一下 Python 的装饰器"

    # 没有 System Prompt — 回答可能很长很泛
    print("--- 无 System Prompt ---")
    r1 = client.messages.create(
        model=model_name,
        max_tokens=200,
        messages=[{"role": "user", "content": question}]
    )
    for block in r1.content:
        if block.type == "text":
            print(f"  {block.text[:150]}...\n")

    # 有针对性的 System Prompt — 回答精准
    print("--- 有 System Prompt (前端视角) ---")
    r2 = client.messages.create(
        model=model_name,
        max_tokens=200,
        system="你是 Python 导师，用户是前端工程师。用 JavaScript 的概念类比解释，回答控制在 3 句话以内。",
        messages=[{"role": "user", "content": question}]
    )
    for block in r2.content:
        if block.type == "text":
            print(f"  {block.text}\n")

    # 角色扮演 System Prompt
    print("--- 角色扮演 System Prompt ---")
    r3 = client.messages.create(
        model=model_name,
        max_tokens=200,
        system="你是一个毒舌但专业的编程老师，回答时带点幽默和吐槽，但知识点要准确。",
        messages=[{"role": "user", "content": question}]
    )
    for block in r3.content:
        if block.type == "text":
            print(f"  {block.text}\n")

# system_prompt_comparison()


# ----- 5. Few-shot Prompting — 用示例教 AI -----
# Few-shot = 在 prompt 中给几个输入→输出的示例
# 这比用文字描述规则更有效！
#
# 类比前端: 像给组件写 Storybook 示例，看示例比看文档更直观

def few_shot_demo():
    """Few-shot: 用示例教 AI 做格式化输出"""

    print("=== Few-shot Prompting ===\n")

    # Zero-shot: 直接问，格式不可控
    print("--- Zero-shot (不给示例) ---")
    r1 = client.messages.create(
        model=model_name,
        max_tokens=100,
        messages=[
            {"role": "user", "content": "把这个需求转换成 Git commit 信息: 修复了登录页面在手机端输入框无法获取焦点的问题"}
        ]
    )
    for block in r1.content:
        if block.type == "text":
            print(f"  {block.text}\n")

    # Few-shot: 给示例，输出格式可控
    print("--- Few-shot (给 2 个示例) ---")
    r2 = client.messages.create(
        model=model_name,
        max_tokens=100,
        system="你是一个 Git commit 信息生成器。根据用户描述的需求，生成规范的 commit message。",
        messages=[
            # 示例 1
            {"role": "user", "content": "添加了用户头像上传功能"},
            {"role": "assistant", "content": "feat(profile): add avatar upload functionality"},
            # 示例 2
            {"role": "user", "content": "解决了购物车数量显示为负数的bug"},
            {"role": "assistant", "content": "fix(cart): resolve negative quantity display issue"},
            # 真正的问题
            {"role": "user", "content": "修复了登录页面在手机端输入框无法获取焦点的问题"}
        ]
    )
    for block in r2.content:
        if block.type == "text":
            print(f"  {block.text}\n")

# few_shot_demo()


# ----- 6. 模型"幻觉"演示 -----
# 幻觉 = 模型编造看起来合理但实际不存在的信息
# 这是大模型最大的坑之一！

def hallucination_demo():
    """演示模型幻觉 — AI 可能会编造不存在的东西"""

    print("=== 模型幻觉演示 ===\n")
    print("注意: 下面的回答可能包含编造的信息！\n")

    # 问一个容易产生幻觉的问题
    questions = [
        "npm 包 super-fast-validator-2024 的作者是谁？",  # 不存在的包
        "Python 3.15 新增了什么特性？",  # 不存在的版本
    ]

    for q in questions:
        message = client.messages.create(
            model=model_name,
            max_tokens=150,
            messages=[{"role": "user", "content": q}]
        )
        print(f"问: {q}")
        for block in message.content:
            if block.type == "text":
                print(f"答: {block.text}")
        print()

    # 缓解幻觉的方法
    print("--- 缓解幻觉: 加上约束 ---")
    message = client.messages.create(
        model=model_name,
        max_tokens=100,
        system="如果你不确定或不知道答案，请直接说'我不确定'，不要编造信息。",
        messages=[
            {"role": "user", "content": "npm 包 super-fast-validator-2024 的作者是谁？"}
        ]
    )
    for block in message.content:
        if block.type == "text":
            print(f"加约束后: {block.text}\n")

# hallucination_demo()


# ===========================================
# 练习
# ===========================================

# TODO 1: 写一个函数 find_best_temperature(question, options=[0, 0.3, 0.7, 1.0])
# - 对每个 temperature 调用 3 次，打印结果
# - 人工观察哪个 temperature 最适合这个问题
# 测试问题: "给变量取名：存储用户最后登录时间"
def find_best_temperature(question: str, options=None):
    if options is None:
        options = [0, 0.3, 0.7, 1.0]
    # pass  # 替换为你的代码
    for option in options:
        print("--- temperature =", option, "---")
        message = client.messages.create(
            model=model_name,
            max_tokens=200,
            temperature=option,
            messages=[{"role": "user", "content": question}]
        )
        text = ""
        for (index, block) in enumerate(message.content):
            print(f"block: {block}{index}")
            if block.type == "text":
                text += block.text.strip()
        print(f"  回答: {text}")
        print()
find_best_temperature("给变量取名：存储用户最后登录时间")
# TODO 2: 写一个 Few-shot 翻译器
# - System Prompt: "你是中英文翻译器"
# - 给 2 个示例（中→英）
# - 然后翻译用户输入的中文
def translate(text: str) -> str:
    pass  # 替换为你的代码


# TODO 3: 写一个"安全问答"函数
# - 接收用户问题
# - System Prompt 中要求: 不确定就说不知道，回答要注明信息来源
# - 返回回复
def safe_ask(question: str) -> str:
    pass  # 替换为你的代码


# 取消注释测试:
# find_best_temperature("给变量取名：存储用户最后登录时间")
# print(translate("这个组件需要支持暗黑模式"))
# print(safe_ask("React 19 有哪些新特性？"))
