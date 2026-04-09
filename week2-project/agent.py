# ===========================================
# agent.py — LangChain Agent 组装
# ===========================================
# 用 create_react_agent 把所有工具串起来
# Agent 自动决定：
# - 拿到简历 → 调 parse_resume 提取
# - 需要估薪 → 调 salary_estimate
# - 需要评级 → 调 experience_level
# - 简单问题 → 直接回答
#
# 复习：
# - Day 5: create_react_agent, @tool, agent.stream
# - Day 4: ChatOpenAI, LCEL
# ===========================================

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from tools import ALL_TOOLS


# ===========================================
# 1. 初始化模型
# ===========================================

llm = ChatOpenAI(
    model=os.getenv("MINIMAX_MODEL_NAME"),
    api_key=os.getenv("MINIMAX_API_KEY"),
    base_url=os.getenv("MINIMAX_API_BASE"),
    max_tokens=1000,
)


# ===========================================
# 2. 创建 Agent
# ===========================================

SYSTEM_PROMPT = """你是一个 AI 简历分析助手，能帮用户：
1. 解析简历 — 从文本中提取姓名、年限、技能、学历、期望薪资
2. 估算薪资 — 根据年限和技能评估市场薪资范围
3. 评估级别 — 根据年限判断初级/中级/高级/专家

工作流程：
- 用户给你简历文本时，先用 parse_resume 提取信息
- 提取完后，自动用 salary_estimate 估薪，用 experience_level 评级
- 最后给出完整的分析报告

用中文回答，简洁专业。必须使用工具查询，不要自己编造数据。"""

agent = create_react_agent(
    model=llm,
    tools=ALL_TOOLS,
    prompt=SYSTEM_PROMPT,
)


# ===========================================
# 3. 调用函数
# ===========================================

def ask_agent(question: str) -> str:
    """调用 Agent 并返回最终回复"""
    result = agent.invoke({"messages": [HumanMessage(content=question)]})
    return result["messages"][-1].content


def run_agent_verbose(question: str):
    """运行 Agent 并打印每一步过程"""
    print(f"问题: {question}\n")

    for step in agent.stream({"messages": [HumanMessage(content=question)]}):
        for node_name, node_output in step.items():
            if node_name == "agent":
                msg = node_output["messages"][-1]
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    for tc in msg.tool_calls:
                        print(f"  [调用工具] {tc['name']}({tc['args']})")
                else:
                    print(f"  [最终回答] {msg.content[:200]}...")
            elif node_name == "tools":
                msg = node_output["messages"][-1]
                content = msg.content if len(msg.content) <= 100 else msg.content[:100] + "..."
                print(f"  [工具结果] {content}")

    print()


# ===========================================
# 测试
# ===========================================
if __name__ == "__main__":
    # 测试 1：完整简历分析
    run_agent_verbose("""帮我分析这份简历：
    李四，8年后端开发经验，精通 Java、Spring、MySQL、Redis、Kubernetes。
    硕士毕业于北京大学。期望薪资 40k-50k。
    """)

    # 测试 2：只问薪资
    # print(ask_agent("一个 3 年经验，会 React 和 TypeScript 的前端，大概能拿多少？"))

    # 测试 3：只问级别
    # print(ask_agent("工作 5 年算什么级别？"))
