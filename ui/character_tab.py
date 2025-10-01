# ui/character_tab.py
# -*- coding: utf-8 -*-
import customtkinter as ctk
import os
from tkinter import filedialog, messagebox
from ui.context_menu import TextWidgetContextMenu
from .chinese_labels import chinese_labels

def build_character_tab(self):
    self.character_tab = self.tabview.add(chinese_labels["character_tab"])
    self.character_tab.columnconfigure(0, weight=1)
    self.character_tab.rowconfigure(1, weight=1)

    # 标签
    label = ctk.CTkLabel(self.character_tab, text=chinese_labels["character_state"], font=("Microsoft YaHei", 14, "bold"))
    label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

    # 文本框
    self.character_state_text = ctk.CTkTextbox(self.character_tab, wrap="word")
    TextWidgetContextMenu(self.character_state_text)
    self.character_state_text.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

    # 按钮框架
    btn_frame = ctk.CTkFrame(self.character_tab)
    btn_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
    btn_frame.columnconfigure((0, 1), weight=1)

    # 加载按钮
    load_btn = ctk.CTkButton(btn_frame, text=chinese_labels["refresh"], command=self.load_character_state, font=("Microsoft YaHei", 12))
    load_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

    # 保存按钮
    save_btn = ctk.CTkButton(btn_frame, text=chinese_labels["save_character_state"], command=self.save_character_state, font=("Microsoft YaHei", 12))
    save_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

def load_character_state(self):
    try:
        # 修复文件路径问题，使用保存路径
        filepath = self.filepath_var.get().strip()
        if filepath:
            full_path = os.path.join(filepath, "character_state.txt")
            content = self.utils.read_file(full_path)
        else:
            # 如果没有设置保存路径，使用默认路径
            content = self.utils.read_file("character_state.txt")
        self.character_state_text.delete("0.0", "end")
        self.character_state_text.insert("0.0", content)
        self.log("已加载角色状态。")
    except FileNotFoundError:
        self.log("未找到 character_state.txt 文件。")
    except Exception as e:
        self.log(f"加载角色状态时出错: {str(e)}")

def save_character_state(self):
    try:
        content = self.character_state_text.get("0.0", "end").strip()
        # 修复文件路径问题，使用保存路径
        filepath = self.filepath_var.get().strip()
        if filepath:
            full_path = os.path.join(filepath, "character_state.txt")
            self.utils.save_string_to_txt(content, full_path)
        else:
            # 如果没有设置保存路径，使用默认路径
            self.utils.save_string_to_txt(content, "character_state.txt")
        self.log("角色状态已保存。")
    except Exception as e:
        self.log(f"保存角色状态时出错: {str(e)}")