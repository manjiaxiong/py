# Day 3：评估与调试 — 让 AI 应用可测试、可观测

## 学习目标

掌握 AI 应用的评估和调试方法，建立"可测试、可观测"的开发习惯。

## 为什么 AI 应用需要评估？

Day 1-2 你已经能让 AI 提取数据了，但你发现：
- 同一个 Prompt，换个输入就翻车
- 改了一行 Prompt，之前能跑的 case 突然不行了
- 出了问题不知道是 Prompt 的锅还是模型的锅

传统软件测试：`assert add(1, 2) == 3` → 永远成立
AI 应用评估：`assert extract("iPhone 8999元")["price"] == 8999` → 大概率成立，但偶尔不成立

**这就是为什么 AI 应用需要专门的评估体系，而不是直接用单元测试。**

JS 类比：更像 E2E 测试——跑一批 case，看通过率，而不是追求 100% 通过。

## 学习内容

### 1. 评估集（Eval Dataset）

评估集 = 一组 {输入, 期望输出} 的集合，存成 JSON 文件：

```json
{
  "id": "eval_001",
  "input": "iPhone 15 Pro 256GB 深蓝色 售价 8999 元",
  "task": "extract_product",
  "expected": {"name": "iPhone 15 Pro", "price": 8999, "color": "深蓝色"},
  "check_fields": ["name", "price"],
  "tags": ["商品提取", "基础"]
}
```

**设计原则：**
- 覆盖正常 case（基础输入，确保基本功能）
- 覆盖边界 case（信息不全、格式奇怪、极端输入）
- 用 `tags` 分类，方便按场景筛选
- 用 `check_fields` 指定哪些字段必须正确（不要求所有字段精确匹配）

JS 类比：
```js
// Jest 测试用例
const testCases = [
  { input: "iPhone 15 8999元", expected: { name: "iPhone 15", price: 8999 } },
  { input: "没说价格的手机", expected: { name: "", price: 0 } },  // 边界 case
]
```

### 2. 带日志的 API 调用

每次调 API 都要记录日志，出问题时才能快速定位：

```python
log_entry = {
    "timestamp": "2024-01-15T10:30:00",
    "prompt": "提取商品信息...",
    "response": '{"name": "iPhone", "price": 8999}',
    "elapsed_ms": 1200,        # 耗时
    "input_tokens": 150,       # 输入 token
    "output_tokens": 50,       # 输出 token
    "total_tokens": 200,       # 总 token（= 费用）
}
```

JS 类比：就像给 `fetch` 加 interceptor 记录请求日志：
```js
axios.interceptors.response.use(response => {
  console.log({ url: response.config.url, status: response.status, duration: Date.now() - start })
  return response
})
```

### 3. 匹配策略

AI 的输出不是确定的，所以不能只用精确匹配：

| 匹配策略 | 适用场景 | 示例 |
|----------|---------|------|
| 精确匹配 | 数字、布尔值 | `actual["price"] == 8999` |
| 包含匹配 | 字符串（AI 可能多加字） | `"张三" in actual["name"]` |
| 列表匹配 | 数组（顺序可能不同） | `all(s in actual["skills"] for s in expected["skills"])` |
| AI 评判 | 开放式文本 | 让另一个 AI 判断语义是否一致 |

JS 类比：
```js
expect(actual.price).toBe(8999)              // 精确匹配
expect(actual.name).toContain("张三")         // 包含匹配
expect(actual.skills).toEqual(expect.arrayContaining(["React"]))  // 列表匹配
```

### 4. 衡量指标

跑完评估后关注这几个数字：

| 指标 | 含义 | 参考值 |
|------|------|--------|
| 通过率 | 正确 case 占比 | 目标 >= 90% |
| 平均延迟 | 每次调用耗时 | 生产环境 < 3s |
| 总 token | 所有调用消耗的 token | 越少越省钱 |
| 失败模式 | 失败 case 的共性 | 用来指导 prompt 优化方向 |

### 5. 失败样本分析

光知道"失败了"不够，要分析失败的**模式**：

| 失败模式 | 原因 | 解决方法 |
|----------|------|---------|
| JSON 解析失败 | AI 夹带了多余文字 | Prompt 加"不要加代码块标记" |
| 字段值错误 | AI 理解有误 | 加 Few-shot 示例 |
| 缺少字段 | Schema 定义不清 | 用 Tool Use 替代 Prompt 约束法 |
| 边界 case 失败 | 没有特殊处理 | 加边界 case 的 Few-shot |

JS 类比：类似 Sentry 的 error grouping——把相似的错误归类，找出根因。

### 6. 回归测试

场景：你觉得 Prompt 可以优化，改了一版。问题是——新 Prompt 在新 case 上好了，但旧 case 会不会退化？

```
V1 Prompt: "提取商品信息，返回 JSON"
V2 Prompt: "提取商品信息，返回 JSON（加了 few-shot 示例）"

V1 通过率: 80% (4/5)
V2 通过率: 100% (5/5)  → 看起来更好

但如果 V1 能过的 case 在 V2 里反而挂了 → 退化！
```

**做法：改 Prompt 之前先跑一遍评估，改之后再跑一遍，对比。**

JS 类比：就像视觉回归测试（Percy / Chromatic），截图对比改动前后的 UI 差异。

### 7. 日志持久化

内存里的日志重启就没了，要写到文件里。推荐用 JSONL 格式（每行一条 JSON）：

```
{"timestamp": "...", "prompt": "...", "response": "...", "elapsed_ms": 1200}
{"timestamp": "...", "prompt": "...", "response": "...", "elapsed_ms": 800}
```

**为什么用 JSONL 而不是 JSON？**
- JSON：需要一次性读写整个文件，文件大了很卡
- JSONL：可以逐行追加（`"a"` 模式），适合日志场景

JS 类比：类似 winston logger 写 JSON 格式日志文件。

## JS vs Python 评估对比

| 概念 | 前端场景 | AI 评估场景 |
|------|---------|------------|
| 单元测试 | Jest `expect().toBe()` | 精确匹配 check_fields |
| E2E 测试 | Playwright 跑一批场景 | `run_eval()` 跑评估集 |
| 视觉回归 | Percy 截图对比 | 回归测试对比通过率 |
| 请求日志 | axios interceptor | `ask_with_log()` 记录 |
| 错误监控 | Sentry error grouping | 失败样本分析 |
| 覆盖率 | Istanbul coverage | tags 覆盖不同场景 |

## 关键要点

1. **AI 评估 ≠ 传统单测** — 追求通过率 >= 阈值，不是 100%
2. **评估集是资产** — 要版本控制，持续积累，每次遇到新 bug 就加一条
3. **改 Prompt 必跑回归** — 防止"修一个 bug 引入两个 bug"
4. **日志是最好的调试工具** — 记录 prompt/response/token/耗时
5. **关注失败模式** — 不是一条一条修，而是找共性批量解决

## 推荐资源

- [OpenAI Eval 框架](https://github.com/openai/evals)
- [Anthropic Prompt 评估指南](https://docs.anthropic.com/en/docs/build-with-claude/develop-tests)
- [Braintrust — AI 评估平台](https://www.braintrust.dev/)
