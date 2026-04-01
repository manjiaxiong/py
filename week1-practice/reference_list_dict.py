# ===========================================
# Python 列表(List) 和 字典(Dict) 常用方法
# ===========================================
# 对应 JS 的 Array 和 Object
# 每个方法都有 JS 类比，直接运行看效果
# ===========================================


# ===========================================
# 一、列表 List = JS 的 Array
# ===========================================

print("=== 列表基础操作 ===\n")

fruits = ["apple", "banana", "cherry"]

# --- 增 ---

# append = JS push（末尾加一个）
fruits.append("durian")
print(f"append: {fruits}")  # ['apple', 'banana', 'cherry', 'durian']

# insert = JS splice(i, 0, item)（指定位置插入）
fruits.insert(1, "avocado")
print(f"insert(1, ...): {fruits}")  # ['apple', 'avocado', 'banana', 'cherry', 'durian']

# extend = JS push(...items) 或 concat（合并另一个列表）
fruits.extend(["elderberry", "fig"])
print(f"extend: {fruits}")

# + 拼接（不修改原列表，返回新列表）= JS concat
new_list = fruits + ["grape"]
print(f"+ 拼接: {new_list}")

# --- 删 ---

# pop = JS pop()（删末尾）/ splice(i, 1)（删指定位置）
last = fruits.pop()       # 删末尾，返回被删的元素
print(f"pop(): {last}, 剩余: {fruits}")

second = fruits.pop(1)    # 删索引 1
print(f"pop(1): {second}, 剩余: {fruits}")

# remove = 按值删第一个匹配项（JS 没有直接对应，要 indexOf + splice）
fruits.remove("banana")
print(f"remove('banana'): {fruits}")

# clear = 清空（JS: arr.length = 0）
temp = [1, 2, 3]
temp.clear()
print(f"clear: {temp}")  # []

# --- 查 ---

print(f"\n=== 列表查找 ===\n")

nums = [10, 20, 30, 20, 40]

# index = JS indexOf（找第一个匹配的索引）
print(f"index(20): {nums.index(20)}")  # 1
try:
    print(f"index(99): {nums.index(99)}")
except ValueError as e:
    print(f"index(99): {e}")  # ValueError: 99 is not in list
# count = 计数（JS 没有，要用 filter().length）
print(f"count(20): {nums.count(20)}")  # 2

# in = JS includes（判断是否存在）
print(f"30 in nums: {30 in nums}")  # True
print(f"99 in nums: {99 in nums}")  # False

# len = JS .length
print(f"len: {len(nums)}")  # 5

# --- 排序 ---

print(f"\n=== 列表排序 ===\n")

# sort = 原地排序（修改原列表）= JS sort()
nums = [3, 1, 4, 1, 5, 9]
nums.sort()
print(f"sort(): {nums}")  # [1, 1, 3, 4, 5, 9]

# 倒序
nums.sort(reverse=True)
print(f"sort(reverse=True): {nums}")  # [9, 5, 4, 3, 1, 1]

# sorted = 返回新列表，不改原列表（JS 没有，要 [...arr].sort()）
original = [3, 1, 4]
new_sorted = sorted(original)
print(f"sorted(): {new_sorted}, 原列表不变: {original}")

# ⭐ key 参数 — 自定义排序规则
# 这就是你问的 logs.sort(key=lambda x: x['timestamp'])

students = [
    {"name": "小明", "score": 85, "age": 20},
    {"name": "小红", "score": 92, "age": 22},
    {"name": "小刚", "score": 78, "age": 19},
]

# 按 score + age 综合排序
students.sort(key=lambda x: x['score'] + x['age'])
print(f"按 score+age 升序: {[s['name'] for s in students]}")  # ['小刚', '小明', '小红']

# 按 score 降序
students.sort(key=lambda x: x['score'], reverse=True)
print(f"按分数降序: {[s['name'] for s in students]}")  # ['小红', '小明', '小刚']

# 按 name 长度排序
words = ["banana", "pie", "watermelon", "kiwi"]
words.sort(key=lambda x: len(x))
print(f"按长度排序: {words}")  # ['pie', 'kiwi', 'banana', 'watermelon']

# JS 对比:
# students.sort((a, b) => a.score - b.score)       // 数字排序
# words.sort((a, b) => a.length - b.length)         // 按长度排序

# --- reverse ---

# reverse = JS reverse()（原地反转）
items = [1, 2, 3]
items.reverse()
print(f"reverse: {items}")  # [3, 2, 1]

# --- 切片 ---

print(f"\n=== 切片 (JS 的 slice) ===\n")

arr = [0, 1, 2, 3, 4, 5]

print(f"arr[1:4]:  {arr[1:4]}")   # [1, 2, 3]     JS: arr.slice(1, 4)
print(f"arr[:3]:   {arr[:3]}")    # [0, 1, 2]     JS: arr.slice(0, 3)
print(f"arr[2:]:   {arr[2:]}")    # [2, 3, 4, 5]  JS: arr.slice(2)
print(f"arr[-2:]:  {arr[-2:]}")   # [4, 5]        JS: arr.slice(-2)
print(f"arr[::2]:  {arr[::2]}")   # [0, 2, 4]     每隔一个取（JS 没有）
print(f"arr[::-1]: {arr[::-1]}")  # [5, 4, 3, 2, 1, 0]  反转（JS 没有）

# --- 列表推导式 ---

print(f"\n=== 列表推导式 (JS 的 map/filter) ===\n")

nums = [1, 2, 3, 4, 5]

# map: 每个元素 * 2
doubled = [x * 2 for x in nums]         # JS: nums.map(x => x * 2)
print(f"map: {doubled}")

# filter: 取偶数
evens = [x for x in nums if x % 2 == 0]  # JS: nums.filter(x => x % 2 === 0)
print(f"filter: {evens}")

# map + filter: 偶数 * 10
result = [x * 10 for x in nums if x % 2 == 0]  # JS: nums.filter(...).map(...)
print(f"map+filter: {result}")


# ===========================================
# 二、字典 Dict = JS 的 Object / Map
# ===========================================

print(f"\n=== 字典基础操作 ===\n")

user = {"name": "小明", "age": 25, "city": "北京"}

# --- 增/改 ---

# 直接赋值 = JS obj.key = value
user["email"] = "xm@test.com"   # 新增
user["age"] = 26                 # 修改
print(f"增/改: {user}")

# update = JS Object.assign() / 展开运算符
user.update({"age": 27, "phone": "123"})
print(f"update: {user}")

# --- 删 ---

# del = JS delete obj.key
del user["phone"]
print(f"del: {user}")

# pop = 删除并返回值（JS 没有直接对应）
email = user.pop("email")
print(f"pop('email'): {email}, 剩余: {user}")

# pop 带默认值（key 不存在不报错）
result = user.pop("不存在的key", "默认值")
print(f"pop(不存在): {result}")

# --- 查 ---

print(f"\n=== 字典查找 ===\n")

config = {"host": "localhost", "port": 3000, "debug": True}

# [] 取值（key 不存在会报错 KeyError）
print(f"config['host']: {config['host']}")

# get 取值（key 不存在返回 None 或默认值，不报错）
# = JS 的 obj.key ?? defaultValue
print(f"get('host'): {config.get('host')}")
print(f"get('timeout'): {config.get('timeout')}")          # None
print(f"get('timeout', 30): {config.get('timeout', 30)}")  # 30

# in 判断 key 是否存在 = JS 的 'key' in obj
print(f"'port' in config: {'port' in config}")      # True
print(f"'timeout' in config: {'timeout' in config}")  # False

# --- 遍历 ---

print(f"\n=== 字典遍历 ===\n")

data = {"a": 1, "b": 2, "c": 3}

# keys = JS Object.keys()
print(f"keys: {list(data.keys())}")

# values = JS Object.values()
print(f"values: {list(data.values())}")

# items = JS Object.entries()
print(f"items: {list(data.items())}")

# 遍历 key-value = JS for (const [k, v] of Object.entries(obj))
for key, value in data.items():
    print(f"  {key} => {value}")

# --- 字典推导式 ---

print(f"\n=== 字典推导式 ===\n")

# 类比 JS: Object.fromEntries(arr.map(([k, v]) => [k, v * 2]))
prices = {"apple": 5, "banana": 3, "cherry": 8}

# 所有价格翻倍
doubled_prices = {k: v * 2 for k, v in prices.items()}
print(f"翻倍: {doubled_prices}")

# 过滤：只要价格 > 4 的
expensive = {k: v for k, v in prices.items() if v > 4}
print(f"过滤: {expensive}")

# key-value 互换
flipped = {v: k for k, v in prices.items()}
print(f"互换: {flipped}")


# ===========================================
# 三、实用技巧
# ===========================================

print(f"\n=== 实用技巧 ===\n")

# --- enumerate = JS forEach 带 index ---
# JS: arr.forEach((item, index) => ...)
colors = ["red", "green", "blue"]
for i, color in enumerate(colors):
    print(f"  {i}: {color}")

# --- zip = 同时遍历多个列表 ---
# JS 没有直接对应
names = ["小明", "小红", "小刚"]
scores = [85, 92, 78]
for name, score in zip(names, scores):
    print(f"  {name}: {score}分")

# --- any / all ---
# any = JS some()   至少一个满足
# all = JS every()  全部满足
nums = [2, 4, 6, 7, 8]
print(f"any(奇数): {any(x % 2 == 1 for x in nums)}")  # True (7是奇数)
print(f"all(正数): {all(x > 0 for x in nums)}")         # True

# --- min / max / sum ---
scores = [85, 92, 78, 95, 60]
print(f"min: {min(scores)}, max: {max(scores)}, sum: {sum(scores)}")

# 对字典列表用 key
students = [
    {"name": "小明", "score": 85},
    {"name": "小红", "score": 92},
]
best = max(students, key=lambda x: x['score'])
print(f"最高分: {best['name']} ({best['score']})")
