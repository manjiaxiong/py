# ===========================================
# Day 2: 结构化输出 — 让 AI 返回你想要的格式
# ===========================================
# JSON Mode、Tool Use、Pydantic 验证
# 从"AI 随便说"到"AI 严格按格式返回"
# ===========================================

import os
import json
from pathlib import Path
from dotenv import load_dotenv
from anthropic import Anthropic

# 初始化
load_dotenv(Path(__file__).parent / ".env")

client = Anthropic(
    api_key=os.getenv("MINIMAX_API_KEY"),
    base_url=os.getenv("MINIMAX_API_BASE"),
)
MODEL = os.getenv("MINIMAX_MODEL_NAME")


# ===========================================
# 1. Prompt 约束法 — 最简单的结构化输出
# ===========================================
# 直接在 Prompt 里要求返回 JSON
# 优点：简单快速
# 缺点：AI 偶尔会夹带多余文字

print("=== 1. Prompt 约束法 ===\n")


def extract_with_prompt(text):
    """
    用 Prompt 约束让 AI 返回 JSON

    关键技巧：
    1. 明确说"直接返回 JSON"
    2. 给出 JSON 的样例格式
    3. 说"不要加 markdown 代码块"
    """
    response = client.messages.create(
        model=MODEL,
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": f"""从以下文本中提取商品信息，直接返回 JSON（不要加 markdown 代码块标记，不要加任何解释）：

格式：{{"name": "商品名", "price": 数字, "color": "颜色", "storage": "存储容量"}}

文本：{text}"""
        }]
    )

    raw = response.content[0].text.strip()

    # ⚠️ AI 可能返回带 ```json ... ``` 的格式，需要清理
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        raw = raw.rsplit("```", 1)[0].strip()

    # 解析 JSON
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        print(f"⚠️ JSON 解析失败，原始回复: {raw}")
        return None


# 测试
# result = extract_with_prompt("iPhone 15 Pro 256GB 深蓝色 售价 8999 元")
# print(f"提取结果: {result}")
# print(f"类型: {type(result)}")  # <class 'dict'> — 已经是 Python 字典了
# if result:
#     print(f"价格: {result.get('price')} 元")


# ===========================================
# 2. Tool Use — 最稳定的结构化输出（⭐ 推荐）
# ===========================================
# 定义"工具"，AI 被迫按工具的参数格式返回
# JS 类比：给 AI 一个 TypeScript interface，它必须按这个返回

print(f"\n{'='*50}")
print("=== 2. Tool Use（推荐） ===\n")

# --- 定义工具 ---
# 每个工具就是一个 JSON Schema，描述了参数的名称、类型、是否必填
# JS 类比：
# interface ExtractProduct {
#   name: string       // required
#   price: number      // required
#   color?: string     // optional
#   storage?: string   // optional
# }

extract_tool = {
    "name": "extract_product",
    "description": "从文本中提取商品信息。当用户提供商品描述时调用此工具。",
    "input_schema": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "商品名称（品牌+型号）"
            },
            "price": {
                "type": "number",
                "description": "价格（纯数字，单位：元）"
            },
            "color": {
                "type": "string",
                "description": "颜色"
            },
            "storage": {
                "type": "string",
                "description": "存储容量（如 256GB）"
            },
        },
        # required: 必填字段（和 TypeScript 的必填属性一样）
        "required": ["name", "price"]
    }
}


def extract_with_tool(text):
    """
    用 Tool Use 提取结构化数据

    流程：
    1. 把工具定义传给 API（tools 参数）
    2. AI 看到用户输入后，决定调用哪个工具
    3. AI 按工具的 input_schema 格式返回参数
    4. 我们从 response 中提取工具调用的参数

    tool_choice={"type": "tool", "name": "extract_product"}
    → 强制 AI 调用这个工具（不给它"不调用"的选项）
    → JS 类比：就像 fetch 请求的 method: "POST"，不是可选的
    """
    response = client.messages.create(
        model=MODEL,
        max_tokens=300,
        messages=[{"role": "user", "content": f"提取这段文本的商品信息：{text}"}],
        tools=[extract_tool],
        # tool_choice 控制 AI 是否必须调用工具：
        # {"type": "auto"}  → AI 自己决定是否调用（默认）
        # {"type": "any"}   → 必须调用某个工具
        # {"type": "tool", "name": "xxx"} → 必须调用指定的工具
        tool_choice={"type": "tool", "name": "extract_product"},
    )

    # 从 response 中找到工具调用的内容
    # response.content 是一个列表，可能包含文本和工具调用
    print(f"完整回复内容: {response.content}")  # 调试用，看看 AI 的原始回复结构
    for block in response.content:
        if block.type == "tool_use":
            # block.input 就是 AI 按 schema 填好的参数（已经是 dict 了！）
            return block.input

    return None


# 测试
# result = extract_with_tool("华为 Mate 60 Pro 512GB 雅丹黑 售价 6999 元")
# print(f"Tool Use 结果: {result}")
# print(f"类型: {type(result)}")  # <class 'dict'>
# if result:
#     print(f"商品: {result.get('name')}, 价格: {result.get('price')}元")

# 对比 Prompt 约束法：
# - Prompt 法: AI 返回文本 → 我们 json.loads() → dict
# - Tool Use:  AI 直接返回 dict（SDK 已经帮你解析好了）
# Tool Use 更稳定，因为 AI 被 schema 约束，不会多输出内容


# ===========================================
# 3. 多工具 — 让 AI 自己选择用哪个
# ===========================================
# 给 AI 多个工具，它根据用户输入自动选择

print(f"\n{'='*50}")
print("=== 3. 多工具选择 ===\n")

# 定义多个工具
tools = [
    {
        "name": "get_weather",
        "description": "查询城市天气。当用户问天气相关问题时调用。",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "城市名"},
                "date": {"type": "string", "description": "日期，如 today/tomorrow"},
            },
            "required": ["city"]
        }
    },
    {
        "name": "calculate",
        "description": "进行数学计算。当用户需要计算时调用。",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "数学表达式"},
            },
            "required": ["expression"]
        }
    },
    {
        "name": "search_product",
        "description": "搜索商品信息。当用户问商品相关问题时调用。",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "搜索关键词"},
                "max_price": {"type": "number", "description": "最高价格"},
            },
            "required": ["query"]
        }
    },
]


def smart_router(user_input):
    """
    智能路由 — AI 自动选择合适的工具

    JS 类比：
    就像 React Router 根据 URL 自动匹配路由
    const routes = [
      { path: '/weather', component: Weather },
      { path: '/calc', component: Calculator },
      { path: '/search', component: Search },
    ]
    只不过这里是 AI 根据自然语言来"匹配路由"
    """
    response = client.messages.create(
        model=MODEL,
        max_tokens=300,
        messages=[{"role": "user", "content": user_input}],
        tools=tools,
        tool_choice={"type": "any"},  # 必须调用一个工具，但 AI 自己选
    )

    for block in response.content:
        if block.type == "tool_use":
            return {
                "tool": block.name,      # AI 选了哪个工具
                "params": block.input,   # 填了什么参数
            }
    return None


# 测试：不同的输入，AI 选不同的工具
test_inputs = [
    "北京今天天气怎么样",
    "帮我算一下 128 * 3 + 99",
    "帮我搜一下 5000 元以内的手机",
]

# for user_input in test_inputs:
#     result = smart_router(user_input)
#     if result:
#         print(f"输入: {user_input}")
#         print(f"  → 工具: {result['tool']}")
#         print(f"  → 参数: {result['params']}\n")


# ===========================================
# 4. Tool Use 完整流程 — 真正执行工具
# ===========================================
# 上面只是让 AI "选择"工具，这里展示完整流程：
# AI 选择工具 → 我们执行 → 把结果返回给 AI → AI 生成最终回复

print(f"\n{'='*50}")
print("=== 4. Tool Use 完整流程 ===\n")


def execute_tool(tool_name, params):
    """
    执行工具（模拟真实调用）

    在真实项目中，这里会调用真正的 API：
    - get_weather → 调用天气 API
    - calculate → eval() 或调用计算引擎
    - search_product → 调用电商 API
    """
    if tool_name == "get_weather":
        # 模拟天气数据
        return {"city": params["city"], "temp": "25°C", "condition": "晴", "humidity": "40%"}
    elif tool_name == "calculate":
        try:
            # ⚠️ eval 有安全风险，生产环境不要用
            result = eval(params["expression"])
            return {"expression": params["expression"], "result": result}
        except Exception:
            return {"error": "计算错误"}
    elif tool_name == "search_product":
        return {"products": [{"name": "Redmi Note 13", "price": 1099}, {"name": "OPPO A3", "price": 1299}]}
    return {"error": "未知工具"}


def chat_with_tools(user_input):
    """
    完整的 Tool Use 对话流程

    步骤：
    1. 用户提问 → 发给 AI
    2. AI 决定调用哪个工具（返回 tool_use）
    3. 我们执行工具，拿到结果
    4. 把结果返回给 AI（role: "tool"）
    5. AI 根据工具结果生成最终回复

    JS 类比：
    类似于 middleware 模式：
    request → AI router → tool handler → response → AI formatter → final response
    """
    messages = [{"role": "user", "content": user_input}]

    # 第一轮：AI 选择工具
    response = client.messages.create(
        model=MODEL,
        max_tokens=500,
        messages=messages,
        tools=tools,
    )
    print(f"AI 原始回复: {response}")  # 调试用，看看 AI 的原始回复结构
    # 检查 AI 是否要调用工具
    # stop_reason == "tool_use" 表示 AI 想调用工具
    if response.stop_reason == "tool_use":
        # 找到工具调用
        tool_block = None
        for block in response.content:
            if block.type == "tool_use":
                tool_block = block
                break

        if tool_block:
            print(f"  AI 选择工具: {tool_block.name}")
            print(f"  工具参数: {tool_block.input}")

            # 执行工具
            tool_result = execute_tool(tool_block.name, tool_block.input)
            print(f"  工具结果: {tool_result}")

            # 第二轮：把工具结果返回给 AI
            # ⚠️ 注意 messages 的结构：
            # 1. 先把 AI 的回复（包含 tool_use）加进去
            # 2. 再加一条 role="user" 的消息，包含 tool_result
            messages.append({"role": "assistant", "content": response.content})
            messages.append({
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": tool_block.id,  # 必须和 tool_use 的 id 对应
                    "content": json.dumps(tool_result, ensure_ascii=False),
                }]
            })

            # AI 根据工具结果生成最终回复
            final_response = client.messages.create(
                model=MODEL,
                max_tokens=500,
                messages=messages,
                tools=tools,
            )
            return final_response.content[0].text
    else:
        # AI 不需要工具，直接回复
        return response.content[0].text


# 测试完整流程
# print("--- 完整 Tool Use 流程 ---")
# answer = chat_with_tools("北京今天天气如何？")
# print(f"  最终回复: {answer}\n")

# answer = chat_with_tools("128 乘以 3 加 99 等于多少？")
# print(f"  最终回复: {answer}")


# ===========================================
# 5. Pydantic 验证 — 确保数据格式正确
# ===========================================
# Tool Use 已经很稳定了，但如果用 Prompt 法，
# 需要额外验证 AI 返回的 JSON 是否符合预期

print(f"\n{'='*50}")
print("=== 5. Pydantic 数据验证 ===\n")

# 先检查是否安装了 pydantic
try:
    from pydantic import BaseModel, Field, ValidationError

    # 定义数据模型（= TypeScript interface + 运行时验证）
    class ProductInfo(BaseModel):
        """
        商品信息模型

        JS 类比 (Zod):
        const ProductSchema = z.object({
          name: z.string(),
          price: z.number().positive(),
          color: z.string().default("未知"),
          storage: z.string().optional(),
        })
        """
        name: str                                  # 必填
        price: float = Field(gt=0)                 # 必填，且必须 > 0
        color: str = "未知"                         # 有默认值 = 可选
        storage: str | None = None                  # 可选，默认 None

    # --- 验证合法数据 ---
    valid_data = {"name": "iPhone 15", "price": 5999, "color": "黑色"}
    product = ProductInfo(**valid_data)
    print(f"✅ 合法数据: {product}")
    print(f"   name={product.name}, price={product.price}")

    # --- 验证非法数据 ---
    try:
        bad_data = {"name": "iPhone 15", "price": -100}  # 价格为负！
        ProductInfo(**bad_data)
    except ValidationError as e:
        print(f"\n❌ 非法数据被拦截: {e.errors()[0]['msg']}")

    # --- 验证缺少必填字段 ---
    try:
        missing_data = {"color": "黑色"}  # 没有 name 和 price！
        ProductInfo(**missing_data)
    except ValidationError as e:
        print(f"❌ 缺少必填字段: {[err['loc'][0] for err in e.errors()]}")

    # --- 实际使用：验证 AI 返回的数据 ---
    def safe_extract(text):
        """带 Pydantic 验证的数据提取"""
        raw = extract_with_prompt(text)
        if raw is None:
            return None
        try:
            return ProductInfo(**raw)
        except ValidationError as e:
            print(f"⚠️ AI 返回数据不合法: {e}")
            return None

    result = safe_extract("MacBook Air M3 8+256 星光色 7999 元")
    if result:
        print(f"\n✅ 验证通过: {result.model_dump()}")

except ImportError:
    print("⚠️ pydantic 未安装，跳过此节")
    print("安装命令: pip install pydantic")


# ===========================================
# 6. 实用封装 — 通用的结构化提取函数
# ===========================================

print(f"\n{'='*50}")
print("=== 6. 通用结构化提取 ===\n")


def structured_extract(text, schema, tool_name="extract_data"):
    """
    通用的结构化数据提取函数

    参数:
        text: 要提取的文本
        schema: JSON Schema 定义（参数格式）
        tool_name: 工具名称

    用法:
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"},
            },
            "required": ["name"]
        }
        result = structured_extract("张三今年25岁", schema)
        # → {"name": "张三", "age": 25}

    JS 类比:
    async function structuredExtract<T>(text: string, schema: JSONSchema): Promise<T> {
      const response = await client.messages.create({ tools: [{ inputSchema: schema }] })
      return response.content.find(b => b.type === 'tool_use')?.input
    }
    """
    tool = {
        "name": tool_name,
        "description": f"从文本中提取结构化信息",
        "input_schema": schema,
    }

    response = client.messages.create(
        model=MODEL,
        max_tokens=500,
        messages=[{"role": "user", "content": f"从以下文本中提取信息：\n{text}"}],
        tools=[tool],
        tool_choice={"type": "tool", "name": tool_name},
    )

    for block in response.content:
        if block.type == "tool_use":
            return block.input
    return None


# 测试：提取人物信息
# person_schema = {
#     "type": "object",
#     "properties": {
#         "name": {"type": "string", "description": "姓名"},
#         "age": {"type": "number", "description": "年龄"},
#         "job": {"type": "string", "description": "职业"},
#         "city": {"type": "string", "description": "所在城市"},
#     },
#     "required": ["name"]
# }

# person = structured_extract("小明今年28岁，是深圳的一名前端工程师", person_schema)
# print(f"人物信息: {json.dumps(person, ensure_ascii=False, indent=2)}")

# 测试：提取事件信息
# event_schema = {
#     "type": "object",
#     "properties": {
#         "event": {"type": "string", "description": "事件名称"},
#         "date": {"type": "string", "description": "日期"},
#         "location": {"type": "string", "description": "地点"},
#         "attendees": {"type": "number", "description": "参加人数"},
#     },
#     "required": ["event"]
# }

# event = structured_extract("下周三在北京国际会议中心举办AI技术大会，预计500人参加", event_schema)
# print(f"\n事件信息: {json.dumps(event, ensure_ascii=False, indent=2)}")


# ===========================================
# 总结
# ===========================================

print(f"\n{'='*50}")
print("=== 总结 ===")
print("""
结构化输出三种方式：

1. Prompt 约束  — 简单但不够稳定，适合快速测试
2. Tool Use     — 最稳定最推荐，AI 严格按 schema 返回
3. Pydantic     — 验证层，确保数据格式正确

Tool Use 完整流程：
  用户提问 → AI 选工具 → 执行工具 → 返回结果 → AI 生成回复

下一课：Day 3 LangChain 基础
""")
