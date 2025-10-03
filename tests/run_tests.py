#!/usr/bin/env python3
"""
测试运行脚本
运行STORY-002 BUILD阶段Day1的所有测试
"""

import sys
import os
import subprocess

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_test(test_file):
    """运行单个测试文件"""
    print(f"\n{'='*60}")
    print(f"运行测试: {test_file}")
    print(f"{'='*60}")

    try:
        # 使用虚拟环境的Python运行测试
        result = subprocess.run([
            os.path.join(os.path.dirname(os.path.dirname(__file__)), '.venv', 'Scripts', 'python.exe'),
            test_file
        ], capture_output=True, text=True, encoding='utf-8')

        print(result.stdout)
        if result.stderr:
            print("错误输出:")
            print(result.stderr)

        return result.returncode == 0

    except Exception as e:
        print(f"运行测试失败: {e}")
        return False

def main():
    """主函数"""
    print("STORY-002 BUILD阶段Day1 测试套件")
    print("运行所有测试...")

    # 测试文件列表
    test_files = [
        'test_base_components_fixed.py',  # 修复版测试
        # 'test_base_components.py',        # 原始测试（仅供参考）
    ]

    passed = 0
    total = len(test_files)

    for test_file in test_files:
        if run_test(test_file):
            passed += 1
            print(f"✅ {test_file} 通过")
        else:
            print(f"❌ {test_file} 失败")

    print(f"\n{'='*60}")
    print(f"测试结果: {passed}/{total} 通过")
    print(f"{'='*60}")

    if passed == total:
        print("🎉 所有测试通过！")
        return True
    else:
        print("💥 有测试失败")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)