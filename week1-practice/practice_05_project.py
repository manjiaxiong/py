# ===========================================
# 练习 5：综合项目 — 代码学习笔记生成器（⭐⭐⭐⭐）
# ===========================================
#
# 这是第一周的毕业项目，综合运用所有知识点:
# - 文件读写 (Path, open, json)
# - 类和模块拆分 (Config, Scanner, NoteGenerator)
# - API 调用 (anthropic SDK)
# - 异步并发 (asyncio.gather + AsyncAnthropic)
# - 装饰器 (@timer)
# - 异常处理 (try/except)
# - 结构化输出 (让 AI 返回 JSON)
# - 环境变量 (.env)
#
# 【项目结构】
#
# week1-practice/
# ├── practice_05_project.py      ← 主入口（你在这里）
# ├── note_generator/
# │   ├── __init__.py              ← 包的入口，统一导出
# │   ├── config.py                ← 配置管理（环境变量、路径）
# │   ├── scanner.py               ← 文件扫描（递归搜索 .py）
# │   └── generator.py             ← AI 笔记生成（异步并发调用）
# └── output/
#     ├── notes_report.md          ← 生成的 Markdown 报告
#     └── notes_data.json          ← 原始 JSON 数据
#
# 【运行方式】
#
# python week1-practice/practice_05_project.py                         # 默认扫描教程目录
# python week1-practice/practice_05_project.py ../week1-python-ai-basics  # 指定目录
#
# ===========================================

import sys
import asyncio
import io
from pathlib import Path

# ⚠️ Windows 终端默认用 GBK 编码，打印 emoji 会报错
# 强制 stdout 用 UTF-8（errors="replace" 表示遇到编码不了的字符用 ? 替代，不报错）
# JS 不存在这个问题，因为 Node.js 默认就是 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# 从 note_generator 包导入三个类
# 这里能直接导入是因为 __init__.py 里做了统一导出
# JS 类比: import { Config, Scanner, NoteGenerator } from './note_generator'
from note_generator import Config, Scanner, NoteGenerator


async def run(target_dir):
    """
    主流程 — async 函数，因为里面要 await AI 调用

    JS 类比:
    async function run(targetDir) {
      const config = new Config()
      const scanner = new Scanner(targetDir)
      const files = scanner.scan()
      const generator = new NoteGenerator(config, scanner)
      const notes = await generator.generateAll(files)
      ...
    }
    """
    # 1. 初始化配置
    print("=" * 50)
    print("📚 代码学习笔记生成器")
    print("=" * 50)

    config = Config()
    print(f"\n{config}\n")

    # 2. 扫描文件
    print("-" * 50)
    scanner = Scanner(target_dir)
    files = scanner.scan()
    scanner.get_summary(files)

    if not files:
        print("⚠️ 没有找到 .py 文件，退出")
        return

    # 3. AI 生成笔记（异步并行）
    print(f"\n{'-' * 50}")
    print(f"🤖 开始 AI 分析（共 {len(files)} 个文件，并行调用）...\n")

    generator = NoteGenerator(config, scanner)
    notes = await generator.generate_all(files)  # 并行调用 AI

    # 4. 生成报告
    print(f"\n{'-' * 50}")
    print("📝 生成报告...\n")

    report = generator.generate_report(notes)
    md_path = generator.save_report(report, notes)

    # 5. 完成
    print(f"\n{'=' * 50}")
    print(f"✅ 完成！共生成 {len(notes)} 条学习笔记")
    print(f"📄 查看报告: {md_path}")
    print("=" * 50)


def main():
    """
    入口函数 — 处理命令行参数，启动异步主流程

    sys.argv = 命令行参数列表
    sys.argv[0] = 脚本自身路径
    sys.argv[1] = 第一个参数（用户指定的目录）

    JS 类比: process.argv[2]（Node.js 前两个是 node 和脚本路径）

    asyncio.run() = 启动异步事件循环并运行 async 函数
    JS 类比: 顶层 await（Node.js ESM 模块里可以直接 await）
    """
    # 解析命令行参数：用户可以指定扫描目录
    if len(sys.argv) > 1:
        # 用户指定了目录
        target_dir = Path(sys.argv[1])
        # 如果是相对路径，基于脚本所在目录解析（避免 cwd 的坑）
        if not target_dir.is_absolute():
            target_dir = Path(__file__).parent / target_dir
    else:
        # 默认扫描教程目录 week1-python-ai-basics
        target_dir = Path(__file__).parent.parent / "week1-python-ai-basics"

    print(f"目标目录: {target_dir}")

    # asyncio.run() 启动异步事件循环
    # 整个 Python 程序只需要调用一次 asyncio.run()
    # 它会创建事件循环 → 运行 async 函数 → 结束后关闭循环
    try:
        asyncio.run(run(target_dir))
    except KeyboardInterrupt:
        print("\n\n⏹️ 用户中断，退出")
    except Exception as e:
        print(f"\n❌ 程序出错: {e}")
        # import traceback
        # traceback.print_exc()  # 取消注释可以看完整错误栈


# __name__ == "__main__" 的含义：
# 只有直接运行这个文件时才执行 main()
# 如果被 import 导入，则不执行
# JS 没有直接对应，但类似于:
# if (require.main === module) { main() }  // CommonJS
if __name__ == "__main__":
    main()
