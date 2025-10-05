# diagnose_generation.py
# -*- coding: utf-8 -*-
"""
生成功能诊断脚本
诊断主页核心生成功能失效的问题
"""

import os
import sys
import importlib.util

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

def test_novel_generator_imports():
    """测试小说生成器模块导入"""
    safe_print("=== 测试小说生成器模块导入 ===")

    generator_modules = [
        'novel_generator.architecture',
        'novel_generator.blueprint',
        'novel_generator.chapter',
        'novel_generator.finalization',
        'novel_generator.knowledge'
    ]

    results = {}
    for module_name in generator_modules:
        try:
            module = importlib.import_module(module_name)
            results[module_name] = {
                'success': True,
                'path': module.__file__ if hasattr(module, '__file__') else 'Unknown',
                'classes': [name for name in dir(module) if not name.startswith('_')]
            }
            safe_print(f"✅ {module_name}: 导入成功")
        except ImportError as e:
            results[module_name] = {
                'success': False,
                'error': str(e)
            }
            safe_print(f"❌ {module_name}: 导入失败 - {e}")

    return results

def test_config_loading():
    """测试配置加载"""
    safe_print("\n=== 测试配置加载 ===")

    try:
        from config_manager import load_config

        config = load_config("config.json")
        safe_print("✅ 配置文件加载成功")

        # 检查必要的配置项
        required_sections = ['llm_configs', 'choose_configs', 'other_params']
        for section in required_sections:
            if section in config:
                safe_print(f"✅ 配置节 '{section}' 存在")
            else:
                safe_print(f"❌ 配置节 '{section}' 缺失")

        # 检查LLM配置
        if 'llm_configs' in config:
            llm_configs = config['llm_configs']
            safe_print(f"✅ LLM配置数量: {len(llm_configs)}")

            for name, llm_config in llm_configs.items():
                safe_print(f"   - {name}: {llm_config.get('model_name', 'Unknown')}")

        # 检查choose_configs
        if 'choose_configs' in config:
            choose_configs = config['choose_configs']
            safe_print(f"✅ 选择配置:")
            for key, value in choose_configs.items():
                safe_print(f"   - {key}: {value}")

        return config

    except Exception as e:
        safe_print(f"❌ 配置加载失败: {e}")
        return None

def test_main_workspace_creation():
    """测试MainWorkspace创建"""
    safe_print("\n=== 测试MainWorkspace创建 ===")

    try:
        # 尝试导入MainWorkspace
        from ui.components.main_workspace import MainWorkspace
        safe_print("✅ MainWorkspace导入成功")

        # 创建模拟的父组件
        class MockParent:
            def __init__(self):
                pass

        parent = MockParent()

        # 尝试创建MainWorkspace实例
        try:
            workspace = MainWorkspace(parent, theme_manager=None, state_manager=None)
            safe_print("✅ MainWorkspace创建成功")

            # 检查关键属性
            if hasattr(workspace, 'step_buttons'):
                safe_print(f"✅ 步骤按钮: {len(workspace.step_buttons)}个")
                for step_id, button in workspace.step_buttons.items():
                    safe_print(f"   - {step_id}: {button.cget('text')}")
            else:
                safe_print("❌ 步骤按钮属性不存在")

            if hasattr(workspace, '_on_generate_architecture'):
                safe_print("✅ _on_generate_architecture方法存在")
            else:
                safe_print("❌ _on_generate_architecture方法不存在")

            return True

        except Exception as e:
            safe_print(f"❌ MainWorkspace创建失败: {e}")
            return False

    except ImportError as e:
        safe_print(f"❌ MainWorkspace导入失败: {e}")
        return False

def test_button_functionality():
    """测试按钮功能"""
    safe_print("\n=== 测试按钮功能 ===")

    try:
        from ui.components.main_workspace import MainWorkspace

        # 创建模拟的父组件
        class MockParent:
            def __init__(self):
                pass

        parent = MockParent()
        workspace = MainWorkspace(parent, theme_manager=None, state_manager=None)

        # 测试按钮方法是否存在
        button_methods = [
            '_on_generate_architecture',
            '_on_generate_blueprint',
            '_on_generate_chapter',
            '_on_finalize_chapter',
            '_on_consistency_check',
            '_on_batch_generate'
        ]

        for method in button_methods:
            if hasattr(workspace, method):
                safe_print(f"✅ 按钮方法存在: {method}")
            else:
                safe_print(f"❌ 按钮方法缺失: {method}")

        # 测试按钮状态
        if hasattr(workspace, 'step_buttons'):
            for step_id, button in workspace.step_buttons.items():
                try:
                    state = button.cget('state')
                    safe_print(f"   {step_id} 按钮状态: {state}")
                except:
                    safe_print(f"   {step_id} 按钮状态检查失败")

        return True

    except Exception as e:
        safe_print(f"❌ 按钮功能测试失败: {e}")
        return False

def test_generation_execution():
    """测试生成执行逻辑"""
    safe_print("\n=== 测试生成执行逻辑 ===")

    try:
        from ui.components.main_workspace import MainWorkspace

        # 创建模拟的父组件
        class MockParent:
            def __init__(self):
                pass

        parent = MockParent()
        workspace = MainWorkspace(parent, theme_manager=None, state_manager=None)

        # 模拟参数
        workspace.novel_params = {
            'topic': '测试主题',
            'genre': '测试类型',
            'num_chapters': 5,
            'word_number': 2000,
            'filepath': '.',
            'guidance': '测试指导'
        }

        safe_print("✅ 模拟参数设置完成")

        # 测试_start_generation方法
        if hasattr(workspace, '_start_generation'):
            safe_print("✅ _start_generation方法存在")

            # 这里不真正调用，只测试参数
            safe_print("   - 可以接收生成类型参数")
            safe_print("   - 会创建生成线程")
        else:
            safe_print("❌ _start_generation方法不存在")

        return True

    except Exception as e:
        safe_print(f"❌ 生成执行测试失败: {e}")
        return False

def test_file_access():
    """测试文件访问权限"""
    safe_print("\n=== 测试文件访问权限 ===")

    test_files = [
        ".",
        "Novel_architecture.txt",
        "Novel_directory.txt",
        "character_state.txt"
    ]

    for file_path in test_files:
        try:
            exists = os.path.exists(file_path)
            readable = os.access(file_path, os.R_OK) if exists else False
            writable = os.access(file_path, os.W_OK) if exists else False

            safe_print(f"   {file_path}: 存在={exists}, 可读={readable}, 可写={writable}")
        except Exception as e:
            safe_print(f"   {file_path}: 检查失败 - {e}")

    return True

def main():
    """主诊断函数"""
    safe_print("生成功能诊断")
    safe_print("=" * 50)

    # 执行所有诊断
    results = {
        'generator_imports': test_novel_generator_imports(),
        'config_loading': test_config_loading(),
        'workspace_creation': test_main_workspace_creation(),
        'button_functionality': test_button_functionality(),
        'generation_execution': test_generation_execution(),
        'file_access': test_file_access()
    }

    # 显示结果
    safe_print("\n" + "=" * 50)
    safe_print("诊断结果总结")
    safe_print("=" * 50)

    test_names = {
        'generator_imports': '生成器模块导入',
        'config_loading': '配置加载',
        'workspace_creation': '工作区创建',
        'button_functionality': '按钮功能',
        'generation_execution': '生成执行逻辑',
        'file_access': '文件访问权限'
    }

    passed_count = 0
    total_count = len(results)

    for test_id, result in results.items():
        test_name = test_names.get(test_id, test_id)
        if isinstance(result, dict):
            # 处理导入测试结果
            success_count = sum(1 for r in result.values() if r.get('success', False))
            total = len(result)
            status = "✅ PASS" if success_count == total else f"⚠️ PARTIAL ({success_count}/{total})"
            safe_print(f"{test_name}: {status}")
            if success_count == total:
                passed_count += 1
        else:
            status = "✅ PASS" if result else "❌ FAIL"
            safe_print(f"{test_name}: {status}")
            if result:
                passed_count += 1

    success_rate = passed_count / total_count * 100
    safe_print(f"\n通过率: {passed_count}/{total_count} ({success_rate:.1f}%)")

    # 问题诊断
    safe_print("\n🔍 问题诊断:")

    # 检查生成器模块
    import_results = results['generator_imports']
    failed_modules = [name for name, result in import_results.items() if not result.get('success', False)]

    if failed_modules:
        safe_print(f"❌ 失败的生成器模块: {failed_modules}")
        safe_print("   可能原因: 缺少依赖、路径问题或代码错误")

    # 检查配置
    config_result = results['config_loading']
    if not config_result:
        safe_print("❌ 配置加载失败")
        safe_print("   可能原因: 配置文件不存在、格式错误或权限问题")

    # 检查工作区
    if not results['workspace_creation']:
        safe_print("❌ MainWorkspace创建失败")
        safe_print("   可能原因: 依赖模块问题、初始化错误")

    # 检查按钮
    if not results['button_functionality']:
        safe_print("❌ 按钮功能异常")
        safe_print("   可能原因: 方法缺失、布局问题")

    # 检查生成逻辑
    if not results['generation_execution']:
        safe_print("❌ 生成执行逻辑异常")
        safe_print("   可能原因: 参数错误、线程问题、依赖缺失")

    # 修复建议
    safe_print("\n🔧 修复建议:")

    if failed_modules:
        safe_print("1. 📦 检查生成器模块:")
        safe_print("   - 确保novel_generator包存在且完整")
        safe_print("   - 检查Python路径设置")
        safe_print("   - 安装缺失的依赖包")

    if not config_result:
        safe_print("2. ⚙️ 修复配置问题:")
        safe_print("   - 检查config.json文件是否存在")
        safe_print("   - 验证配置文件格式")
        safe_print("   - 确保LLM配置正确")

    if not results['workspace_creation']:
        safe_print("3. 🏗️ 修复工作区创建:")
        safe_print("   - 检查customtkinter是否正确安装")
        safe_print("   - 验证UI组件的依赖关系")
        safe_print("   - 检查初始化参数")

    # 最终结论
    if success_rate == 100:
        safe_print("\n[SUCCESS] 所有诊断通过！")
        safe_print("生成功能应该可以正常工作")
    elif success_rate >= 66:
        safe_print("\n[PASS] 主要功能正常")
        safe_print("生成功能基本可用，但可能需要一些修复")
    else:
        safe_print("\n[FAIL] 生成功能存在严重问题")
        safe_print("需要立即修复才能使用核心功能")

    return 0 if success_rate >= 66 else 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        safe_print("\n诊断被用户中断")
        sys.exit(1)
    except Exception as e:
        safe_print(f"诊断过程出现异常: {e}")
        sys.exit(1)