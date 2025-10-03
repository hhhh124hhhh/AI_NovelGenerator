# main.py
# -*- coding: utf-8 -*-
import os
import customtkinter as ctk
from ui import NovelGeneratorGUI

# 尝试导入主题系统
try:
    from theme_system import ThemeManager, StyleUtils
    THEME_SYSTEM_AVAILABLE = True
except ImportError:
    THEME_SYSTEM_AVAILABLE = False

def main():
    # 设置CustomTkinter外观
    ctk.set_appearance_mode("dark")  # 默认深色模式
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()

    # 如果主题系统可用，则初始化主题管理器
    if THEME_SYSTEM_AVAILABLE:
        try:
            theme_manager = ThemeManager()

            # 将主题管理器注入到GUI中
            gui = NovelGeneratorGUI(app, theme_manager=theme_manager)

        except Exception as e:
            print(f"主题系统初始化失败，使用默认主题: {e}")
            gui = NovelGeneratorGUI(app)
    else:
        gui = NovelGeneratorGUI(app)

    app.mainloop()

if __name__ == "__main__":
    main()