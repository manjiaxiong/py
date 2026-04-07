# Day 1：Prompt Engineering — 让 AI 听懂你的话

## 学习目标

掌握 Prompt 工程的核心技巧，让 AI 的回答更准确、更可控。

## 为什么要学 Prompt Engineering？

你第一周已经会调用 API 了，但你发现：
- AI 有时候答非所问
- 返回格式不稳定
- 同一个问题每次回答不一样

Prompt Engineering 就是解决这些问题的——**用更好的提示词，让 AI 给出更好的回答**。

类比：就像你给初级开发写需求文档，写得越清楚，交付质量越高。

## 学习内容

### 1. Prompt 的基本结构

一个好的 Prompt 通常包含：

```
角色（Role）     → 你是谁
任务（Task）     → 你要做什么
格式（Format）   → 用什么格式回答
约束（Constraint）→ 不要做什么
示例（Example）  → 给一个参考
```

JS 类比：就像写一个函数的 JSDoc 注释 —— 参数说明越清楚，调用方越不容易出错。

### 2. Few-shot Prompting（少样本提示）

给 AI 几个输入→输出的示例，让它模仿格式：

```
用户：修复了登录页面点击无反应的bug
助手：fix: 修复登录页面点击事件未绑定的问题

用户：把用户列表改成了分页加载
助手：feat: 用户列表改为分页加载模式

用户：重构了支付模块的代码结构
助手：???（AI 自己推断格式）
```

**要点：2-3 个示例最佳，太多反而浪费 token**

### 3. Chain-of-Thought（思维链）

让 AI 分步推理，而不是直接给答案：

❌ 差的 Prompt：
```
这段代码有什么bug？
```

✅ 好的 Prompt：
```
请分析这段代码：
1. 先说明代码的意图
2. 逐行检查可能的问题
3. 给出修复建议和修复后的代码
```

类比：就像 Code Review，不是只说"有bug"，而是说明推理过程。

### 4. System Prompt 设计原则

System Prompt = 给 AI 设定角色和行为规则

```python
system = """你是一个资深 Python 代码审查员。

规则：
1. 只关注代码质量问题，不要重写整个函数
2. 每个问题给出：问题描述 → 影响 → 修复建议
3. 用中文回答
4. 如果代码没问题，直接说"代码看起来不错"
"""
```

**设计技巧：**
- 明确角色：不要只说"你是助手"，要说具体是什么领域的专家
- 定义边界：明确说什么该做、什么不该做
- 规定格式：告诉 AI 用什么结构输出
- 给约束：限制回答长度、语言、风格

### 5. Prompt 反模式（常见错误）

| 反模式 | 为什么不好 | 改进 |
|--------|----------|------|
| 太模糊："帮我优化代码" | AI 不知道优化什么方面 | "帮我优化这段代码的性能，重点关注循环和内存使用" |
| 太长：塞了一堆背景 | 关键信息被淹没 | 把核心需求放在开头，背景放后面 |
| 无约束："随便怎么回答都行" | 格式不可控 | 明确输出格式（JSON/Markdown/列表） |
| 负面指令："不要用递归" | AI 反而更容易用递归 | "请用循环实现" |

### 6. Prompt 模板化

把 Prompt 做成可复用的模板，用变量填充：

```python
template = """分析以下 {language} 代码，找出潜在问题：

```{language}
{code}
```

请按以下格式回答：
1. 代码意图：一句话总结
2. 发现的问题：列表形式
3. 修复建议：给出修改后的代码
"""

# 使用时填充变量
prompt = template.format(language="Python", code=user_code)
```

JS 类比：
```js
const template = (lang, code) => `分析以下 ${lang} 代码...`
```

## JS vs Python Prompt 开发对比

| 概念 | 前端场景 | Prompt 场景 |
|------|---------|------------|
| 需求文档 | 写给开发看的 PRD | System Prompt |
| 示例代码 | Storybook stories | Few-shot examples |
| 接口约定 | TypeScript interface | 输出格式约束 |
| 单元测试 | Jest test cases | 对同一 Prompt 多次测试 |
| Code Review | 逐行审查 | Chain-of-Thought 分步分析 |

## 关键要点

1. **结构化 > 自由发挥** — 给 AI 明确的格式要求
2. **示例 > 描述** — 给 2-3 个 Few-shot 比长篇描述有效
3. **分步 > 一步到位** — Chain-of-Thought 让推理更准确
4. **正面 > 负面** — "请用X" 比 "不要用Y" 效果好
5. **简洁 > 冗长** — Prompt 越短越好，但不能少关键信息

## 推荐资源

- [Anthropic Prompt Engineering Guide](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering)
- [Prompt Engineering Guide 中文版](https://www.promptingguide.ai/zh)
