# Day 2：结构化输出 — 让 AI 返回你想要的格式

## 学习目标

让 AI 的回答从"自由发挥"变成"严格按格式返回"，掌握 JSON Mode、Tool Use、输出验证。

## 为什么需要结构化输出？

Day 1 你学会了写好 Prompt，但 AI 的回答还是"文本"。实际开发中你需要的是**数据**：

```
AI 回答: "这个商品价格是 99 元，颜色是黑色"     ← 文本，没法直接用
你需要:  {"price": 99, "color": "黑色"}          ← JSON，直接塞进代码
```

JS 类比：就像后端 API 必须返回 JSON，而不是返回一段话让前端自己解析。

## 学习内容

### 1. Prompt 约束法（最简单）

直接在 Prompt 里告诉 AI "返回 JSON"：

```python
prompt = """提取信息，直接返回 JSON（不要加 markdown 代码块）：
{"name": "...", "price": 数字, "color": "..."}

输入：iPhone 15 黑色 128GB 售价 5999 元"""
```

**优点：** 简单，不需要额外工具
**缺点：** AI 偶尔会加 ```json 标记、多输出解释文字，不够稳定

### 2. Tool Use / Function Calling（推荐）

告诉 AI "你有一个工具可以调用"，AI 就会严格按工具的参数格式返回：

```python
tools = [{
    "name": "extract_product",
    "description": "提取商品信息",
    "input_schema": {
        "type": "object",
        "properties": {
            "name":  {"type": "string", "description": "商品名称"},
            "price": {"type": "number", "description": "价格（数字）"},
            "color": {"type": "string", "description": "颜色"},
        },
        "required": ["name", "price"]
    }
}]
```

JS 类比：
```js
// 就像给 API 定义一个 TypeScript interface
// AI 被迫按这个 interface 返回数据
interface Product {
  name: string
  price: number
  color?: string
}
```

**优点：** 格式最稳定，AI 严格按 schema 返回
**缺点：** 写起来稍复杂

### 3. Pydantic 验证（Python 特色）

用 Pydantic 定义数据模型，验证 AI 返回的 JSON 是否合法：

```python
from pydantic import BaseModel

class Product(BaseModel):
    name: str
    price: float
    color: str = "未知"   # 默认值
```

JS 类比：
```js
// 类似于 Zod schema 验证
const ProductSchema = z.object({
  name: z.string(),
  price: z.number(),
  color: z.string().default("未知"),
})
```

### 4. 三种方式对比

| 方式 | 稳定性 | 复杂度 | 适用场景 |
|------|--------|--------|---------|
| Prompt 约束 | ⭐⭐ | 简单 | 快速原型、简单场景 |
| Tool Use | ⭐⭐⭐⭐ | 中等 | 生产环境、需要严格格式 |
| Pydantic | ⭐⭐⭐ | 中等 | 需要类型验证、数据清洗 |

### 5. Tool Use 进阶 — 让 AI 调用多个工具

可以给 AI 多个工具，让它自己判断用哪个：

```python
tools = [
    {"name": "get_weather", ...},     # 查天气
    {"name": "search_product", ...},  # 搜商品
    {"name": "calculate", ...},       # 计算
]

# AI 收到 "北京今天多少度" → 自动选择 get_weather
# AI 收到 "iPhone 多少钱"   → 自动选择 search_product
```

JS 类比：就像 React Router 根据 URL 自动匹配路由。

### 6. 错误处理

AI 返回的 JSON 可能不合法，必须做防御：

```python
import json

try:
    data = json.loads(ai_response)
except json.JSONDecodeError:
    # 回退方案：让 AI 重新生成
    pass
```

## 关键要点

1. **Tool Use 最稳定** — 生产环境首选
2. **Prompt 约束最快** — 原型验证时用
3. **一定要验证** — 永远不要信任 AI 返回的 JSON，先 parse 再用
4. **给默认值** — 用 Pydantic 或 dict.get() 处理缺失字段
5. **有退路** — JSON 解析失败时要有兜底方案

## 推荐资源

- [Anthropic Tool Use 文档](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
- [Pydantic 官方文档](https://docs.pydantic.dev/)
