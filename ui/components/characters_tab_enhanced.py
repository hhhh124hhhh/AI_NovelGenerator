# ui/components/characters_tab_enhanced.py
# -*- coding: utf-8 -*-
"""
增强的角色管理标签页组件 - BMAD方法的Modernize组件
解决角色信息与UI面板的实时同步问题
集成统一刷新按钮功能
"""

import logging
import os
import json
from typing import Dict, Any, Optional, Callable, List
import customtkinter as ctk
from tkinter import messagebox, font as tk_font
from utils import read_file, save_string_to_txt

# 导入数据桥接器
try:
    from ..data_bridge import get_data_bridge
    DATA_BRIDGE_AVAILABLE = True
except ImportError:
    DATA_BRIDGE_AVAILABLE = False

# 导入刷新按钮组件
try:
    from .refresh_button import RefreshableTabFrame
    REFRESH_BUTTON_AVAILABLE = True
except ImportError:
    REFRESH_BUTTON_AVAILABLE = False

logger = logging.getLogger(__name__)


class CharactersTabEnhanced(ctk.CTkFrame):
    """
    增强的角色管理标签页组件

    新增功能：
    - 实时数据同步
    - 自动更新UI
    - 文件变化监听
    - 智能数据转换
    """

    def __init__(self, parent: ctk.CTkFrame, theme_manager, state_manager=None, main_window=None, **kwargs):
        """
        初始化增强角色管理标签页

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

        # 数据桥接器
        if DATA_BRIDGE_AVAILABLE:
            self.data_bridge = get_data_bridge()
            self.data_bridge.register_listener('characters', self._on_characters_updated)
        else:
            self.data_bridge = None

        # 角色数据
        self.characters = []
        self.current_character = None
        self.filtered_characters = []

        # 组件引用
        self.characters_list_frame = None
        self.character_detail_frame = None
        self.search_entry = None
        self.add_button = None
        self.save_button = None
        self.delete_button = None
        self.refreshable_frame = None

        # 文件监听
        self.character_file_path = None
        self.last_file_modified = None

        # 回调函数
        self.character_changed_callback = None

        # 初始化组件
        self._create_enhanced_layout()
        self._setup_file_monitoring()
        self._load_characters_data()

        logger.debug("CharactersTabEnhanced 组件初始化完成")

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
                "角色管理",
                self._refresh_characters
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
            text="角色管理",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(side="left", padx=20, pady=15)

        # 刷新按钮
        refresh_button = ctk.CTkButton(
            title_frame,
            text="刷新",
            command=self._refresh_characters,
            width=80,
            height=35
        )
        refresh_button.pack(side="right", padx=20, pady=7)

        # 导入按钮
        import_button = ctk.CTkButton(
            title_frame,
            text="导入",
            command=self._import_characters,
            width=80,
            height=35
        )
        import_button.pack(side="right", padx=5, pady=7)

        # 导出按钮
        export_button = ctk.CTkButton(
            title_frame,
            text="导出",
            command=self._export_characters,
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
            parent_frame = self

        # 左侧面板 - 角色列表
        self.left_panel = ctk.CTkFrame(parent_frame, fg_color="#2A2A2A")
        self.left_panel.pack(side="left", fill="y", padx=(0, 5))
        self.left_panel.configure(width=350)

        # 右侧面板 - 角色详情
        self.right_panel = ctk.CTkFrame(parent_frame, fg_color="transparent")
        self.right_panel.pack(side="right", fill="both", expand=True, padx=(5, 0))

        # 构建面板内容
        self._build_character_list_panel()
        self._build_character_detail_panel()

    def _build_character_list_panel(self):
        """构建角色列表面板"""
        # 搜索框
        search_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        search_frame.pack(fill="x", padx=15, pady=15)

        search_label = ctk.CTkLabel(
            search_frame,
            text="搜索角色:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        search_label.pack(anchor="w", pady=(0, 5))

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="输入角色名称...",
            height=35
        )
        self.search_entry.pack(fill="x")
        self.search_entry.bind("<KeyRelease>", self._on_character_search)

        # 角色列表
        list_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        list_frame.pack(fill="both", expand=True, padx=15, pady=10)

        # 使用ScrollableFrame
        self.characters_scroll = ctk.CTkScrollableFrame(
            list_frame,
            height=500,
            fg_color="#333333"
        )
        self.characters_scroll.pack(fill="both", expand=True)

        # 添加角色按钮
        button_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        button_frame.pack(fill="x", padx=15, pady=15)

        self.add_button = ctk.CTkButton(
            button_frame,
            text="+ 添加新角色",
            command=self._add_new_character,
            fg_color="#2E7D32",
            hover_color="#388E3C",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.add_button.pack(fill="x", pady=(0, 10))

    def _build_character_detail_panel(self):
        """构建角色详情面板"""
        if not self.current_character:
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
        self.detail_tabview.add("背景设定")
        self.detail_tabview.add("关系网络")
        self.detail_tabview.add("状态跟踪")

        # 构建各标签页内容
        self._build_basic_info_tab()
        self._build_background_tab()
        self._build_relationships_tab()
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
            text="📝\n\n请选择或创建一个角色\n\n点击左侧的\"添加新角色\"按钮开始",
            font=ctk.CTkFont(size=16),
            text_color="#888888"
        )
        empty_label.pack(expand=True)

    def _build_basic_info_tab(self):
        """构建基本信息标签页"""
        tab = self.detail_tabview.tab("基本信息")

        # 角色名称
        name_frame = ctk.CTkFrame(tab, fg_color="transparent")
        name_frame.pack(fill="x", pady=10)

        name_label = ctk.CTkLabel(
            name_frame,
            text="角色名称:",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=100
        )
        name_label.pack(side="left", padx=(0, 10))

        self.name_entry = ctk.CTkEntry(
            name_frame,
            height=35,
            font=ctk.CTkFont(size=12)
        )
        self.name_entry.pack(side="left", fill="x", expand=True)

        # 角色描述
        desc_frame = ctk.CTkFrame(tab, fg_color="transparent")
        desc_frame.pack(fill="x", pady=10)

        desc_label = ctk.CTkLabel(
            desc_frame,
            text="角色描述:",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=100
        )
        desc_label.pack(side="left", padx=(0, 10))

        self.desc_textbox = ctk.CTkTextbox(
            desc_frame,
            height=100,
            font=ctk.CTkFont(size=12)
        )
        self.desc_textbox.pack(side="left", fill="both", expand=True)

        # 性格特征
        traits_frame = ctk.CTkFrame(tab, fg_color="transparent")
        traits_frame.pack(fill="x", pady=10)

        traits_label = ctk.CTkLabel(
            traits_frame,
            text="性格特征:",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=100
        )
        traits_label.pack(side="left", padx=(0, 10))

        self.traits_textbox = ctk.CTkTextbox(
            traits_frame,
            height=80,
            font=ctk.CTkFont(size=12)
        )
        self.traits_textbox.pack(side="left", fill="both", expand=True)

        # 外貌描述
        appearance_frame = ctk.CTkFrame(tab, fg_color="transparent")
        appearance_frame.pack(fill="x", pady=10)

        appearance_label = ctk.CTkLabel(
            appearance_frame,
            text="外貌描述:",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=100
        )
        appearance_label.pack(side="left", padx=(0, 10))

        self.appearance_textbox = ctk.CTkTextbox(
            appearance_frame,
            height=80,
            font=ctk.CTkFont(size=12)
        )
        self.appearance_textbox.pack(side="left", fill="both", expand=True)

    def _build_background_tab(self):
        """构建背景设定标签页"""
        tab = self.detail_tabview.tab("背景设定")

        # 背景故事
        bg_label = ctk.CTkLabel(
            tab,
            text="背景故事:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        bg_label.pack(anchor="w", pady=(10, 5))

        self.background_textbox = ctk.CTkTextbox(
            tab,
            height=200,
            font=ctk.CTkFont(size=12)
        )
        self.background_textbox.pack(fill="both", expand=True, padx=(0, 10), pady=(0, 10))

    def _build_relationships_tab(self):
        """构建关系网络标签页"""
        tab = self.detail_tabview.tab("关系网络")

        # 关系网络
        rel_label = ctk.CTkLabel(
            tab,
            text="角色关系:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        rel_label.pack(anchor="w", pady=(10, 5))

        self.relationships_textbox = ctk.CTkTextbox(
            tab,
            height=200,
            font=ctk.CTkFont(size=12)
        )
        self.relationships_textbox.pack(fill="both", expand=True, padx=(0, 10), pady=(0, 10))

    def _build_state_tab(self):
        """构建状态跟踪标签页"""
        tab = self.detail_tabview.tab("状态跟踪")

        # 角色状态
        state_label = ctk.CTkLabel(
            tab,
            text="当前状态:",
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
            text="保存角色",
            command=self._save_current_character,
            fg_color="#2E7D32",
            hover_color="#388E3C",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.save_button.pack(side="left", padx=(0, 10), fill="x", expand=True)

        # 删除按钮
        self.delete_button = ctk.CTkButton(
            button_frame,
            text="删除角色",
            command=self._delete_current_character,
            fg_color="#D32F2F",
            hover_color="#F44336",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.delete_button.pack(side="right", fill="x", expand=True)

    def _on_characters_updated(self, characters: List[Dict[str, Any]]):
        """角色数据更新回调"""
        self.characters = characters
        self.filtered_characters = characters.copy()
        self._refresh_character_list()

        # 如果当前角色被删除，切换到第一个角色
        if self.current_character and self.current_character not in self.characters:
            if self.characters:
                self.current_character = self.characters[0]
                self._load_character_to_form()
            else:
                self.current_character = None
                self._show_empty_state()

    def _refresh_character_list(self):
        """刷新角色列表"""
        # 清空现有列表
        for widget in self.characters_scroll.winfo_children():
            widget.destroy()

        # 显示角色列表
        for character in self.filtered_characters:
            self._create_character_item(character)

    def _create_character_item(self, character: Dict[str, Any]):
        """创建角色列表项"""
        item_frame = ctk.CTkFrame(
            self.characters_scroll,
            fg_color="#404040",
            corner_radius=8
        )
        item_frame.pack(fill="x", pady=5)

        # 角色名称
        name_label = ctk.CTkLabel(
            item_frame,
            text=character.get('name', '未命名角色'),
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        name_label.pack(fill="x", padx=15, pady=(10, 5))

        # 角色描述
        desc = character.get('description', '')
        if desc:
            desc_label = ctk.CTkLabel(
                item_frame,
                text=desc[:50] + "..." if len(desc) > 50 else desc,
                font=ctk.CTkFont(size=11),
                text_color="#AAAAAA",
                anchor="w",
                wraplength=300
            )
            desc_label.pack(fill="x", padx=15, pady=(0, 5))

        # 点击事件
        def on_click(event=None):
            self.current_character = character
            self._load_character_to_form()
            self._highlight_selected_item(item_frame)

        item_frame.bind("<Button-1>", on_click)
        name_label.bind("<Button-1>", on_click)
        if desc:
            desc_label.bind("<Button-1>", on_click)

    def _highlight_selected_item(self, selected_frame):
        """高亮选中项"""
        # 重置所有项的颜色
        for widget in self.characters_scroll.winfo_children():
            widget.configure(fg_color="#404040")

        # 高亮选中项
        selected_frame.configure(fg_color="#3B82F6")

    def _load_character_to_form(self):
        """加载角色数据到表单"""
        if not self.current_character:
            return

        # 清空现有详情面板
        for widget in self.right_panel.winfo_children():
            widget.destroy()

        # 重新构建详情面板
        self._build_character_detail_panel()

        # 填充数据
        if hasattr(self, 'name_entry'):
            self.name_entry.delete(0, 'end')
            self.name_entry.insert(0, self.current_character.get('name', ''))

        if hasattr(self, 'desc_textbox'):
            self.desc_textbox.delete('1.0', 'end')
            self.desc_textbox.insert('1.0', self.current_character.get('description', ''))

        if hasattr(self, 'traits_textbox'):
            self.traits_textbox.delete('1.0', 'end')
            self.traits_textbox.insert('1.0', '\n'.join(self.current_character.get('traits', [])))

        if hasattr(self, 'appearance_textbox'):
            self.appearance_textbox.delete('1.0', 'end')
            self.appearance_textbox.insert('1.0', self.current_character.get('appearance', ''))

        if hasattr(self, 'background_textbox'):
            self.background_textbox.delete('1.0', 'end')
            self.background_textbox.insert('1.0', self.current_character.get('background', ''))

        if hasattr(self, 'relationships_textbox'):
            relationships = self.current_character.get('relationships', {})
            rel_text = '\n'.join([f"{k}: {v}" for k, v in relationships.items()])
            self.relationships_textbox.delete('1.0', 'end')
            self.relationships_textbox.insert('1.0', rel_text)

        if hasattr(self, 'state_textbox'):
            state_text = self.current_character.get('state', '')
            self.state_textbox.delete('1.0', 'end')
            self.state_textbox.insert('1.0', state_text)

    def _on_character_search(self, event):
        """角色搜索"""
        query = self.search_entry.get().lower()
        if not query:
            self.filtered_characters = self.characters.copy()
        else:
            self.filtered_characters = [
                char for char in self.characters
                if query in char.get('name', '').lower() or
                   query in char.get('description', '').lower()
            ]

        self._refresh_character_list()

    def _add_new_character(self):
        """添加新角色"""
        new_character = {
            'id': len(self.characters) + 1,
            'name': f'新角色{len(self.characters) + 1}',
            'description': '',
            'traits': [],
            'appearance': '',
            'background': '',
            'relationships': {},
            'state': ''
        }

        if self.data_bridge:
            self.data_bridge.add_character(new_character)
        else:
            self.characters.append(new_character)
            self._on_characters_updated(self.characters)

        # 选中新角色
        self.current_character = new_character
        self._load_character_to_form()

    def _save_current_character(self):
        """保存当前角色"""
        if not self.current_character:
            return

        # 收集表单数据
        updates = {
            'name': self.name_entry.get() if hasattr(self, 'name_entry') else '',
            'description': self.desc_textbox.get('1.0', 'end-1c') if hasattr(self, 'desc_textbox') else '',
            'traits': self.traits_textbox.get('1.0', 'end-1c').split('\n') if hasattr(self, 'traits_textbox') else [],
            'appearance': self.appearance_textbox.get('1.0', 'end-1c') if hasattr(self, 'appearance_textbox') else '',
            'background': self.background_textbox.get('1.0', 'end-1c') if hasattr(self, 'background_textbox') else '',
        }

        if hasattr(self, 'relationships_textbox'):
            rel_text = self.relationships_textbox.get('1.0', 'end-1c')
            relationships = {}
            for line in rel_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    relationships[key.strip()] = value.strip()
            updates['relationships'] = relationships

        if hasattr(self, 'state_textbox'):
            updates['state'] = self.state_textbox.get('1.0', 'end-1c')

        # 更新数据
        if self.data_bridge:
            self.data_bridge.update_character(self.current_character['id'], updates)
        else:
            self.current_character.update(updates)
            self._on_characters_updated(self.characters)

        messagebox.showinfo("成功", "角色信息已保存")

    def _delete_current_character(self):
        """删除当前角色"""
        if not self.current_character:
            return

        if messagebox.askyesno("确认删除", f"确定要删除角色 \"{self.current_character.get('name', '未命名')}\" 吗？"):
            if self.data_bridge:
                self.data_bridge.delete_character(self.current_character['id'])
            else:
                self.characters.remove(self.current_character)
                self._on_characters_updated(self.characters)

            self.current_character = None

    def _refresh_characters(self):
        """刷新角色列表"""
        self._load_characters_data()

    def _import_characters(self):
        """导入角色"""
        # TODO: 实现导入功能
        messagebox.showinfo("提示", "导入功能开发中")

    def _export_characters(self):
        """导出角色"""
        # TODO: 实现导出功能
        messagebox.showinfo("提示", "导出功能开发中")

    def _setup_file_monitoring(self):
        """设置文件监听"""
        # TODO: 实现文件监听
        pass

    def _load_characters_data(self):
        """加载角色数据"""
        # 尝试从不同来源加载角色数据
        character_data = []

        # 1. 尝试从data_bridge加载
        if self.data_bridge:
            try:
                # 尝试从标准文件路径加载
                if hasattr(self.main_window, 'current_project_path'):
                    project_path = self.main_window.current_project_path
                    character_file = os.path.join(project_path, 'Novel_setting.txt')

                    if os.path.exists(character_file):
                        self.data_bridge.load_characters_from_file(character_file)
                        character_data = self.data_bridge.get_data('characters')
            except Exception as e:
                logger.warning(f"从data_bridge加载角色数据失败: {e}")

        # 2. 尝试从小说生成结果加载
        if not character_data:
            try:
                # 检查是否有生成的角色文件
                possible_files = [
                    './Novel_setting.txt',
                    './novel_output/Novel_setting.txt',
                    './test_output/Novel_setting.txt'
                ]

                for file_path in possible_files:
                    if os.path.exists(file_path):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if self.data_bridge:
                                self.data_bridge.load_characters_from_file(file_path)
                                character_data = self.data_bridge.get_data('characters')
                            else:
                                character_data = self._parse_character_content(content)
                        break

            except Exception as e:
                logger.warning(f"从文件加载角色数据失败: {e}")

        # 3. 如果还是没有数据，创建默认角色
        if not character_data:
            character_data = [
                {
                    'id': 1,
                    'name': '主角',
                    'description': '故事的主要角色',
                    'traits': ['勇敢', '聪明'],
                    'appearance': '',
                    'background': '',
                    'relationships': {},
                    'state': ''
                }
            ]

        # 更新数据
        if self.data_bridge:
            self.data_bridge.update_data('characters', character_data, notify=True)
        else:
            self.characters = character_data
            self._on_characters_updated(character_data)

        logger.info(f"加载了 {len(character_data)} 个角色")

    def _parse_character_content(self, content: str) -> List[Dict[str, Any]]:
        """解析角色内容"""
        characters = []

        try:
            # 尝试解析JSON格式
            if content.strip().startswith('[') or content.strip().startswith('{'):
                import json
                data = json.loads(content)
                if isinstance(data, list):
                    characters = data
                elif isinstance(data, dict):
                    characters = [data]
            else:
                # 简单的文本解析
                lines = content.split('\n')
                current_char = {}

                for line in lines:
                    line = line.strip()
                    if not line:
                        continue

                    if '角色' in line or '人物' in line:
                        if current_char:
                            characters.append(current_char)
                        current_char = {
                            'name': line,
                            'description': '',
                            'traits': [],
                            'appearance': '',
                            'background': '',
                            'relationships': {},
                            'state': ''
                        }
                    elif current_char:
                        if '特征' in line or '性格' in line:
                            current_char['traits'].append(line)
                        elif '外貌' in line:
                            current_char['appearance'] += line + '\n'
                        elif '背景' in line:
                            current_char['background'] += line + '\n'
                        else:
                            current_char['description'] += line + '\n'

                if current_char:
                    characters.append(current_char)

            # 标准化数据
            for i, char in enumerate(characters):
                char['id'] = i + 1
                if 'traits' not in char:
                    char['traits'] = []
                if 'relationships' not in char:
                    char['relationships'] = {}
                if 'state' not in char:
                    char['state'] = ''

        except Exception as e:
            logger.error(f"解析角色内容失败: {e}")
            # 创建默认角色
            characters = [{
                'id': 1,
                'name': '默认角色',
                'description': content[:200] + "..." if len(content) > 200 else content,
                'traits': [],
                'appearance': '',
                'background': '',
                'relationships': {},
                'state': ''
            }]

        return characters

    def update_characters_from_generation(self, character_content: str):
        """从小说生成更新角色信息"""
        try:
            # 解析新生成的角色内容
            new_characters = self._parse_character_content(character_content)

            if new_characters:
                # 更新到数据桥接器
                if self.data_bridge:
                    self.data_bridge.update_data('characters', new_characters, notify=True)
                else:
                    self.characters = new_characters
                    self._on_characters_updated(new_characters)

                logger.info(f"从生成内容更新了 {len(new_characters)} 个角色")
                return True

        except Exception as e:
            logger.error(f"更新角色信息失败: {e}")

        return False