# ===========================================
# Day 2: LangGraph — 图结构 Agent 编排
# ===========================================
# LangGraph = 用图（Graph）来编排 Agent 工作流
#
# 类比：
# LangChain Agent = 黑盒函数，你不知道它内部走了几步
# LangGraph      = 可视化流程图，每个节点干什么一目了然
#
# 前端类比：
# LangChain Agent = 一个大组件，内部逻辑不透明
# LangGraph       = XState 状态机 / Redux 有限状态图
# ===========================================

# 安装：
# pip install langgraph langchain-core

import sys
import json
from pathlib import Path
from dotenv import load_dotenv
from typing import TypedDict, Annotated

sys.path.append(str(Path(__file__).resolve().parent.parent))

load_dotenv(Path(__file__).parent / ".env")

from utils import get_client, ask

client, MODEL = get_client(Path(__file__).parent / ".env")


# ===========================================
# 1. 为什么需要 LangGraph
# ===========================================
# LangChain Agent 的问题：
# 1. 流程不可控 — Agent 自己决定一切，难以调试
# 2. 无法暂停 — 不能在中间加人工审核
# 3. 状态管理差 — 难以追踪 Agent 做了什么
#
# LangGraph 解决：
# 1. 图结构 — 节点(Node)做事，边(Edge)控制流程
# 2. 可暂停 — 任意节点前后可以 interrupt
# 3. 状态透明 — State 对象记录所有信息
#
# JS 类比：
# LangChain Agent → 一个 async function，内部逻辑是黑盒
# LangGraph → XState 状态机，每个 state + transition 都明确定义

print("=== Section 1: 为什么需要 LangGraph ===")
print("LangChain Agent: 黑盒，不可控")
print("LangGraph: 图结构，每个节点和边都可见可控")
print()


# ===========================================
# 2. 核心概念：State / Node / Edge
# ===========================================
# State  — 共享数据对象，所有节点都能读写
#           JS 类比：Redux store / React useState
#
# Node   — 执行单元，一个函数（接收 state，返回更新）
#           JS 类比：reducer 函数 (state) => newState
#
# Edge   — 连接节点，控制执行顺序
#           固定边：A → B（无条件跳转）
#           条件边：if 条件 → A else → B
#           JS 类比：route 路由 / switch case

from langgraph.graph import StateGraph, END

# 定义 State（就像 TypeScript interface）
# JS 类比：
# interface WorkflowState {
#   topic: string;
#   research: string;
#   outline: string;
#   draft: string;
#   review: string;
# }


class WritingState(TypedDict):
    """写作助手的状态"""
    topic: str           # 写作主题
    research: str        # 研究结果
    outline: str         # 大纲
    draft: str           # 草稿
    review: str          # 审核意见
    status: str          # 当前状态


# 定义 Node（每个节点是一个函数）
# JS 类比：
# const researchNode = async (state) => {
#   const research = await llm.ask(`研究 ${state.topic}`);
#   return { ...state, research };
# }

def research_node(state: WritingState) -> dict:
    """研究节点 — 查找主题相关信息"""
    topic = state["topic"]
    result = ask(client, MODEL, f"用 2-3 句话简要介绍：{topic}", max_tokens=200)
    print(f"  📚 研究完成: {result[:60]}...")
    return {"research": result, "status": "researched"}


def outline_node(state: WritingState) -> dict:
    """大纲节点 — 根据研究生成大纲"""
    prompt = f"""根据以下研究内容，生成一个 3 点大纲（每点一句话）：

研究内容：{state['research']}

主题：{state['topic']}"""
    result = ask(client, MODEL, prompt, max_tokens=200)
    print(f"  📝 大纲完成: {result[:60]}...")
    return {"outline": result, "status": "outlined"}


def draft_node(state: WritingState) -> dict:
    """草稿节点 — 根据大纲写草稿"""
    prompt = f"""根据大纲写一篇短文（100 字左右）：

大纲：{state['outline']}

要求：简洁、易懂、有条理"""
    result = ask(client, MODEL, prompt, max_tokens=300)
    print(f"  ✍️ 草稿完成: {result[:60]}...")
    return {"draft": result, "status": "drafted"}


def review_node(state: WritingState) -> dict:
    """审核节点 — 评价草稿质量"""
    prompt = f"""评价以下文章，给出一句话评价和一个分数（1-10分）：

{state['draft']}

格式：分数: N/10, 评价: xxx"""
    result = ask(client, MODEL, prompt, max_tokens=100)
    print(f"  🔍 审核完成: {result[:60]}...")
    return {"review": result, "status": "reviewed"}


print("=== Section 2: 核心概念 ===")
print("State  = 共享数据 (TypedDict)")
print("Node   = 处理函数 (state) → updates")
print("Edge   = 连接关系 (A → B)")
print()


# ===========================================
# 3. 构建简单工作流图
# ===========================================
# 写作助手流程：
# research → outline → draft → review → END
#
# 就像一条流水线：
# 研究 → 列大纲 → 写草稿 → 审核 → 完成

# 创建图
workflow = StateGraph(WritingState)

# 添加节点（注册处理函数）
workflow.add_node("research", research_node)
workflow.add_node("outline", outline_node)
workflow.add_node("draft", draft_node)
workflow.add_node("review", review_node)

# 设置入口
workflow.set_entry_point("research")

# 添加边（定义流程）
workflow.add_edge("research", "outline")
workflow.add_edge("outline", "draft")
workflow.add_edge("draft", "review")
workflow.add_edge("review", END)

# 编译（生成可执行的 app）
# JS 类比：const machine = createMachine(config)
app = workflow.compile()

# 运行
print("=== Section 3: 线性工作流 ===")
print("流程：research → outline → draft → review → END\n")

result = app.invoke({"topic": "Python 异步编程", "research": "", "outline": "", "draft": "", "review": "", "status": "start"})

print(f"\n最终状态: {result['status']}")
print(f"审核意见: {result['review']}")


# ===========================================
# 4. 条件边 — 根据结果决定走向
# ===========================================
# 条件边 = 根据当前 state 决定下一个节点
#
# JS 类比：
# switch (state.status) {
#   case 'approved': return 'publish';
#   case 'rejected': return 'revise';
# }
#
# 场景：审核通过 → 结束，审核不通过 → 回到草稿修改

# def should_continue(state: WritingState) -> str:
#     """
#     条件判断：审核是否通过
#
#     JS 类比：
#     const shouldContinue = (state) => {
#         return state.review.includes('7') ? 'end' : 'revise';
#     }
#     """
#     review = state.get("review", "")
#     # 简单判断：如果评分 >= 7 就通过
#     for score in range(7, 11):
#         if f"{score}/10" in review or f"{score}分" in review:
#             return "end"
#     return "revise"
#
#
# # 带条件边的工作流
# workflow2 = StateGraph(WritingState)
# workflow2.add_node("research", research_node)
# workflow2.add_node("outline", outline_node)
# workflow2.add_node("draft", draft_node)
# workflow2.add_node("review", review_node)
#
# workflow2.set_entry_point("research")
# workflow2.add_edge("research", "outline")
# workflow2.add_edge("outline", "draft")
# workflow2.add_edge("draft", "review")
#
# # 条件边：审核后决定是结束还是回去修改
# workflow2.add_conditional_edges(
#     "review",
#     should_continue,
#     {"end": END, "revise": "draft"},
# )
#
# app2 = workflow2.compile()
#
# print("\n=== Section 4: 条件边 ===")
# print("审核通过 → END，不通过 → 回到 draft\n")
#
# result2 = app2.invoke({
#     "topic": "Docker 容器化部署",
#     "research": "", "outline": "", "draft": "", "review": "", "status": "start",
# })
# print(f"\n最终审核: {result2['review']}")


# ===========================================
# 5. 人工介入节点（Human-in-the-loop）
# ===========================================
# 在关键步骤暂停，等人工审核后继续
#
# JS 类比：
# const result = await workflow.runUntil('review');
# // 暂停，等用户确认
# const feedback = await getUserInput();
# await workflow.resume(feedback);
#
# LangGraph 实现：
# 1. compile(checkpointer=MemorySaver()) — 开启状态保存
# 2. interrupt_before=["review"] — 在 review 前暂停
# 3. 用户确认后用 Command(resume=feedback) 继续

# from langgraph.checkpoint.memory import MemorySaver
#
# # 带人工介入的工作流
# workflow3 = StateGraph(WritingState)
# workflow3.add_node("research", research_node)
# workflow3.add_node("outline", outline_node)
# workflow3.add_node("draft", draft_node)
# workflow3.add_node("review", review_node)
#
# workflow3.set_entry_point("research")
# workflow3.add_edge("research", "outline")
# workflow3.add_edge("outline", "draft")
# workflow3.add_edge("draft", "review")
# workflow3.add_edge("review", END)
#
# # 编译：加 checkpointer + interrupt
# checkpointer = MemorySaver()
# app3 = workflow3.compile(
#     checkpointer=checkpointer,
#     interrupt_before=["review"],  # 在审核前暂停
# )
#
# config = {"configurable": {"thread_id": "demo-1"}}
#
# print("\n=== Section 5: 人工介入 ===")
# print("在 review 节点前暂停，等待人工确认\n")
#
# # 第一次运行 — 会在 review 前暂停
# result3 = app3.invoke(
#     {"topic": "AI Agent 开发", "research": "", "outline": "", "draft": "", "review": "", "status": "start"},
#     config,
# )
# print(f"\n⏸️ 暂停在 review 前")
# print(f"当前草稿: {result3['draft'][:100]}...")
#
# # 模拟人工确认（实际项目中等用户输入）
# print("\n👤 人工确认：继续审核")
#
# # 恢复执行
# from langgraph.types import Command
# result3_final = app3.invoke(Command(resume="approved"), config)
# print(f"审核结果: {result3_final['review']}")
