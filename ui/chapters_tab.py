# ui/chapters_tab.py
# -*- coding: utf-8 -*-
import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from ui.context_menu import TextWidgetContextMenu
from .chinese_labels import chinese_labels

def build_chapters_tab(self):
    self.chapters_tab = self.tabview.add(chinese_labels["chapters_tab"])
    self.chapters_tab.columnconfigure(0, weight=1)
    self.chapters_tab.rowconfigure(1, weight=1)
    self.chapters_tab.rowconfigure(3, weight=2)

    # 章节列表标签
    chapter_list_label = ctk.CTkLabel(self.chapters_tab, text=chinese_labels["chapter_list"], font=("Microsoft YaHei", 14, "bold"))
    chapter_list_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

    # 章节列表框架
    list_frame = ctk.CTkFrame(self.chapters_tab)
    list_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
    list_frame.columnconfigure(0, weight=1)
    list_frame.rowconfigure(0, weight=1)

    # 章节列表
    self.chapter_listbox = ctk.CTkScrollableFrame(list_frame, orientation="vertical")
    self.chapter_listbox.grid(row=0, column=0, sticky="nsew")

    # 章节内容标签
    content_label = ctk.CTkLabel(self.chapters_tab, text=chinese_labels["chapter_content_display"], font=("Microsoft YaHei", 14, "bold"))
    content_label.grid(row=2, column=0, padx=10, pady=(10, 5), sticky="w")

    # 章节内容文本框
    self.chapter_content_text = ctk.CTkTextbox(self.chapters_tab, wrap="word")
    TextWidgetContextMenu(self.chapter_content_text)
    self.chapter_content_text.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")

    # 按钮框架
    btn_frame = ctk.CTkFrame(self.chapters_tab)
    btn_frame.grid(row=4, column=0, padx=10, pady=5, sticky="ew")
    btn_frame.columnconfigure((0, 1, 2, 3, 4, 5), weight=1)  # 增加一列权重

    # 刷新列表按钮
    refresh_btn = ctk.CTkButton(btn_frame, text=chinese_labels["refresh_chapter_list"], command=self.refresh_chapters_list, font=("Microsoft YaHei", 12))
    refresh_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

    # 独立刷新按钮（重复添加以提高可见性）
    refresh_btn2 = ctk.CTkButton(btn_frame, text="🔄 刷新", command=self.refresh_chapters_list, font=("Microsoft YaHei", 12))
    refresh_btn2.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    # 上一章按钮
    prev_btn = ctk.CTkButton(btn_frame, text=chinese_labels["prev_chapter"], command=self.prev_chapter, font=("Microsoft YaHei", 12))
    prev_btn.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

    # 下一章按钮
    next_btn = ctk.CTkButton(btn_frame, text=chinese_labels["next_chapter"], command=self.next_chapter, font=("Microsoft YaHei", 12))
    next_btn.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

    # 保存当前章节按钮
    save_btn = ctk.CTkButton(btn_frame, text=chinese_labels["save_current_chapter"], command=self.save_current_chapter, font=("Microsoft YaHei", 12))
    save_btn.grid(row=0, column=4, padx=5, pady=5, sticky="ew")

def refresh_chapters_list(self):
    """刷新章节列表"""
    # 清空现有章节按钮
    for widget in self.chapter_listbox.winfo_children():
        widget.destroy()
        
    # 获取章节文件路径
    filepath = self.filepath_var.get().strip()
    if not filepath:
        self.log("请先设置保存路径。")
        return
        
    chapters_dir = os.path.join(filepath, "Chapters")
    if not os.path.exists(chapters_dir):
        self.log("章节目录不存在。")
        return
        
    # 获取章节文件列表
    chapter_files = []
    try:
        for filename in os.listdir(chapters_dir):
            if filename.startswith("chapter_") and filename.endswith(".txt"):
                chapter_files.append(filename)
        chapter_files.sort()  # 按文件名排序
        
        # 创建章节按钮
        for i, filename in enumerate(chapter_files):
            chapter_num = filename.replace("chapter_", "").replace(".txt", "")
            btn = ctk.CTkButton(
                self.chapter_listbox,
                text=f"第{chapter_num}章",
                command=lambda f=filename: self.on_chapter_selected(f),
                font=("Microsoft YaHei", 12),
                width=120
            )
            btn.grid(row=i, column=0, padx=5, pady=2, sticky="ew")
            
        self.log(f"已刷新章节列表，共找到 {len(chapter_files)} 个章节。")
    except Exception as e:
        self.log(f"刷新章节列表时出错: {str(e)}")

def on_chapter_selected(self, filename):
    """当选中章节时加载内容"""
    try:
        filepath = self.filepath_var.get().strip()
        if not filepath:
            self.log("请先设置保存路径。")
            return
            
        chapter_path = os.path.join(filepath, "Chapters", filename)
        with open(chapter_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        self.chapter_content_text.delete("0.0", "end")
        self.chapter_content_text.insert("0.0", content)
        self.log(f"已加载章节: {filename}")
    except Exception as e:
        self.log(f"加载章节内容时出错: {str(e)}")

def load_chapter_content(self, chapter_num):
    """加载指定章节内容"""
    try:
        filepath = self.filepath_var.get().strip()
        if not filepath:
            self.log("请先设置保存路径。")
            return
            
        chapter_path = os.path.join(filepath, "Chapters", f"chapter_{chapter_num}.txt")
        with open(chapter_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        self.chapter_content_text.delete("0.0", "end")
        self.chapter_content_text.insert("0.0", content)
        self.log(f"已加载第{chapter_num}章内容。")
    except FileNotFoundError:
        self.log(f"未找到第{chapter_num}章文件。")
    except Exception as e:
        self.log(f"加载章节内容时出错: {str(e)}")

def save_current_chapter(self):
    """保存当前章节内容"""
    try:
        # 从章节内容文本框获取内容
        content = self.chapter_content_text.get("0.0", "end").strip()
        
        # 获取当前章节号
        chapter_num = self.chapter_num_var.get().strip()
        if not chapter_num:
            self.log("请先设置章节号。")
            return
            
        # 获取保存路径
        filepath = self.filepath_var.get().strip()
        if not filepath:
            self.log("请先设置保存路径。")
            return
            
        # 创建章节目录
        chapters_dir = os.path.join(filepath, "Chapters")
        os.makedirs(chapters_dir, exist_ok=True)
        
        # 保存文件
        chapter_path = os.path.join(chapters_dir, f"chapter_{chapter_num}.txt")
        with open(chapter_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        self.log(f"第{chapter_num}章已保存。")
    except Exception as e:
        self.log(f"保存章节时出错: {str(e)}")

def prev_chapter(self):
    """上一章"""
    try:
        current_chapter = int(self.chapter_num_var.get().strip())
        if current_chapter > 1:
            new_chapter = current_chapter - 1
            self.chapter_num_var.set(str(new_chapter))
            self.load_chapter_content(new_chapter)
        else:
            self.log("已经是第一章了。")
    except ValueError:
        self.log("章节号格式不正确。")
    except Exception as e:
        self.log(f"切换章节时出错: {str(e)}")

def next_chapter(self):
    """下一章"""
    try:
        current_chapter = int(self.chapter_num_var.get().strip())
        new_chapter = current_chapter + 1
        self.chapter_num_var.set(str(new_chapter))
        self.load_chapter_content(new_chapter)
    except ValueError:
        self.log("章节号格式不正确。")
    except Exception as e:
        self.log(f"切换章节时出错: {str(e)}")