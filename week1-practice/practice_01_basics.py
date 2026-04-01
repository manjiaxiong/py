# ===========================================
# 练习 1：Python 基础（对应 Day 1）
# ===========================================
# 不要翻教程！先自己写，卡住了再回去看 01_basics.py
# ===========================================


# --- 题目 1: 学生成绩处理 ---
# 给定一个学生成绩字典列表，完成以下任务

students = [
    {"name": "Alice", "scores": [85, 92, 78]},
    {"name": "Bob", "scores": [90, 88, 95]},
    {"name": "Charlie", "scores": [72, 65, 80]},
    {"name": "Diana", "scores": [98, 95, 100]},
    {"name": "Eve", "scores": [60, 55, 70]},
]

# TODO 1.1: 写一个函数 calc_average(scores) 计算平均分
# 输入: [85, 92, 78]  输出: 85.0
def calc_average(scores):
    if not scores:
        return 0.0
    return sum(scores) / len(scores)

# TODO 1.2: 给每个学生加上 "average" 字段
# 结果: [{"name": "Alice", "scores": [...], "average": 85.0}, ...]
for student in students:
    student["average"] = calc_average(student["scores"])

# TODO 1.3: 用列表推导式筛选出平均分 >= 85 的学生姓名
# 结果: ["Bob", "Diana"]
high_achievers = [student["name"] for student in students if student["average"] >= 85]
print(high_achievers)
# TODO 1.4: 写一个函数 get_grade(average) 返回等级
# >= 90: "A",  >= 80: "B",  >= 70: "C",  >= 60: "D",  < 60: "F"
def get_grade(average):
    if average >= 90:
        return "A"
    elif average >= 80:
        return "B"
    elif average >= 70:
        return "C"
    elif average >= 60:
        return "D"
    else:
        return "F"

# TODO 1.5: 打印成绩单，格式如下:
# ┌──────────┬────────┬───────┐
# │ 姓名     │ 平均分  │ 等级  │
# ├──────────┼────────┼───────┤
# │ Alice    │  85.0  │  B    │
# │ Bob      │  91.0  │  A    │
# │ ...      │  ...   │  ...  │
# └──────────┴────────┴───────┘
# 提示: 用 f-string 的对齐语法 f"{'Alice':<10}" 左对齐占 10 位
print("┌──────────┬────────┬───────┐")
print("│ {:<10} │ {:>6}  │ {:^5} │".format("姓名", "平均分", "等级"))
print("├──────────┼────────┼───────┤")
for student in students:
    name = student["name"]
    average = student["average"]
    grade = get_grade(average)
    print("│ {:<10} │ {:>6.1f}  │ {:^5} │".format(name, average, grade))
print("└──────────┴────────┴───────┘")  

# --- 题目 2: 数据转换 ---

# TODO 2.1: 给定一个嵌套字典，写一个函数 flatten(data, prefix="")
# 把嵌套结构展平成一层
# 输入: {"user": {"name": "Alice", "address": {"city": "Beijing"}}}
# 输出: {"user.name": "Alice", "user.address.city": "Beijing"}
# 提示: 用递归，判断 isinstance(value, dict)
def flatten(data, prefix=""):
    result = {}
    for key, value in data.items():
        new_key = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            result.update(flatten(value, new_key))
        else:
            result[new_key] = value
    return result

# TODO 2.2: 反过来，写一个 unflatten(data) 把展平的字典还原成嵌套结构
# 输入: {"user.name": "Alice", "user.address.city": "Beijing"}
# 输出: {"user": {"name": "Alice", "address": {"city": "Beijing"}}}

def unflatten(data):
    result = {}
    for key, value in data.items():
        parts = key.split(".")
        current = result
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value
    return result