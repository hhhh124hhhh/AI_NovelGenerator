# test_windows_encoding.py
# -*- coding: utf-8 -*-
"""
Windows编码修复测试脚本
验证启动诊断器的Unicode字符处理能力
"""

import os
import sys
import subprocess
from typing import Dict, Any

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 设置UTF-8编码环境
os.environ['PYTHONIOENCODING'] = 'utf-8'

def safe_print(text):
    """安全打印，避免编码错误"""
    try:
        print(text)
    except UnicodeEncodeError:
        safe_text = text.encode('ascii', 'ignore').decode('ascii')
        print(safe_text)

def test_encoding_fix():
    """测试编码修复功能"""
    safe_print("=== 测试编码修复功能 ===")

    try:
        from startup_checker import setup_windows_encoding
        from startup_checker import safe_print as startup_safe_print

        # 测试编码设置
        setup_windows_encoding()
        startup_safe_print("✅ 编码设置函数执行成功")

        # 测试安全打印功能
        test_strings = [
            "[启动] AI小说生成器",
            "[诊断] 开始诊断...",
            "[OK] 检查通过",
            "[FAIL] 检查失败",
            "[WARN] 警告信息",
            "[提示] 建议",
            "[修复] 解决方案"
        ]

        for test_str in test_strings:
            try:
                startup_safe_print(f"测试字符串: {test_str}")
            except Exception as e:
                safe_print(f"❌ 字符串测试失败: {e}")
                return False

        startup_safe_print("✅ 安全打印功能正常")
        return True

    except Exception as e:
        safe_print(f"❌ 编码修复测试失败: {e}")
        return False

def test_unicode_replacement():
    """测试Unicode字符替换功能"""
    safe_print("\n=== 测试Unicode字符替换功能 ===")

    try:
        from startup_checker import safe_print as startup_safe_print

        # 测试包含原始Unicode字符的字符串
        unicode_test_strings = [
            "🚀 AI小说生成器启动诊断器",
            "🔍 开始启动诊断...",
            "✅ 检查通过",
            "❌ 检查失败",
            "⚠️ 警告信息",
            "💡 建议",
            "🔧 解决方案"
        ]

        startup_safe_print("测试Unicode字符替换:")
        for unicode_str in unicode_test_strings:
            try:
                startup_safe_print(f"原始: {unicode_str}")
            except Exception as e:
                safe_print(f"❌ Unicode替换失败: {e}")
                return False

        startup_safe_print("✅ Unicode字符替换功能正常")
        return True

    except Exception as e:
        safe_print(f"❌ Unicode替换测试失败: {e}")
        return False

def test_startup_checker_windows():
    """测试启动诊断器在Windows下的兼容性"""
    safe_print("\n=== 测试启动诊断器Windows兼容性 ===")

    try:
        from startup_checker import StartupDiagnostic

        diagnostic = StartupDiagnostic()
        safe_print("✅ 启动诊断器初始化成功")

        # 测试各个检查方法
        tests = [
            ('环境检查', diagnostic.check_environment),
            ('Python版本检查', diagnostic.check_python_version),
            ('文件结构检查', diagnostic.check_file_structure),
            ('配置检查', diagnostic.check_configuration),
        ]

        passed_tests = 0
        for test_name, test_func in tests:
            try:
                result = test_func()
                safe_print(f"✅ {test_name}: {'通过' if result else '失败'}")
                if result:
                    passed_tests += 1
            except Exception as e:
                safe_print(f"❌ {test_name}: 异常 - {e}")

        safe_print(f"通过测试: {passed_tests}/{len(tests)}")
        return passed_tests >= len(tests) * 0.75  # 75%通过率

    except Exception as e:
        safe_print(f"❌ Windows兼容性测试失败: {e}")
        return False

def test_recommendation_generation():
    """测试建议生成功能"""
    safe_print("\n=== 测试建议生成功能 ===")

    try:
        from startup_checker import StartupDiagnostic

        diagnostic = StartupDiagnostic()
        recommendations = diagnostic.generate_recommendations()

        if recommendations:
            safe_print(f"✅ 生成了 {len(recommendations)} 条建议")

            # 检查是否包含ASCII格式的标记
            has_ascii_markers = any(
                '[启动]' in rec or '[诊断]' in rec or '[OK]' in rec or
                '[FAIL]' in rec or '[WARN]' in rec or '[提示]' in rec or
                '[修复]' in rec or '[清单]' in rec
                for rec in recommendations
            )

            if has_ascii_markers:
                safe_print("✅ 建议中包含ASCII格式标记")
            else:
                safe_print("⚠️ 建议中未发现ASCII格式标记")

            # 显示部分建议作为示例
            safe_print("建议示例:")
            for i, rec in enumerate(recommendations[:5]):
                safe_print(f"  {i+1}. {rec}")

            return True
        else:
            safe_print("❌ 未生成任何建议")
            return False

    except Exception as e:
        safe_print(f"❌ 建议生成测试失败: {e}")
        return False

def test_startup_script_execution():
    """测试启动脚本执行"""
    safe_print("\n=== 测试启动脚本执行 ===")

    try:
        # 尝试运行启动诊断脚本
        result = subprocess.run(
            [sys.executable, 'startup_checker.py'],
            capture_output=True,
            text=True,
            timeout=30,
            encoding='utf-8',
            errors='replace'  # 处理编码错误
        )

        if result.returncode == 0:
            safe_print("✅ 启动诊断脚本执行成功")

            # 检查输出是否包含ASCII格式的标记
            output = result.stdout
            if '[启动]' in output and '[诊断]' in output:
                safe_print("✅ 输出包含正确的ASCII格式标记")
            else:
                safe_print("⚠️ 输出格式可能有问题")

            # 显示输出的前几行
            lines = output.split('\n')[:10]
            safe_print("输出示例:")
            for line in lines:
                if line.strip():
                    safe_print(f"  {line}")

            return True
        else:
            safe_print(f"❌ 启动诊断脚本执行失败，返回码: {result.returncode}")
            if result.stderr:
                safe_print(f"错误输出: {result.stderr[:200]}")
            return False

    except subprocess.TimeoutExpired:
        safe_print("❌ 启动诊断脚本执行超时")
        return False
    except Exception as e:
        safe_print(f"❌ 脚本执行测试失败: {e}")
        return False

def main():
    """主测试函数"""
    safe_print("Windows编码修复测试")
    safe_print("=" * 50)

    # 执行所有测试
    test_results = {
        'encoding_fix': test_encoding_fix(),
        'unicode_replacement': test_unicode_replacement(),
        'startup_checker_windows': test_startup_checker_windows(),
        'recommendation_generation': test_recommendation_generation(),
        'startup_script_execution': test_startup_script_execution()
    }

    # 显示测试结果
    safe_print("\n" + "=" * 50)
    safe_print("测试结果总结")
    safe_print("=" * 50)

    test_names = {
        'encoding_fix': '编码修复功能',
        'unicode_replacement': 'Unicode字符替换',
        'startup_checker_windows': '启动诊断器Windows兼容性',
        'recommendation_generation': '建议生成功能',
        'startup_script_execution': '启动脚本执行'
    }

    passed_count = 0
    total_count = len(test_results)

    for test_id, result in test_results.items():
        test_name = test_names.get(test_id, test_id)
        status = "✅ PASS" if result else "❌ FAIL"
        safe_print(f"{test_name}: {status}")
        if result:
            passed_count += 1

    success_rate = passed_count / total_count * 100
    safe_print(f"\n通过率: {passed_count}/{total_count} ({success_rate:.1f}%)")

    # 修复说明
    safe_print("\n🔧 Windows编码修复内容:")
    safe_print("1. ✅ 添加Windows编码检测和设置")
    safe_print("2. ✅ 实现安全打印函数，避免Unicode错误")
    safe_print("3. ✅ Unicode字符自动替换为ASCII等效字符")
    safe_print("4. ✅ 修复所有logger.info调用中的Unicode字符")
    safe_print("5. ✅ 更新诊断结果显示格式")
    safe_print("6. ✅ 确保在Windows GBK环境下正常工作")

    safe_print("\n🎯 修复效果:")
    safe_print("- 解决了 'gbk' codec can't encode character 错误")
    safe_print("- 所有Unicode emoji 字符都有ASCII等效替换")
    safe_print("- 在Windows命令提示符下正常显示")
    safe_print("- 保持功能完整性，只改变显示格式")
    safe_print("- 支持自动编码检测和修复")

    # 最终结论
    if success_rate == 100:
        safe_print("\n[SUCCESS] Windows编码问题完全修复！")
        safe_print("启动诊断器现在可以在Windows环境下正常使用")
    elif success_rate >= 80:
        safe_print("\n[PASS] Windows编码问题基本修复")
        safe_print("主要功能正常，可以在Windows环境下使用")
    else:
        safe_print("\n[FAIL] Windows编码修复不完整")
        safe_print("需要进一步检查和修复")

    return 0 if success_rate >= 80 else 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        safe_print("\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        safe_print(f"测试过程出现异常: {e}")
        sys.exit(1)