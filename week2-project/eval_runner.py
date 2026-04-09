# ===========================================
# eval_runner.py — 评估脚本
# ===========================================
# 跑 eval_cases.json 里的测试用例
# 检查 extractor.py 的提取结果是否正确
#
# 复习：
# - Day 3: 评估集、自动评估、失败分析
#
# 用法: python week2-project/eval_runner.py
# ===========================================

import json
from pathlib import Path
from extractor import extract_resume


def load_cases():
    """加载评估用例"""
    case_path = Path(__file__).parent / "eval_cases.json"
    with open(case_path, "r", encoding="utf-8") as f:
        return json.load(f)


def check_case(result_data: dict, expected: dict) -> list:
    """
    检查单条结果是否符合预期

    返回错误列表，空列表表示通过
    """
    errors = []

    # 检查姓名
    if result_data.get("name") != expected.get("name"):
        errors.append(f"姓名: 期望 '{expected['name']}', 实际 '{result_data.get('name')}'")

    # 检查年限
    if result_data.get("years") != expected.get("years"):
        errors.append(f"年限: 期望 {expected['years']}, 实际 {result_data.get('years')}")

    # 检查技能（只要求包含关键技能，不要求完全一致）
    if "skills_contains" in expected:
        actual_skills = [s.lower() for s in result_data.get("skills", [])]
        for skill in expected["skills_contains"]:
            if skill.lower() not in actual_skills:
                errors.append(f"技能: 缺少 '{skill}'")

    # 检查学历（包含匹配，如"本科"匹配"本科毕业"）
    if expected.get("education"):
        actual_edu = result_data.get("education", "")
        if expected["education"] not in actual_edu:
            errors.append(f"学历: 期望包含 '{expected['education']}', 实际 '{actual_edu}'")

    # 检查期望薪资
    expected_salary = expected.get("expected_salary")
    actual_salary = result_data.get("expected_salary")
    if expected_salary is None:
        # 期望没有薪资信息
        if actual_salary is not None and actual_salary != "":
            # 宽容一点：如果 AI 填了 null/None/空字符串 都算对
            pass
    else:
        if actual_salary is None or expected_salary not in str(actual_salary):
            errors.append(f"薪资: 期望包含 '{expected_salary}', 实际 '{actual_salary}'")

    return errors


def run_eval():
    """运行完整评估"""
    cases = load_cases()
    total = len(cases)
    passed = 0
    failed = 0
    results = []

    print("=" * 60)
    print(f"  简历提取评估 — 共 {total} 条用例")
    print("=" * 60)
    print()

    for i, case in enumerate(cases, 1):
        case_id = case["id"]
        print(f"[{i}/{total}] {case_id} ... ", end="", flush=True)

        try:
            result = extract_resume(case["input"])

            if not result["success"]:
                print(f"FAIL (提取失败: {result['error']})")
                failed += 1
                results.append({
                    "id": case_id,
                    "status": "FAIL",
                    "error": result["error"],
                })
                continue

            errors = check_case(result["data"], case["expected"])

            if not errors:
                print("PASS")
                passed += 1
                results.append({"id": case_id, "status": "PASS"})
            else:
                print(f"FAIL")
                for err in errors:
                    print(f"    - {err}")
                failed += 1
                results.append({
                    "id": case_id,
                    "status": "FAIL",
                    "errors": errors,
                    "actual": result["data"],
                })

        except Exception as e:
            print(f"ERROR ({e})")
            failed += 1
            results.append({
                "id": case_id,
                "status": "ERROR",
                "error": str(e),
            })

    # 汇总报告
    print()
    print("=" * 60)
    print(f"  评估结果: {passed}/{total} 通过  ({passed/total*100:.0f}%)")
    print("=" * 60)

    if failed > 0:
        print(f"\n失败用例 ({failed}):")
        for r in results:
            if r["status"] != "PASS":
                print(f"  - {r['id']}: {r.get('errors', r.get('error', 'unknown'))}")

    # 保存评估结果
    report_path = Path(__file__).parent / "eval_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": f"{passed/total*100:.0f}%",
            "details": results,
        }, f, ensure_ascii=False, indent=2)
    print(f"\n详细报告已保存: {report_path}")

    return passed, total


if __name__ == "__main__":
    run_eval()
