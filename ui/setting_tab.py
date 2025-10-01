# ui/setting_tab.py
# -*- coding: utf-8 -*-
import customtkinter as ctk
from tkinter import filedialog, messagebox
from ui.context_menu import TextWidgetContextMenu
from .chinese_labels import chinese_labels

def build_setting_tab(self):
    self.setting_tab = self.tabview.add(chinese_labels["setting_tab"])
    self.setting_tab.columnconfigure(0, weight=1)
    self.setting_tab.rowconfigure(1, weight=1)

    # 标签
    label = ctk.CTkLabel(self.setting_tab, text=chinese_labels["novel_setting"], font=("Microsoft YaHei", 14, "bold"))
    label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

    # 文本框
    self.novel_architecture_text = ctk.CTkTextbox(self.setting_tab, wrap="word")
    TextWidgetContextMenu(self.novel_architecture_text)
    self.novel_architecture_text.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

    # 按钮框架
    btn_frame = ctk.CTkFrame(self.setting_tab)
    btn_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
    btn_frame.columnconfigure((0, 1), weight=1)

    # 加载按钮
    load_btn = ctk.CTkButton(btn_frame, text=chinese_labels["refresh"], command=self.load_novel_architecture, font=("Microsoft YaHei", 12))
    load_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

    # 保存按钮
    save_btn = ctk.CTkButton(btn_frame, text=chinese_labels["save_novel_setting"], command=self.save_novel_architecture, font=("Microsoft YaHei", 12))
    save_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

def load_novel_architecture(self):
    try:
        content = self.utils.read_file("Novel_setting.txt")
        self.novel_architecture_text.delete("0.0", "end")
        self.novel_architecture_text.insert("0.0", content)
        self.log("已加载小说设定。")
    except FileNotFoundError:
        self.log("未找到 Novel_setting.txt 文件。")
    except Exception as e:
        self.log(f"加载小说设定时出错: {str(e)}")

def save_novel_architecture(self):
    try:
        content = self.novel_architecture_text.get("0.0", "end").strip()
        self.utils.save_string_to_txt(content, "Novel_setting.txt")
        self.log("小说设定已保存。")
    except Exception as e:
        self.log(f"保存小说设定时出错: {str(e)}")