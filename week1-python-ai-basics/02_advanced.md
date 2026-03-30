# Day 2：Python 进阶 — 类、模块、异步编程

## 学习内容

1. **类 (Class)** — 等价于 JS 的 class，但有 `self` 关键字
2. **模块与导入** — 等价于 JS 的 import/export
3. **异常处理** — try/except，等价于 JS 的 try/catch
4. **异步编程** — async/await，和 JS 几乎一样的语法
5. **类型提示** — 类似 TypeScript 的类型标注

## JS vs Python 速查

| 概念 | JavaScript | Python |
|------|-----------|--------|
| 类定义 | `class Foo {}` | `class Foo:` |
| 构造函数 | `constructor()` | `__init__(self)` |
| this | `this.name` | `self.name` |
| 继承 | `class B extends A` | `class B(A):` |
| 导入 | `import { x } from './mod'` | `from mod import x` |
| 默认导出 | `export default` | 无，直接 import 模块 |
| try/catch | `try {} catch(e) {}` | `try: ... except Exception as e:` |
| async/await | `async function` | `async def` |
| Promise | `new Promise(...)` | `asyncio.Future` |
| Promise.all | `Promise.all([...])` | `asyncio.gather(...)` |
| 类型标注 | TypeScript `: string` | `: str`（运行时不强制） |

## 注意事项

- **self 不能省略**：类方法的第一个参数必须是 `self`，相当于 JS 的 `this`，但要显式写出
- **Python 没有 private**：约定用 `_` 前缀表示私有（如 `_internal_method`），但实际上仍可访问
- **async 必须用 asyncio 驱动**：不能直接调用 `async def` 函数，必须通过 `asyncio.run()` 或 `await`
- **类型提示不强制**：Python 的类型标注只是提示，运行时不检查，但 IDE 和 mypy 会用
- **异常要具体**：尽量 `except ValueError` 而非 `except Exception`，避免吞掉意外错误
