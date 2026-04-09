# ===========================================
# tools.py — 自定义工具（LangChain @tool）
# ===========================================
# 给 Agent 用的工具：薪资估算、经验评级、简历提取
# 用 @tool 装饰器定义（Day 5 学的）
#
# JS 类比：
# @tool 装饰器 = 把一个普通函数注册为 AI 可调用的 API endpoint
# ===========================================

import json
from langchain_core.tools import tool
from extractor import extract_resume


# ===========================================
# 1. 薪资估算工具
# ===========================================

@tool
def salary_estimate(years: int, skills: str) -> str:
    """根据工作年限和技能估算薪资范围。当需要评估候选人薪资水平时使用。

    Args:
        years: 工作年限
        skills: 技能列表，用逗号分隔，如 "React,TypeScript,Node.js"
    """
    # 基础薪资（按年限）
    base_salary = {
        (0, 1): (5, 10),     # 0-1年: 5k-10k
        (1, 3): (10, 18),    # 1-3年: 10k-18k
        (3, 5): (15, 25),    # 3-5年: 15k-25k
        (5, 8): (20, 35),    # 5-8年: 20k-35k
        (8, 99): (30, 50),   # 8年以上: 30k-50k
    }

    low, high = 8, 15  # 默认值
    for (min_y, max_y), (l, h) in base_salary.items():
        if min_y <= years < max_y:
            low, high = l, h
            break

    # 热门技能加成
    hot_skills = {
        "react": 2, "vue": 1, "typescript": 2, "node.js": 1,
        "python": 2, "go": 3, "rust": 3, "kubernetes": 3,
        "ai": 3, "机器学习": 3, "大模型": 4, "langchain": 3,
        "java": 1, "spring": 1, "mysql": 1, "redis": 2,
    }

    skill_list = [s.strip().lower() for s in skills.split(",")]
    bonus = sum(hot_skills.get(s, 0) for s in skill_list)
    bonus = min(bonus, 10)  # 加成上限 10k

    low += bonus
    high += bonus

    return json.dumps({
        "salary_range": f"{low}k-{high}k",
        "base_range": f"{low - bonus}k-{high - bonus}k",
        "skill_bonus": f"+{bonus}k",
        "hot_skills_found": [s for s in skill_list if s in hot_skills],
    }, ensure_ascii=False)


# ===========================================
# 2. 经验评级工具
# ===========================================

@tool
def experience_level(years: int) -> str:
    """根据工作年限评估经验级别。当需要判断候选人级别时使用。

    Args:
        years: 工作年限
    """
    if years < 1:
        level, desc = "实习/应届", "需要培养，适合初级岗位"
    elif years < 3:
        level, desc = "初级", "能独立完成模块开发，需要指导"
    elif years < 5:
        level, desc = "中级", "能独立负责项目，有一定架构能力"
    elif years < 8:
        level, desc = "高级", "能带小团队，有系统设计能力"
    else:
        level, desc = "专家/架构师", "能把控技术方向，有丰富的大型项目经验"

    return json.dumps({
        "years": years,
        "level": level,
        "description": desc,
    }, ensure_ascii=False)


# ===========================================
# 3. 简历提取工具（包装 extractor.py）
# ===========================================

@tool
def parse_resume(resume_text: str) -> str:
    """从简历文本中提取结构化信息（姓名、年限、技能、学历、期望薪资）。当用户提供简历文本需要分析时使用。

    Args:
        resume_text: 简历文本内容
    """
    result = extract_resume(resume_text)
    return json.dumps(result, ensure_ascii=False)


# ===========================================
# 导出所有工具
# ===========================================
ALL_TOOLS = [parse_resume, salary_estimate, experience_level]


if __name__ == "__main__":
    # 快速测试
    print("=== 测试薪资估算 ===")
    print(salary_estimate.invoke({"years": 5, "skills": "React,TypeScript,Node.js"}))

    print("\n=== 测试经验评级 ===")
    print(experience_level.invoke({"years": 5}))
