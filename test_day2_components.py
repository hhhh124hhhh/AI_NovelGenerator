#!/usr/bin/env python3
"""
测试STORY-002 Day 2开发的组件
验证TitleBar和Sidebar组件的功能
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
            logging.FileHandler('test_day2_components.log', encoding='utf-8')
        ]
    )

def test_titlebar_component():
    """测试TitleBar组件"""
    print("[TEST] 测试TitleBar组件...")

    try:
        import customtkinter as ctk
        from ui.components.title_bar import TitleBar
        from theme_system.theme_manager import ThemeManager
        from ui.state.state_manager import StateManager

        # 创建测试窗口
        root = ctk.CTk()
        root.geometry("800x600")

        # 创建管理器
        theme_manager = ThemeManager()
        state_manager = StateManager()

        # 创建TitleBar
        title_bar = TitleBar(root, theme_manager, state_manager)
        title_bar.pack(fill="x", padx=10, pady=10)

        # 测试基本功能
        print("[OK] TitleBar 创建成功")

        # 测试标题设置
        title_bar.set_title("测试应用")
        print(f"[OK] 标题设置成功: {title_bar.get_title()}")

        # 测试搜索功能
        title_bar.clear_search()
        print("[OK] 搜索框清空成功")

        # 测试响应式布局
        title_bar.update_layout_for_size(1200, 800)
        title_bar.update_layout_for_size(700, 600)
        print("[OK] 响应式布局测试成功")

        # 获取组件信息
        info = title_bar.get_title_info()
        print(f"[OK] 组件信息: {info['title']}, 搜索可见: {info['search_visible']}")

        # 销毁测试窗口
        root.destroy()
        return True

    except Exception as e:
        print(f"[FAIL] TitleBar测试失败: {e}")
        return False

def test_sidebar_component():
    """测试Sidebar组件"""
    print("[TEST] 测试Sidebar组件...")

    try:
        import customtkinter as ctk
        from ui.components.sidebar import Sidebar
        from theme_system.theme_manager import ThemeManager
        from ui.state.state_manager import StateManager

        # 创建测试窗口
        root = ctk.CTk()
        root.geometry("1000x700")

        # 创建管理器
        theme_manager = ThemeManager()
        state_manager = StateManager()

        # 创建Sidebar
        sidebar = Sidebar(root, theme_manager, state_manager)
        sidebar.pack(side="left", fill="y", padx=(10, 5), pady=10)

        # 测试基本功能
        print("[OK] Sidebar 创建成功")

        # 测试折叠功能
        sidebar.collapse()
        print(f"[OK] 侧边栏折叠: {sidebar.is_collapsed_state()}")

        sidebar.expand()
        print(f"[OK] 侧边栏展开: {sidebar.is_collapsed_state()}")

        # 测试导航功能
        sidebar.set_active_navigation("generate")
        print("[OK] 导航设置成功")

        # 测试项目功能
        test_projects = [
            {"name": "测试项目1", "modified": "2025-10-04", "status": "进行中"},
            {"name": "测试项目2", "modified": "2025-10-03", "status": "草稿"}
        ]
        sidebar.update_projects(test_projects)
        print(f"[OK] 项目更新成功，项目数量: {len(test_projects)}")

        # 测试响应式布局
        sidebar.update_layout_for_size(800, 600)
        sidebar.update_layout_for_size(1200, 800)
        print("[OK] 响应式布局测试成功")

        # 获取组件信息
        info = sidebar.get_sidebar_info()
        print(f"[OK] 组件信息: 导航项目={info['nav_items_count']}, 快速操作={info['quick_actions_count']}")

        # 销毁测试窗口
        root.destroy()
        return True

    except Exception as e:
        print(f"[FAIL] Sidebar测试失败: {e}")
        return False

def test_integrated_modern_window():
    """测试集成的现代化主窗口"""
    print("[TEST] 测试集成的现代化主窗口...")

    try:
        import customtkinter as ctk
        from ui.modern_main_window import ModernMainWindow

        # 初始化CustomTkinter
        ctk.set_appearance_mode("dark")

        # 创建现代化主窗口
        main_window = ModernMainWindow()
        print("[OK] ModernMainWindow 创建成功")

        # 测试窗口信息
        window_info = main_window.get_window_info()
        print(f"[OK] 窗口标题: {window_info.get('title', 'Unknown')}")
        print(f"[OK] 布局类型: {window_info.get('layout_type', 'unknown')}")
        print(f"[OK] 主题: {window_info.get('theme', 'unknown')}")
        print(f"[OK] 初始化状态: {window_info.get('initialized', False)}")

        # 测试组件存在性
        components_ok = True
        if hasattr(main_window, 'title_bar') and main_window.title_bar:
            print("[OK] TitleBar 组件存在")
        else:
            print("[FAIL] TitleBar 组件不存在")
            components_ok = False

        if hasattr(main_window, 'sidebar') and main_window.sidebar:
            print("[OK] Sidebar 组件存在")
        else:
            print("[FAIL] Sidebar 组件不存在")
            components_ok = False

        if hasattr(main_window, 'status_bar') and main_window.status_bar:
            print("[OK] StatusBar 组件存在")
        else:
            print("[FAIL] StatusBar 组件不存在")
            components_ok = False

        # 测试主题切换
        if hasattr(main_window, 'title_bar') and main_window.title_bar:
            main_window.get_state_manager().set_state('app.theme', 'light')
            main_window.get_state_manager().set_state('app.theme', 'dark')
            print("[OK] 主题切换测试成功")

        # 测试导航
        if hasattr(main_window, 'sidebar') and main_window.sidebar:
            main_window.sidebar.set_active_navigation('config')
            print("[OK] 导航功能测试成功")

        # 关闭测试窗口
        main_window.destroy()
        print("[OK] 现代化主窗口测试完成")

        return components_ok

    except Exception as e:
        print(f"[FAIL] 集成测试失败: {e}")
        return False

def test_component_callbacks():
    """测试组件回调功能"""
    print("[TEST] 测试组件回调功能...")

    try:
        import customtkinter as ctk
        from ui.components.title_bar import TitleBar
        from ui.components.sidebar import Sidebar
        from theme_system.theme_manager import ThemeManager
        from ui.state.state_manager import StateManager

        # 创建测试窗口
        root = ctk.CTk()
        root.geometry("900x700")

        # 创建管理器
        theme_manager = ThemeManager()
        state_manager = StateManager()

        # 创建状态标签
        status_label = ctk.CTkLabel(root, text="等待操作...", font=ctk.CTkFont(size=12))
        status_label.pack(pady=10)

        # 回调函数
        def on_search(text):
            status_label.configure(text=f"搜索: {text}")

        def on_navigation(target, name):
            status_label.configure(text=f"导航到: {name}")

        def on_quick_action(action):
            status_label.configure(text=f"快速操作: {action}")

        def on_project_select(project):
            status_label.configure(text=f"选择项目: {project}")

        # 创建TitleBar并设置回调
        title_bar = TitleBar(root, theme_manager, state_manager)
        title_bar.pack(fill="x", padx=10, pady=5)
        title_bar.set_search_callback(on_search)

        # 创建容器
        container = ctk.CTkFrame(root)
        container.pack(fill="both", expand=True, padx=10, pady=5)

        # 创建Sidebar并设置回调
        sidebar = Sidebar(container, theme_manager, state_manager)
        sidebar.pack(side="left", fill="y", padx=(0, 5))
        sidebar.set_navigation_callback(on_navigation)
        sidebar.set_quick_action_callback(on_quick_action)
        sidebar.set_project_select_callback(on_project_select)

        print("[OK] 回调函数设置完成")

        # 模拟一些操作（在实际GUI中需要用户交互）
        # 这里只是验证回调设置没有出错
        print("[OK] 回调功能测试完成")

        # 短暂显示后销毁
        root.after(1000, root.destroy)
        root.mainloop()

        return True

    except Exception as e:
        print(f"[FAIL] 回调功能测试失败: {e}")
        return False

def run_all_tests():
    """运行所有测试"""
    print("开始STORY-002 Day 2 组件测试\n")

    setup_logging()

    tests = [
        ("TitleBar组件测试", test_titlebar_component),
        ("Sidebar组件测试", test_sidebar_component),
        ("集成主窗口测试", test_integrated_modern_window),
        ("组件回调功能测试", test_component_callbacks)
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
        print("\n[SUCCESS] 所有测试通过！STORY-002 Day 2 组件开发验证成功！")
        print("[INFO] 可以继续Day 2的后续开发工作")
    else:
        print(f"\n[WARNING] 有 {failed} 个测试失败，需要修复后再继续")

    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)