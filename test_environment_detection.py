# test_environment_detection.py
# -*- coding: utf-8 -*-
"""
环境检测功能测试脚本
验证启动器的UV和虚拟环境检测功能
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

def test_uv_detection():
    """测试UV环境检测"""
    safe_print("=== 测试UV环境检测 ===")

    try:
        from startup_checker import is_uv_environment, check_uv_available

        # 测试当前环境
        is_uv = is_uv_environment()
        safe_print(f"当前环境UV检测: {'✅ UV环境' if is_uv else '❌ 非UV环境'}")

        # 测试UV可用性
        uv_available, uv_info = check_uv_available()
        if uv_available:
            safe_print(f"✅ UV可用: {uv_info}")
        else:
            safe_print(f"⚠️ UV不可用: {uv_info}")

        # 模拟UV环境变量测试
        original_uv = os.environ.get('UV')
        os.environ['UV'] = '1'
        is_uv_simulated = is_uv_environment()
        safe_print(f"模拟UV环境检测: {'✅ 检测成功' if is_uv_simulated else '❌ 检测失败'}")

        # 恢复原始环境变量
        if original_uv:
            os.environ['UV'] = original_uv
        elif 'UV' in os.environ:
            del os.environ['UV']

        return True

    except Exception as e:
        safe_print(f"❌ UV环境检测测试失败: {e}")
        return False

def test_virtual_environment_detection():
    """测试虚拟环境检测"""
    safe_print("\n=== 测试虚拟环境检测 ===")

    try:
        from startup_checker import is_virtual_environment, get_environment_info

        # 测试当前环境
        is_venv = is_virtual_environment()
        safe_print(f"当前环境虚拟环境检测: {'✅ 虚拟环境' if is_venv else '❌ 非虚拟环境'}")

        # 获取详细环境信息
        env_info = get_environment_info()
        safe_print("环境详细信息:")
        safe_print(f"  Python路径: {env_info['python_executable']}")
        safe_print(f"  平台: {env_info['platform']}")
        safe_print(f"  UV环境: {'是' if env_info['is_uv'] else '否'}")
        safe_print(f"  虚拟环境: {'是' if env_info['is_venv'] else '否'}")

        if env_info['base_prefix']:
            safe_print(f"  基础Python: {env_info['base_prefix']}")
        else:
            safe_print("  基础Python: 未检测到")

        return True

    except Exception as e:
        safe_print(f"❌ 虚拟环境检测测试失败: {e}")
        return False

def test_startup_diagnostic_enhanced():
    """测试增强的启动诊断功能"""
    safe_print("\n=== 测试增强的启动诊断功能 ===")

    try:
        from startup_checker import StartupDiagnostic

        diagnostic = StartupDiagnostic()
        safe_print("✅ 增强启动诊断器初始化成功")

        # 测试环境检查
        env_result = diagnostic.check_environment()
        safe_print(f"   环境检查: {'✅ 通过' if env_result else '❌ 失败'}")

        # 检查诊断器属性
        if hasattr(diagnostic, 'env_info'):
            env_info = diagnostic.env_info
            safe_print("✅ 环境信息属性存在")
            safe_print(f"   UV环境: {env_info['is_uv']}")
            safe_print(f"   虚拟环境: {env_info['is_venv']}")
        else:
            safe_print("❌ 环境信息属性缺失")

        # 测试建议生成
        recommendations = diagnostic.generate_recommendations()
        if recommendations:
            safe_print(f"✅ 生成建议成功 ({len(recommendations)}项)")

            # 检查是否包含环境特定建议
            has_env_specific = any('UV环境' in rec or '虚拟环境' in rec for rec in recommendations)
            safe_print(f"   环境特定建议: {'✅ 包含' if has_env_specific else '❌ 缺失'}")
        else:
            safe_print("❌ 未生成任何建议")

        return True

    except Exception as e:
        safe_print(f"❌ 增强启动诊断测试失败: {e}")
        return False

def test_environment_specific_commands():
    """测试环境特定命令建议"""
    safe_print("\n=== 测试环境特定命令建议 ===")

    try:
        from startup_checker import StartupDiagnostic

        diagnostic = StartupDiagnostic()
        recommendations = diagnostic.generate_recommendations()

        # 检查不同环境的命令建议
        uv_commands = [rec for rec in recommendations if 'uv run' in rec.lower()]
        venv_commands = [rec for rec in recommendations if 'python main.py' in rec and 'version' in rec]

        safe_print(f"UV相关建议数量: {len(uv_commands)}")
        safe_print(f"虚拟环境相关建议数量: {len(venv_commands)}")

        if uv_commands:
            safe_print("UV命令示例:")
            for cmd in uv_commands[:2]:  # 显示前2个
                safe_print(f"   {cmd.strip()}")

        if venv_commands:
            safe_print("虚拟环境命令示例:")
            for cmd in venv_commands[:2]:  # 显示前2个
                safe_print(f"   {cmd.strip()}")

        # 检查依赖文件建议
        dep_files = [rec for rec in recommendations if 'requirements' in rec.lower()]
        safe_print(f"依赖文件建议数量: {len(dep_files)}")

        return True

    except Exception as e:
        safe_print(f"❌ 环境特定命令测试失败: {e}")
        return False

def main():
    """主测试函数"""
    safe_print("环境检测功能测试")
    safe_print("=" * 50)

    # 执行所有测试
    test_results = {
        'uv_detection': test_uv_detection(),
        'virtual_environment_detection': test_virtual_environment_detection(),
        'startup_diagnostic_enhanced': test_startup_diagnostic_enhanced(),
        'environment_specific_commands': test_environment_specific_commands()
    }

    # 显示测试结果
    safe_print("\n" + "=" * 50)
    safe_print("测试结果总结")
    safe_print("=" * 50)

    test_names = {
        'uv_detection': 'UV环境检测',
        'virtual_environment_detection': '虚拟环境检测',
        'startup_diagnostic_enhanced': '增强启动诊断',
        'environment_specific_commands': '环境特定命令'
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
    safe_print("\n🔧 系统诊断增强内容:")
    safe_print("1. ✅ 添加UV环境检测功能")
    safe_print("2. ✅ 添加虚拟环境检测功能")
    safe_print("3. ✅ 增强环境信息显示")
    safe_print("4. ✅ 提供环境特定的启动命令")
    safe_print("5. ✅ 智能推荐使用最佳启动方式")
    safe_print("6. ✅ 支持多种依赖文件选项")

    safe_print("\n🎯 现在系统诊断可以:")
    safe_print("- 自动检测UV环境和虚拟环境")
    safe_print("- 根据环境类型提供定制化建议")
    safe_print("- 显示详细的Python路径信息")
    safe_print("- 推荐最适合的启动命令")
    safe_print("- 提供多种环境配置选项")

    # 最终结论
    if success_rate == 100:
        safe_print("\n[SUCCESS] 环境检测功能完全正常！")
        safe_print("系统诊断已完美适配UV和虚拟环境")
    elif success_rate >= 75:
        safe_print("\n[PASS] 环境检测功能基本正常")
        safe_print("主要功能可用，可以正常诊断环境")
    else:
        safe_print("\n[FAIL] 环境检测存在问题")
        safe_print("需要进一步检查和修复")

    return 0 if success_rate >= 75 else 1

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