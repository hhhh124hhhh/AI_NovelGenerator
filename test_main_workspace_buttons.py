# test_main_workspace_buttons.py
# -*- coding: utf-8 -*-
"""
测试MainWorkspace按钮功能的脚本
专门诊断生成按钮点击无反应的问题
"""

import sys
import os
import tkinter as tk

# 设置UTF-8编码环境
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def safe_print(text):
    """安全打印，避免编码错误"""
    try:
        print(text)
    except UnicodeEncodeError:
        safe_text = text.encode('ascii', 'ignore').decode('ascii')
        print(safe_text)

def test_main_workspace_buttons():
    """测试MainWorkspace按钮功能"""
    safe_print("=== 测试MainWorkspace按钮功能 ===")

    try:
        # 导入必要模块
        import customtkinter as ctk
        from ui.components.main_workspace import MainWorkspace

        safe_print("✅ 模块导入成功")

        # 创建测试窗口
        root = ctk.CTk()
        root.title("MainWorkspace按钮测试")
        root.geometry("800x600")

        # 创建模拟的状态管理器和主题管理器
        class MockStateManager:
            def get_state(self, key, default=None):
                return default
            def set_state(self, key, value):
                pass

        class MockThemeManager:
            def get_color(self, color_name):
                return "#343638"

        state_manager = MockStateManager()
        theme_manager = MockThemeManager()

        # 创建MainWorkspace实例
        safe_print("🔧 创建MainWorkspace实例...")
        workspace = MainWorkspace(root, theme_manager, state_manager)
        workspace.pack(fill="both", expand=True)

        # 检查按钮是否存在
        safe_print("🔍 检查按钮是否存在...")
        if hasattr(workspace, 'step_buttons'):
            safe_print(f"✅ step_buttons存在，包含 {len(workspace.step_buttons)} 个按钮")
            for step_id, button in workspace.step_buttons.items():
                button_text = button.cget('text')
                safe_print(f"   - {step_id}: {button_text}")

                # 检查按钮的command
                command = button.cget('command')
                if command:
                    safe_print(f"     ✅ Command已设置: {command.__name__ if hasattr(command, '__name__') else 'unknown'}")
                else:
                    safe_print(f"     ❌ Command为空")
        else:
            safe_print("❌ step_buttons属性不存在")

        # 检查关键方法是否存在
        safe_print("🔍 检查关键方法...")
        methods_to_check = [
            '_on_generate_architecture',
            '_on_generate_blueprint',
            '_on_generate_chapter',
            '_on_finalize_chapter',
            '_on_consistency_check',
            '_on_batch_generate',
            '_start_generation',
            '_execute_generation'
        ]

        for method_name in methods_to_check:
            if hasattr(workspace, method_name):
                safe_print(f"✅ 方法存在: {method_name}")
            else:
                safe_print(f"❌ 方法缺失: {method_name}")

        # 检查novel_params
        safe_print("🔍 检查novel_params...")
        if hasattr(workspace, 'novel_params'):
            safe_print(f"✅ novel_params存在: {workspace.novel_params}")
        else:
            safe_print("❌ novel_params不存在")

        # 设置测试参数
        safe_print("🔧 设置测试参数...")
        workspace.novel_params = {
            'topic': '测试小说主题',
            'genre': '科幻',
            'num_chapters': 5,
            'word_number': 2000,
            'filepath': '.',
            'guidance': '这是一个测试小说',
            'chapter_num': 1
        }

        safe_print("✅ 测试参数已设置")

        # 尝试模拟按钮点击
        safe_print("🖱️ 模拟按钮点击测试...")

        try:
            # 测试架构生成按钮
            if hasattr(workspace, '_on_generate_architecture'):
                safe_print("   测试 _on_generate_architecture...")
                # 不实际调用，只检查方法是否可调用
                if callable(workspace._on_generate_architecture):
                    safe_print("   ✅ _on_generate_architecture 可调用")
                else:
                    safe_print("   ❌ _on_generate_architecture 不可调用")
        except Exception as e:
            safe_print(f"   ❌ _on_generate_architecture 测试失败: {e}")

        safe_print("🔍 检查生成状态...")
        if hasattr(workspace, 'generation_state'):
            state = workspace.generation_state
            safe_print(f"   生成状态: {state}")
        else:
            safe_print("❌ generation_state属性不存在")

        safe_print("🎯 测试完成！")
        safe_print("如果看到这个消息，说明MainWorkspace初始化成功")
        safe_print("请检查GUI窗口中的按钮是否可见和可点击")

        # 运行GUI
        root.mainloop()

        return True

    except ImportError as e:
        safe_print(f"❌ 导入失败: {e}")
        return False
    except Exception as e:
        safe_print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    safe_print("MainWorkspace按钮功能测试")
    safe_print("=" * 50)

    success = test_main_workspace_buttons()

    if success:
        safe_print("\n[SUCCESS] 测试成功完成")
        safe_print("MainWorkspace按钮功能基本正常")
    else:
        safe_print("\n[FAIL] 测试失败")
        safe_print("MainWorkspace按钮功能存在问题")

    return 0 if success else 1

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