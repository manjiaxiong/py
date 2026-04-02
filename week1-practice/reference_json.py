# ===========================================
# Python JSON 常用操作
# ===========================================
# 对应 JS 的 JSON.parse / JSON.stringify
# 每个方法都有 JS 类比，直接运行看效果
# ===========================================

import json
from pathlib import Path
from datetime import datetime


# ===========================================
# 一、JSON 字符串 ↔ Python 字典
# ===========================================
# json.dumps() = JSON.stringify()  Python → JSON 字符串
# json.loads() = JSON.parse()      JSON 字符串 → Python

print("=== JSON 基础：dumps / loads ===\n")

# --- dumps: Python dict → JSON 字符串 ---
# = JS: JSON.stringify(obj)

user = {"name": "小明", "age": 25, "skills": ["Python", "JS"]}

# 基本用法
json_str = json.dumps(user)
print(f"dumps 默认: {json_str}")
# {"name": "\u5c0f\u660e", "age": 25, "skills": ["Python", "JS"]}
# ⚠️ 中文被转成了 Unicode 编码！

# ensure_ascii=False: 中文正常显示（常用！）
json_str = json.dumps(user, ensure_ascii=False)
print(f"dumps 中文: {json_str}")
# {"name": "小明", "age": 25, "skills": ["Python", "JS"]}

# indent: 格式化输出（= JSON.stringify(obj, null, 2)）
json_pretty = json.dumps(user, ensure_ascii=False, indent=2)
print(f"dumps 格式化:\n{json_pretty}")
# {
#   "name": "小明",
#   "age": 25,
#   "skills": [
#     "Python",
#     "JS"
#   ]
# }

# sort_keys: 按 key 排序（= JSON.stringify(obj, null, 2) 不支持，JS 没有直接对应）
json_sorted = json.dumps(user, ensure_ascii=False, indent=2, sort_keys=True)
print(f"dumps 排序:\n{json_sorted}")
# {
#   "age": 25,
#   "name": "小明",
#   "skills": [
#     "Python",
#     "JS"
#   ]
# }

# --- loads: JSON 字符串 → Python dict ---
# = JS: JSON.parse(str)

print(f"\n=== loads: JSON 字符串 → Python ===\n")

json_text = '{"name": "小红", "age": 22, "active": true}'
data = json.loads(json_text)
print(f"loads: {data}")          # {'name': '小红', 'age': 22, 'active': True}
print(f"type: {type(data)}")     # <class 'dict'>
print(f"name: {data['name']}")   # 小红

# ⚠️ JSON 和 Python 类型映射：
# JSON        →  Python
# -------------------------
# {}          →  dict
# []          →  list
# "string"   →  str
# 123 / 1.5  →  int / float
# true       →  True
# false      →  False
# null       →  None

# 验证 null → None
json_null = '{"value": null}'
print(f"null → None: {json.loads(json_null)}")  # {'value': None}

# ⚠️ 非法 JSON 会报错
try:
    json.loads("{'name': '错误'}")  # 单引号不是合法 JSON！
except json.JSONDecodeError as e:
    print(f"JSON 解析错误: {e}")
# JS 同理: JSON.parse("{'name': '错误'}") 也会报错


# ===========================================
# 二、JSON 文件读写
# ===========================================
# json.dump()  = 写入文件（JS: fs.writeFileSync + JSON.stringify）
# json.load()  = 从文件读（JS: JSON.parse(fs.readFileSync(...))）

print(f"\n=== JSON 文件读写：dump / load ===\n")

# --- dump: 写 JSON 到文件 ---

config = {
    "host": "localhost",
    "port": 3000,
    "debug": True,
    "database": {
        "name": "mydb",
        "tables": ["users", "posts"]
    }
}

# 写入文件
config_path = Path(__file__).parent / "temp_config.json"
with open(config_path, "w", encoding="utf-8") as f:
    json.dump(config, f, ensure_ascii=False, indent=2)
print(f"已写入: {config_path}")

# JS 对比:
# fs.writeFileSync('config.json', JSON.stringify(config, null, 2))

# --- load: 从文件读 JSON ---

with open(config_path, "r", encoding="utf-8") as f:
    loaded = json.load(f)
print(f"从文件读取: {loaded}")         # {'host': 'localhost', 'port': 3000, ...}
print(f"port: {loaded['port']}")       # 3000
print(f"db name: {loaded['database']['name']}")  # mydb

# JS 对比:
# const loaded = JSON.parse(fs.readFileSync('config.json', 'utf-8'))

# ⚠️ dump vs dumps / load vs loads 的区别：
# dump()  → 写入文件（file）    dumps() → 返回字符串（string）
# load()  → 从文件读（file）    loads() → 从字符串读（string）
# 记忆：带 s 的是 string，不带 s 的是 file

# 清理临时文件
config_path.unlink()


# ===========================================
# 三、嵌套 JSON 操作
# ===========================================

print(f"\n=== 嵌套 JSON 操作 ===\n")

api_response = {
    "code": 200,
    "data": {
        "users": [
            {"id": 1, "name": "小明", "tags": ["admin", "dev"]},
            {"id": 2, "name": "小红", "tags": ["dev"]},
        ],
        "total": 2
    },
    "message": "success"
}

# --- 嵌套取值 ---

# 直接取（key 不存在会报 KeyError）
print(f"第一个用户: {api_response['data']['users'][0]['name']}")  # 小明
# JS: apiResponse.data.users[0].name

# 安全取值：用 get()（key 不存在返回 None，不报错）
print(f"safe get: {api_response.get('data', {}).get('users', [])}")
# JS: apiResponse?.data?.users ?? []  （可选链 + 空值合并）

# --- 嵌套修改 ---

# 直接改
api_response["data"]["users"][0]["name"] = "小明(管理员)"
print(f"修改后: {api_response['data']['users'][0]['name']}")  # 小明(管理员)

# 新增嵌套字段
api_response["data"]["users"][0]["email"] = "xm@test.com"
print(f"新增字段: {api_response['data']['users'][0]}")
# {'id': 1, 'name': '小明(管理员)', 'tags': ['admin', 'dev'], 'email': 'xm@test.com'}

# --- 合并字典 ---

defaults = {"theme": "light", "lang": "zh", "fontSize": 14}
user_settings = {"theme": "dark", "fontSize": 16}

# update(): 原地合并（修改 defaults）
merged = {**defaults, **user_settings}   # 不修改原字典
print(f"合并: {merged}")  # {'theme': 'dark', 'lang': 'zh', 'fontSize': 16}
# JS: const merged = { ...defaults, ...userSettings }

# Python 3.9+ 还可以用 |
# merged = defaults | user_settings


# ===========================================
# 四、处理特殊类型
# ===========================================

print(f"\n=== 处理不可序列化的类型 ===\n")

# ⚠️ datetime 等对象不能直接 json.dumps，会报错
data_with_date = {"name": "小明", "created_at": datetime.now()}

try:
    json.dumps(data_with_date)
except TypeError as e:
    print(f"报错: {e}")  # Object of type datetime is not JSON serializable

# 解决方案: 用 default 参数自定义转换规则
def json_serializer(obj):
    """遇到不认识的类型，在这里处理"""
    if isinstance(obj, datetime):
        return obj.strftime("%Y-%m-%d %H:%M:%S")
    raise TypeError(f"Type {type(obj)} is not JSON serializable")

result = json.dumps(data_with_date, ensure_ascii=False, default=json_serializer)
print(f"自定义序列化: {result}")
# {"name": "小明", "created_at": "2026-04-02 12:00:00"}

# JS 对比:
# JSON.stringify(obj, (key, value) => {
#   if (value instanceof Date) return value.toISOString()
#   return value
# })


# ===========================================
# 五、实用技巧
# ===========================================

print(f"\n=== 实用技巧 ===\n")

# --- 技巧 1: 封装 JSON 读写函数（项目中常用） ---

def read_json(file_path):
    """读取 JSON 文件，文件不存在返回空字典"""
    path = Path(file_path)
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def write_json(file_path, data):
    """写入 JSON 文件"""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 用法:
# config = read_json("config.json")
# config["newKey"] = "value"
# write_json("config.json", config)

# JS 对比:
# const readJson = (path) => JSON.parse(fs.readFileSync(path, 'utf-8'))
# const writeJson = (path, data) => fs.writeFileSync(path, JSON.stringify(data, null, 2))

# --- 技巧 2: 用 json.dumps 调试打印（比 print(dict) 好看） ---

messy_data = {"users": [{"name": "小明", "scores": [85, 92]}, {"name": "小红", "scores": [90, 88]}]}

# 普通 print: 一坨
print(f"普通 print: {messy_data}")

# json.dumps 格式化: 清晰
print(f"json 格式化:\n{json.dumps(messy_data, ensure_ascii=False, indent=2)}")

# JS 对比: console.log(JSON.stringify(obj, null, 2))

# --- 技巧 3: 深拷贝（简单粗暴） ---

import copy

original = {"a": [1, 2, 3], "b": {"c": 4}}

# 方式 1: json 序列化/反序列化（只适用于可序列化的数据）
deep_copy1 = json.loads(json.dumps(original))

# 方式 2: copy.deepcopy（更通用）
deep_copy2 = copy.deepcopy(original)

deep_copy1["a"].append(99)
print(f"原始: {original['a']}")     # [1, 2, 3]  不受影响
print(f"拷贝: {deep_copy1['a']}")   # [1, 2, 3, 99]

# JS 对比:
# const deepCopy = JSON.parse(JSON.stringify(obj))          // 方式 1
# const deepCopy = structuredClone(obj)                     // 方式 2 (现代 JS)
