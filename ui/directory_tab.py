# ui/directory_tab.py
# -*- coding: utf-8 -*-
import customtkinter as ctk
import os
from tkinter import filedialog, messagebox
from ui.context_menu import TextWidgetContextMenu
from .chinese_labels import chinese_labels

def build_directory_tab(self):
    self.directory_tab = self.tabview.add(chinese_labels["directory_tab"])
    self.directory_tab.columnconfigure(0, weight=1)
    self.directory_tab.rowconfigure(1, weight=1)

    # 标签
    label = ctk.CTkLabel(self.directory_tab, text=chinese_labels["chapter_directory"], font=("Microsoft YaHei", 14, "bold"))
    label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

    # 文本框
    self.chapter_blueprint_text = ctk.CTkTextbox(self.directory_tab, wrap="word")
    TextWidgetContextMenu(self.chapter_blueprint_text)
    self.chapter_blueprint_text.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

    # 按钮框架
    btn_frame = ctk.CTkFrame(self.directory_tab)
    btn_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
    btn_frame.columnconfigure((0, 1, 2), weight=1)  # 修改为3列权重

    # 刷新按钮 - 新增
    refresh_btn = ctk.CTkButton(btn_frame, text=chinese_labels["refresh"], command=self.load_chapter_blueprint, font=("Microsoft YaHei", 12))
    refresh_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

    # 加载按钮
    load_btn = ctk.CTkButton(btn_frame, text="加载", command=self.load_chapter_blueprint, font=("Microsoft YaHei", 12))
    load_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    # 保存按钮
    save_btn = ctk.CTkButton(btn_frame, text=chinese_labels["save_chapter_directory"], command=self.save_chapter_blueprint, font=("Microsoft YaHei", 12))
    save_btn.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

def load_chapter_blueprint(self):
    try:
        # 修复文件路径问题，使用保存路径
        filepath = self.filepath_var.get().strip()
        if filepath:
            full_path = os.path.join(filepath, "Novel_directory.txt")
            content = self.utils.read_file(full_path)
        else:
            # 如果没有设置保存路径，使用默认路径
            content = self.utils.read_file("Novel_directory.txt")
        self.chapter_blueprint_text.delete("0.0", "end")
        self.chapter_blueprint_text.insert("0.0", content)
        self.log("已加载章节目录。")
    except FileNotFoundError:
        self.log("未找到 Novel_directory.txt 文件。")
    except Exception as e:
        self.log(f"加载章节目录时出错: {str(e)}")

def save_chapter_blueprint(self):
    try:
        # 修复文件路径问题，使用保存路径
        content = self.chapter_blueprint_text.get("0.0", "end").strip()
        filepath = self.filepath_var.get().strip()
        if filepath:
            full_path = os.path.join(filepath, "Novel_directory.txt")
            self.utils.save_string_to_txt(content, full_path)
        else:
            # 如果没有设置保存路径，使用默认路径
            self.utils.save_string_to_txt(content, "Novel_directory.txt")
        self.log("章节目录已保存。")
    except Exception as e:
        self.log(f"保存章节目录时出错: {str(e)}")