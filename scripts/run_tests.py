# scripts/run_tests.py

"""
InferOps - 模拟测试运行器

这个脚本用于发现并运行项目中的所有单元测试。
它会查找 `tests/` 目录下所有以 `test_` 开头的文件，并执行它们。

在真实的项目中，这通常会由 `pytest` 或 `unittest` 命令行工具直接完成。
这个脚本是对该过程的一个封装，可以加入一些自定义的设置或报告。
"""

import unittest
import os
import sys

def run_all_tests():
    """发现并运行所有测试。"""
    print("="*70)
    print("  InferOps - 开始运行单元测试")
    print("="*70)

    # 设置测试目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    test_dir = os.path.join(project_root, 'tests')

    # 将项目根目录和 gateway 目录添加到 sys.path，以便测试文件可以导入模块
    sys.path.insert(0, project_root)
    sys.path.insert(0, os.path.join(project_root, 'gateway'))

    if not os.path.isdir(test_dir):
        print(f"\n错误: 测试目录 '{test_dir}' 未找到。")
        print("请确保你已经创建了 `tests` 目录并添加了测试文件。")
        print("="*70)
        sys.exit(1)

    # 使用 unittest 的 TestLoader 来发现测试
    # 它会查找所有 `test_*.py` 文件
    loader = unittest.TestLoader()
    suite = loader.discover(test_dir, pattern='test_*.py')

    if suite.countTestCases() == 0:
        print("\n未发现任何测试用例。")
        print("请确保在 `tests` 目录中有以 `test_` 开头的 Python 文件，")
        print("并且其中包含继承自 `unittest.TestCase` 的类。")
        print("="*70)
        return

    # 使用 TextTestRunner 来运行测试套件
    # verbosity=2 会打印更详细的输出
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "-"*70)
    print("测试结果总结:")
    if result.wasSuccessful():
        print("  ✅ 所有测试通过!")
    else:
        print("  ❌ 部分测试失败。")
        print(f"  - 总计运行: {result.testsRun}")
        print(f"  - 失败: {len(result.failures)}")
        print(f"  - 错误: {len(result.errors)}")
    print("="*70)

if __name__ == '__main__':
    run_all_tests()
