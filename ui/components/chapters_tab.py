"""
现代化章节管理标签页组件 - AI小说生成器的章节管理界面
包含章节列表、内容编辑、导航功能等
"""

import logging
import os
from typing import Dict, Any, Optional, Callable, List
import customtkinter as ctk
from tkinter import messagebox
from utils import read_file, save_string_to_txt

logger = logging.getLogger(__name__)


class ChaptersTab(ctk.CTkFrame):
    """
    现代化章节管理标签页组件

    功能：
    - 章节列表管理
    - 章节内容编辑
    - 章节导航
    - 章节状态跟踪
    - 章节导出导入
    """

    def __init__(self, parent: ctk.CTkFrame, theme_manager, state_manager=None, **kwargs):
        """
        初始化章节管理标签页

        Args:
            parent: 父组件
            theme_manager: 主题管理器
            state_manager: 状态管理器
            **kwargs: 其他参数
        """
        # 初始化CustomTkinter Frame
        super().__init__(parent, **kwargs)

        # 存储管理器引用
        self.theme_manager = theme_manager
        self.state_manager = state_manager

        # 章节数据
        self.chapters = []
        self.current_chapter = None
        self.current_chapter_index = 0

        # 组件引用
        self.chapters_listbox = None
        self.chapter_content_text = None
        self.chapter_info_text = None

        # 回调函数
        self.chapter_changed_callback = None

        # 初始化组件
        self._create_chapters_layout()
        self._load_chapters_data()

        logger.debug("ChaptersTab 组件初始化完成")

    def _create_chapters_layout(self):
        """创建章节管理布局"""
        # 配置主框架
        self.configure(
            corner_radius=8,
            fg_color="transparent"
        )

        # 创建左右分栏布局
        self.left_panel = ctk.CTkFrame(self, fg_color="#2A2A2A")
        self.left_panel.pack(side="left", fill="y", padx=(10, 5), pady=10)
        self.left_panel.configure(width=300)

        self.right_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.right_panel.pack(side="right", fill="both", expand=True, padx=(5, 10), pady=10)

        # 构建左侧面板 - 章节列表
        self._build_chapter_list_panel()

        # 构建右侧面板 - 章节内容
        self._build_chapter_content_panel()

    def _build_chapter_list_panel(self):
        """构建章节列表面板"""
        # 标题
        title_label = ctk.CTkLabel(
            self.left_panel,
            text="章节列表",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(10, 15))

        # 章节导航按钮
        nav_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        nav_frame.pack(fill="x", padx=10, pady=(0, 10))

        prev_button = ctk.CTkButton(
            nav_frame,
            text="◀ 上一章",
            command=self._prev_chapter,
            width=100
        )
        prev_button.pack(side="left", padx=(0, 5))

        next_button = ctk.CTkButton(
            nav_frame,
            text="下一章 ▶",
            command=self._next_chapter,
            width=100
        )
        next_button.pack(side="right", padx=(5, 0))

        # 当前章节指示
        self.current_chapter_label = ctk.CTkLabel(
            nav_frame,
            text="第1章",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.current_chapter_label.pack(side="left", expand=True)

        # 搜索框
        search_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        search_frame.pack(fill="x", padx=10, pady=(0, 10))

        search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="搜索章节..."
        )
        search_entry.pack(fill="x")
        search_entry.bind("<KeyRelease>", self._on_chapter_search)

        # 章节列表
        list_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # 使用ScrollableFrame来显示章节列表
        self.chapters_scroll = ctk.CTkScrollableFrame(
            list_frame,
            height=350
        )
        self.chapters_scroll.pack(fill="both", expand=True)

        # 添加新章节按钮
        add_button = ctk.CTkButton(
            self.left_panel,
            text="+ 添加新章节",
            command=self._add_new_chapter,
            fg_color="#2E7D32",
            hover_color="#388E3C",
            height=40
        )
        add_button.pack(fill="x", padx=10, pady=(0, 10))

    def _build_chapter_content_panel(self):
        """构建章节内容面板"""
        # 创建标签页视图
        self.content_tabview = ctk.CTkTabview(
            self.right_panel,
            segmented_button_fg_color="#2A2A2A",
            segmented_button_selected_color="#404040",
            segmented_button_unselected_color="#1E1E1E"
        )
        self.content_tabview.pack(fill="both", expand=True)

        # 添加标签页
        self.content_tab = self.content_tabview.add("章节内容")
        self.info_tab = self.content_tabview.add("章节信息")
        self.summary_tab = self.content_tabview.add("章节摘要")

        # 构建各个标签页内容
        self._build_chapter_content_tab()
        self._build_chapter_info_tab()
        self._build_chapter_summary_tab()

        # 底部操作按钮
        self._create_action_buttons()

    def _build_chapter_content_tab(self):
        """构建章节内容标签页"""
        # 主容器
        content_frame = ctk.CTkFrame(self.content_tab, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 章节标题
        title_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 10))

        title_label = ctk.CTkLabel(
            title_frame,
            text="章节标题:",
            width=100,
            anchor="w"
        )
        title_label.pack(side="left", padx=(0, 10))

        self.chapter_title_entry = ctk.CTkEntry(
            title_frame,
            placeholder_text="输入章节标题"
        )
        self.chapter_title_entry.pack(side="left", fill="x", expand=True)

        # 字数统计
        self.word_count_label = ctk.CTkLabel(
            content_frame,
            text="字数: 0",
            text_color="gray"
        )
        self.word_count_label.pack(anchor="w", pady=(0, 5))

        # 内容文本框
        self.chapter_content_text = ctk.CTkTextbox(
            content_frame,
            height=400,
            wrap="word"
        )
        self.chapter_content_text.pack(fill="both", expand=True, pady=(0, 10))

        # 绑定文本变化事件
        self.chapter_content_text.bind("<KeyRelease>", self._update_word_count)

        # 内容更新时间
        self.update_time_label = ctk.CTkLabel(
            content_frame,
            text="最后更新: --",
            text_color="gray"
        )
        self.update_time_label.pack(fill="x")

    def _build_chapter_info_tab(self):
        """构建章节信息标签页"""
        # 主容器
        info_frame = ctk.CTkFrame(self.info_tab, fg_color="transparent")
        info_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 章节编号
        number_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        number_frame.pack(fill="x", pady=5)

        number_label = ctk.CTkLabel(
            number_frame,
            text="章节编号:",
            width=100,
            anchor="w"
        )
        number_label.pack(side="left", padx=(0, 10))

        self.chapter_number_entry = ctk.CTkEntry(
            number_frame,
            placeholder_text="例如: 第1章"
        )
        self.chapter_number_entry.pack(side="left", fill="x", expand=True)

        # 章节类型
        type_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        type_frame.pack(fill="x", pady=5)

        type_label = ctk.CTkLabel(
            type_frame,
            text="章节类型:",
            width=100,
            anchor="w"
        )
        type_label.pack(side="left", padx=(0, 10))

        self.chapter_type_var = ctk.StringVar(value="正文")
        self.chapter_type_combo = ctk.CTkComboBox(
            type_frame,
            variable=self.chapter_type_var,
            values=["正文", "序章", "尾声", "番外", "回忆"]
        )
        self.chapter_type_combo.pack(side="left", fill="x", expand=True)

        # 章节状态
        status_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        status_frame.pack(fill="x", pady=5)

        status_label = ctk.CTkLabel(
            status_frame,
            text="章节状态:",
            width=100,
            anchor="w"
        )
        status_label.pack(side="left", padx=(0, 10))

        self.chapter_status_var = ctk.StringVar(value="草稿")
        self.chapter_status_combo = ctk.CTkComboBox(
            status_frame,
            variable=self.chapter_status_var,
            values=["草稿", "初稿", "修改中", "已完成", "已发布"]
        )
        self.chapter_status_combo.pack(side="left", fill="x", expand=True)

        # 章节大纲
        outline_label = ctk.CTkLabel(
            info_frame,
            text="章节大纲:",
            anchor="w"
        )
        outline_label.pack(fill="x", pady=(15, 5))

        self.chapter_outline_text = ctk.CTkTextbox(
            info_frame,
            height=150
        )
        self.chapter_outline_text.pack(fill="x", pady=(0, 10))

        # 章节备注
        notes_label = ctk.CTkLabel(
            info_frame,
            text="章节备注:",
            anchor="w"
        )
        notes_label.pack(fill="x", pady=(10, 5))

        self.chapter_notes_text = ctk.CTkTextbox(
            info_frame,
            height=100
        )
        self.chapter_notes_text.pack(fill="x")

    def _build_chapter_summary_tab(self):
        """构建章节摘要标签页"""
        # 主容器
        summary_frame = ctk.CTkFrame(self.summary_tab, fg_color="transparent")
        summary_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 摘要标签
        summary_label = ctk.CTkLabel(
            summary_frame,
            text="章节摘要",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        summary_label.pack(fill="x", pady=(0, 10))

        # 自动生成摘要按钮
        generate_button = ctk.CTkButton(
            summary_frame,
            text="生成摘要",
            command=self._generate_summary,
            fg_color="#FF9800",
            hover_color="#F57C00"
        )
        generate_button.pack(pady=(0, 10))

        # 摘要文本框
        self.chapter_summary_text = ctk.CTkTextbox(
            summary_frame,
            height=400
        )
        self.chapter_summary_text.pack(fill="both", expand=True)

    def _create_action_buttons(self):
        """创建操作按钮"""
        button_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        button_frame.pack(fill="x", padx=10, pady=(0, 10))

        # 保存当前章节按钮
        save_button = ctk.CTkButton(
            button_frame,
            text="保存章节",
            command=self._save_current_chapter,
            fg_color="#1976D2",
            hover_color="#2196F3",
            height=40
        )
        save_button.pack(side="left", fill="x", expand=True, padx=(0, 5))

        # 删除章节按钮
        delete_button = ctk.CTkButton(
            button_frame,
            text="删除章节",
            command=self._delete_current_chapter,
            fg_color="#D32F2F",
            hover_color="#F44336",
            height=40
        )
        delete_button.pack(side="left", fill="x", expand=True, padx=(5, 5))

        # 导出按钮
        export_button = ctk.CTkButton(
            button_frame,
            text="导出",
            command=self._export_chapter,
            fg_color="#388E3C",
            hover_color="#4CAF50",
            height=40
        )
        export_button.pack(side="left", fill="x", expand=True, padx=(5, 0))

    def _load_chapters_data(self):
        """加载章节数据"""
        try:
            # 尝试从文件加载章节目录
            content = read_file("Novel_directory.txt")
            if content:
                self._parse_chapter_data(content)
            else:
                self._create_default_chapters()

        except FileNotFoundError:
            logger.info("未找到章节目录文件，创建默认章节")
            self._create_default_chapters()
        except Exception as e:
            logger.error(f"加载章节数据失败: {e}")
            self._create_default_chapters()

    def _parse_chapter_data(self, content: str):
        """解析章节数据"""
        # 这里实现章节数据解析逻辑
        # 暂时创建示例数据
        self._create_sample_chapters()

    def _create_default_chapters(self):
        """创建默认章节"""
        self._create_sample_chapters()

    def _create_sample_chapters(self):
        """创建示例章节"""
        sample_chapters = [
            {
                "number": "第1章",
                "title": "序章：开始",
                "type": "序章",
                "status": "草稿",
                "content": "这是第一章的内容，故事的开始...",
                "outline": "介绍主角和背景",
                "notes": "需要完善细节",
                "summary": ""
            },
            {
                "number": "第2章",
                "title": "初遇",
                "type": "正文",
                "status": "草稿",
                "content": "主角遇到了重要角色...",
                "outline": "角色相遇和初步交流",
                "notes": "",
                "summary": ""
            },
            {
                "number": "第3章",
                "title": "冒险开始",
                "type": "正文",
                "status": "草稿",
                "content": "真正的冒险从这里开始...",
                "outline": "主要情节的展开",
                "notes": "",
                "summary": ""
            }
        ]

        for chapter_data in sample_chapters:
            self._add_chapter_to_list(chapter_data)

        # 选择第一个章节
        if self.chapters:
            self._select_chapter(self.chapters[0])

    def _add_chapter_to_list(self, chapter_data: Dict[str, Any]):
        """添加章节到列表"""
        self.chapters.append(chapter_data)
        self._create_chapter_item(chapter_data)

    def _create_chapter_item(self, chapter_data: Dict[str, Any]):
        """创建章节列表项"""
        # 创建章节项框架
        item_frame = ctk.CTkFrame(
            self.chapters_scroll,
            fg_color="#333333",
            corner_radius=8
        )
        item_frame.pack(fill="x", padx=5, pady=3)

        # 章节编号
        number_label = ctk.CTkLabel(
            item_frame,
            text=chapter_data["number"],
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        number_label.pack(fill="x", padx=10, pady=(8, 2))

        # 章节标题
        title_label = ctk.CTkLabel(
            item_frame,
            text=chapter_data["title"],
            font=ctk.CTkFont(size=13),
            anchor="w"
        )
        title_label.pack(fill="x", padx=10, pady=(0, 2))

        # 章节状态
        status_label = ctk.CTkLabel(
            item_frame,
            text=chapter_data["status"],
            font=ctk.CTkFont(size=11),
            text_color="#4CAF50",
            anchor="w"
        )
        status_label.pack(fill="x", padx=10, pady=(0, 2))

        # 字数统计
        word_count = len(chapter_data.get("content", ""))
        word_count_label = ctk.CTkLabel(
            item_frame,
            text=f"字数: {word_count}",
            font=ctk.CTkFont(size=10),
            text_color="gray",
            anchor="w"
        )
        word_count_label.pack(fill="x", padx=10, pady=(0, 8))

        # 绑定点击事件
        def on_item_click(event=None):
            self._select_chapter(chapter_data)

        item_frame.bind("<Button-1>", on_item_click)
        number_label.bind("<Button-1>", on_item_click)
        title_label.bind("<Button-1>", on_item_click)
        status_label.bind("<Button-1>", on_item_click)
        word_count_label.bind("<Button-1>", on_item_click)

        # 存储框架引用
        chapter_data["frame"] = item_frame

    def _select_chapter(self, chapter_data: Dict[str, Any]):
        """选择章节"""
        self.current_chapter = chapter_data
        self.current_chapter_index = self.chapters.index(chapter_data)

        # 更新章节信息
        self.chapter_number_entry.delete(0, "end")
        self.chapter_number_entry.insert(0, chapter_data["number"])

        self.chapter_title_entry.delete(0, "end")
        self.chapter_title_entry.insert(0, chapter_data["title"])

        self.chapter_type_var.set(chapter_data["type"])
        self.chapter_status_var.set(chapter_data["status"])

        self.chapter_content_text.delete("1.0", "end")
        self.chapter_content_text.insert("1.0", chapter_data.get("content", ""))

        self.chapter_outline_text.delete("1.0", "end")
        self.chapter_outline_text.insert("1.0", chapter_data.get("outline", ""))

        self.chapter_notes_text.delete("1.0", "end")
        self.chapter_notes_text.insert("1.0", chapter_data.get("notes", ""))

        self.chapter_summary_text.delete("1.0", "end")
        self.chapter_summary_text.insert("1.0", chapter_data.get("summary", ""))

        # 更新当前章节指示
        self.current_chapter_label.configure(text=chapter_data["number"])

        # 更新字数统计
        self._update_word_count()

        # 高亮选中的章节项
        self._highlight_selected_chapter(chapter_data)

        # 触发回调
        if self.chapter_changed_callback:
            self.chapter_changed_callback(chapter_data)

    def _highlight_selected_chapter(self, selected_chapter: Dict[str, Any]):
        """高亮选中的章节项"""
        for chapter in self.chapters:
            if "frame" in chapter:
                if chapter == selected_chapter:
                    chapter["frame"].configure(fg_color="#404040")
                else:
                    chapter["frame"].configure(fg_color="#333333")

    def _prev_chapter(self):
        """上一章"""
        if self.current_chapter_index > 0:
            prev_chapter = self.chapters[self.current_chapter_index - 1]
            self._select_chapter(prev_chapter)

    def _next_chapter(self):
        """下一章"""
        if self.current_chapter_index < len(self.chapters) - 1:
            next_chapter = self.chapters[self.current_chapter_index + 1]
            self._select_chapter(next_chapter)

    def _add_new_chapter(self):
        """添加新章节"""
        # 创建新章节数据
        chapter_num = len(self.chapters) + 1
        new_chapter = {
            "number": f"第{chapter_num}章",
            "title": f"新章节 {chapter_num}",
            "type": "正文",
            "status": "草稿",
            "content": "",
            "outline": "",
            "notes": "",
            "summary": ""
        }

        self._add_chapter_to_list(new_chapter)
        self._select_chapter(new_chapter)

        # 聚焦到标题输入框
        self.chapter_title_entry.focus_set()
        self.chapter_title_entry.select_range(0, "end")

    def _save_current_chapter(self):
        """保存当前章节"""
        if not self.current_chapter:
            messagebox.showwarning("警告", "请先选择一个章节")
            return

        try:
            # 更新章节数据
            self.current_chapter.update({
                "number": self.chapter_number_entry.get(),
                "title": self.chapter_title_entry.get(),
                "type": self.chapter_type_var.get(),
                "status": self.chapter_status_var.get(),
                "content": self.chapter_content_text.get("1.0", "end-1c"),
                "outline": self.chapter_outline_text.get("1.0", "end-1c"),
                "notes": self.chapter_notes_text.get("1.0", "end-1c"),
                "summary": self.chapter_summary_text.get("1.0", "end-1c")
            })

            # 更新列表显示
            self._update_chapter_display(self.current_chapter)

            # 保存到文件
            self._save_chapters_to_file()

            messagebox.showinfo("成功", "章节保存成功！")

        except Exception as e:
            logger.error(f"保存章节失败: {e}")
            messagebox.showerror("错误", f"保存章节失败: {e}")

    def _delete_current_chapter(self):
        """删除当前章节"""
        if not self.current_chapter:
            messagebox.showwarning("警告", "请先选择一个章节")
            return

        if messagebox.askyesno("确认", f"确定要删除章节 '{self.current_chapter['title']}' 吗？"):
            try:
                # 从列表中移除
                self.chapters.remove(self.current_chapter)

                # 销毁UI框架
                if "frame" in self.current_chapter:
                    self.current_chapter["frame"].destroy()

                # 重新编号章节
                self._renumber_chapters()

                # 选择其他章节
                if self.chapters:
                    if self.current_chapter_index < len(self.chapters):
                        new_index = self.current_chapter_index
                    else:
                        new_index = len(self.chapters) - 1
                    self._select_chapter(self.chapters[new_index])
                else:
                    self.current_chapter = None
                    self._clear_chapter_form()

                # 保存到文件
                self._save_chapters_to_file()

                messagebox.showinfo("成功", "章节删除成功！")

            except Exception as e:
                logger.error(f"删除章节失败: {e}")
                messagebox.showerror("错误", f"删除章节失败: {e}")

    def _update_chapter_display(self, chapter_data: Dict[str, Any]):
        """更新章节显示"""
        if "frame" not in chapter_data:
            return

        frame = chapter_data["frame"]
        widgets = frame.winfo_children()

        # 更新编号
        if widgets:
            widgets[0].configure(text=chapter_data["number"])

        # 更新标题
        if len(widgets) > 1:
            widgets[1].configure(text=chapter_data["title"])

        # 更新状态
        if len(widgets) > 2:
            widgets[2].configure(text=chapter_data["status"])

        # 更新字数
        if len(widgets) > 3:
            word_count = len(chapter_data.get("content", ""))
            widgets[3].configure(text=f"字数: {word_count}")

    def _renumber_chapters(self):
        """重新编号章节"""
        for i, chapter in enumerate(self.chapters):
            old_number = chapter["number"]
            new_number = f"第{i+1}章"

            if old_number != new_number:
                chapter["number"] = new_number
                if "frame" in chapter:
                    widgets = chapter["frame"].winfo_children()
                    if widgets:
                        widgets[0].configure(text=new_number)

    def _clear_chapter_form(self):
        """清空章节表单"""
        self.chapter_number_entry.delete(0, "end")
        self.chapter_title_entry.delete(0, "end")
        self.chapter_type_var.set("正文")
        self.chapter_status_var.set("草稿")
        self.chapter_content_text.delete("1.0", "end")
        self.chapter_outline_text.delete("1.0", "end")
        self.chapter_notes_text.delete("1.0", "end")
        self.chapter_summary_text.delete("1.0", "end")
        self.current_chapter_label.configure(text="无章节")

    def _save_chapters_to_file(self):
        """保存章节到文件"""
        try:
            # 生成章节目录
            content = "小说章节目录\n\n"
            for chapter in self.chapters:
                content += f"{chapter['number']}: {chapter['title']}\n"
                content += f"状态: {chapter['status']}\n"
                content += f"大纲: {chapter.get('outline', '')}\n"
                content += "-" * 50 + "\n\n"

            save_string_to_txt(content, "Novel_directory.txt")

            # 保存各章节内容到单独文件
            for chapter in self.chapters:
                chapter_filename = f"chapter_{chapter['number'].replace('章', '')}.txt"
                chapter_content = f"{chapter['number']}: {chapter['title']}\n\n"
                chapter_content += f"状态: {chapter['status']}\n"
                chapter_content += f"大纲: {chapter.get('outline', '')}\n\n"
                chapter_content += f"内容:\n{chapter.get('content', '')}\n\n"
                chapter_content += f"备注: {chapter.get('notes', '')}\n"

                save_string_to_txt(chapter_content, chapter_filename)

        except Exception as e:
            logger.error(f"保存章节文件失败: {e}")

    def _update_word_count(self, event=None):
        """更新字数统计"""
        content = self.chapter_content_text.get("1.0", "end-1c")
        word_count = len(content)
        self.word_count_label.configure(text=f"字数: {word_count}")

    def _on_chapter_search(self, event):
        """章节搜索处理"""
        search_text = event.widget.get().lower()

        for chapter in self.chapters:
            if "frame" in chapter:
                # 检查是否匹配搜索
                title_match = search_text in chapter["title"].lower()
                content_match = search_text in chapter.get("content", "").lower()
                outline_match = search_text in chapter.get("outline", "").lower()

                if title_match or content_match or outline_match:
                    chapter["frame"].pack(fill="x", padx=5, pady=3)
                else:
                    chapter["frame"].pack_forget()

    def _generate_summary(self):
        """生成章节摘要"""
        if not self.current_chapter:
            messagebox.showwarning("警告", "请先选择一个章节")
            return

        content = self.chapter_content_text.get("1.0", "end-1c")
        if not content:
            messagebox.showwarning("警告", "章节内容为空")
            return

        # 简单的摘要生成（取前200字符）
        summary = content[:200] + "..." if len(content) > 200 else content

        self.chapter_summary_text.delete("1.0", "end")
        self.chapter_summary_text.insert("1.0", summary)

        messagebox.showinfo("成功", "摘要生成成功！")

    def _export_chapter(self):
        """导出章节"""
        if not self.current_chapter:
            messagebox.showwarning("警告", "请先选择一个章节")
            return

        try:
            # 生成导出内容
            content = f"{self.current_chapter['number']}: {self.current_chapter['title']}\n"
            content += f"状态: {self.current_chapter['status']}\n"
            content += f"大纲: {self.current_chapter.get('outline', '')}\n\n"
            content += f"内容:\n{self.current_chapter.get('content', '')}\n\n"
            content += f"备注: {self.current_chapter.get('notes', '')}\n"

            # 保存到文件
            filename = f"{self.current_chapter['number']}_{self.current_chapter['title']}.txt"
            save_string_to_txt(content, filename)

            messagebox.showinfo("成功", f"章节已导出到 {filename}")

        except Exception as e:
            logger.error(f"导出章节失败: {e}")
            messagebox.showerror("错误", f"导出章节失败: {e}")

    def set_chapter_changed_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """设置章节变化回调函数"""
        self.chapter_changed_callback = callback

    def get_current_chapter(self) -> Optional[Dict[str, Any]]:
        """获取当前选中的章节"""
        return self.current_chapter

    def get_all_chapters(self) -> List[Dict[str, Any]]:
        """获取所有章节"""
        return self.chapters

    def apply_theme_style(self, theme_data: Dict[str, Any]):
        """应用主题样式"""
        try:
            colors = theme_data.get('colors', {})

            # 更新标签页样式
            if hasattr(self, 'content_tabview'):
                self.content_tabview.configure(
                    segmented_button_fg_color=colors.get('surface', '#2A2A2A'),
                    segmented_button_selected_color=colors.get('primary', '#404040'),
                    segmented_button_unselected_color=colors.get('background', '#1E1E1E')
                )

        except Exception as e:
            logger.error(f"应用主题到章节标签页失败: {e}")

    def get_chapters_info(self) -> Dict[str, Any]:
        """获取章节标签页信息"""
        return {
            'total_chapters': len(self.chapters),
            'current_chapter': self.current_chapter['title'] if self.current_chapter else None,
            'current_index': self.current_chapter_index,
            'has_callback': self.chapter_changed_callback is not None
        }