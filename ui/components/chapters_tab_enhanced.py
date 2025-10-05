# ui/components/chapters_tab_enhanced.py
# -*- coding: utf-8 -*-
"""
增强的章节管理标签页组件
集成统一刷新按钮功能，提供手动刷新能力
"""

import logging
import os
import json
from typing import Dict, Any, Optional, Callable, List
import customtkinter as ctk
from tkinter import messagebox
from utils import read_file, save_string_to_txt

# 导入刷新按钮组件
try:
    from .refresh_button import RefreshableTabFrame
    REFRESH_BUTTON_AVAILABLE = True
except ImportError:
    REFRESH_BUTTON_AVAILABLE = False

logger = logging.getLogger(__name__)


class ChaptersTabEnhanced(ctk.CTkFrame):
    """
    增强的章节管理标签页组件

    新增功能：
    - 统一刷新按钮
    - 手动章节更新
    - 文件变化检测
    - 章节状态跟踪
    """

    def __init__(self, parent: ctk.CTkFrame, theme_manager, state_manager=None, main_window=None, **kwargs):
        """
        初始化增强章节管理标签页

        Args:
            parent: 父组件
            theme_manager: 主题管理器
            state_manager: 状态管理器
            main_window: 主窗口引用
            **kwargs: 其他参数
        """
        # 初始化CustomTkinter Frame
        super().__init__(parent, **kwargs)

        # 存储管理器引用
        self.theme_manager = theme_manager
        self.state_manager = state_manager
        self.main_window = main_window

        # 章节数据
        self.chapters = []
        self.current_chapter = None
        self.filtered_chapters = []

        # 组件引用
        self.chapters_list_frame = None
        self.chapter_detail_frame = None
        self.search_entry = None
        self.refreshable_frame = None

        # 文件路径
        self.chapter_file_path = None
        self.last_file_modified = None

        # 初始化组件
        self._create_enhanced_layout()
        self._load_chapters_data()

        logger.debug("ChaptersTabEnhanced 组件初始化完成")

    def _create_enhanced_layout(self):
        """创建增强的布局"""
        # 配置主框架
        self.configure(
            corner_radius=8,
            fg_color="transparent"
        )

        # 使用可刷新框架
        if REFRESH_BUTTON_AVAILABLE:
            self.refreshable_frame = RefreshableTabFrame(
                self,
                "章节管理",
                self._refresh_chapters
            )
            self.refreshable_frame.pack(fill="both", expand=True)

            # 获取内容框架
            content_frame = self.refreshable_frame.get_content_frame()
        else:
            # 回退到传统布局
            self._create_traditional_layout()
            return

        # 创建左右分栏
        self._create_split_layout(content_frame)

    def _create_traditional_layout(self):
        """创建传统布局（当刷新按钮不可用时）"""
        # 创建标题栏
        title_frame = ctk.CTkFrame(self, fg_color="#2A2A2A", height=50)
        title_frame.pack(fill="x", padx=10, pady=10)
        title_frame.pack_propagate(False)

        # 标题
        title_label = ctk.CTkLabel(
            title_frame,
            text="章节管理",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(side="left", padx=20, pady=15)

        # 刷新按钮
        refresh_button = ctk.CTkButton(
            title_frame,
            text="刷新",
            command=self._refresh_chapters,
            width=80,
            height=35,
            fg_color="#2196F3",
            hover_color="#1976D2"
        )
        refresh_button.pack(side="right", padx=20, pady=7)

        # 导入按钮
        import_button = ctk.CTkButton(
            title_frame,
            text="导入",
            command=self._import_chapters,
            width=80,
            height=35
        )
        import_button.pack(side="right", padx=5, pady=7)

        # 导出按钮
        export_button = ctk.CTkButton(
            title_frame,
            text="导出",
            command=self._export_chapters,
            width=80,
            height=35
        )
        export_button.pack(side="right", padx=5, pady=7)

        # 创建主内容区域
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # 创建左右分栏
        self._create_split_layout(content_frame)

    def _create_split_layout(self, parent_frame=None):
        """创建左右分栏布局"""
        if parent_frame is None:
            parent_frame = self.get_content_frame()

        # 左侧面板 - 章节列表
        self.left_panel = ctk.CTkFrame(parent_frame, fg_color="#2A2A2A")
        self.left_panel.pack(side="left", fill="y", padx=(0, 5))
        self.left_panel.configure(width=350)

        # 右侧面板 - 章节详情
        self.right_panel = ctk.CTkFrame(parent_frame, fg_color="transparent")
        self.right_panel.pack(side="right", fill="both", expand=True, padx=(5, 0))

        # 构建面板内容
        self._build_chapter_list_panel()
        self._build_chapter_detail_panel()

    def get_content_frame(self):
        """获取内容框架"""
        if hasattr(self, 'refreshable_frame') and self.refreshable_frame:
            return self.refreshable_frame.get_content_frame()
        elif hasattr(self, 'content_frame'):
            return self.content_frame
        else:
            # 如果都不存在，返回自身
            return self

    def _build_chapter_list_panel(self):
        """构建章节列表面板"""
        # 搜索框
        search_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        search_frame.pack(fill="x", padx=15, pady=15)

        search_label = ctk.CTkLabel(
            search_frame,
            text="搜索章节:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        search_label.pack(anchor="w", pady=(0, 5))

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="输入章节标题...",
            height=35
        )
        self.search_entry.pack(fill="x")
        self.search_entry.bind("<KeyRelease>", self._on_chapter_search)

        # 章节列表
        list_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        list_frame.pack(fill="both", expand=True, padx=15, pady=10)

        # 使用ScrollableFrame
        self.chapters_scroll = ctk.CTkScrollableFrame(
            list_frame,
            height=500,
            fg_color="#333333"
        )
        self.chapters_scroll.pack(fill="both", expand=True)

        # 添加新章节按钮
        button_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        button_frame.pack(fill="x", padx=15, pady=15)

        self.add_button = ctk.CTkButton(
            button_frame,
            text="+ 添加新章节",
            command=self._add_new_chapter,
            fg_color="#2E7D32",
            hover_color="#388E3C",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.add_button.pack(fill="x", pady=(0, 10))

    def _build_chapter_detail_panel(self):
        """构建章节详情面板"""
        if not self.current_chapter:
            # 显示空状态
            self._show_empty_state()
            return

        # 创建标签页视图
        self.detail_tabview = ctk.CTkTabview(
            self.right_panel,
            segmented_button_fg_color="#2A2A2A",
            segmented_button_selected_color="#3B82F6",
            text_color="#FFFFFF",
            text_color_disabled="#888888"
        )
        self.detail_tabview.pack(fill="both", expand=True, padx=15, pady=15)

        # 添加标签页
        self.detail_tabview.add("基本信息")
        self.detail_tabview.add("章节内容")
        self.detail_tabview.add("编辑笔记")
        self.detail_tabview.add("状态跟踪")

        # 构建各标签页内容
        self._build_basic_info_tab()
        self._build_content_tab()
        self._build_notes_tab()
        self._build_state_tab()

        # 操作按钮
        self._build_action_buttons()

    def _show_empty_state(self):
        """显示空状态"""
        empty_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        empty_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # 空状态图标和文字
        empty_label = ctk.CTkLabel(
            empty_frame,
            text="📖\n\n请选择或创建一个章节\n\n点击左侧的\"添加新章节\"按钮开始",
            font=ctk.CTkFont(size=16),
            text_color="#888888"
        )
        empty_label.pack(expand=True)

    def _build_basic_info_tab(self):
        """构建基本信息标签页"""
        tab = self.detail_tabview.tab("基本信息")

        # 章节标题
        title_frame = ctk.CTkFrame(tab, fg_color="transparent")
        title_frame.pack(fill="x", pady=10)

        title_label = ctk.CTkLabel(
            title_frame,
            text="章节标题:",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=100
        )
        title_label.pack(side="left", padx=(0, 10))

        self.title_entry = ctk.CTkEntry(
            title_frame,
            height=35,
            font=ctk.CTkFont(size=12)
        )
        self.title_entry.pack(side="left", fill="x", expand=True)

        # 章节序号
        number_frame = ctk.CTkFrame(tab, fg_color="transparent")
        number_frame.pack(fill="x", pady=10)

        number_label = ctk.CTkLabel(
            number_frame,
            text="章节序号:",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=100
        )
        number_label.pack(side="left", padx=(0, 10))

        self.number_entry = ctk.CTkEntry(
            number_frame,
            height=35,
            font=ctk.CTkFont(size=12)
        )
        self.number_entry.pack(side="left", fill="x", expand=True)

        # 章节摘要
        summary_frame = ctk.CTkFrame(tab, fg_color="transparent")
        summary_frame.pack(fill="x", pady=10)

        summary_label = ctk.CTkLabel(
            summary_frame,
            text="章节摘要:",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=100
        )
        summary_label.pack(side="left", padx=(0, 10))

        self.summary_textbox = ctk.CTkTextbox(
            summary_frame,
            height=100,
            font=ctk.CTkFont(size=12)
        )
        self.summary_textbox.pack(side="left", fill="both", expand=True)

    def _build_content_tab(self):
        """构建章节内容标签页"""
        tab = self.detail_tabview.tab("章节内容")

        # 章节内容
        content_label = ctk.CTkLabel(
            tab,
            text="章节内容:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        content_label.pack(anchor="w", pady=(10, 5))

        self.content_textbox = ctk.CTkTextbox(
            tab,
            height=300,
            font=ctk.CTkFont(size=12)
        )
        self.content_textbox.pack(fill="both", expand=True, padx=(0, 10), pady=(0, 10))

    def _build_notes_tab(self):
        """构建编辑笔记标签页"""
        tab = self.detail_tabview.tab("编辑笔记")

        # 编辑笔记
        notes_label = ctk.CTkLabel(
            tab,
            text="编辑笔记:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        notes_label.pack(anchor="w", pady=(10, 5))

        self.notes_textbox = ctk.CTkTextbox(
            tab,
            height=200,
            font=ctk.CTkFont(size=12)
        )
        self.notes_textbox.pack(fill="both", expand=True, padx=(0, 10), pady=(0, 10))

    def _build_state_tab(self):
        """构建状态跟踪标签页"""
        tab = self.detail_tabview.tab("状态跟踪")

        # 章节状态
        state_label = ctk.CTkLabel(
            tab,
            text="章节状态:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        state_label.pack(anchor="w", pady=(10, 5))

        self.state_textbox = ctk.CTkTextbox(
            tab,
            height=200,
            font=ctk.CTkFont(size=12)
        )
        self.state_textbox.pack(fill="both", expand=True, padx=(0, 10), pady=(0, 10))

    def _build_action_buttons(self):
        """构建操作按钮"""
        button_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        button_frame.pack(fill="x", padx=15, pady=(0, 15))

        # 保存按钮
        self.save_button = ctk.CTkButton(
            button_frame,
            text="保存章节",
            command=self._save_current_chapter,
            fg_color="#2E7D32",
            hover_color="#388E3C",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.save_button.pack(side="left", padx=(0, 10), fill="x", expand=True)

        # 删除按钮
        self.delete_button = ctk.CTkButton(
            button_frame,
            text="删除章节",
            command=self._delete_current_chapter,
            fg_color="#D32F2F",
            hover_color="#F44336",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.delete_button.pack(side="right", fill="x", expand=True)

    def _refresh_chapters(self):
        """刷新章节数据"""
        try:
            self._load_chapters_data()

            if self.refreshable_frame:
                self.refreshable_frame.show_refresh_success()
            elif hasattr(self, 'refresh_button'):
                # 传统按钮反馈
                original_text = self.refresh_button.cget('text')
                self.refresh_button.configure(text="✓ 刷新成功")
                self.after(2000, lambda: self.refresh_button.configure(text=original_text))

            logger.info("章节数据刷新成功")

        except Exception as e:
            logger.error(f"刷新章节数据失败: {e}")

            if self.refreshable_frame:
                self.refreshable_frame.show_refresh_error()
            elif hasattr(self, 'refresh_button'):
                original_text = self.refresh_button.cget('text')
                self.refresh_button.configure(text="✗ 刷新失败")
                self.after(2000, lambda: self.refresh_button.configure(text=original_text))

    def _load_chapters_data(self):
        """加载章节数据"""
        # 尝试从不同来源加载章节数据
        chapter_data = []

        try:
            # 检查是否有生成的章节文件
            possible_files = [
                './Novel_directory.txt',
                './novel_output/Novel_directory.txt',
                './test_output/Novel_directory.txt',
                './chapter_1.txt',
                './novel_output/chapter_1.txt'
            ]

            for file_path in possible_files:
                if os.path.exists(file_path):
                    chapters = self._parse_chapter_file(file_path)
                    if chapters:
                        chapter_data.extend(chapters)
                        logger.info(f"从 {file_path} 加载了 {len(chapters)} 个章节")
                        break

        except Exception as e:
            logger.warning(f"从文件加载章节数据失败: {e}")

        # 如果没有数据，创建默认章节
        if not chapter_data:
            chapter_data = [
                {
                    'id': 1,
                    'number': 1,
                    'title': '第一章',
                    'summary': '故事的开端',
                    'content': '这是第一章的内容...',
                    'notes': '',
                    'state': '未开始'
                }
            ]

        # 更新数据
        self.chapters = chapter_data
        self.filtered_chapters = chapter_data.copy()
        self._refresh_chapter_list()

        # 如果当前章节被删除，切换到第一个章节
        if self.current_chapter and self.current_chapter not in self.chapters:
            if self.chapters:
                self.current_chapter = self.chapters[0]
                self._load_chapter_to_form()
            else:
                self.current_chapter = None
                self._show_empty_state()

        logger.info(f"加载了 {len(chapter_data)} 个章节")

    def _parse_chapter_file(self, file_path: str) -> List[Dict[str, Any]]:
        """解析章节文件"""
        chapters = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 简单的章节解析逻辑
            lines = content.split('\n')
            current_chapter = {}
            chapter_id = 1

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # 检测章节标题
                if '第' in line and '章' in line:
                    if current_chapter:
                        current_chapter['id'] = chapter_id
                        chapters.append(current_chapter)
                        chapter_id += 1

                    current_chapter = {
                        'number': chapter_id,
                        'title': line,
                        'summary': '',
                        'content': '',
                        'notes': '',
                        'state': '未开始'
                    }
                elif current_chapter:
                    if '摘要' in line or '简介' in line:
                        current_chapter['summary'] += line + '\n'
                    else:
                        current_chapter['content'] += line + '\n'

            # 添加最后一个章节
            if current_chapter:
                current_chapter['id'] = chapter_id
                chapters.append(current_chapter)

        except Exception as e:
            logger.error(f"解析章节文件失败: {e}")

        return chapters

    def _refresh_chapter_list(self):
        """刷新章节列表"""
        # 清空现有列表
        for widget in self.chapters_scroll.winfo_children():
            widget.destroy()

        # 显示章节列表
        for chapter in self.filtered_chapters:
            self._create_chapter_item(chapter)

    def _create_chapter_item(self, chapter: Dict[str, Any]):
        """创建章节列表项"""
        item_frame = ctk.CTkFrame(
            self.chapters_scroll,
            fg_color="#404040",
            corner_radius=8
        )
        item_frame.pack(fill="x", pady=5)

        # 章节标题
        title_label = ctk.CTkLabel(
            item_frame,
            text=f"第{chapter.get('number', chapter.get('id', '?'))}章: {chapter.get('title', '未命名')}",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        title_label.pack(fill="x", padx=15, pady=(10, 5))

        # 章节摘要
        summary = chapter.get('summary', '')
        if summary:
            summary_label = ctk.CTkLabel(
                item_frame,
                text=summary[:50] + "..." if len(summary) > 50 else summary,
                font=ctk.CTkFont(size=11),
                text_color="#AAAAAA",
                anchor="w",
                wraplength=300
            )
            summary_label.pack(fill="x", padx=15, pady=(0, 5))

        # 章节状态
        state = chapter.get('state', '未开始')
        state_label = ctk.CTkLabel(
            item_frame,
            text=f"状态: {state}",
            font=ctk.CTkFont(size=10),
            text_color="#888888",
            anchor="w"
        )
        state_label.pack(fill="x", padx=15, pady=(0, 10))

        # 点击事件
        def on_click(event=None):
            self.current_chapter = chapter
            self._load_chapter_to_form()
            self._highlight_selected_item(item_frame)

        item_frame.bind("<Button-1>", on_click)
        title_label.bind("<Button-1>", on_click)
        if summary:
            summary_label.bind("<Button-1>", on_click)

    def _highlight_selected_item(self, selected_frame):
        """高亮选中项"""
        # 重置所有项的颜色
        for widget in self.chapters_scroll.winfo_children():
            widget.configure(fg_color="#404040")

        # 高亮选中项
        selected_frame.configure(fg_color="#3B82F6")

    def _load_chapter_to_form(self):
        """加载章节数据到表单"""
        if not self.current_chapter:
            return

        # 清空现有详情面板
        for widget in self.right_panel.winfo_children():
            widget.destroy()

        # 重新构建详情面板
        self._build_chapter_detail_panel()

        # 填充数据
        if hasattr(self, 'title_entry'):
            self.title_entry.delete(0, 'end')
            self.title_entry.insert(0, self.current_chapter.get('title', ''))

        if hasattr(self, 'number_entry'):
            self.number_entry.delete(0, 'end')
            self.number_entry.insert(0, str(self.current_chapter.get('number', self.current_chapter.get('id', ''))))

        if hasattr(self, 'summary_textbox'):
            self.summary_textbox.delete('1.0', 'end')
            self.summary_textbox.insert('1.0', self.current_chapter.get('summary', ''))

        if hasattr(self, 'content_textbox'):
            self.content_textbox.delete('1.0', 'end')
            self.content_textbox.insert('1.0', self.current_chapter.get('content', ''))

        if hasattr(self, 'notes_textbox'):
            self.notes_textbox.delete('1.0', 'end')
            self.notes_textbox.insert('1.0', self.current_chapter.get('notes', ''))

        if hasattr(self, 'state_textbox'):
            self.state_textbox.delete('1.0', 'end')
            self.state_textbox.insert('1.0', self.current_chapter.get('state', '未开始'))

    def _on_chapter_search(self, event):
        """章节搜索"""
        query = self.search_entry.get().lower()
        if not query:
            self.filtered_chapters = self.chapters.copy()
        else:
            self.filtered_chapters = [
                chapter for chapter in self.chapters
                if query in chapter.get('title', '').lower() or
                   query in chapter.get('summary', '').lower()
            ]

        self._refresh_chapter_list()

    def _add_new_chapter(self):
        """添加新章节"""
        new_chapter = {
            'id': len(self.chapters) + 1,
            'number': len(self.chapters) + 1,
            'title': f'第{len(self.chapters) + 1}章',
            'summary': '',
            'content': '',
            'notes': '',
            'state': '未开始'
        }

        self.chapters.append(new_chapter)
        self.filtered_chapters = self.chapters.copy()
        self._refresh_chapter_list()

        # 选中新章节
        self.current_chapter = new_chapter
        self._load_chapter_to_form()

    def _save_current_chapter(self):
        """保存当前章节"""
        if not self.current_chapter:
            return

        # 收集表单数据
        updates = {
            'title': self.title_entry.get() if hasattr(self, 'title_entry') else '',
            'number': int(self.number_entry.get()) if hasattr(self, 'number_entry') and self.number_entry.get().isdigit() else self.current_chapter.get('number'),
            'summary': self.summary_textbox.get('1.0', 'end-1c') if hasattr(self, 'summary_textbox') else '',
            'content': self.content_textbox.get('1.0', 'end-1c') if hasattr(self, 'content_textbox') else '',
            'notes': self.notes_textbox.get('1.0', 'end-1c') if hasattr(self, 'notes_textbox') else '',
            'state': self.state_textbox.get('1.0', 'end-1c') if hasattr(self, 'state_textbox') else '未开始'
        }

        # 更新数据
        self.current_chapter.update(updates)
        self._refresh_chapter_list()

        messagebox.showinfo("成功", "章节信息已保存")

    def _delete_current_chapter(self):
        """删除当前章节"""
        if not self.current_chapter:
            return

        if messagebox.askyesno("确认删除", f"确定要删除章节 \"{self.current_chapter.get('title', '未命名')}\" 吗？"):
            self.chapters.remove(self.current_chapter)
            self.filtered_chapters.remove(self.current_chapter)
            self._refresh_chapter_list()

            self.current_chapter = None

    def _import_chapters(self):
        """导入章节"""
        # TODO: 实现导入功能
        messagebox.showinfo("提示", "导入功能开发中")

    def _export_chapters(self):
        """导出章节"""
        # TODO: 实现导出功能
        messagebox.showinfo("提示", "导出功能开发中")