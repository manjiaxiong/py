# ===========================================
# Day 1: Python 基础 — 对比 JavaScript 快速上手
# ===========================================

# ----- 1. 变量与数据类型 -----
# JS:  const name = "Alice"
# Py:  不需要 const/let/var，直接赋值
name = "Alice"
age = 25
is_developer = True  # 注意：True/False 首字母大写，不是 true/false
salary = 15000.5

print(f"姓名: {name}, 年龄: {age}")  # f-string 类似 JS 的模板字符串 `${}`

# 查看类型
print(type(name))    # <class 'str'>
print(type(age))     # <class 'int'>
print(type(is_developer))  # <class 'bool'>


# ----- 2. 字符串操作 -----
# Python 字符串方法和 JS 很像
greeting = "hello world"
print(greeting.upper())       # JS: greeting.toUpperCase()
print(greeting.split(" "))    # JS: greeting.split(" ") — 一样的！
print(len(greeting))          # JS: greeting.length — Python 用 len() 函数
print("hello" in greeting)    # JS: greeting.includes("hello") — Python 更简洁


# ----- 3. 列表 (List) = JS 的 Array -----
fruits = ["apple", "banana", "cherry"]
fruits.append("orange")       # JS: fruits.push("orange")
print(fruits[0])              # 和 JS 一样用下标
print(fruits[-1])             # Python 特有：-1 表示最后一个元素！

# 列表切片 — JS 没有的超好用功能
print(fruits[1:3])            # ['banana', 'cherry'] — 取下标 1 到 2
print(fruits[:2])             # ['apple', 'banana'] — 前两个
print(fruits[2:])             # ['cherry', 'orange'] — 从第3个到末尾

# 列表推导式 — 类似 JS 的 .map() 但更简洁
numbers = [1, 2, 3, 4, 5]
# JS:  const doubled = numbers.map(n => n * 2)
doubled = [n * 2 for n in numbers]
ffu = [n * 3 for n in numbers]
print(doubled)  # [2, 4, 6, 8, 10]
print(ffu)      # [3, 6, 9, 12, 15]

# 带条件的列表推导式 — 类似 .filter().map()
# JS:  numbers.filter(n => n > 2).map(n => n * 2)
result = [n * 2 for n in numbers if n > 2]
print(result)  # [6, 8, 10]


# ----- 4. 字典 (Dict) = JS 的 Object -----
person = {
    "name": "Bob",
    "age": 30,
    "skills": ["Python", "JavaScript"]
}
print(person["name"])          # JS: person.name 或 person["name"]
person["email"] = "bob@ex.com" # 添加新键值对，和 JS 一样

# 安全获取（不会报错）
print(person.get("phone", "未填写"))  # JS: person.phone ?? "未填写"

# 遍历字典
for key, value in person.items():
    print(f"  {key}: {value}")


# ----- 5. 函数 -----
# JS:  function greet(name, greeting = "Hello") { return `${greeting}, ${name}!` }
# JS:  const greet = (name, greeting = "Hello") => `${greeting}, ${name}!`
""""参数:
    name: 用户的名字
    greeting: 问候语"""
def greet(name, greeting="Hello"):
    """这是文档字符串(docstring)，类似 JSDoc"""
    return f"{greeting}, {name}!"

print(greet("Alice"))
print(greet("Bob", "Hi"))

# 多返回值 — JS 需要返回数组或对象，Python 直接用元组
def get_user_info():
    return "Alice", 25, "developer"

name, age, role = get_user_info()  # 解构赋值，类似 JS 的 const [a, b, c] = ...
print(f"{name} is {age}, role: {role}")


# ----- 6. 条件和循环 -----
# Python 用缩进代替 {} 花括号！这是最大的区别
score = 85

# JS: if (score >= 90) { ... } else if (score >= 60) { ... }
if score >= 90:
    print("优秀")
elif score >= 60:
    print("及格")
else:
    print("不及格")

# for 循环
# JS: for (let i = 0; i < 5; i++)
for i in range(5):
    print(i, end=" ")  # 0 1 2 3 4
print()  # 换行

# for...of 等价写法
# JS: for (const fruit of fruits)
for fruit in fruits:
    print(fruit)


# ===========================================
# 练习：试着修改下面的代码，完成小任务
# ===========================================

# TODO 1: 创建一个包含你喜欢的 5 个编程语言的列表
my_languages = ["Python", "JavaScript", "Java", "C++", "Go"]  # 在这里填入

# TODO 2: 用列表推导式筛选出名字长度大于 4 的语言
long_names = [ lan for lan in my_languages if len(lan) > 4]  # 修改这行

# TODO 3: 创建一个函数，接收一个列表，返回列表中最长的字符串
def find_longest(items):
    """返回列表中最长的字符串"""
    if not items:
        return None  # 处理空列表
    longest = items[0]
    for item in items:
        if len(item) > len(longest):
            longest = item
    return longest

# 取消下面的注释来测试你的代码：
# print("我喜欢的语言:", my_languages)
# print("名字较长的语言:", long_names)
# print("最长的语言名:", find_longest(my_languages))
