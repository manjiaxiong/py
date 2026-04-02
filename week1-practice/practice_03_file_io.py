# ===========================================
# 练习 3：文件读写（对应 Day 3 + Day 6）
# ===========================================
# 不看教程，自己写！
# ===========================================

import json
from pathlib import Path
from datetime import datetime


# --- 题目 1: 学习日志系统 ---

# TODO 1.1: 写一个函数 add_log(log_file, content)
# - 如果文件不存在，创建一个新的 JSON 文件，结构: {"logs": []}
# - 如果文件已存在，读取现有内容
# - 追加一条日志: {"timestamp": "2026-04-01 10:30:00", "content": "学了装饰器"}
# - 写回文件
# 提示: 用 json.load() 读, json.dump() 写, datetime.now().strftime() 格式化时间
def add_log(log_file, content):
    log_path = Path(log_file)
    if log_path.exists():
        with open(log_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"logs": []}
    new_log = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "content": content
    }
    data["logs"].append(new_log)
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
add_log("learning.json", "学习了 Python 变量和数据类型")
add_log("learning.json", "完成了类和继承的练习")
add_log("learning.json", "学会了用装饰器给函数计时")
# TODO 1.2: 写一个函数 show_logs(log_file)
# - 读取日志文件，按时间顺序打印所有日志
# - 格式: [2026-04-01 10:30:00] 学了装饰器
def show_logs(log_file):
    log_path = Path(log_file)
    if not log_path.exists():
        print("日志文件不存在")
        return
    with open(log_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    logs = data.get("logs", [])
    logs.sort(key=lambda x: x['timestamp'])
    for log in logs:
        print(f"[{log['timestamp']}] {log['content']}")

# TODO 1.3: 写一个函数 search_logs(log_file, keyword)
# - 在日志中搜索包含关键词的条目
# - 返回匹配的日志列表

def search_logs(log_file, keyword):
    log_path = Path(log_file)
    if not log_path.exists():
        print("日志文件不存在")
        return []
    with open(log_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    logs = data.get("logs", [])
    # matched = filter(lambda log: keyword in log['content'], logs)
    matched = [log for log in logs if keyword in log['content']]
    return list(matched)
# 测试:
# add_log("learning.json", "学习了 Python 变量和数据类型")
# add_log("learning.json", "完成了类和继承的练习")
# add_log("learning.json", "学会了用装饰器给函数计时")
# show_logs("learning.json")
# print(search_logs("learning.json", "装饰器"))


# --- 题目 2: 代码文件统计 ---

# TODO 2.1: 写一个函数 scan_py_files(directory)
# - 扫描指定目录下所有 .py 文件（包括子目录）
# - 返回文件列表，每个文件包含: {"path": "...", "lines": 行数, "size_kb": 大小}
# 提示: 用 Path.rglob("*.py") 递归搜索

def scan_py_files(directory):
    py_files = []
    for file_path in Path(directory).rglob("*.py"):
        if file_path.is_file():
            lines = sum(1 for _ in open(file_path, "r", encoding="utf-8"))
            size_kb = file_path.stat().st_size / 1024
            py_files.append({
                "path": str(file_path),
                "lines": lines,
                "size_kb": round(size_kb, 2)
            })
    return py_files

# ⚠️ 相对路径的坑：
# "../xxx" 是相对于【终端的工作目录(cwd)】，不是相对于【脚本所在目录】
# 如果在 VSCode 根目录运行，cwd 是 d:/code/py/，"../" 就指向了 d:/code/，路径就错了
#
# 解决方案：用 __file__ 获取脚本自身路径，再拼接相对路径
# Path(__file__).parent = 当前脚本所在目录（等价于 JS 的 __dirname）
# 这样无论从哪个目录运行脚本，路径都是正确的
#
# JS 对比:
# const targetDir = path.resolve(__dirname, '../week1-python-ai-basics')
target_dir = Path(__file__).parent.parent / "week1-python-ai-basics"
# print(scan_py_files(target_dir))
scan_py_files(target_dir)
# print(sum(500 for _ in [1, 2, 3]))
# TODO 2.2: 写一个函数 generate_report(directory)
# - 调用 scan_py_files 获取文件列表
# - 打印统计报告:
#   总文件数: 10
#   总代码行数: 500
#   最大文件: xxx.py (120 行)
#   最小文件: xxx.py (5 行)
# - 将报告同时保存到 report.json


# 测试:
# generate_report("../week1-python-ai-basics")
