# ===========================================
# 练习 2：类与模块（对应 Day 2）
# ===========================================
# 不看教程，自己写！
# ===========================================


# --- 题目 1: 任务管理系统 ---
# 用面向对象的方式实现一个简单的任务管理

# TODO 1.1: 创建 Task 类
# 属性:
#   - title: str (任务标题)
#   - priority: str ("high" / "medium" / "low")
#   - done: bool (是否完成，默认 False)
# 方法:
#   - complete() → 标记为完成
#   - __str__() → 返回 "[x] 标题 (优先级)" 或 "[ ] 标题 (优先级)"

class Task:
    def __init__(self, title, priority, done=False):
        if priority not in ["high", "medium", "low"]:
            raise ValueError("Invalid priority. Must be 'high', 'medium', or 'low'.")
        self.title = title
        self.priority = priority
        self.done = done
    def complete(self):
        self.done = True
    def __str__(self):
        status = "x" if self.done else " "
        return f"[{status}] {self.title} ({self.priority})"
# TODO 1.2: 创建 TaskManager 类
# 属性:
#   - tasks: list[Task]
# 方法:
#   - add(title, priority="medium") → 添加任务，返回 Task 对象
#   - complete(title) → 按标题标记完成
#   - list_all() → 打印所有任务
#   - list_pending() → 只打印未完成的任务
#   - get_stats() → 返回 {"total": x, "done": x, "pending": x}
class TaskManager:
    def __init__(self):
        self.tasks = []
    def add(self, title, priority="medium"):
        task = Task(title, priority)
        self.tasks.append(task)
        return task
    def complete(self, title):
        for task in self.tasks:
            if task.title == title:
                task.complete()
                return True
        return False
    def list_all(self):
        for task in self.tasks:
            print(task)
    def list_pending(self):
        for task in self.tasks:
            if not task.done:
                print(task)
    def get_stats(self):
        total = len(self.tasks)
        done = sum(1 for task in self.tasks if task.done)
        pending = total - done
        return {"total": total, "done": done, "pending": pending}
# TODO 1.3: 测试你的代码
# manager = TaskManager()
# manager.add("学习 Python 基础", "high")
# manager.add("完成 API 调用练习", "high")
# manager.add("整理学习笔记", "low")
# manager.complete("学习 Python 基础")
# manager.list_all()
# print(manager.get_stats())


# --- 题目 2: 继承 ---

# TODO 2.1: 创建 TimedTask(Task) 子类
# 额外属性:
#   - deadline: str (截止日期，如 "2026-04-05")
# 重写 __str__():
#   - 在父类基础上加上截止日期 "[x] 标题 (优先级) | 截止: 2026-04-05"
class TimedTask(Task):
    def __init__(self, title, priority, deadline, done=False):
        super().__init__(title, priority, done)
        self.deadline = deadline
    def __str__(self):
        base_str = super().__str__()
        return f"{base_str} | 截止: {self.deadline}"

# TODO 2.2: 给 TaskManager 加一个 export_json() 方法
# 把所有任务导出为 JSON 字符串
# 提示: Task 对象不能直接 json.dumps，需要先转成 dict
def export_json(task_manager):
    tasks_data = []
    for task in task_manager.tasks:
        task_dict = {
            "title": task.title,
            "priority": task.priority,
            "done": task.done
        }
        if isinstance(task, TimedTask):
            task_dict["deadline"] = task.deadline
        tasks_data.append(task_dict)
    return json.dumps(tasks_data, ensure_ascii=False, indent=2)
