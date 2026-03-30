# ===========================================
# Day 2: Python 进阶 — 类、模块、异步编程
# ===========================================

# ----- 1. 类 (Class) -----
# JS:  class User { constructor(name) { this.name = name } }
# Py:  self 代替 this，__init__ 代替 constructor

class Person:
    """一个简单的 Person 类"""

    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age
class User(Person):
    """用户类 — 演示 Python 面向对象"""

    def __init__(self, name: str, age: int):
        super().__init__(name, age)
        self._login_count = 0  # _ 前缀表示"私有"（约定，非强制）

    def greet(self) -> str:
        """实例方法 — 注意第一个参数必须是 self"""
        return f"Hi, I'm {self.name}, {self.age} years old"

    def login(self):
        self._login_count += 1
        print(f"{self.name} 登录了，累计 {self._login_count} 次")

# 使用类
user = User("Alice", 25)
print(user.greet())
user.login()
user.login()


# 继承 — JS: class Admin extends User
class Admin(User):
    def __init__(self, name: str, age: int, role: str = "admin"):
        super().__init__(name, age)  # JS: super(name, age)
        self.role = role

    def greet(self) -> str:
        """方法重写"""
        return f"[{self.role}] {super().greet()}"

admin = Admin("Bob", 30)
print(admin.greet())


# ----- 2. 模块与导入 -----
# Python 的导入系统，类比 JS 的 import

# JS:  import os from 'os'            →  import os
# JS:  import { path } from 'os'      →  from os import path
# JS:  import * as os from 'os'       →  import os (本身就是这样)
# JS:  import { x as y } from 'mod'   →  from mod import x as y

import os
import json
from datetime import datetime, timedelta
from pathlib import Path  # 比 os.path 更现代的路径处理

# 常用示例
print(f"当前目录: {os.getcwd()}")
print(f"当前文件路径: {Path().resolve()}")
print(f"当前时间: {datetime.now()}")
print(f"明天: {datetime.now() + timedelta(days=1)}")

# JSON 处理 — 和 JS 几乎一样
# JS: JSON.stringify(obj)  →  json.dumps(obj)
# JS: JSON.parse(str)      →  json.loads(str)
data = {"name": "Alice", "scores": [90, 85, 92]}
# ensure_ascii=False 让中文正常显示，indent=2 美化输出
json_str = json.dumps(data, ensure_ascii=False, indent=2)
print(f"JSON 字符串:\n{json_str}")
parsed = json.loads(json_str)
print(f"解析回来: {parsed['name']}")


# ----- 3. 异常处理 -----
# JS:  try { ... } catch(e) { ... } finally { ... }
# Py:  try: ... except: ... finally: ...

def safe_divide(a, b):
    try:
        result = a / b
        return result
    except ZeroDivisionError:
        print("错误：不能除以零！")
        return None
    except TypeError as e:
        print(f"类型错误: {e}")
        return None
    finally:
        print("（计算完毕）")  # 无论如何都会执行

result = safe_divide(10, 3)
if result is not None:
    print(f"原始结果: {result}")
    print(f"保留三位小数: {result:.3f}")
    print(f"保留整数（四舍五入）: {round(result)}")
    print(f"保留整数（直接取整）: {int(result)}")

print(safe_divide(10, 0))
print(safe_divide("10", 3))


# ----- 4. 异步编程 (async/await) -----
# 这部分和 JS 的 async/await 非常像！
# 区别：JS 用事件循环自动驱动，Python 需要 asyncio

import asyncio

async def fetch_data(name: str, delay: float) -> str:
    """模拟异步请求 — 类似 JS 的 fetch()"""
    print(f"开始获取 {name} ...")
    await asyncio.sleep(delay)  # JS: await new Promise(r => setTimeout(r, delay))
    return f"{name} 的数据（耗时 {delay}s）"

async def main():
    # 串行执行 — 一个接一个
    print("=== 串行执行 ===")
    result1 = await fetch_data("用户信息", 1)
    result2 = await fetch_data("订单列表", 1)
    print(result1)
    print(result2)

    # 并行执行 — 类似 Promise.all()
    print("\n=== 并行执行 (asyncio.gather) ===")
    results = await asyncio.gather(
        fetch_data("用户信息", 1.1),
        fetch_data("订单列表", 0.3),
        fetch_data("商品详情", 1)
    )
    for r in results:
        print(r)

# 运行异步函数 — JS 里顶层可以直接 await，Python 需要这样启动
asyncio.run(main())


# ----- 5. 类型提示 (Type Hints) -----
# Python 的类型标注 — 类似 TypeScript 但不强制
# 运行时不报错，但 IDE 会给提示，后面用 AI SDK 时会大量用到

from typing import Optional

def process_user(
    name: str,
    age: int,
    email: Optional[str] = None  # Optional 表示可以是 None
) -> dict:
    """
    类型标注示例:
    - name: str  → TS 的 name: string
    - age: int   → TS 的 age: number
    - Optional[str] → TS 的 string | null
    - -> dict → TS 的 返回类型 : Record<string, any>
    """
    return {
        "name": name,
        "age": age,
        "email": email or "未提供"
    }

result = process_user("Alice", 25, "alice@example.com")
print(result)

# 更多类型标注
from typing import Union

def format_id(id: Union[int, str]) -> str:
    """Union[int, str] 等价于 TS 的 number | string"""
    return f"ID-{id}"

print(format_id(42))
print(format_id("abc"))


# ===========================================
# 练习
# ===========================================

# TODO 1: 创建一个 ChatMessage 类
# - 属性: role (str), content (str), timestamp (datetime)
# - 方法: format() 返回格式化字符串 "[时间] role: content"
class ChatMessage:
    def __init__(self, role: str, content: str, timestamp: datetime):
        self.role = role
        self.content = content
        self.timestamp = timestamp

    def format(self) -> str:
        time_str = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        return f"[{time_str}] {self.role}: {self.content}"

chat = ChatMessage("user", "Hello!", datetime.now())
print(chat.format())
# TODO 2: 写一个异步函数 fetch_multiple，接收一个 URL 列表(字符串列表)
# 对每个 URL 模拟 0.5s 延迟获取，最后并行返回所有结果
async def fetch_multiple(urls: list[str]) -> list[str]:
    pass  # 替换为你的代码


# TODO 3: 写一个函数 safe_parse_json
# 接收一个字符串，尝试解析为 JSON，失败返回 None
def safe_parse_json(text: str) -> Optional[dict]:
    pass  # 替换为你的代码


# 取消注释测试：
# msg = ChatMessage("user", "Hello!")
# print(msg.format())

# asyncio.run(fetch_multiple(["https://api.example.com/users", "https://api.example.com/orders"]))

# print(safe_parse_json('{"name": "test"}'))
# print(safe_parse_json('invalid json'))
