# ===========================================
# 练习 2：结构化输出（对应 Day 2）
# ===========================================
# 不看教程，自己写！
# 卡住了再回去看 02_structured_output.py
# ===========================================

import os
import json
from pathlib import Path
from dotenv import load_dotenv
from anthropic import Anthropic

# TODO 0: 初始化（自己写）
load_dotenv(Path(__file__).parent / ".env")

client = Anthropic(
    api_key=os.getenv("MINIMAX_API_KEY"),
    base_url=os.getenv("MINIMAX_API_BASE"),
)
MODEL = os.getenv("MINIMAX_MODEL_NAME")


# --- 题目 1: Prompt 约束法提取 ---

def extract_resume(text):
    """用 Prompt 约束法从简历描述中提取信息"""
    response = client.messages.create(
        model=MODEL,
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": f"""从以下简历描述中提取信息，直接返回 JSON（不要加 markdown 代码块标记，不要加任何解释）：

格式：{{"name": "姓名", "experience_years": 数字, "skills": ["技能1", "技能2"], "education": "学历+学校"}}

文本：{text}"""
        }]
    )

    raw = response.content[0].text.strip()

    # 清理可能的 markdown 代码块
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        raw = raw.rsplit("```", 1)[0].strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        print(f"JSON 解析失败，原始回复: {raw}")
        return None


# 测试
# print("=== 题目 1: Prompt 约束法提取简历 ===\n")
# print(extract_resume("张三，5年前端开发经验，熟练掌握 React、TypeScript、Node.js，本科毕业于浙江大学"))
# print(extract_resume("李四，3年 Python 后端开发，精通 Django 和 FastAPI，硕士毕业于清华大学"))


# --- 题目 2: Tool Use 单工具 ---

extract_restaurant_tool = {
    "name": "extract_restaurant",
    "description": "从餐厅评价中提取结构化信息。",
    "input_schema": {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "餐厅名称"},
            "rating": {"type": "number", "description": "评分（1-5）"},
            "cuisine": {"type": "string", "description": "菜系"},
            "price_per_person": {"type": "number", "description": "人均消费（元）"},
            "recommendation": {
                "type": "array",
                "items": {"type": "string"},
                "description": "推荐菜品列表"
            },
        },
        "required": ["name", "rating", "cuisine", "price_per_person", "recommendation"]
    }
}


def extract_restaurant(text):
    """用 Tool Use 从餐厅评价中提取结构化数据"""
    response = client.messages.create(
        model=MODEL,
        max_tokens=300,
        messages=[{"role": "user", "content": f"提取这段餐厅评价的信息：{text}"}],
        tools=[extract_restaurant_tool],
        tool_choice={"type": "tool", "name": "extract_restaurant"},
    )

    for block in response.content:
        if block.type == "tool_use":
            return block.input
    return None


# 测试
# print(f"\n{'='*50}")
# print("=== 题目 2: Tool Use 提取餐厅信息 ===\n")
# print(extract_restaurant("昨天去了海底捞，环境不错服务很好，川菜火锅，人均150，推荐番茄锅底和虾滑"))
# print(extract_restaurant("外婆家的西湖醋鱼真不错，杭帮菜，人均80，4星推荐，还有东坡肉也好吃"))


# --- 题目 3: 多工具路由 ---

support_tools = [
    {
        "name": "check_order",
        "description": "查询订单状态。当用户询问订单物流、到货时间时调用。",
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "订单号"},
            },
            "required": ["order_id"]
        }
    },
    {
        "name": "report_issue",
        "description": "报告商品问题。当用户反馈商品质量问题、破损等时调用。",
        "input_schema": {
            "type": "object",
            "properties": {
                "issue_type": {"type": "string", "description": "问题类型，如 破损/功能故障/缺件"},
                "description": {"type": "string", "description": "问题详细描述"},
            },
            "required": ["issue_type", "description"]
        }
    },
    {
        "name": "request_refund",
        "description": "申请退款。当用户明确要求退款时调用。",
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "订单号"},
                "reason": {"type": "string", "description": "退款原因"},
            },
            "required": ["order_id", "reason"]
        }
    },
]


def smart_support(user_input):
    """智能客服路由器：AI 根据用户输入自动选择合适的工具"""
    response = client.messages.create(
        model=MODEL,
        max_tokens=300,
        messages=[{"role": "user", "content": user_input}],
        tools=support_tools,
        tool_choice={"type": "any"},
    )
    print(f"AI 回复: {response.content}")
    for block in response.content:
        if block.type == "tool_use":
            return {"tool": block.name, "params": block.input}
    return None


# 测试
print(f"\n{'='*50}")
print("=== 题目 3: 多工具路由 ===\n")
print(smart_support("我的订单 #12345 到哪了"))
print(smart_support("收到的商品有破损，屏幕裂了"))
print(smart_support("订单 #67890 我要退款，发错颜色了"))


# --- 题目 4: 完整 Tool Use 流程 ---

chat_tools = [
    {
        "name": "calculate",
        "description": "进行数学计算。当用户需要计算数学表达式时调用。",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "数学表达式，如 (100+200)*0.8"},
            },
            "required": ["expression"]
        }
    },
    {
        "name": "translate",
        "description": "翻译文本到目标语言。当用户要求翻译时调用。",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "要翻译的文本"},
                "target_lang": {"type": "string", "description": "目标语言，如 日语/英语/法语"},
            },
            "required": ["text", "target_lang"]
        }
    },
]


def execute_tool(tool_name, params):
    """模拟执行工具"""
    if tool_name == "calculate":
        try:
            result = eval(params["expression"])
            return {"expression": params["expression"], "result": result}
        except Exception:
            return {"error": "计算错误"}
    elif tool_name == "translate":
        # 模拟翻译结果
        translations = {
            "日语": "こんにちは世界",
            "英语": "Hello World",
            "法语": "Bonjour le monde",
        }
        translated = translations.get(params["target_lang"], f"[{params['target_lang']}翻译结果]")
        return {"original": params["text"], "translated": translated, "target_lang": params["target_lang"]}
    return {"error": "未知工具"}


def chat_with_tools(user_input):
    """完整 Tool Use 流程：用户提问 -> AI 选工具 -> 执行工具 -> 返回结果 -> AI 生成回复"""
    messages = [{"role": "user", "content": user_input}]

    # 第一轮：AI 选择工具
    response = client.messages.create(
        model=MODEL,
        max_tokens=500,
        messages=messages,
        tools=chat_tools,
    )

    if response.stop_reason == "tool_use":
        tool_block = None
        for block in response.content:
            if block.type == "tool_use":
                tool_block = block
                break

        if tool_block:
            print(f"  AI 选择工具: {tool_block.name}, 参数: {tool_block.input}")

            # 执行工具
            tool_result = execute_tool(tool_block.name, tool_block.input)
            print(f"  工具执行结果: {tool_result}")

            # 第二轮：把工具结果返回给 AI，让它生成最终回复
            messages.append({"role": "assistant", "content": response.content})
            messages.append({
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": tool_block.id,
                    "content": json.dumps(tool_result, ensure_ascii=False),
                }]
            })

            final_response = client.messages.create(
                model=MODEL,
                max_tokens=500,
                messages=messages,
                tools=chat_tools,
            )
            return final_response.content[0].text
    else:
        return response.content[0].text


# 测试
# print(f"\n{'='*50}")
# print("=== 题目 4: 完整 Tool Use 流程 ===\n")
# print(f"回复: {chat_with_tools('帮我算一下 (100 + 200) * 0.8 是多少')}\n")
# print(f"回复: {chat_with_tools('把 Hello World 翻译成日语')}")


# --- 题目 5: Pydantic 验证 ---

# print(f"\n{'='*50}")
# print("=== 题目 5: Pydantic 验证 ===\n")
#
# try:
#     from pydantic import BaseModel, Field, ValidationError
#
#     class MovieReview(BaseModel):
#         title: str
#         rating: float = Field(ge=1, le=10)
#         genre: str
#         summary: str = Field(max_length=100)
#         recommend: bool
#
#     # Tool Use 提取 + Pydantic 验证
#     extract_movie_tool = {
#         "name": "extract_movie_review",
#         "description": "从影评文本中提取电影评价信息。",
#         "input_schema": {
#             "type": "object",
#             "properties": {
#                 "title": {"type": "string", "description": "电影名称"},
#                 "rating": {"type": "number", "description": "评分（1-10）"},
#                 "genre": {"type": "string", "description": "电影类型，如 科幻/喜剧/动作"},
#                 "summary": {"type": "string", "description": "一句话总结，最多100字"},
#                 "recommend": {"type": "boolean", "description": "是否推荐"},
#             },
#             "required": ["title", "rating", "genre", "summary", "recommend"]
#         }
#     }
#
#     def extract_movie_review(text):
#         """用 Tool Use 提取 + Pydantic 验证"""
#         # 1. Tool Use 提取
#         response = client.messages.create(
#             model=MODEL,
#             max_tokens=300,
#             messages=[{"role": "user", "content": f"提取这段影评的信息：{text}"}],
#             tools=[extract_movie_tool],
#             tool_choice={"type": "tool", "name": "extract_movie_review"},
#         )
#
#         raw_data = None
#         for block in response.content:
#             if block.type == "tool_use":
#                 raw_data = block.input
#                 break
#
#         if not raw_data:
#             print("AI 未返回工具调用")
#             return None
#
#         # 2. Pydantic 验证
#         try:
#             review = MovieReview(**raw_data)
#             return review
#         except ValidationError as e:
#             print(f"数据验证失败: {e}")
#             return None
#
#     # 测试
#     review1 = extract_movie_review("看了《星际穿越》，科幻神作，打9分，诺兰的时空叙事太震撼了，强烈推荐")
#     print(f"影评1: {review1.model_dump() if review1 else None}\n")
#
#     review2 = extract_movie_review("《熊出没》还行吧，动画片，给6分，适合小朋友看，大人就算了")
#     print(f"影评2: {review2.model_dump() if review2 else None}")
#
# except ImportError:
#     print("pydantic 未安装，跳过此题")
#     print("安装命令: pip install pydantic")
