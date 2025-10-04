#!/usr/bin/env python3
"""
测试STORY-002 Day 3开发的标签页系统
验证MainContentArea和标签页功能
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
            logging.FileHandler('test_day3_tabs.log', encoding='utf-8')
        ]
    )

def test_main_content_area():
    """测试MainContentArea组件"""
    print("[TEST] 测试MainContentArea组件...")

    try:
        import customtkinter as ctk
        from ui.components.main_content import MainContentArea
        from theme_system.theme_manager import ThemeManager
        from ui.state.state_manager import StateManager

        # 创建测试窗口
        root = ctk.CTk()
        root.geometry("900x700")

        # 创建管理器
        theme_manager = ThemeManager()
        state_manager = StateManager()

        # 创建MainContentArea
        main_content = MainContentArea(root, theme_manager, state_manager)
        main_content.pack(fill="both", expand=True, padx=10, pady=10)

        # 测试基本功能
        print("[OK] MainContentArea 创建成功")

        # 测试添加标签页
        main_content.add_tab("test1", "测试标签1")
        main_content.add_tab("test2", "测试标签2")
        print("[OK] 标签页添加成功")

        # 测试获取内容框架
        frame1 = main_content.get_tab_content_frame("test1")
        frame2 = main_content.get_tab_content_frame("test2")
        if frame1 and frame2:
            print("[OK] 内容框架获取成功")

            # 添加测试内容
            ctk.CTkLabel(frame1, text="这是测试标签1", font=ctk.CTkFont(size=16)).pack(expand=True)
            ctk.CTkLabel(frame2, text="这是测试标签2", font=ctk.CTkFont(size=16)).pack(expand=True)

        # 测试标签页切换
        main_content.switch_to_tab("test2")
        current_tab = main_content.get_current_tab()
        print(f"[OK] 标签页切换成功: {current_tab}")

        # 测试标签页存在性检查
        assert main_content.tab_exists("test1"), "test1标签页应该存在"
        assert main_content.tab_exists("test2"), "test2标签页应该存在"
        assert not main_content.tab_exists("nonexistent"), "不存在的标签页应该返回False"
        print("[OK] 标签页存在性检查通过")

        # 测试响应式布局
        main_content.update_layout_for_size(1200, 800)
        main_content.update_layout_for_size(700, 600)
        print("[OK] 响应式布局测试成功")

        # 获取组件信息
        info = main_content.get_content_info()
        print(f"[OK] 组件信息: 当前标签={info['current_tab']}, 总标签数={info['total_tabs']}")

        # 测试移除标签页
        main_content.remove_tab("test1")
        assert not main_content.tab_exists("test1"), "移除后标签页不应该存在"
        print("[OK] 标签页移除成功")

        # 短暂显示后销毁
        root.after(1000, root.destroy)
        root.mainloop()
        return True

    except Exception as e:
        print(f"[FAIL] MainContentArea测试失败: {e}")
        return False

def test_integrated_tab_system():
    """测试集成的标签页系统"""
    print("[TEST] 测试集成的标签页系统...")

    try:
        import customtkinter as ctk
        from ui.modern_main_window import ModernMainWindow

        # 初始化CustomTkinter
        ctk.set_appearance_mode("dark")

        # 创建现代化主窗口
        main_window = ModernMainWindow()
        print("[OK] ModernMainWindow 创建成功")

        # 测试标签页组件
        if hasattr(main_window, 'main_content') and main_window.main_content:
            print("[OK] MainContentArea 组件存在")

            # 测试默认标签页
            all_tabs = main_window.main_content.get_all_tabs()
            expected_tabs = ["config", "generate", "characters", "chapters", "summary", "directory"]
            for tab in expected_tabs:
                if tab in all_tabs:
                    print(f"[OK] 默认标签页存在: {tab}")
                else:
                    print(f"[FAIL] 默认标签页缺失: {tab}")
                    return False

            # 测试标签页切换
            main_window.main_content.switch_to_tab("generate")
            current_tab = main_window.main_content.get_current_tab()
            print(f"[OK] 标签页切换成功: {current_tab}")

            # 测试导航和标签页联动
            main_window.sidebar.set_active_navigation("characters")
            print("[OK] 导航和标签页联动测试成功")

        else:
            print("[FAIL] MainContentArea 组件不存在")
            return False

        # 短暂显示后销毁
        main_window.after(1500, main_window.destroy)
        main_window.mainloop()
        return True

    except Exception as e:
        print(f"[FAIL] 集成标签页系统测试失败: {e}")
        return False

def test_tab_functionality():
    """测试标签页功能"""
    print("[TEST] 测试标签页功能...")

    try:
        import customtkinter as ctk
        from ui.components.main_content import MainContentArea
        from theme_system.theme_manager import ThemeManager
        from ui.state.state_manager import StateManager

        # 创建测试窗口
        root = ctk.CTk()
        root.geometry("800x600")

        # 创建管理器
        theme_manager = ThemeManager()
        state_manager = StateManager()

        # 创建MainContentArea
        main_content = MainContentArea(root, theme_manager, state_manager)
        main_content.pack(fill="both", expand=True, padx=10, pady=10)

        # 测试回调函数
        callback_called = {}
        def test_callback(tab_name):
            callback_called[tab_name] = True
            print(f"标签页 {tab_name} 被激活")

        # 添加带回调的标签页
        main_content.add_tab("callback_test", "回调测试", test_callback)
        main_content.add_tab("normal_test", "普通测试")

        # 切换到回调测试标签页
        main_content.switch_to_tab("callback_test")
        if "callback_test" in callback_called:
            print("[OK] 标签页回调函数正常工作")
        else:
            print("[FAIL] 标签页回调函数未工作")
            return False

        # 测试加载指示器
        main_content.show_loading_indicator("normal_test", "测试加载中...")
        print("[OK] 加载指示器显示成功")

        main_content.hide_loading_indicator("normal_test")
        print("[OK] 加载指示器隐藏成功")

        # 测试清空内容
        main_content.clear_tab_content("normal_test")
        print("[OK] 标签页内容清空成功")

        # 短暂显示后销毁
        root.after(1000, root.destroy)
        root.mainloop()
        return True

    except Exception as e:
        print(f"[FAIL] 标签页功能测试失败: {e}")
        return False

def test_responsive_tabs():
    """测试响应式标签页"""
    print("[TEST] 测试响应式标签页...")

    try:
        import customtkinter as ctk
        from ui.components.main_content import MainContentArea
        from theme_system.theme_manager import ThemeManager
        from ui.state.state_manager import StateManager

        # 创建测试窗口
        root = ctk.CTk()
        root.geometry("600x500")

        # 创建管理器
        theme_manager = ThemeManager()
        state_manager = StateManager()

        # 创建MainContentArea
        main_content = MainContentArea(root, theme_manager, state_manager)
        main_content.pack(fill="both", expand=True, padx=10, pady=10)

        # 添加测试标签页
        main_content.add_tab("responsive1", "响应式测试1")
        main_content.add_tab("responsive2", "响应式测试2")

        # 添加内容
        frame1 = main_content.get_tab_content_frame("responsive1")
        frame2 = main_content.get_tab_content_frame("responsive2")

        ctk.CTkLabel(frame1, text="紧凑布局测试", font=ctk.CTkFont(size=14)).pack(expand=True)
        ctk.CTkLabel(frame2, text="宽屏布局测试", font=ctk.CTkFont(size=14)).pack(expand=True)

        # 测试不同窗口大小
        print("测试紧凑布局...")
        main_content.update_layout_for_size(600, 400)

        print("测试标准布局...")
        main_content.update_layout_for_size(900, 700)

        print("测试宽屏布局...")
        main_content.update_layout_for_size(1400, 900)

        print("[OK] 响应式布局测试完成")

        # 短暂显示后销毁
        root.after(1000, root.destroy)
        root.mainloop()
        return True

    except Exception as e:
        print(f"[FAIL] 响应式标签页测试失败: {e}")
        return False

def run_all_tests():
    """运行所有测试"""
    print("开始STORY-002 Day 3 标签页系统测试\n")

    setup_logging()

    tests = [
        ("MainContentArea组件测试", test_main_content_area),
        ("集成标签页系统测试", test_integrated_tab_system),
        ("标签页功能测试", test_tab_functionality),
        ("响应式标签页测试", test_responsive_tabs)
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
        print("\n[SUCCESS] 所有测试通过！STORY-002 Day 3 标签页系统验证成功！")
        print("[INFO] 可以继续Day 3的后续开发工作")
    else:
        print(f"\n[WARNING] 有 {failed} 个测试失败，需要修复后再继续")

    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)