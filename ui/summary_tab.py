# ui/summary_tab.py
# -*- coding: utf-8 -*-
import customtkinter as ctk
import os
from tkinter import filedialog, messagebox
from ui.context_menu import TextWidgetContextMenu
from .chinese_labels import chinese_labels

def build_summary_tab(self):
    self.summary_tab = self.tabview.add(chinese_labels["summary_tab"])
    self.summary_tab.columnconfigure(0, weight=1)
    self.summary_tab.rowconfigure(1, weight=1)

    # 标签
    label = ctk.CTkLabel(self.summary_tab, text=chinese_labels["global_summary"], font=("Microsoft YaHei", 14, "bold"))
    label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

    # 文本框
    self.global_summary_text = ctk.CTkTextbox(self.summary_tab, wrap="word")
    TextWidgetContextMenu(self.global_summary_text)
    self.global_summary_text.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

    # 按钮框架
    btn_frame = ctk.CTkFrame(self.summary_tab)
    btn_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
    btn_frame.columnconfigure((0, 1), weight=1)

    # 加载按钮
    load_btn = ctk.CTkButton(btn_frame, text=chinese_labels["refresh"], command=self.load_global_summary, font=("Microsoft YaHei", 12))
    load_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

    # 保存按钮
    save_btn = ctk.CTkButton(btn_frame, text=chinese_labels["save_global_summary"], command=self.save_global_summary, font=("Microsoft YaHei", 12))
    save_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

def load_global_summary(self):
    try:
        # 修复文件路径问题，使用保存路径
        filepath = self.filepath_var.get().strip()
        if filepath:
            full_path = os.path.join(filepath, "global_summary.txt")
            content = self.utils.read_file(full_path)
        else:
            # 如果没有设置保存路径，使用默认路径
            content = self.utils.read_file("global_summary.txt")
        self.global_summary_text.delete("0.0", "end")
        self.global_summary_text.insert("0.0", content)
        self.log("已加载全局摘要。")
    except FileNotFoundError:
        self.log("未找到 global_summary.txt 文件。")
    except Exception as e:
        self.log(f"加载全局摘要时出错: {str(e)}")

def save_global_summary(self):
    try:
        content = self.global_summary_text.get("0.0", "end").strip()
        # 修复文件路径问题，使用保存路径
        filepath = self.filepath_var.get().strip()
        if filepath:
            full_path = os.path.join(filepath, "global_summary.txt")
            self.utils.save_string_to_txt(content, full_path)
        else:
            # 如果没有设置保存路径，使用默认路径
            self.utils.save_string_to_txt(content, "global_summary.txt")
        self.log("全局摘要已保存。")
    except Exception as e:
        self.log(f"保存全局摘要时出错: {str(e)}")