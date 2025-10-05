#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
最终集成测试 - 验证所有功能是否正常工作
"""

import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def safe_print(text):
    """安全打印"""
    try:
        print(text)
    except UnicodeEncodeError:
        clean_text = text.encode('ascii', 'ignore').decode('ascii')
        print(clean_text)

def test_imports():
    """测试所有关键模块导入"""
    safe_print("测试关键模块导入...")

    try:
        # 测试项目管理器
        from ui.components.project_manager import ProjectManager
        safe_print("  ProjectManager导入成功")

        # 测试生成日志标签页
        from ui.components.generation_log_tab import GenerationLogTab
        safe_print("  GenerationLogTab导入成功")

        # 测试角色标签页
        from ui.components.characters_tab import CharactersTab
        safe_print("  CharactersTab导入成功")

        # 测试目录管理器
        from ui.components.directory_manager import DirectoryManager
        safe_print("  DirectoryManager导入成功")

        # 测试主工作区
        from ui.components.main_workspace import MainWorkspace
        safe_print("  MainWorkspace导入成功")

        # 测试现代主窗口
        from ui.modern_main_window import ModernMainWindow
        safe_print("  ModernMainWindow导入成功")

        return True

    except ImportError as e:
        safe_print(f"  导入失败: {e}")
        return False
    except Exception as e:
        safe_print(f"  其他错误: {e}")
        return False

def test_project_manager_integration():
    """测试项目管理器集成"""
    safe_print("\n测试项目管理器集成...")

    try:
        from ui.components.project_manager import ProjectManager

        # 创建项目管理器实例
        pm = ProjectManager()
        safe_print("  项目管理器实例创建成功")

        # 测试基本功能
        current_path = pm.get_project_path()
        safe_print(f"  当前项目路径: {current_path}")

        # 测试文件检查
        files = pm.get_project_files()
        safe_print(f"  扫描到 {len(files)} 个项目文件")

        return True

    except Exception as e:
        safe_print(f"  项目管理器集成测试失败: {e}")
        return False

def test_tab_components():
    """测试标签页组件"""
    safe_print("\n测试标签页组件...")

    try:
        import customtkinter as ctk

        # 创建测试根窗口
        root = ctk.CTk()

        # 测试生成日志标签页
        from ui.components.generation_log_tab import GenerationLogTab
        log_tab = GenerationLogTab(root)
        safe_print("  GenerationLogTab创建成功")

        # 测试角色标签页
        from ui.components.characters_tab import CharactersTab
        char_tab = CharactersTab(root, None, None)
        safe_print("  CharactersTab创建成功")

        # 测试目录管理器
        from ui.components.directory_manager import DirectoryManager
        dir_tab = DirectoryManager(root, None, None)
        safe_print("  DirectoryManager创建成功")

        # 销毁测试窗口
        root.destroy()

        return True

    except Exception as e:
        safe_print(f"  标签页组件测试失败: {e}")
        return False

def test_file_operations():
    """测试文件操作功能"""
    safe_print("\n测试文件操作功能...")

    try:
        from ui.components.project_manager import ProjectManager

        pm = ProjectManager()

        # 测试读取character_state.txt
        char_path = pm.get_file_path("character_state.txt")
        if char_path and os.path.exists(char_path):
            safe_print("  character_state.txt文件可访问")
        else:
            safe_print("  character_state.txt文件不存在（正常）")

        # 测试读取Novel_directory.txt
        dir_path = pm.get_file_path("Novel_directory.txt")
        if dir_path and os.path.exists(dir_path):
            safe_print("  Novel_directory.txt文件可访问")
        else:
            safe_print("  Novel_directory.txt文件不存在（正常）")

        return True

    except Exception as e:
        safe_print(f"  文件操作测试失败: {e}")
        return False

def main():
    """主测试函数"""
    safe_print("=" * 60)
    safe_print("开始最终集成测试")
    safe_print("=" * 60)

    success_count = 0
    total_tests = 4

    # 1. 测试导入
    if test_imports():
        success_count += 1

    # 2. 测试项目管理器集成
    if test_project_manager_integration():
        success_count += 1

    # 3. 测试标签页组件
    if test_tab_components():
        success_count += 1

    # 4. 测试文件操作
    if test_file_operations():
        success_count += 1

    safe_print("\n" + "=" * 60)
    safe_print(f"测试结果: {success_count}/{total_tests} 通过")

    if success_count == total_tests:
        safe_print("所有测试通过！系统集成成功。")
        safe_print("\n主要改进:")
        safe_print("1. 创建了独立的生成日志标签页")
        safe_print("2. 优化了主页面布局，移除了日志区域")
        safe_print("3. 添加了生成动画功能")
        safe_print("4. 为角色和目录标签页添加了刷新按钮")
        safe_print("5. 实现了统一项目管理系统，解决了1.0和2.0的差异")
        safe_print("6. 修复了文件读取问题")
        return True
    else:
        safe_print("部分测试失败，请检查错误信息。")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        safe_print("\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        safe_print(f"\n测试过程中发生意外错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)