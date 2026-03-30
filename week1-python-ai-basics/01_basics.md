# Day 1：Python 基础 — 对比 JavaScript 快速上手

## 学习内容

1. **变量与数据类型** — 直接赋值，无需 const/let/var
2. **字符串操作** — f-string、常用方法
3. **列表 (List)** — 等价于 JS 的 Array，额外掌握切片和列表推导式
4. **字典 (Dict)** — 等价于 JS 的 Object
5. **函数** — def 定义、默认参数、多返回值
6. **条件与循环** — 缩进代替花括号、range()、elif

## JS vs Python 速查

| 概念 | JavaScript | Python |
|------|-----------|--------|
| 声明变量 | `const name = "Alice"` | `name = "Alice"` |
| 布尔值 | `true / false` | `True / False` |
| 模板字符串 | `` `Hello, ${name}` `` | `f"Hello, {name}"` |
| 字符串长度 | `str.length` | `len(str)` |
| 包含判断 | `str.includes("x")` | `"x" in str` |
| 数组追加 | `arr.push(item)` | `arr.append(item)` |
| 最后一个元素 | `arr[arr.length - 1]` | `arr[-1]` |
| map | `arr.map(n => n * 2)` | `[n * 2 for n in arr]` |
| filter + map | `arr.filter(…).map(…)` | `[n * 2 for n in arr if n > 2]` |
| 对象取值 | `obj.key` 或 `obj["key"]` | `dict["key"]` 或 `dict.get("key")` |
| 函数定义 | `function fn() {}` | `def fn():` |
| 解构赋值 | `const [a, b] = arr` | `a, b = tuple` |
| 代码块 | `{ ... }` | 缩进（4个空格） |
| else if | `else if` | `elif` |
| 空值 | `null / undefined` | `None` |

## 注意事项

- **缩进是语法**：Python 用缩进（4个空格）代替花括号，缩进错误会直接报错，这是前端转 Python 最容易踩的坑
- **无分号**：Python 语句末尾不需要 `;`
- **布尔值大写**：`True` / `False` / `None` 首字母大写
- **字典取值**：`dict["key"]` 如果 key 不存在会报 `KeyError`，用 `dict.get("key", 默认值)` 更安全
- **range() 不含末尾**：`range(5)` 是 0-4，和 JS 的习惯一致但要记住

## 练习

文件底部有 3 个 TODO 练习题，完成后取消注释运行验证。
