# ===========================================
# 练习 2：LangGraph（对应 Day 2）
# ===========================================
# 不看教程，自己写！
# 卡住了再回去看 02_langgraph.py / 02_langgraph.md
# ===========================================

import sys
from pathlib import Path
from typing import TypedDict
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).resolve().parent.parent))
load_dotenv(Path(__file__).parent / ".env")

from utils import get_client, ask
from langgraph.graph import StateGraph, END

client, MODEL = get_client(Path(__file__).parent / ".env")


# --- 题目 1: 定义 State 和 Node ---

# TODO 1.1: 定义邮件处理工作流的 State
class EmailState(TypedDict):
    email_text: str       # 原始邮件内容
    category: str         # 分类结果（spam / normal / urgent）
    summary: str          # 邮件摘要
    reply: str            # 回复草稿
    status: str           # 当前状态


# TODO 1.2: 实现分类节点
def classify_node(state: EmailState) -> dict:
    """分类邮件：spam / normal / urgent"""
    prompt = f"""分析这封邮件属于哪个类别，只回答一个词：spam、normal 或 urgent

邮件内容：{state['email_text']}"""
    result = ask(client, MODEL, prompt, max_tokens=20)
    category = "normal"
    for cat in ["spam", "urgent", "normal"]:
        if cat in result.lower():
            category = cat
            break
    print(f"  📧 分类: {category}")
    return {"category": category, "status": "classified"}


print("=== 题目 1: State 和 Node ===")
test_state = {"email_text": "紧急：服务器宕机了，请立刻处理！", "category": "", "summary": "", "reply": "", "status": ""}
result = classify_node(test_state)
print(f"  返回: {result}")


# --- 题目 2: 构建线性工作流 ---

# TODO 2.1: 实现摘要节点
def summarize_node(state: EmailState) -> dict:
    """用一句话总结邮件"""
    result = ask(client, MODEL, f"用一句话总结：{state['email_text']}", max_tokens=100)
    print(f"  📝 摘要: {result[:50]}...")
    return {"summary": result, "status": "summarized"}


# TODO 2.2: 实现回复节点
def reply_node(state: EmailState) -> dict:
    """生成回复草稿"""
    prompt = f"""根据邮件内容和分类，写一个简短的回复（30字以内）。

邮件: {state['email_text']}
分类: {state['category']}
摘要: {state['summary']}"""
    result = ask(client, MODEL, prompt, max_tokens=100)
    print(f"  ✉️ 回复: {result[:50]}...")
    return {"reply": result, "status": "replied"}


# TODO 2.3: 构建线性工作流 classify → summarize → reply → END
linear_graph = StateGraph(EmailState)
linear_graph.add_node("classify", classify_node)
linear_graph.add_node("summarize", summarize_node)
linear_graph.add_node("reply", reply_node)

linear_graph.set_entry_point("classify")
linear_graph.add_edge("classify", "summarize")
linear_graph.add_edge("summarize", "reply")
linear_graph.add_edge("reply", END)

linear_app = linear_graph.compile()

print("\n=== 题目 2: 线性工作流 ===")
print("流程: classify → summarize → reply → END\n")
result = linear_app.invoke({
    "email_text": "你好，请问下周二的会议改到几点了？",
    "category": "", "summary": "", "reply": "", "status": "",
})
print(f"\n  最终状态: {result['status']}")
print(f"  分类: {result['category']}")


# --- 题目 3: 条件边 ---

# TODO 3.1: spam 邮件直接结束，normal/urgent 继续处理
def route_email(state: EmailState) -> str:
    """
    条件路由：
    spam → end（不回复垃圾邮件）
    normal/urgent → summarize
    """
    if state["category"] == "spam":
        print("  🗑️ 垃圾邮件，跳过处理")
        return "end"
    return "process"


# conditional_graph = StateGraph(EmailState)
# conditional_graph.add_node("classify", classify_node)
# conditional_graph.add_node("summarize", summarize_node)
# conditional_graph.add_node("reply", reply_node)
#
# conditional_graph.set_entry_point("classify")
# conditional_graph.add_conditional_edges(
#     "classify",
#     route_email,
#     {"end": END, "process": "summarize"},
# )
# conditional_graph.add_edge("summarize", "reply")
# conditional_graph.add_edge("reply", END)
#
# conditional_app = conditional_graph.compile()
#
# print("\n=== 题目 3: 条件边 ===")
# print("spam → END, normal/urgent → summarize → reply\n")
#
# # 测试垃圾邮件
# result_spam = conditional_app.invoke({
#     "email_text": "恭喜你中了一等奖！点击领取100万！",
#     "category": "", "summary": "", "reply": "", "status": "",
# })
# print(f"  垃圾邮件结果: category={result_spam['category']}, status={result_spam['status']}")
#
# # 测试正常邮件
# result_normal = conditional_app.invoke({
#     "email_text": "下周三上午 10 点有个技术评审会，请准时参加。",
#     "category": "", "summary": "", "reply": "", "status": "",
# })
# print(f"  正常邮件结果: category={result_normal['category']}, reply={result_normal['reply'][:30]}...")


# --- 题目 4: 人工介入 ---

# TODO 4.1: 在 reply 之前加人工介入（interrupt_before）
# from langgraph.checkpoint.memory import MemorySaver
# from langgraph.types import Command
#
# human_graph = StateGraph(EmailState)
# human_graph.add_node("classify", classify_node)
# human_graph.add_node("summarize", summarize_node)
# human_graph.add_node("reply", reply_node)
#
# human_graph.set_entry_point("classify")
# human_graph.add_edge("classify", "summarize")
# human_graph.add_edge("summarize", "reply")
# human_graph.add_edge("reply", END)
#
# checkpointer = MemorySaver()
# human_app = human_graph.compile(
#     checkpointer=checkpointer,
#     interrupt_before=["reply"],  # 回复前暂停
# )
#
# print("\n=== 题目 4: 人工介入 ===")
# config = {"configurable": {"thread_id": "email-1"}}
#
# # 第一次运行 — 在 reply 前暂停
# result_pause = human_app.invoke({
#     "email_text": "项目延期了，需要重新排期。",
#     "category": "", "summary": "", "reply": "", "status": "",
# }, config)
# print(f"  ⏸️ 暂停, 摘要: {result_pause['summary'][:50]}...")
#
# # 恢复
# result_resume = human_app.invoke(Command(resume="继续"), config)
# print(f"  ▶️ 恢复, 回复: {result_resume['reply'][:50]}...")


# --- 题目 5: 综合 — 研究助手工作流 ---

# TODO 5.1: 构建研究助手
# 流程：topic → research → check_quality → (good → summarize → END) / (bad → research again)

class ResearchState(TypedDict):
    topic: str
    research: str
    quality_score: int
    summary: str
    attempts: int
    status: str


def research_node(state: ResearchState) -> dict:
    """研究主题"""
    attempts = state.get("attempts", 0) + 1
    result = ask(client, MODEL, f"用 3-5 句话介绍：{state['topic']}", max_tokens=300)
    print(f"  🔍 研究 (第{attempts}次): {result[:50]}...")
    return {"research": result, "attempts": attempts, "status": "researched"}


def check_quality_node(state: ResearchState) -> dict:
    """评估研究质量"""
    prompt = f"给这段研究内容打分 1-10（只回答数字）：\n{state['research']}"
    score_text = ask(client, MODEL, prompt, max_tokens=10)
    score = 7  # 默认值
    for num in range(1, 11):
        if str(num) in score_text:
            score = num
    print(f"  📊 质量评分: {score}/10")
    return {"quality_score": score, "status": "checked"}


def summarize_research_node(state: ResearchState) -> dict:
    """总结研究结果"""
    result = ask(client, MODEL, f"用一句话总结：{state['research']}", max_tokens=100)
    print(f"  📋 总结: {result[:50]}...")
    return {"summary": result, "status": "done"}


def should_retry(state: ResearchState) -> str:
    """质量不够 且 没超过 3 次 → 重新研究"""
    if state["quality_score"] >= 7 or state.get("attempts", 0) >= 3:
        return "good"
    return "retry"


# research_graph = StateGraph(ResearchState)
# research_graph.add_node("research", research_node)
# research_graph.add_node("check", check_quality_node)
# research_graph.add_node("summarize", summarize_research_node)
#
# research_graph.set_entry_point("research")
# research_graph.add_edge("research", "check")
# research_graph.add_conditional_edges(
#     "check",
#     should_retry,
#     {"good": "summarize", "retry": "research"},
# )
# research_graph.add_edge("summarize", END)
#
# research_app = research_graph.compile()
#
# print("\n=== 题目 5: 研究助手 ===")
# result = research_app.invoke({
#     "topic": "WebAssembly 的应用场景",
#     "research": "", "quality_score": 0, "summary": "", "attempts": 0, "status": "",
# })
# print(f"\n  最终总结: {result['summary']}")
# print(f"  研究次数: {result['attempts']}")
