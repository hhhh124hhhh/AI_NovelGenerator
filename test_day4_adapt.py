#!/usr/bin/env python3
"""
测试STORY-002 Day 4开发的ADAPT阶段功能
验证配置和生成标签页的迁移和集成
"""

import os
import sys
import logging

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('test_day4_adapt.log', encoding='utf-8')
        ]
    )

def test_config_tab():
    """测试配置标签页组件"""
    print("[TEST] 测试ConfigTab组件...")

    try:
        import customtkinter as ctk
        from ui.components.config_tab import ConfigTab
        from theme_system.theme_manager import ThemeManager
        from ui.state.state_manager import StateManager

        # 创建测试窗口
        root = ctk.CTk()
        root.geometry("900x700")

        # 创建管理器
        theme_manager = ThemeManager()
        state_manager = StateManager()

        # 创建ConfigTab
        config_tab = ConfigTab(root, theme_manager, state_manager)
        config_tab.pack(fill="both", expand=True, padx=10, pady=10)

        # 测试基本功能
        print("[OK] ConfigTab 创建成功")

        # 测试配置信息获取
        info = config_tab.get_config_info()
        if info:
            print(f"[OK] 配置信息获取成功: {info}")

        # 测试主题样式应用
        theme_data = {
            'colors': {
                'surface': '#2A2A2A',
                'primary': '#404040',
                'background': '#1E1E1E'
            }
        }
        config_tab.apply_theme_style(theme_data)
        print("[OK] 主题样式应用成功")

        # 测试配置变化回调
        callback_called = False
        def test_callback(config):
            nonlocal callback_called
            callback_called = True
            print("配置变化回调被触发")

        config_tab.set_config_changed_callback(test_callback)
        print("[OK] 配置变化回调设置成功")

        # 短暂显示后销毁
        root.after(1000, root.destroy)
        root.mainloop()
        return True

    except Exception as e:
        print(f"[FAIL] ConfigTab测试失败: {e}")
        return False

def test_generate_tab():
    """测试生成标签页组件"""
    print("[TEST] 测试GenerateTab组件...")

    try:
        import customtkinter as ctk
        from ui.components.generate_tab import GenerateTab
        from theme_system.theme_manager import ThemeManager
        from ui.state.state_manager import StateManager

        # 创建测试窗口
        root = ctk.CTk()
        root.geometry("1000x800")

        # 创建管理器
        theme_manager = ThemeManager()
        state_manager = StateManager()

        # 创建GenerateTab
        generate_tab = GenerateTab(root, theme_manager, state_manager)
        generate_tab.pack(fill="both", expand=True, padx=10, pady=10)

        # 测试基本功能
        print("[OK] GenerateTab 创建成功")

        # 测试生成信息获取
        info = generate_tab.get_generation_info()
        if info:
            print(f"[OK] 生成信息获取成功: {info}")

        # 测试主题样式应用
        theme_data = {
            'colors': {
                'surface': '#2A2A2A',
                'primary': '#404040',
                'background': '#1E1E1E'
            }
        }
        generate_tab.apply_theme_style(theme_data)
        print("[OK] 主题样式应用成功")

        # 测试生成回调设置
        callback_called = False
        def test_started_callback(gen_type):
            nonlocal callback_called
            print(f"生成开始回调: {gen_type}")

        def test_completed_callback(gen_type, result):
            print(f"生成完成回调: {gen_type}")

        generate_tab.set_generation_started_callback(test_started_callback)
        generate_tab.set_generation_completed_callback(test_completed_callback)
        print("[OK] 生成回调设置成功")

        # 测试生成状态检查
        is_generating = generate_tab.is_generation_in_progress()
        print(f"[OK] 生成状态检查: {is_generating}")

        # 短暂显示后销毁
        root.after(1000, root.destroy)
        root.mainloop()
        return True

    except Exception as e:
        print(f"[FAIL] GenerateTab测试失败: {e}")
        return False

def test_integrated_adapt_system():
    """测试集成的ADAPT系统"""
    print("[TEST] 测试集成的ADAPT系统...")

    try:
        import customtkinter as ctk
        from ui.modern_main_window import ModernMainWindow

        # 初始化CustomTkinter
        ctk.set_appearance_mode("dark")

        # 创建现代化主窗口
        main_window = ModernMainWindow()
        print("[OK] ModernMainWindow 创建成功")

        # 测试配置标签页集成
        if hasattr(main_window, 'config_tab') and main_window.config_tab:
            print("[OK] ConfigTab 组件已集成到主窗口")

            # 测试配置信息
            config_info = main_window.config_tab.get_config_info()
            print(f"[OK] 配置标签页信息: {config_info}")
        else:
            print("[FAIL] ConfigTab 组件未集成")
            return False

        # 测试生成标签页集成
        if hasattr(main_window, 'generate_tab') and main_window.generate_tab:
            print("[OK] GenerateTab 组件已集成到主窗口")

            # 测试生成信息
            gen_info = main_window.generate_tab.get_generation_info()
            print(f"[OK] 生成标签页信息: {gen_info}")
        else:
            print("[FAIL] GenerateTab 组件未集成")
            return False

        # 测试主内容区域
        if hasattr(main_window, 'main_content') and main_window.main_content:
            print("[OK] MainContentArea 组件存在")

            # 测试标签页列表
            all_tabs = main_window.main_content.get_all_tabs()
            print(f"[OK] 可用标签页: {all_tabs}")

            # 测试切换到配置标签页
            main_window.main_content.switch_to_tab("config")
            current_tab = main_window.main_content.get_current_tab()
            print(f"[OK] 切换到配置标签页: {current_tab}")

            # 测试切换到生成标签页
            main_window.main_content.switch_to_tab("generate")
            current_tab = main_window.main_content.get_current_tab()
            print(f"[OK] 切换到生成标签页: {current_tab}")

        else:
            print("[FAIL] MainContentArea 组件不存在")
            return False

        # 短暂显示后销毁
        main_window.after(1500, main_window.destroy)
        main_window.mainloop()
        return True

    except Exception as e:
        print(f"[FAIL] 集成ADAPT系统测试失败: {e}")
        return False

def test_adapt_functionality():
    """测试ADAPT功能"""
    print("[TEST] 测试ADAPT功能...")

    try:
        import customtkinter as ctk
        from ui.modern_main_window import ModernMainWindow

        # 创建现代化主窗口
        main_window = ModernMainWindow()
        print("[OK] ModernMainWindow 创建成功")

        # 测试配置功能
        if hasattr(main_window, 'config_tab'):
            print("[OK] 测试配置功能...")

            # 模拟配置变化
            test_config = {
                'llm': {
                    'provider': 'TestProvider',
                    'model': 'test-model'
                }
            }

            # 触发配置变化回调
            main_window._on_config_changed(test_config)
            print("[OK] 配置变化回调测试成功")

        # 测试生成功能
        if hasattr(main_window, 'generate_tab'):
            print("[OK] 测试生成功能...")

            # 触发生成开始回调
            main_window._on_generation_started("architecture")
            print("[OK] 生成开始回调测试成功")

            # 触发生成完成回调
            main_window._on_generation_completed("blueprint", "测试结果")
            print("[OK] 生成完成回调测试成功")

        # 测试导航和标签页联动
        print("[OK] 测试导航和标签页联动...")
        main_window.sidebar.set_active_navigation("config")
        print("[OK] 导航到配置标签页成功")

        main_window.sidebar.set_active_navigation("generate")
        print("[OK] 导航到生成标签页成功")

        # 短暂显示后销毁
        main_window.after(1000, main_window.destroy)
        main_window.mainloop()
        return True

    except Exception as e:
        print(f"[FAIL] ADAPT功能测试失败: {e}")
        return False

def run_all_tests():
    """运行所有测试"""
    print("开始STORY-002 Day 4 ADAPT阶段功能测试\n")

    setup_logging()

    tests = [
        ("ConfigTab组件测试", test_config_tab),
        ("GenerateTab组件测试", test_generate_tab),
        ("集成ADAPT系统测试", test_integrated_adapt_system),
        ("ADAPT功能测试", test_adapt_functionality)
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"执行: {test_name}")
        print('='*50)

        try:
            if test_func():
                passed += 1
                print(f"[OK] {test_name} 通过")
            else:
                failed += 1
                print(f"[FAIL] {test_name} 失败")
        except Exception as e:
            failed += 1
            print(f"[ERROR] {test_name} 异常: {e}")

    print(f"\n{'='*50}")
    print("测试结果汇总")
    print('='*50)
    print(f"[OK] 通过: {passed}")
    print(f"[FAIL] 失败: {failed}")
    print(f"[INFO] 成功率: {passed/(passed+failed)*100:.1f}%")

    if failed == 0:
        print("\n[SUCCESS] 所有测试通过！STORY-002 Day 4 ADAPT阶段验证成功！")
        print("[INFO] 可以继续Day 4的后续开发工作")
    else:
        print(f"\n[WARNING] 有 {failed} 个测试失败，需要修复后再继续")

    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)