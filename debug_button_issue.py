# debug_button_issue.py
# -*- coding: utf-8 -*-
"""
调试按钮无响应问题的脚本
检查MainWorkspace是否正确显示在正确的标签页中
"""

import sys
import os

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

def test_main_workspace_visibility():
    """测试MainWorkspace在界面中的可见性"""
    safe_print("=== 测试MainWorkspace可见性 ===")

    try:
        import customtkinter as ctk
        from ui.modern_main_window import ModernMainWindow

        safe_print("✅ 成功导入ModernMainWindow")

        # 创建应用但不显示主窗口
        app = ModernMainWindow()
        app.withdraw()  # 隐藏主窗口

        # 检查MainWorkspace是否被创建
        if hasattr(app, 'main_workspace'):
            safe_print("✅ MainWorkspace已创建")

            # 检查MainWorkspace是否有按钮
            if hasattr(app.main_workspace, 'step_buttons'):
                safe_print(f"✅ MainWorkspace有 {len(app.main_workspace.step_buttons)} 个按钮")

                for step_id, button in app.main_workspace.step_buttons.items():
                    text = button.cget('text')
                    safe_print(f"   - {step_id}: {text}")

                    # 检查按钮是否可见和启用
                    try:
                        state = button.cget('state')
                        visible = button.winfo_ismapped() if hasattr(button, 'winfo_ismapped') else "unknown"
                        safe_print(f"     状态: {state}, 可见: {visible}")
                    except Exception as e:
                        safe_print(f"     按钮状态检查失败: {e}")
            else:
                safe_print("❌ MainWorkspace没有step_buttons属性")
        else:
            safe_print("❌ ModernMainWindow没有main_workspace属性")

        # 检查标签页结构
        if hasattr(app, 'main_content'):
            safe_print("✅ 找到main_content")

            if hasattr(app.main_content, 'content_frames'):
                safe_print(f"✅ 找到content_frames: {list(app.main_content.content_frames.keys())}")

                # 检查main标签页
                if 'main' in app.main_content.content_frames:
                    main_frame = app.main_content.content_frames['main']
                    safe_print("✅ 找到main标签页框架")

                    # 检查MainWorkspace是否在main标签页中
                    children = main_frame.winfo_children()
                    safe_print(f"main标签页中的子组件数量: {len(children)}")

                    for child in children:
                        class_name = child.__class__.__name__
                        safe_print(f"   - {class_name}: {child}")

                        if class_name == 'MainWorkspace':
                            safe_print("✅ MainWorkspace确实在main标签页中")
                else:
                    safe_print("❌ 没有找到main标签页")
            else:
                safe_print("❌ main_content没有content_frames属性")
        else:
            safe_print("❌ 没有找到main_content")

        # 检查当前显示的标签页
        if hasattr(app, 'main_content') and hasattr(app.main_content, 'current_tab'):
            current_tab = app.main_content.current_tab
            safe_print(f"✅ 当前显示的标签页: {current_tab}")

            if current_tab != 'main':
                safe_print("⚠️ 当前不是main标签页，这可能是按钮看不到的原因！")
                safe_print("建议切换到main标签页来查看生成按钮")
        else:
            safe_print("❌ 无法确定当前显示的标签页")

        app.destroy()
        return True

    except Exception as e:
        safe_print(f"❌ 测试失败: {e}")
        import traceback
        safe_print(f"错误详情: {traceback.format_exc()}")
        return False

def test_simple_main_workspace():
    """测试独立的MainWorkspace"""
    safe_print("\n=== 测试独立MainWorkspace ===")

    try:
        import customtkinter as ctk
        from ui.components.main_workspace import MainWorkspace

        # 创建测试窗口
        root = ctk.CTk()
        root.title("MainWorkspace测试")
        root.geometry("800x600")

        # 创建MainWorkspace
        workspace = MainWorkspace(root, theme_manager=None, state_manager=None)
        workspace.pack(fill="both", expand=True)

        safe_print("✅ 独立MainWorkspace创建成功")
        safe_print("✅ 请检查窗口中是否有生成按钮")
        safe_print("如果能看到按钮，说明MainWorkspace本身没问题")
        safe_print("问题可能在于MainWorkspace在主界面中的集成")

        # 运行GUI
        root.mainloop()

        return True

    except Exception as e:
        safe_print(f"❌ 独立测试失败: {e}")
        return False

def main():
    """主函数"""
    safe_print("MainWorkspace按钮无响应问题调试")
    safe_print("=" * 50)

    # 测试MainWorkspace可见性
    result1 = test_main_workspace_visibility()

    safe_print("\n" + "=" * 50)
    safe_print("调试总结和建议:")

    if result1:
        safe_print("✅ MainWorkspace创建和集成正常")
        safe_print("🔍 可能的问题:")
        safe_print("1. 用户可能在错误的标签页中（不在main标签页）")
        safe_print("2. MainWorkspace可能被其他组件遮挡")
        safe_print("3. 用户界面可能需要滚动才能看到按钮")

        safe_print("\n💡 解决方案:")
        safe_print("1. 确保切换到'主页'标签页")
        safe_print("2. 检查窗口大小是否足够显示所有内容")
        safe_print("3. 查看界面底部的日志区域确认按钮点击")

        safe_print("\n🚀 测试建议:")
        safe_print("运行独立MainWorkspace测试来验证按钮功能")
    else:
        safe_print("❌ MainWorkspace集成存在问题")
        safe_print("需要检查组件初始化过程")

    # 询问是否运行独立测试
    try:
        response = input("\n是否运行独立MainWorkspace测试？(y/n): ").lower()
        if response in ['y', 'yes', '是']:
            test_simple_main_workspace()
    except:
        safe_print("跳过独立测试")

    return 0 if result1 else 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        safe_print("\n调试被用户中断")
        sys.exit(1)
    except Exception as e:
        safe_print(f"调试过程出现异常: {e}")
        sys.exit(1)