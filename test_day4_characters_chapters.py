#!/usr/bin/env python3
"""
测试STORY-002 Day 4开发的角色和章节管理功能
验证CharactersTab和ChaptersTab组件的迁移和集成
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
            logging.FileHandler('test_day4_characters_chapters.log', encoding='utf-8')
        ]
    )

def test_characters_tab():
    """测试角色管理标签页组件"""
    print("[TEST] 测试CharactersTab组件...")

    try:
        import customtkinter as ctk
        from ui.components.characters_tab import CharactersTab
        from theme_system.theme_manager import ThemeManager
        from ui.state.state_manager import StateManager

        # 创建测试窗口
        root = ctk.CTk()
        root.geometry("1200x800")

        # 创建管理器
        theme_manager = ThemeManager()
        state_manager = StateManager()

        # 创建CharactersTab
        characters_tab = CharactersTab(root, theme_manager, state_manager)
        characters_tab.pack(fill="both", expand=True, padx=10, pady=10)

        # 测试基本功能
        print("[OK] CharactersTab 创建成功")

        # 测试角色信息获取
        info = characters_tab.get_characters_info()
        if info:
            print(f"[OK] 角色信息获取成功: {info}")

        # 测试获取所有角色
        all_characters = characters_tab.get_all_characters()
        print(f"[OK] 获取所有角色成功，共 {len(all_characters)} 个角色")

        # 测试主题样式应用
        theme_data = {
            'colors': {
                'surface': '#2A2A2A',
                'primary': '#404040',
                'background': '#1E1E1E'
            }
        }
        characters_tab.apply_theme_style(theme_data)
        print("[OK] 主题样式应用成功")

        # 测试角色变化回调
        callback_called = False
        def test_callback(character):
            nonlocal callback_called
            callback_called = True
            print(f"角色变化回调被触发: {character.get('name', 'Unknown')}")

        characters_tab.set_character_changed_callback(test_callback)
        print("[OK] 角色变化回调设置成功")

        # 测试当前角色获取
        current_char = characters_tab.get_current_character()
        if current_char:
            print(f"[OK] 当前角色获取成功: {current_char.get('name', 'Unknown')}")

        # 短暂显示后销毁
        root.after(1000, root.destroy)
        root.mainloop()
        return True

    except Exception as e:
        print(f"[FAIL] CharactersTab测试失败: {e}")
        return False

def test_chapters_tab():
    """测试章节管理标签页组件"""
    print("[TEST] 测试ChaptersTab组件...")

    try:
        import customtkinter as ctk
        from ui.components.chapters_tab import ChaptersTab
        from theme_system.theme_manager import ThemeManager
        from ui.state.state_manager import StateManager

        # 创建测试窗口
        root = ctk.CTk()
        root.geometry("1300x800")

        # 创建管理器
        theme_manager = ThemeManager()
        state_manager = StateManager()

        # 创建ChaptersTab
        chapters_tab = ChaptersTab(root, theme_manager, state_manager)
        chapters_tab.pack(fill="both", expand=True, padx=10, pady=10)

        # 测试基本功能
        print("[OK] ChaptersTab 创建成功")

        # 测试章节信息获取
        info = chapters_tab.get_chapters_info()
        if info:
            print(f"[OK] 章节信息获取成功: {info}")

        # 测试获取所有章节
        all_chapters = chapters_tab.get_all_chapters()
        print(f"[OK] 获取所有章节成功，共 {len(all_chapters)} 个章节")

        # 测试主题样式应用
        theme_data = {
            'colors': {
                'surface': '#2A2A2A',
                'primary': '#404040',
                'background': '#1E1E1E'
            }
        }
        chapters_tab.apply_theme_style(theme_data)
        print("[OK] 主题样式应用成功")

        # 测试章节变化回调
        callback_called = False
        def test_callback(chapter):
            nonlocal callback_called
            callback_called = True
            print(f"章节变化回调被触发: {chapter.get('title', 'Unknown')}")

        chapters_tab.set_chapter_changed_callback(test_callback)
        print("[OK] 章节变化回调设置成功")

        # 测试当前章节获取
        current_chapter = chapters_tab.get_current_chapter()
        if current_chapter:
            print(f"[OK] 当前章节获取成功: {current_chapter.get('title', 'Unknown')}")

        # 短暂显示后销毁
        root.after(1000, root.destroy)
        root.mainloop()
        return True

    except Exception as e:
        print(f"[FAIL] ChaptersTab测试失败: {e}")
        return False

def test_integrated_characters_chapters_system():
    """测试集成的角色和章节管理系统"""
    print("[TEST] 测试集成的角色和章节管理系统...")

    try:
        import customtkinter as ctk
        from ui.modern_main_window import ModernMainWindow

        # 初始化CustomTkinter
        ctk.set_appearance_mode("dark")

        # 创建现代化主窗口
        main_window = ModernMainWindow()
        print("[OK] ModernMainWindow 创建成功")

        # 测试角色标签页集成
        if hasattr(main_window, 'characters_tab') and main_window.characters_tab:
            print("[OK] CharactersTab 组件已集成到主窗口")

            # 测试角色信息
            char_info = main_window.characters_tab.get_characters_info()
            print(f"[OK] 角色标签页信息: {char_info}")

            # 测试角色列表
            all_chars = main_window.characters_tab.get_all_characters()
            print(f"[OK] 角色列表: {[c.get('name', 'Unknown') for c in all_chars]}")
        else:
            print("[FAIL] CharactersTab 组件未集成")
            return False

        # 测试章节标签页集成
        if hasattr(main_window, 'chapters_tab') and main_window.chapters_tab:
            print("[OK] ChaptersTab 组件已集成到主窗口")

            # 测试章节信息
            chap_info = main_window.chapters_tab.get_chapters_info()
            print(f"[OK] 章节标签页信息: {chap_info}")

            # 测试章节列表
            all_chaps = main_window.chapters_tab.get_all_chapters()
            print(f"[OK] 章节列表: {[c.get('title', 'Unknown') for c in all_chaps]}")
        else:
            print("[FAIL] ChaptersTab 组件未集成")
            return False

        # 测试主内容区域
        if hasattr(main_window, 'main_content') and main_window.main_content:
            print("[OK] MainContentArea 组件存在")

            # 测试标签页列表
            all_tabs = main_window.main_content.get_all_tabs()
            print(f"[OK] 可用标签页: {all_tabs}")

            # 测试切换到角色标签页
            main_window.main_content.switch_to_tab("characters")
            current_tab = main_window.main_content.get_current_tab()
            print(f"[OK] 切换到角色标签页: {current_tab}")

            # 测试切换到章节标签页
            main_window.main_content.switch_to_tab("chapters")
            current_tab = main_window.main_content.get_current_tab()
            print(f"[OK] 切换到章节标签页: {current_tab}")

        else:
            print("[FAIL] MainContentArea 组件不存在")
            return False

        # 短暂显示后销毁
        main_window.after(1500, main_window.destroy)
        main_window.mainloop()
        return True

    except Exception as e:
        print(f"[FAIL] 集成角色和章节系统测试失败: {e}")
        return False

def test_characters_chapters_functionality():
    """测试角色和章节功能"""
    print("[TEST] 测试角色和章节功能...")

    try:
        import customtkinter as ctk
        from ui.modern_main_window import ModernMainWindow

        # 创建现代化主窗口
        main_window = ModernMainWindow()
        print("[OK] ModernMainWindow 创建成功")

        # 测试角色功能
        if hasattr(main_window, 'characters_tab'):
            print("[OK] 测试角色功能...")

            # 测试角色选择和状态更新
            all_chars = main_window.characters_tab.get_all_characters()
            if all_chars:
                first_char = all_chars[0]
                main_window.characters_tab._select_character(first_char)
                print(f"[OK] 角色选择测试成功: {first_char.get('name', 'Unknown')}")

            # 测试角色状态更新回调
            main_window._on_character_changed({"name": "测试角色"})
            print("[OK] 角色状态更新回调测试成功")

        # 测试章节功能
        if hasattr(main_window, 'chapters_tab'):
            print("[OK] 测试章节功能...")

            # 测试章节选择和状态更新
            all_chaps = main_window.chapters_tab.get_all_chapters()
            if all_chaps:
                first_chap = all_chaps[0]
                main_window.chapters_tab._select_chapter(first_chap)
                print(f"[OK] 章节选择测试成功: {first_chap.get('title', 'Unknown')}")

            # 测试章节状态更新回调
            main_window._on_chapter_changed({"title": "测试章节"})
            print("[OK] 章节状态更新回调测试成功")

        # 测试导航和标签页联动
        print("[OK] 测试导航和标签页联动...")
        main_window.sidebar.set_active_navigation("characters")
        print("[OK] 导航到角色标签页成功")

        main_window.sidebar.set_active_navigation("chapters")
        print("[OK] 导航到章节标签页成功")

        # 短暂显示后销毁
        main_window.after(1000, main_window.destroy)
        main_window.mainloop()
        return True

    except Exception as e:
        print(f"[FAIL] 角色和章节功能测试失败: {e}")
        return False

def run_all_tests():
    """运行所有测试"""
    print("开始STORY-002 Day 4 角色和章节管理功能测试\n")

    setup_logging()

    tests = [
        ("CharactersTab组件测试", test_characters_tab),
        ("ChaptersTab组件测试", test_chapters_tab),
        ("集成角色和章节系统测试", test_integrated_characters_chapters_system),
        ("角色和章节功能测试", test_characters_chapters_functionality)
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
        print("\n[SUCCESS] 所有测试通过！STORY-002 Day 4 角色和章节管理功能验证成功！")
        print("[INFO] 可以继续Day 4的后续开发工作")
    else:
        print(f"\n[WARNING] 有 {failed} 个测试失败，需要修复后再继续")

    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)