# ===========================================
# Python 3.8 ~ 3.13 新语法速查
# ===========================================
# 按版本整理，每个特性都有 JS 类比
# 你的版本: 3.11，标注了 ✅ 能用 / ❌ 不能用
# ===========================================


# ===========================================
# Python 3.8 — 海象运算符 :=  ✅
# ===========================================
# 赋值的同时返回值，减少重复代码
# JS 没有直接对应，最接近的是 if (x = getValue())（但 JS 不推荐这样写）

print("=== 3.8 海象运算符 := ===\n")

# --- 之前：要写两行 ---
data = "hello"
if data:
    print(f"普通写法: {data}")

# --- 现在：一行搞定 ---
if (data := "hello"):
    print(f"海象运算符: {data}")

# --- 实际场景 1: 循环读取 ---
# while (line := f.readline()):
#     process(line)
# 等价于:
# line = f.readline()
# while line:
#     process(line)
#     line = f.readline()

# --- 实际场景 2: 列表推导式中避免重复计算 ---
nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# 之前: len() 被调用两次
# result = [(len(str(n)), str(n)) for n in nums if len(str(n)) > 1]

# 现在: 只算一次
result = [(length, str(n)) for n in nums if (length := len(str(n))) > 1]
print(f"海象 + 推导式: {result}")  # [(2, '10')]

# --- 实际场景 3: 正则匹配 ---
import re
text = "我的邮箱是 test@example.com"
if (match := re.search(r'\S+@\S+', text)):
    print(f"找到邮箱: {match.group()}")  # test@example.com


# ===========================================
# Python 3.9 — 字典合并 | 和类型注解简化  ✅
# ===========================================

print(f"\n=== 3.9 字典合并 | ===\n")

# --- 字典合并运算符 | ---
# = JS: { ...defaults, ...user }

defaults = {"theme": "light", "lang": "zh", "fontSize": 14}
user_settings = {"theme": "dark", "fontSize": 16}

# | 合并，返回新字典（不改原字典）
merged = defaults | user_settings
print(f"| 合并: {merged}")  # {'theme': 'dark', 'lang': 'zh', 'fontSize': 16}

# |= 原地合并（修改原字典）
# = JS: Object.assign(defaults, user)
defaults_copy = defaults.copy()
defaults_copy |= user_settings
print(f"|= 原地合并: {defaults_copy}")  # {'theme': 'dark', 'lang': 'zh', 'fontSize': 16}

# 对比旧写法:
# merged = {**defaults, **user_settings}     # 3.5+ 就能用
# defaults.update(user_settings)             # 原地合并旧写法

# --- 类型注解简化 ---
# 之前 (3.8):
# from typing import List, Dict, Optional
# def foo(items: List[int]) -> Dict[str, int]: ...

# 现在 (3.9+): 直接用内置类型，不用导入
def foo(items: list[int]) -> dict[str, int]:
    return {str(i): i for i in items}

# str | None 替代 Optional[str]（3.10 才完全支持，见下方）


# ===========================================
# Python 3.10 — match/case 模式匹配  ✅
# ===========================================
# = JS 的 switch，但强大得多

print(f"\n=== 3.10 match/case 模式匹配 ===\n")

# --- 基础用法: 像 switch ---

status = 404

match status:
    case 200:
        msg = "成功"
    case 404:
        msg = "未找到"
    case 500:
        msg = "服务器错误"
    case _:                      # _ = default
        msg = "未知状态"

print(f"状态码 {status}: {msg}")  # 状态码 404: 未找到

# JS 对比:
# switch(status) {
#   case 200: msg = "成功"; break;
#   case 404: msg = "未找到"; break;
#   default: msg = "未知状态";
# }

# --- 进阶: 解构字典（JS switch 做不到） ---

event = {"type": "click", "x": 100, "y": 200}

match event:
    case {"type": "click", "x": x, "y": y}:
        print(f"点击坐标: ({x}, {y})")  # 点击坐标: (100, 200)
    case {"type": "scroll", "direction": d}:
        print(f"滚动方向: {d}")
    case _:
        print("未知事件")

# JS 类似写法（但没这么优雅）:
# const { type } = event
# if (type === 'click') { const { x, y } = event; ... }

# --- 进阶: 解构列表 ---

command = ["move", 10, 20]

match command:
    case ["quit"]:
        print("退出")
    case ["move", x, y]:
        print(f"移动到 ({x}, {y})")  # 移动到 (10, 20)
    case ["say", *words]:            # *words 收集剩余
        print(f"说: {' '.join(words)}")

# --- 进阶: 类型匹配 + 守卫条件 ---

value = 42

match value:
    case int(n) if n > 0:
        print(f"正整数: {n}")    # 正整数: 42
    case int(n) if n < 0:
        print(f"负整数: {n}")
    case str(s):
        print(f"字符串: {s}")

# --- 类型注解: X | Y 替代 Union ---

# 之前 (3.9):
# from typing import Union
# def foo(x: Union[int, str]) -> None: ...

# 现在 (3.10+):
def process(x: int | str) -> None:
    print(x)

# 也可以用在 isinstance
print(f"isinstance(42, int | str): {isinstance(42, int | str)}")  # True


# ===========================================
# Python 3.11 — 异常组 + 更好的错误提示  ✅
# ===========================================

print(f"\n=== 3.11 异常组 ExceptionGroup ===\n")

# --- ExceptionGroup: 一次抛出多个异常 ---
# 适用于并发场景（多个任务同时失败）

# except* 可以分别捕获不同类型
try:
    raise ExceptionGroup("多个错误", [
        ValueError("值错误"),
        TypeError("类型错误"),
    ])
except* ValueError as eg:
    print(f"捕获 ValueError: {eg.exceptions}")  # (ValueError('值错误'),)
except* TypeError as eg:
    print(f"捕获 TypeError: {eg.exceptions}")    # (TypeError('类型错误'),)

# JS 对比: Promise.allSettled() 收集多个失败
# const results = await Promise.allSettled([p1, p2, p3])
# const errors = results.filter(r => r.status === 'rejected')

# --- 更精确的错误提示 ---
# 3.11 的报错信息会精确指向出错的位置
# 比如 x['a']['b']['c'] 报错，会用 ^^^^ 指向具体哪个 key 有问题
# （这个不需要代码演示，你遇到报错时自然会看到）


# ===========================================
# Python 3.12 — f-string 增强 + 类型参数  ❌ 你是3.11
# ===========================================

print(f"\n=== 3.12 新特性（你暂时用不了） ===\n")

# --- f-string 里可以嵌套相同引号了 ---
# 3.11: f"name: {d['name']}" 里面必须用不同引号
# 3.12: f"name: {d["name"]}" 随便嵌套 ✅

# --- 类型参数语法 ---
# 之前:
# from typing import TypeVar
# T = TypeVar('T')
# def first(items: list[T]) -> T: ...

# 3.12:
# def first[T](items: list[T]) -> T:  # 直接在函数上声明泛型
#     return items[0]

# JS 类比: function first<T>(items: T[]): T { return items[0] }


# ===========================================
# Python 3.13 — JIT 编译器 + 改进的 REPL  ❌ 你是3.11
# ===========================================

print(f"\n=== 3.13 新特性（你暂时用不了） ===\n")

# --- 实验性 JIT 编译器 ---
# 自动把热点代码编译成机器码，性能提升
# 不需要改代码，解释器自动优化

# --- 改进的交互式 REPL ---
# python 命令进入交互模式后:
# - 支持多行编辑（之前按回车就执行了）
# - 彩色输出
# - 更好的 tab 补全

# --- 改进的错误提示 ---
# 比 3.11 更精确，颜色高亮

print("提示: 3.12/3.13 的特性等你升级后自然就能用了，不急")


# ===========================================
# 总结: 最实用的新语法（按使用频率排序）
# ===========================================
#
# 1. f-string             3.6+  ✅  — 你每天都在用
# 2. := 海象运算符         3.8+  ✅  — 少写一行代码
# 3. | 字典合并            3.9+  ✅  — 替代 {**a, **b}
# 4. match/case           3.10+ ✅  — 替代一堆 if/elif
# 5. int | str 类型注解    3.10+ ✅  — 替代 Union[int, str]
# 6. except*              3.11+ ✅  — 并发异常处理
# 7. f-string 嵌套引号     3.12+ ❌  — 等升级
