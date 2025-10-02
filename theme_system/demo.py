#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主题系统演示程序
展示主题系统的基本功能和使用方法
"""

import customtkinter as ctk
import sys
import os
import logging

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from theme_system import ThemeManager, StyledButton, StyledFrame, StyledLabel, StyledEntry
from theme_system.components.theme_toggle import ThemeToggleButton, ThemeSelector

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# 设置CustomTkinter外观
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class ThemeDemoApp:
    """主题系统演示应用"""

    def __init__(self):
        # 初始化主题管理器
        self.theme_manager = ThemeManager()

        # 创建主窗口
        self.root = ctk.CTk()
        self.root.title("AI小说生成器 - 主题系统演示")
        self.root.geometry("800x600")

        # 设置窗口图标 (如果有的话)
        # self.root.iconbitmap("icon.ico")

        # 创建界面
        self.setup_ui()

        # 应用初始主题
        self.apply_initial_theme()

    def setup_ui(self):
        """设置用户界面"""
        # 配置主窗口布局
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        # 创建标题栏
        self.create_title_bar()

        # 创建主内容区域
        self.create_main_content()

        # 创建状态栏
        self.create_status_bar()

    def create_title_bar(self):
        """创建标题栏"""
        title_frame = StyledFrame(
            self.root,
            theme_manager=self.theme_manager,
            widget_type="header",
            height=60
        )
        title_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        title_frame.grid_columnconfigure(1, weight=1)

        # 应用标题
        title_label = StyledLabel(
            title_frame,
            text="AI小说生成器 - 主题系统演示",
            font=ctk.CTkFont(size=18, weight="bold"),
            theme_manager=self.theme_manager,
            text_size="xl"
        )
        title_label.grid(row=0, column=0, sticky="w", padx=20, pady=15)

        # 主题切换按钮
        self.theme_toggle = ThemeToggleButton(
            title_frame,
            theme_manager=self.theme_manager,
            on_theme_changed=self.on_theme_changed
        )
        self.theme_toggle.grid(row=0, column=2, sticky="e", padx=20, pady=10)

    def create_main_content(self):
        """创建主内容区域"""
        # 主内容框架
        main_frame = StyledFrame(
            self.root,
            theme_manager=self.theme_manager,
            widget_type="main_content"
        )
        main_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

        # 左侧演示区域
        self.create_demo_area(main_frame)

        # 右侧主题选择器
        self.create_theme_selector(main_frame)

    def create_demo_area(self, parent):
        """创建演示区域"""
        demo_frame = StyledFrame(
            parent,
            theme_manager=self.theme_manager,
            widget_type="demo_area"
        )
        demo_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        demo_frame.grid_columnconfigure(0, weight=1)

        # 演示标题
        demo_title = StyledLabel(
            demo_frame,
            text="组件演示",
            font=ctk.CTkFont(size=16, weight="bold"),
            theme_manager=self.theme_manager,
            text_size="lg"
        )
        demo_title.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))

        # 按钮演示
        self.create_button_demo(demo_frame)

        # 输入框演示
        self.create_input_demo(demo_frame)

        # 标签示演
        self.create_label_demo(demo_frame)

    def create_button_demo(self, parent):
        """创建按钮演示"""
        button_frame = StyledFrame(
            parent,
            theme_manager=self.theme_manager,
            widget_type="button_demo"
        )
        button_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        button_frame.grid_columnconfigure(0, weight=1)

        # 按钮演示标题
        button_title = StyledLabel(
            button_frame,
            text="按钮样式:",
            theme_manager=self.theme_manager
        )
        button_title.grid(row=0, column=0, sticky="w", pady=5)

        # 各种样式的按钮
        buttons = [
            ("主要按钮", "primary"),
            ("次要按钮", "secondary"),
            ("成功按钮", "success"),
            ("警告按钮", "warning"),
            ("危险按钮", "danger")
        ]

        for i, (text, style) in enumerate(buttons):
            btn = StyledButton(
                button_frame,
                text=text,
                button_style=style,
                theme_manager=self.theme_manager,
                width=120
            )
            btn.grid(row=0, column=i+1, padx=5, pady=5)

    def create_input_demo(self, parent):
        """创建输入框演示"""
        input_frame = StyledFrame(
            parent,
            theme_manager=self.theme_manager,
            widget_type="input_demo"
        )
        input_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        input_frame.grid_columnconfigure(1, weight=1)

        # 输入框演示标题
        input_title = StyledLabel(
            input_frame,
            text="输入框样式:",
            theme_manager=self.theme_manager
        )
        input_title.grid(row=0, column=0, sticky="w", pady=5)

        # 输入框
        entry = StyledEntry(
            input_frame,
            placeholder_text="请输入文本...",
            theme_manager=self.theme_manager,
            width=200
        )
        entry.grid(row=0, column=1, sticky="ew", padx=10, pady=5)

    def create_label_demo(self, parent):
        """创建标签示演"""
        label_frame = StyledFrame(
            parent,
            theme_manager=self.theme_manager,
            widget_type="label_demo"
        )
        label_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=10)
        label_frame.grid_columnconfigure(0, weight=1)

        # 标签示演标题
        label_title = StyledLabel(
            label_frame,
            text="标签样式:",
            theme_manager=self.theme_manager
        )
        label_title.grid(row=0, column=0, sticky="w", pady=5)

        # 各种样式的标签
        labels = [
            ("默认文本", "normal"),
            ("次要文本", "secondary"),
            ("成功文本", "success"),
            ("警告文本", "warning"),
            ("错误文本", "danger")
        ]

        for i, (text, style) in enumerate(labels):
            label = StyledLabel(
                label_frame,
                text=text,
                theme_manager=self.theme_manager
            )
            # 这里可以根据样式设置不同的颜色
            if style == "secondary":
                label.configure(text_color=self.theme_manager.get_color('text_secondary'))
            elif style == "success":
                label.configure(text_color=self.theme_manager.get_color('success'))
            elif style == "warning":
                label.configure(text_color=self.theme_manager.get_color('warning'))
            elif style == "danger":
                label.configure(text_color=self.theme_manager.get_color('error'))

            label.grid(row=1, column=i, padx=5, pady=5)

    def create_theme_selector(self, parent):
        """创建主题选择器"""
        # 主题选择器容器
        selector_frame = StyledFrame(
            parent,
            theme_manager=self.theme_manager,
            widget_type="theme_selector",
            width=250
        )
        selector_frame.grid(row=0, column=1, sticky="nse", padx=10, pady=10)

        # 主题选择器
        self.theme_selector = ThemeSelector(
            selector_frame,
            theme_manager=self.theme_manager,
            on_theme_changed=self.on_theme_changed
        )
        self.theme_selector.pack(fill="both", expand=True, padx=10, pady=10)

    def create_status_bar(self):
        """创建状态栏"""
        from theme_system.components.theme_toggle import ThemeStatusBar

        self.status_bar = ThemeStatusBar(
            self.root,
            theme_manager=self.theme_manager,
            height=30
        )
        self.status_bar.grid(row=2, column=0, sticky="ew", padx=5, pady=5)

    def apply_initial_theme(self):
        """应用初始主题"""
        current_theme = self.theme_manager.get_current_theme()
        logger.info(f"应用初始主题: {current_theme}")

    def on_theme_changed(self, theme_name: str):
        """主题变化回调"""
        logger.info(f"主题已切换到: {theme_name}")
        # 这里可以添加主题变化时的额外处理逻辑

    def run(self):
        """运行应用"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            logger.info("用户中断程序")
        except Exception as e:
            logger.error(f"程序运行错误: {e}")
        finally:
            # 清理资源
            self.cleanup()

    def cleanup(self):
        """清理资源"""
        try:
            if hasattr(self, 'theme_manager'):
                # 主题管理器会自动清理资源
                pass
            logger.info("资源清理完成")
        except Exception as e:
            logger.error(f"资源清理失败: {e}")


def main():
    """主函数"""
    logger.info("启动主题系统演示程序")

    try:
        # 创建并运行应用
        app = ThemeDemoApp()
        app.run()

    except Exception as e:
        logger.error(f"程序启动失败: {e}")
        return 1

    logger.info("程序正常退出")
    return 0


if __name__ == "__main__":
    sys.exit(main())