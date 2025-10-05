# launch.py
# -*- coding: utf-8 -*-
"""
AI小说生成器 - 智能启动选择器
提供用户友好的版本选择界面
自动检测系统环境和推荐最佳版本
"""

import sys
import os
import subprocess
import time
from typing import Dict, List, Optional

# 尝试导入依赖
try:
    import tkinter as tk
    from tkinter import ttk, messagebox
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False
    print("⚠️  GUI不可用，将使用命令行模式")

try:
    import customtkinter as ctk
    MODERN_GUI_AVAILABLE = True
except ImportError:
    MODERN_GUI_AVAILABLE = False


class LauncherConfig:
    """启动器配置"""

    VERSIONS = {
        "modern": {
            "name": "现代版 (2.0+)",
            "description": "基于最新架构，现代化界面设计",
            "script": "main_modern.py",
            "features": ["现代化UI", "主题系统", "响应式布局", "高级日志"],
            "recommended": True,
            "color": "#2E86AB"
        },
        "classic": {
            "name": "经典版 (1.0)",
            "description": "稳定可靠，功能完整",
            "script": "main_classic.py",
            "features": ["功能完整", "稳定可靠", "久经测试", "生产就绪"],
            "recommended": False,
            "color": "#A23B72"
        },
        "auto": {
            "name": "自动选择",
            "description": "智能检测系统环境，选择最佳版本",
            "script": None,
            "features": ["智能检测", "自动回退", "最佳体验"],
            "recommended": False,
            "color": "#F18F01"
        }
    }

    SYSTEM_INFO = {
        "python_version": sys.version,
        "platform": sys.platform,
        "directory": os.getcwd(),
        "args": sys.argv
    }


class ModernLauncher:
    """现代化启动器界面"""

    def __init__(self):
        self.config = LauncherConfig()
        self.selected_version = "modern"  # 默认选中的版本
        self.setup_window()

    def setup_window(self):
        """设置主窗口"""
        if MODERN_GUI_AVAILABLE:
            self.setup_modern_window()
        else:
            self.setup_classic_window()

    def setup_modern_window(self):
        """设置现代化窗口"""
        import customtkinter as ctk

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("AI小说生成器 - 启动选择器")
        self.root.geometry("800x700")
        self.root.resizable(False, False)

        # 主标题
        title_frame = ctk.CTkFrame(self.root)
        title_frame.pack(fill="x", padx=20, pady=15)

        title_label = ctk.CTkLabel(
            title_frame,
            text="🚀 AI小说生成器",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title_label.pack(pady=8)

        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="选择您想要启动的版本",
            font=ctk.CTkFont(size=16)
        )
        subtitle_label.pack(pady=4)

        # 版本选择区域
        self.versions_frame = ctk.CTkScrollableFrame(self.root)
        self.versions_frame.pack(fill="both", expand=True, padx=20, pady=5)

        self.version_buttons = {}
        self.create_version_cards()

        # 底部按钮
        bottom_frame = ctk.CTkFrame(self.root)
        bottom_frame.pack(fill="x", padx=20, pady=10)

        button_frame = ctk.CTkFrame(bottom_frame)
        button_frame.pack(pady=8)

        self.launch_button = ctk.CTkButton(
            button_frame,
            text="启动选中的版本",
            command=self.launch_selected,
            font=ctk.CTkFont(size=16, weight="bold"),
            width=200,
            height=45,
            fg_color="#00C851",
            hover_color="#00A846"
        )
        self.launch_button.pack(side="left", padx=8, pady=5)

        self.test_button = ctk.CTkButton(
            button_frame,
            text="系统诊断",
            command=self.run_diagnosis,
            font=ctk.CTkFont(size=14),
            width=150,
            height=45,
            fg_color="#FF8800",
            hover_color="#FF6600"
        )
        self.test_button.pack(side="left", padx=8, pady=5)

        self.quit_button = ctk.CTkButton(
            button_frame,
            text="退出",
            command=self.root.quit,
            font=ctk.CTkFont(size=14),
            width=100,
            height=45,
            fg_color="#CC4444",
            hover_color="#AA3333"
        )
        self.quit_button.pack(side="left", padx=8, pady=5)

        # 状态栏
        self.status_label = ctk.CTkLabel(
            self.root,
            text="准备就绪",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=5)

    def setup_classic_window(self):
        """设置经典窗口（当customtkinter不可用时）"""
        import tkinter as tk
        from tkinter import ttk

        self.root = tk.Tk()
        self.root.title("AI小说生成器 - 启动选择器")
        self.root.geometry("600x500")
        self.root.resizable(False, False)

        # 主标题
        title_label = tk.Label(
            self.root,
            text="🚀 AI小说生成器",
            font=("Arial", 24, "bold")
        )
        title_label.pack(pady=20)

        subtitle_label = tk.Label(
            self.root,
            text="选择您想要启动的版本",
            font=("Arial", 14)
        )
        subtitle_label.pack(pady=10)

        # 版本选择
        self.versions_frame = ttk.Frame(self.root)
        self.versions_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.version_var = tk.StringVar(value="modern")
        self.create_classic_version_cards()

        # 按钮
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=20)

        self.launch_button = ttk.Button(
            button_frame,
            text="启动选中的版本",
            command=self.launch_selected
        )
        self.launch_button.pack(side="left", padx=10)

        self.test_button = ttk.Button(
            button_frame,
            text="系统诊断",
            command=self.run_diagnosis
        )
        self.test_button.pack(side="left", padx=10)

        self.quit_button = ttk.Button(
            button_frame,
            text="退出",
            command=self.root.quit
        )
        self.quit_button.pack(side="left", padx=10)

        # 状态栏
        self.status_label = tk.Label(
            self.root,
            text="准备就绪",
            font=("Arial", 10)
        )
        self.status_label.pack(pady=5)

    def create_version_cards(self):
        """创建版本卡片（现代化界面）"""
        import customtkinter as ctk

        for i, (key, version) in enumerate(self.config.VERSIONS.items()):
            if key == "auto":
                continue

            frame = ctk.CTkFrame(self.versions_frame)
            frame.pack(fill="x", pady=8, padx=15)

            # 左侧信息
            info_frame = ctk.CTkFrame(frame)
            info_frame.pack(side="left", fill="both", expand=True, padx=8, pady=8)

            name_label = ctk.CTkLabel(
                info_frame,
                text=version["name"],
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=version["color"]
            )
            name_label.pack(anchor="w", pady=(0, 5))

            desc_label = ctk.CTkLabel(
                info_frame,
                text=version["description"],
                font=ctk.CTkFont(size=14)
            )
            desc_label.pack(anchor="w", pady=(0, 10))

            # 特性标签
            features_frame = ctk.CTkFrame(info_frame)
            features_frame.pack(fill="x")

            for feature in version["features"]:
                feature_label = ctk.CTkLabel(
                    features_frame,
                    text=f"✓ {feature}",
                    font=ctk.CTkFont(size=12)
                )
                feature_label.pack(anchor="w", padx=10, pady=2)

            # 右侧选择按钮
            select_frame = ctk.CTkFrame(frame)
            select_frame.pack(side="right", padx=10, pady=10)

            # 创建选择按钮
            select_button = ctk.CTkButton(
                select_frame,
                text="选择",
                width=80,
                height=35,
                command=lambda k=key: self.select_version(k)
            )
            select_button.pack(pady=20)

            if version["recommended"]:
                recommended_label = ctk.CTkLabel(
                    select_frame,
                    text="推荐",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="#00FF00"
                )
                recommended_label.pack()

            self.version_buttons[key] = select_button

        # 设置默认选中状态
        if "modern" in self.version_buttons:
            self.update_button_selection("modern")

    def select_version(self, version_key):
        """选择版本"""
        self.selected_version = version_key
        self.update_button_selection(version_key)
        self.update_status(f"已选择: {self.config.VERSIONS[version_key]['name']}")

    def update_button_selection(self, selected_key):
        """更新按钮选中状态"""
        for key, button in self.version_buttons.items():
            if key == selected_key:
                button.configure(
                    fg_color="#00FF00",
                    hover_color="#00CC00",
                    text="✓ 已选择"
                )
            else:
                button.configure(
                    fg_color="#2196F3",
                    hover_color="#1976D2",
                    text="选择"
                )

    def create_classic_version_cards(self):
        """创建版本卡片（经典界面）"""
        import tkinter as tk
        from tkinter import ttk

        for i, (key, version) in enumerate(self.config.VERSIONS.items()):
            if key == "auto":
                continue

            frame = ttk.LabelFrame(self.versions_frame, text=version["name"])
            frame.pack(fill="x", pady=10, padx=20)

            # 描述
            desc_label = tk.Label(
                frame,
                text=version["description"],
                font=("Arial", 12)
            )
            desc_label.pack(anchor="w", padx=10, pady=(10, 5))

            # 特性
            features_text = " | ".join([f"✓ {f}" for f in version["features"]])
            features_label = tk.Label(
                frame,
                text=features_text,
                font=("Arial", 10),
                fg="gray"
            )
            features_label.pack(anchor="w", padx=10, pady=(0, 10))

            # 选择按钮
            radio_button = ttk.Radiobutton(
                frame,
                text="选择此版本",
                variable=self.version_var,
                value=key
            )
            radio_button.pack(anchor="w", padx=10, pady=(0, 10))

            if version["recommended"]:
                recommended_label = tk.Label(
                    frame,
                    text="⭐ 推荐版本",
                    font=("Arial", 10, "bold"),
                    fg="green"
                )
                recommended_label.pack(anchor="w", padx=10, pady=(0, 10))

    def launch_selected(self):
        """启动选中的版本"""
        # 使用选中的版本
        selected = self.selected_version

        if selected == "auto":
            self.launch_auto()
        elif selected == "modern":
            self.launch_modern()
        elif selected == "classic":
            self.launch_classic()
        else:
            # 默认启动现代版
            self.launch_modern()

    def launch_modern(self):
        """启动现代版"""
        self.update_status("正在启动现代版...")
        self.run_script("main_modern.py")

    def launch_classic(self):
        """启动经典版"""
        self.update_status("正在启动经典版...")
        self.run_script("main_classic.py")

    def launch_auto(self):
        """自动选择启动"""
        self.update_status("正在智能检测最佳版本...")

        # 简单的自动选择逻辑
        try:
            # 尝试导入现代版依赖
            import customtkinter
            from ui.modern_main_window import ModernMainWindow
            self.launch_modern()
        except:
            self.launch_classic()

    def run_script(self, script_name):
        """运行指定的脚本"""
        try:
            self.update_status(f"正在启动 {script_name}...")

            # 关闭启动器窗口
            self.root.withdraw()

            # 启动脚本
            subprocess.Popen([sys.executable, script_name])

            # 等待一下然后退出启动器
            self.root.after(1000, self.root.quit)

        except Exception as e:
            messagebox.showerror("启动失败", f"无法启动 {script_name}:\n{str(e)}")
            self.root.deiconify()
            self.update_status("启动失败")

    def run_diagnosis(self):
        """运行系统诊断"""
        self.update_status("正在运行系统诊断...")

        try:
            # 运行诊断脚本
            result = subprocess.run(
                [sys.executable, "startup_checker.py"],
                capture_output=True,
                text=True,
                timeout=30
            )

            # 显示诊断结果
            if MODERN_GUI_AVAILABLE:
                import customtkinter as ctk
                diagnosis_window = ctk.CTkToplevel(self.root)
                diagnosis_window.title("系统诊断结果")
                diagnosis_window.geometry("600x400")

                text_widget = ctk.CTkTextbox(diagnosis_window, wrap="word")
                text_widget.pack(fill="both", expand=True, padx=10, pady=10)
            else:
                import tkinter as tk
                diagnosis_window = tk.Toplevel(self.root)
                diagnosis_window.title("系统诊断结果")
                diagnosis_window.geometry("600x400")

                text_widget = tk.Text(diagnosis_window, wrap="word")
                text_widget.pack(fill="both", expand=True, padx=10, pady=10)

            text_widget.insert("1.0", result.stdout)
            if result.stderr:
                text_widget.insert("end", f"\n错误信息:\n{result.stderr}")

            self.update_status("诊断完成")

        except Exception as e:
            messagebox.showerror("诊断失败", f"系统诊断失败:\n{str(e)}")
            self.update_status("诊断失败")

    def update_status(self, message):
        """更新状态栏"""
        if hasattr(self, 'status_label'):
            self.status_label.configure(text=message)
            self.root.update()

    def run(self):
        """运行启动器"""
        self.root.mainloop()


class CommandLineLauncher:
    """命令行启动器"""

    def __init__(self):
        self.config = LauncherConfig()

    def show_banner(self):
        """显示启动横幅"""
        print("🚀 AI小说生成器 - 启动选择器")
        print("=" * 50)

    def show_versions(self):
        """显示可用版本"""
        for key, version in self.config.VERSIONS.items():
            if key == "auto":
                continue

            print(f"\n{version['name']}:")
            print(f"  描述: {version['description']}")
            print(f"  特性: {', '.join(version['features'])}")
            if version['recommended']:
                print("  ⭐ 推荐版本")

    def prompt_choice(self):
        """提示用户选择"""
        while True:
            print("\n请选择要启动的版本:")
            print("1. 现代版 (2.0+) - 推荐")
            print("2. 经典版 (1.0)")
            print("3. 自动选择")
            print("4. 系统诊断")
            print("0. 退出")

            choice = input("\n请输入选择 (0-4): ").strip()

            if choice == "0":
                return None
            elif choice == "1":
                return "modern"
            elif choice == "2":
                return "classic"
            elif choice == "3":
                return "auto"
            elif choice == "4":
                self.run_diagnosis()
            else:
                print("❌ 无效选择，请重试")

    def launch_version(self, version):
        """启动指定版本"""
        if version == "modern":
            print("🚀 启动现代版...")
            os.system("python main_modern.py")
        elif version == "classic":
            print("🔄 启动经典版...")
            os.system("python main_classic.py")
        elif version == "auto":
            print("🤖 智能选择最佳版本...")
            try:
                import customtkinter
                from ui.modern_main_window import ModernMainWindow
                print("✅ 检测到现代版环境，启动现代版")
                os.system("python main_modern.py")
            except:
                print("⚠️  现代版不可用，回退到经典版")
                os.system("python main_classic.py")

    def run_diagnosis(self):
        """运行诊断"""
        print("🔍 运行系统诊断...")
        os.system("python startup_checker.py")

    def run(self):
        """运行命令行启动器"""
        self.show_banner()
        self.show_versions()

        choice = self.prompt_choice()
        if choice:
            self.launch_version(choice)


def main():
    """主函数"""
    print("🎯 AI小说生成器启动器")

    # 根据GUI可用性选择启动器
    if GUI_AVAILABLE:
        try:
            launcher = ModernLauncher()
            launcher.run()
        except Exception as e:
            print(f"⚠️  GUI启动器失败: {e}")
            print("🔄 回退到命令行模式...")
            launcher = CommandLineLauncher()
            launcher.run()
    else:
        launcher = CommandLineLauncher()
        launcher.run()


if __name__ == "__main__":
    main()