# ===========================================
# Day 1: Prompt Engineering — 让 AI 听懂你的话
# ===========================================
# 掌握 Prompt 的核心技巧：Few-shot、Chain-of-Thought、模板化
# 每个技巧都有可运行的代码示例
# ===========================================

import os
from pathlib import Path
from dotenv import load_dotenv
from anthropic import Anthropic

# 加载环境变量
load_dotenv(Path(__file__).parent / ".env")

client = Anthropic(
    api_key=os.getenv("MINIMAX_API_KEY"),
    base_url=os.getenv("MINIMAX_API_BASE"),
)
MODEL = os.getenv("MINIMAX_MODEL_NAME")


def ask(prompt, system="", max_tokens=500):
    """
    封装 API 调用，方便后面反复使用

    参数:
        prompt: 用户消息
        system: 系统提示词（可选）
        max_tokens: 最大回复长度
    """
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=messages,
    )
    return response.content[0].text.strip()


# ===========================================
# 1. 基础 Prompt — 直接提问 vs 结构化提问
# ===========================================

print("=== 1. 基础 Prompt 对比 ===\n")

# ❌ 模糊的 Prompt
bad_prompt = "帮我看看这段代码"

# ✅ 结构化的 Prompt — 明确说了要看什么、怎么回答
good_prompt = """分析以下 Python 代码，找出潜在问题：

```python
def get_user(users, name):
    for user in users:
        if user['name'] == name:
            return user
    return None
```

请按以下格式回答：
1. 代码意图：一句话总结
2. 潜在问题：列表形式，每个问题说明影响
3. 改进建议：给出修改后的代码"""

print("--- 结构化 Prompt 的效果 ---")
result = ask(good_prompt)
print(result, end="", flush=True)


# ===========================================
# 2. Few-shot Prompting — 给示例让 AI 照格式回答
# ===========================================
# 你在第一周的 format_commit 函数里已经用过了！
# 这里更系统地讲解

print(f"\n{'='*50}")
print("=== 2. Few-shot Prompting ===\n")


def extract_info(text):
    """
    用 Few-shot 从文本中提取结构化信息

    原理：给 AI 几个 输入→输出 的示例，它就会模仿格式
    JS 类比：就像给 AI 看了几个单元测试的输入输出，它自己推断逻辑
    """
    # 用 messages 数组构造 few-shot 示例
    # 每一对 user + assistant 就是一个示例
    messages = [
        # 示例 1
        {"role": "user", "content": "张三今年28岁，在北京的字节跳动做前端开发，年薪50万"},
        {"role": "assistant", "content": '{"name": "张三", "age": 28, "city": "北京", "company": "字节跳动", "role": "前端开发", "salary": "50万"}'},

        # 示例 2
        {"role": "user", "content": "李四，32岁，上海腾讯后端工程师，年薪65万"},
        {"role": "assistant", "content": '{"name": "李四", "age": 32, "city": "上海", "company": "腾讯", "role": "后端工程师", "salary": "65万"}'},

        # 真正的输入
        {"role": "user", "content": text},
    ]

    response = client.messages.create(
        model=MODEL,
        max_tokens=200,
        messages=messages,
    )
    return response.content[0].text.strip()


# 测试
test_text = "王五25岁，深圳阿里云的算法工程师，年薪55万"
print(f"输入: {test_text}")
print(f"输出: {extract_info(test_text)}")

# Few-shot 的关键：
# 1. 示例要覆盖不同情况（不同格式的输入）
# 2. 2-3 个示例最佳，太多浪费 token
# 3. 示例的输出格式要完全一致


# ===========================================
# 3. Chain-of-Thought — 让 AI 分步思考
# ===========================================
# 关键词："请一步一步分析"、"Let's think step by step"
# 适合复杂推理、数学计算、代码分析

print(f"\n{'='*50}")
print("=== 3. Chain-of-Thought ===\n")

# ❌ 不用 CoT：AI 可能直接猜一个答案
bad_prompt = "这段代码的时间复杂度是多少？def find(arr, target): ..."

# ✅ 用 CoT：让 AI 展示推理过程
cot_prompt = """分析以下代码的时间复杂度，请一步一步推理：

```python
def find_pairs(arr, target):
    result = []
    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):
            if arr[i] + arr[j] == target:
                result.append((arr[i], arr[j]))
    return result
```

请按以下步骤分析：
1. 识别所有循环结构
2. 分析每层循环的执行次数
3. 计算总的时间复杂度
4. 给出优化建议"""

print("--- Chain-of-Thought 效果 ---")
result = ask(cot_prompt)
print(result)


# ===========================================
# 4. System Prompt 设计 — 给 AI 设角色
# ===========================================

print(f"\n{'='*50}")
print("=== 4. System Prompt 角色设计 ===\n")

# --- 角色 1: 严格的代码审查员 ---
code_reviewer = """你是一个资深 Python 代码审查员（10年经验）。

规则：
1. 只关注代码质量问题（命名、结构、潜在bug）
2. 不要重写整个函数，只指出问题
3. 每个问题用这个格式：
   - 问题：xxx
   - 影响：xxx
   - 建议：xxx
4. 如果代码没问题，直接说"LGTM"
5. 最多列出 3 个最重要的问题"""

# --- 角色 2: 耐心的编程导师 ---
teacher = """你是一个面向 JavaScript 开发者的 Python 导师。

规则：
1. 解释时必须用 JS 类比
2. 先说 Python 怎么写，再说 JS 怎么写，对比差异
3. 用简单的例子，不要用太复杂的代码
4. 语气友好鼓励，不要说"这很简单"之类的话"""

# 同一个问题，不同角色的回答完全不同
question = """看看这段代码：
def process(data):
    result = []
    for item in data:
        if item['status'] == 'active':
            result.append(item['name'].upper())
    return result"""

print("--- 代码审查员的回答 ---")
print(ask(question, system=code_reviewer))

print(f"\n--- 编程导师的回答 ---")
print(ask(question, system=teacher))


# ===========================================
# 5. Prompt 模板 — 可复用的 Prompt
# ===========================================
# 把 Prompt 做成模板，用变量填充
# JS 类比：模板字符串 / React 组件的 props

print(f"\n{'='*50}")
print("=== 5. Prompt 模板化 ===\n")


def create_prompt(template, **kwargs):
    """
    简单的 Prompt 模板引擎

    JS 类比:
    const createPrompt = (template, vars) =>
      template.replace(/\{(\w+)\}/g, (_, key) => vars[key])

    Python 用 .format(**kwargs) 就行，更简洁
    """
    return template.format(**kwargs)


# --- 模板：代码翻译器 ---
translate_template = """将以下 {source_lang} 代码翻译成 {target_lang}。

要求：
1. 保持相同的功能和逻辑
2. 使用 {target_lang} 的最佳实践和惯用写法
3. 添加注释说明 {source_lang} 和 {target_lang} 的关键差异

```{source_lang}
{code}
```"""

# 使用模板
prompt = create_prompt(
    translate_template,
    source_lang="JavaScript",
    target_lang="Python",
    code="""
const fetchUsers = async () => {
  try {
    const res = await fetch('/api/users')
    const data = await res.json()
    return data.filter(u => u.active).map(u => u.name)
  } catch (err) {
    console.error('Failed:', err)
    return []
  }
}
""".strip()
)

print("--- 代码翻译（JS → Python） ---")
print(ask(prompt, max_tokens=800))


# --- 模板：错误诊断器 ---
debug_template = """你是一个 Python 调试专家。

用户遇到了以下错误：

错误信息：
```
{error}
```

相关代码：
```python
{code}
```

请：
1. 解释错误原因（一句话）
2. 指出出错的具体位置
3. 给出修复代码"""

# 这样每次遇到报错，只需要填入 error 和 code 就行


# ===========================================
# 6. Prompt 优化技巧（进阶）
# ===========================================

print(f"\n{'='*50}")
print("=== 6. Prompt 优化技巧 ===\n")

# --- 技巧 1: 用 XML 标签分隔内容 ---
# 当 Prompt 里有多段内容时，用标签帮 AI 区分
xml_prompt = """分析用户的代码和需求，给出修改建议。

<user_requirement>
我想让这个函数支持按多个字段排序，比如先按 score 降序，再按 name 升序
</user_requirement>

<current_code>
def sort_students(students):
    return sorted(students, key=lambda x: x['score'], reverse=True)
</current_code>

请给出修改后的代码和解释。"""

print("--- XML 标签分隔 ---")
print(ask(xml_prompt))

# --- 技巧 2: 给 AI "退路" ---
# 让 AI 在不确定时说"不知道"，减少瞎编（hallucination）
safe_system = """你是一个 Python 技术顾问。

重要规则：
- 如果你不确定答案，请直接说"我不确定，建议查阅官方文档"
- 不要编造不存在的库或函数
- 引用的 API 需要注明版本号"""


# ===========================================
# 总结
# ===========================================

print(f"\n{'='*50}")
print("=== 总结 ===")
print("""
Prompt Engineering 六大技巧：

1. 结构化提问  — 明确 角色/任务/格式/约束
2. Few-shot    — 给 2-3 个示例，AI 照格式回答
3. CoT         — "请一步一步分析"，适合复杂推理
4. System Role — 设定专业角色，约束行为边界
5. 模板化      — 做成可复用的 Prompt 模板
6. XML 分隔    — 多段内容用标签区分，防止混淆

下一课：Day 2 结构化输出（JSON Mode + Tool Use）
""")
