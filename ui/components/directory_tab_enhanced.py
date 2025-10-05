# ui/components/directory_tab_enhanced.py
# -*- coding: utf-8 -*-
"""
增强的目录管理标签页组件
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


class DirectoryTabEnhanced(ctk.CTkFrame):
    """
    增强的目录管理标签页组件

    新增功能：
    - 统一刷新按钮
    - 手动目录更新
    - 目录结构展示
    - 章节概览
    - 导航功能
    """

    def __init__(self, parent: ctk.CTkFrame, theme_manager, state_manager=None, main_window=None, **kwargs):
        """
        初始化增强目录管理标签页

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

        # 目录数据
        self.directory_data = []
        self.current_item = None
        self.filtered_items = []

        # 组件引用
        self.directory_tree_frame = None
        self.detail_frame = None
        self.search_entry = None
        self.refreshable_frame = None

        # 文件路径
        self.directory_file_path = None
        self.last_file_modified = None

        # 初始化组件
        self._create_enhanced_layout()
        self._load_directory_data()

        logger.debug("DirectoryTabEnhanced 组件初始化完成")

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
                "目录管理",
                self._refresh_directory
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
            text="目录管理",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(side="left", padx=20, pady=15)

        # 刷新按钮
        refresh_button = ctk.CTkButton(
            title_frame,
            text="刷新",
            command=self._refresh_directory,
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
            command=self._import_directory,
            width=80,
            height=35
        )
        import_button.pack(side="right", padx=5, pady=7)

        # 导出按钮
        export_button = ctk.CTkButton(
            title_frame,
            text="导出",
            command=self._export_directory,
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

        # 左侧面板 - 目录树
        self.left_panel = ctk.CTkFrame(parent_frame, fg_color="#2A2A2A")
        self.left_panel.pack(side="left", fill="y", padx=(0, 5))
        self.left_panel.configure(width=400)

        # 右侧面板 - 详情
        self.right_panel = ctk.CTkFrame(parent_frame, fg_color="transparent")
        self.right_panel.pack(side="right", fill="both", expand=True, padx=(5, 0))

        # 构建面板内容
        self._build_directory_tree_panel()
        self._build_detail_panel()

    def get_content_frame(self):
        """获取内容框架"""
        if hasattr(self, 'refreshable_frame') and self.refreshable_frame:
            return self.refreshable_frame.get_content_frame()
        elif hasattr(self, 'content_frame'):
            return self.content_frame
        else:
            # 如果都不存在，返回自身
            return self

    def _build_directory_tree_panel(self):
        """构建目录树列表面板"""
        # 搜索框
        search_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        search_frame.pack(fill="x", padx=15, pady=15)

        search_label = ctk.CTkLabel(
            search_frame,
            text="搜索目录:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        search_label.pack(anchor="w", pady=(0, 5))

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="输入章节或内容...",
            height=35
        )
        self.search_entry.pack(fill="x")
        self.search_entry.bind("<KeyRelease>", self._on_directory_search)

        # 目录树
        tree_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, padx=15, pady=10)

        # 使用ScrollableFrame
        self.directory_scroll = ctk.CTkScrollableFrame(
            tree_frame,
            height=500,
            fg_color="#333333"
        )
        self.directory_scroll.pack(fill="both", expand=True)

        # 添加统计信息
        stats_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        stats_frame.pack(fill="x", padx=15, pady=10)

        self.stats_label = ctk.CTkLabel(
            stats_frame,
            text="总计: 0 个章节",
            font=ctk.CTkFont(size=11),
            text_color="#AAAAAA"
        )
        self.stats_label.pack()

    def _build_detail_panel(self):
        """构建详情面板"""
        if not self.current_item:
            # 显示空状态
            self._show_empty_state()
            return

        # 创建详情内容
        self._create_detail_content()

    def _show_empty_state(self):
        """显示空状态"""
        empty_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        empty_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # 空状态图标和文字
        empty_label = ctk.CTkLabel(
            empty_frame,
            text="📋\n\n请选择目录项目\n\n从左侧列表中选择章节或内容",
            font=ctk.CTkFont(size=16),
            text_color="#888888"
        )
        empty_label.pack(expand=True)

    def _create_detail_content(self):
        """创建详情内容"""
        # 清空现有内容
        for widget in self.right_panel.winfo_children():
            widget.destroy()

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
        self.detail_tabview.add("概览")
        self.detail_tabview.add("详细信息")
        self.detail_tabview.add("相关内容")

        # 构建各标签页内容
        self._build_overview_tab()
        self._build_detail_tab()
        self._build_related_tab()

    def _build_overview_tab(self):
        """构建概览标签页"""
        tab = self.detail_tabview.tab("概览")

        if self.current_item and self.current_item.get('type') == 'chapter':
            # 章节概览
            self._build_chapter_overview(tab)
        else:
            # 内容概览
            self._build_content_overview(tab)

    def _build_chapter_overview(self, parent):
        """构建章节概览"""
        chapter = self.current_item

        # 章节基本信息
        info_frame = ctk.CTkFrame(parent, fg_color="transparent")
        info_frame.pack(fill="x", pady=10)

        # 标题
        title_label = ctk.CTkLabel(
            info_frame,
            text=f"📖 {chapter.get('title', '未命名章节')}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#FFFFFF"
        )
        title_label.pack(pady=10)

        # 章节信息
        info_text = f"""
章节序号: {chapter.get('number', '未知')}
状态: {chapter.get('state', '未知')}
字数: {len(chapter.get('content', ''))} 字
创建时间: {chapter.get('created_at', '未知')}
        """

        info_display = ctk.CTkTextbox(parent, height=150, font=ctk.CTkFont(size=12))
        info_display.pack(fill="x", pady=10)
        info_display.insert('1.0', info_text)
        info_display.configure(state='disabled')

        # 章节摘要
        if chapter.get('summary'):
            summary_frame = ctk.CTkFrame(parent, fg_color="transparent")
            summary_frame.pack(fill="both", expand=True, pady=10)

            summary_label = ctk.CTkLabel(
                summary_frame,
                text="章节摘要:",
                font=ctk.CTkFont(size=12, weight="bold")
            )
            summary_label.pack(anchor="w", pady=(0, 5))

            summary_display = ctk.CTkTextbox(
                summary_frame,
                height=100,
                font=ctk.CTkFont(size=12)
            )
            summary_display.pack(fill="both", expand=True)
            summary_display.insert('1.0', chapter['summary'])
            summary_display.configure(state='disabled')

    def _build_content_overview(self, parent):
        """构建内容概览"""
        content = self.current_item

        # 内容信息
        info_frame = ctk.CTkFrame(parent, fg_color="transparent")
        info_frame.pack(fill="x", pady=10)

        # 标题
        title_label = ctk.CTkLabel(
            info_frame,
            text=f"📝 {content.get('title', '未命名内容')}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#FFFFFF"
        )
        title_label.pack(pady=10)

        # 内容信息
        info_text = f"""
类型: {content.get('type', '未知')}
字数: {len(content.get('content', ''))} 字
创建时间: {content.get('created_at', '未知')}
        """

        info_display = ctk.CTkTextbox(parent, height=100, font=ctk.CTkFont(size=12))
        info_display.pack(fill="x", pady=10)
        info_display.insert('1.0', info_text)
        info_display.configure(state='disabled')

        # 内容预览
        if content.get('content'):
            preview_frame = ctk.CTkFrame(parent, fg_color="transparent")
            preview_frame.pack(fill="both", expand=True, pady=10)

            preview_label = ctk.CTkLabel(
                preview_frame,
                text="内容预览:",
                font=ctk.CTkFont(size=12, weight="bold")
            )
            preview_label.pack(anchor="w", pady=(0, 5))

            preview_display = ctk.CTkTextbox(
                preview_frame,
                height=200,
                font=ctk.CTkFont(size=12)
            )
            preview_display.pack(fill="both", expand=True)
            preview_display.insert('1.0', content['content'][:500] + "..." if len(content['content']) > 500 else content['content'])
            preview_display.configure(state='disabled')

    def _build_detail_tab(self):
        """构建详细信息标签页"""
        tab = self.detail_tabview.tab("详细信息")

        if self.current_item and self.current_item.get('type') == 'chapter':
            # 章节详细信息
            self._build_chapter_detail(tab)
        else:
            # 内容详细信息
            self._build_content_detail(tab)

    def _build_chapter_detail(self, parent):
        """构建章节详细信息"""
        chapter = self.current_item

        # 章节内容
        content_label = ctk.CTkLabel(
            parent,
            text="完整章节内容:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        content_label.pack(anchor="w", pady=(10, 5))

        content_display = ctk.CTkTextbox(
            parent,
            height=400,
            font=ctk.CTkFont(size=12)
        )
        content_display.pack(fill="both", expand=True, padx=(0, 10), pady=(0, 10))
        content_display.insert('1.0', chapter.get('content', '暂无内容'))

    def _build_content_detail(self, parent):
        """构建内容详细信息"""
        content = self.current_item

        # 完整内容
        content_label = ctk.CTkLabel(
            parent,
            text="完整内容:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        content_label.pack(anchor="w", pady=(10, 5))

        content_display = ctk.CTkTextbox(
            parent,
            height=400,
            font=ctk.CTkFont(size=12)
        )
        content_display.pack(fill="both", expand=True, padx=(0, 10), pady=(0, 10))
        content_display.insert('1.0', content.get('content', '暂无内容'))

    def _build_related_tab(self):
        """构建相关内容标签页"""
        tab = self.detail_tabview.tab("相关内容")

        related_frame = ctk.CTkFrame(tab, fg_color="transparent")
        related_frame.pack(fill="both", expand=True, padx=15, pady=15)

        related_label = ctk.CTkLabel(
            related_frame,
            text="相关章节和内容",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        related_label.pack(anchor="w", pady=(0, 10))

        # 这里可以添加相关内容的逻辑
        related_display = ctk.CTkTextbox(
            related_frame,
            height=300,
            font=ctk.CTkFont(size=12)
        )
        related_display.pack(fill="both", expand=True)
        related_display.insert('1.0', "相关内容功能开发中...\n\n将显示与当前章节或内容相关的其他项目。")
        related_display.configure(state='disabled')

    def _refresh_directory(self):
        """刷新目录数据"""
        try:
            self._load_directory_data()

            if self.refreshable_frame:
                self.refreshable_frame.show_refresh_success()
            elif hasattr(self, 'refresh_button'):
                # 传统按钮反馈
                original_text = self.refresh_button.cget('text')
                self.refresh_button.configure(text="✓ 刷新成功")
                self.after(2000, lambda: self.refresh_button.configure(text=original_text))

            logger.info("目录数据刷新成功")

        except Exception as e:
            logger.error(f"刷新目录数据失败: {e}")

            if self.refreshable_frame:
                self.refreshable_frame.show_refresh_error()
            elif hasattr(self, 'refresh_button'):
                original_text = self.refresh_button.cget('text')
                self.refresh_button.configure(text="✗ 刷新失败")
                self.after(2000, lambda: self.refresh_button.configure(text=original_text))

    def _load_directory_data(self):
        """加载目录数据"""
        # 尝试从不同来源加载目录数据
        directory_data = []

        try:
            # 检查是否有生成的目录文件
            possible_files = [
                './Novel_directory.txt',
                './novel_output/Novel_directory.txt',
                './test_output/Novel_directory.txt'
            ]

            for file_path in possible_files:
                if os.path.exists(file_path):
                    items = self._parse_directory_file(file_path)
                    if items:
                        directory_data = items
                        logger.info(f"从 {file_path} 加载了 {len(items)} 个目录项")
                        break

        except Exception as e:
            logger.warning(f"从文件加载目录数据失败: {e}")

        # 如果没有数据，创建默认目录项
        if not directory_data:
            directory_data = [
                {
                    'id': 1,
                    'type': 'chapter',
                    'title': '第一章',
                    'number': 1,
                    'summary': '故事的开端',
                    'content': '这是第一章的内容...',
                    'state': '未开始',
                    'created_at': '2025-01-01'
                }
            ]

        # 更新数据
        self.directory_data = directory_data
        self.filtered_items = directory_data.copy()
        self._refresh_directory_tree()
        self._update_stats()

        # 如果当前项被删除，切换到第一个项
        if self.current_item and self.current_item not in self.directory_data:
            if self.directory_data:
                self.current_item = self.directory_data[0]
                self._create_detail_content()
            else:
                self.current_item = None
                self._show_empty_state()

        logger.info(f"加载了 {len(directory_data)} 个目录项")

    def _parse_directory_file(self, file_path: str) -> List[Dict[str, Any]]:
        """解析目录文件"""
        items = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 简单的目录解析逻辑
            lines = content.split('\n')
            current_item = {}
            item_id = 1

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # 检测章节标题
                if '第' in line and '章' in line:
                    if current_item:
                        current_item['id'] = item_id
                        current_item['type'] = 'chapter'
                        items.append(current_item)
                        item_id += 1

                    current_item = {
                        'number': item_id,
                        'title': line,
                        'summary': '',
                        'content': '',
                        'state': '未开始',
                        'created_at': '2025-01-01'
                    }
                elif current_item:
                    if '摘要' in line or '简介' in line:
                        current_item['summary'] += line + '\n'
                    else:
                        current_item['content'] += line + '\n'

            # 添加最后一个章节
            if current_item:
                current_item['id'] = item_id
                current_item['type'] = 'chapter'
                items.append(current_item)

        except Exception as e:
            logger.error(f"解析目录文件失败: {e}")

        return items

    def _refresh_directory_tree(self):
        """刷新目录树"""
        # 清空现有树
        for widget in self.directory_scroll.winfo_children():
            widget.destroy()

        # 显示目录项
        for item in self.filtered_items:
            self._create_directory_item(item)

    def _create_directory_item(self, item: Dict[str, Any]):
        """创建目录项"""
        item_frame = ctk.CTkFrame(
            self.directory_scroll,
            fg_color="#404040",
            corner_radius=8
        )
        item_frame.pack(fill="x", pady=5)

        # 类型图标
        type_icon = "📖" if item.get('type') == 'chapter' else "📝"

        # 标题
        title_label = ctk.CTkLabel(
            item_frame,
            text=f"{type_icon} {item.get('title', '未命名')}",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        title_label.pack(fill="x", padx=15, pady=(10, 5))

        # 摘要
        summary = item.get('summary', '')
        if summary:
            summary_label = ctk.CTkLabel(
                item_frame,
                text=summary[:60] + "..." if len(summary) > 60 else summary,
                font=ctk.CTkFont(size=11),
                text_color="#AAAAAA",
                anchor="w",
                wraplength=350
            )
            summary_label.pack(fill="x", padx=15, pady=(0, 5))

        # 状态和字数
        info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        info_frame.pack(fill="x", padx=15, pady=(0, 10))

        state = item.get('state', '未开始')
        word_count = len(item.get('content', ''))

        info_label = ctk.CTkLabel(
            info_frame,
            text=f"状态: {state} | 字数: {word_count}",
            font=ctk.CTkFont(size=10),
            text_color="#888888",
            anchor="w"
        )
        info_label.pack(fill="x")

        # 点击事件
        def on_click(event=None):
            self.current_item = item
            self._create_detail_content()
            self._highlight_selected_item(item_frame)

        item_frame.bind("<Button-1>", on_click)
        title_label.bind("<Button-1>", on_click)
        if summary:
            summary_label.bind("<Button-1>", on_click)
        info_label.bind("<Button-1>", on_click)

    def _highlight_selected_item(self, selected_frame):
        """高亮选中项"""
        # 重置所有项的颜色
        for widget in self.directory_scroll.winfo_children():
            widget.configure(fg_color="#404040")

        # 高亮选中项
        selected_frame.configure(fg_color="#3B82F6")

    def _update_stats(self):
        """更新统计信息"""
        total_chapters = len([item for item in self.directory_data if item.get('type') == 'chapter'])
        total_items = len(self.directory_data)

        if hasattr(self, 'stats_label'):
            self.stats_label.configure(text=f"总计: {total_items} 项 ({total_chapters} 个章节)")

    def _on_directory_search(self, event):
        """目录搜索"""
        query = self.search_entry.get().lower()
        if not query:
            self.filtered_items = self.directory_data.copy()
        else:
            self.filtered_items = [
                item for item in self.directory_data
                if query in item.get('title', '').lower() or
                   query in item.get('summary', '').lower() or
                   query in item.get('content', '').lower()
            ]

        self._refresh_directory_tree()
        self._update_stats()

    def _import_directory(self):
        """导入目录"""
        # TODO: 实现导入功能
        messagebox.showinfo("提示", "导入功能开发中")

    def _export_directory(self):
        """导出目录"""
        # TODO: 实现导出功能
        messagebox.showinfo("提示", "导出功能开发中")