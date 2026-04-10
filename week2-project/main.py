# ===========================================
# main.py — AI 简历分析助手（命令行交互）
# ===========================================
# 第 2 周综合项目入口
# 整合了 Day 1-5 所有技能：
# - Day 1: API 调用基础
# - Day 2: Tool Use + Pydantic 结构化输出
# - Day 3: 日志记录 + 评估
# - Day 4: LangChain（ChatOpenAI, LCEL）
# - Day 5: Agent + @tool
#
# 用法: python week2-project/main.py
# ===========================================

from agent import ask_agent, run_agent_verbose

# 示例简历，方便快速测试
SAMPLE_RESUMES = [
    """张三，5年前端开发经验，熟练掌握 React、TypeScript、Node.js、Vue。
本科毕业于浙江大学计算机系。期望薪资 25k-35k。""",

    """李四，8年后端开发经验，精通 Java、Spring、MySQL、Redis、Kubernetes。
硕士毕业于北京大学。期望薪资 40k-50k。""",

    """王五，应届毕业生，了解 Python、HTML、CSS。
本科毕业于某普通院校，无工作经验。""",
]


def print_banner():
    print("=" * 50)
    print("  AI 简历分析助手")
    print("  输入简历文本，AI 自动分析")
    print("=" * 50)
    print()
    print("命令：")
    print("  sample 1/2/3  — 使用示例简历")
    print("  verbose       — 切换详细模式（显示 Agent 每一步）")
    print("  quit          — 退出")
    print()


def main():
    print_banner()

    verbose = False

    while True:
        try:
            user_input = input("请输入简历文本（或命令）:\n> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n再见！")
            break

        if not user_input:
            continue

        # 退出
        if user_input.lower() in ("quit", "exit", "q"):
            print("再见！")
            break

        # 切换详细模式
        if user_input.lower() == "verbose":
            verbose = not verbose
            print(f"详细模式: {'开启' if verbose else '关闭'}\n")
            continue

        # 使用示例简历
        if user_input.lower().startswith("sample"):
            parts = user_input.split()
            idx = int(parts[1]) - 1 if len(parts) > 1 else 0
            if 0 <= idx < len(SAMPLE_RESUMES):
                user_input = SAMPLE_RESUMES[idx]
                print(f"\n--- 使用示例简历 {idx + 1} ---")
                print(user_input)
                print("---\n")
            else:
                print(f"示例编号 1-{len(SAMPLE_RESUMES)}，请重试\n")
                continue

        # 调用 Agent
        prompt = f"帮我分析这份简历：\n{user_input}"
        print(prompt, "promptpromptpromptpromptpromptprompt")
        print()
        if verbose:
            run_agent_verbose(prompt)
        else:
            try:
                result = ask_agent(prompt)
                print(f"\n{result}\n")
            except Exception as e:
                print(f"\n出错了: {e}\n")

        print("-" * 50)
        print()


if __name__ == "__main__":
    main()
