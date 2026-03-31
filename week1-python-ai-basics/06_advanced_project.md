# Day 6-7：综合项目 — 带记忆的多功能 AI 助手

## 学习内容

1. **文件读写** — 读取本地文件作为上下文提供给 AI
2. **装饰器实战** — 用装饰器实现函数计时、重试等功能
3. **异步并发** — asyncio 实现并行 AI 调用
4. **结构化输出** — 让 AI 返回 JSON 格式的结构化数据
5. **综合应用** — 整合所有知识构建一个实用工具

## 知识点对照

| 概念 | 前端等价物 | Python 实现 |
|------|-----------|------------|
| 文件读取 | `fs.readFileSync()` | `open()` + `read()` 或 `Path.read_text()` |
| 装饰器 | 高阶函数 / HOC | `@decorator` 语法 |
| 并发请求 | `Promise.all()` | `asyncio.gather()` |
| JSON Schema | Zod / Yup 校验 | `json.loads()` + 手动校验 |
| 错误重试 | axios-retry | 自己写装饰器 |

## 注意事项

- **文件编码**：Windows 上读中文文件要指定 `encoding="utf-8"`，否则可能乱码
- **装饰器本质是高阶函数**：接收函数返回函数，和 React 的 HOC 概念一样
- **结构化输出不一定靠谱**：AI 返回的 JSON 可能格式不对，一定要 try/except
- **async 版本的 anthropic**：用 `anthropic.AsyncAnthropic` 创建异步客户端
- **`with open()` 要养成习惯**：自动关闭文件，类似前端的 `finally` 清理资源
