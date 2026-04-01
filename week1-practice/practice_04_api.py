# ===========================================
# 练习 4：AI API 调用（对应 Day 3 + Day 4）
# ===========================================
# 不看教程，自己写！
# 你需要自己完成: 加载 .env、创建客户端、调用 API、处理返回
# ===========================================


# TODO 0: 自己写出完整的初始化代码
# - 导入需要的库 (os, dotenv, anthropic)
# - 加载 .env
# - 读取 MINIMAX_API_KEY, MINIMAX_API_BASE, MINIMAX_MODEL_NAME
# - 创建 anthropic 客户端
# 不要复制粘贴！自己写！


# --- 题目 1: 多角色对话 ---

# TODO 1.1: 写一个函数 role_play(role_description, question)
# - 用 system prompt 设定角色
# - 调用 API 获取回答
# - 返回回答文本
# 测试:
# print(role_play("你是一个严格的代码审查员", "帮我看看 for i in range(len(arr)) 这行代码"))
# print(role_play("你是一个鼓励型的编程导师", "我总是记不住 Python 语法怎么办"))


# --- 题目 2: 流式输出封装 ---

# TODO 2.1: 写一个函数 stream_ask(question, system="")
# - 流式调用 API
# - 逐字打印回复
# - 返回完整回复文本
# - 要有异常处理


# --- 题目 3: 带重试的 API 调用 ---

# TODO 3.1: 自己写一个 retry 装饰器（不看 Day 6 的代码）
# - 参数: max_retries, delay
# - 失败时打印错误信息并等待后重试
# - 超过次数后抛出异常


# TODO 3.2: 用你写的 retry 装饰器装饰 stream_ask 函数


# --- 题目 4: Few-shot 格式化器 ---

# TODO 4.1: 写一个函数 format_commit(description)
# - 用 few-shot prompting 把中文描述转成规范的 git commit message
# - 在 messages 中提供 2-3 个示例
# - 返回格式化后的 commit message
# 测试:
# print(format_commit("把用户列表从一次全部加载改成了分页加载"))
# print(format_commit("修复了 iOS 上日期选择器显示英文的问题"))
