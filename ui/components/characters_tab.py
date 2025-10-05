"""
现代化角色管理标签页组件 - AI小说生成器的角色管理界面
包含角色创建、编辑、状态跟踪等功能
集成数据桥接器实现实时数据同步
"""

import logging
import os
from typing import Dict, Any, Optional, Callable, List
import customtkinter as ctk
from tkinter import messagebox
from utils import read_file, save_string_to_txt

# 导入数据桥接器
try:
    from ..data_bridge import get_data_bridge
    DATA_BRIDGE_AVAILABLE = True
except ImportError:
    DATA_BRIDGE_AVAILABLE = False

logger = logging.getLogger(__name__)


class CharactersTab(ctk.CTkFrame):
    """
    现代化角色管理标签页组件

    功能：
    - 角色列表管理
    - 角色详细信息编辑
    - 角色状态跟踪
    - 角色关系网络
    - 角色导入导出
    """

    def __init__(self, parent: ctk.CTkFrame, theme_manager, state_manager=None, project_manager=None, **kwargs):
        """
        初始化角色管理标签页

        Args:
            parent: 父组件
            theme_manager: 主题管理器
            state_manager: 状态管理器
            project_manager: 项目管理器
            **kwargs: 其他参数
        """
        # 初始化CustomTkinter Frame
        super().__init__(parent, **kwargs)

        # 存储管理器引用
        self.theme_manager = theme_manager
        self.state_manager = state_manager
        self.project_manager = project_manager

        # 数据桥接器
        if DATA_BRIDGE_AVAILABLE:
            self.data_bridge = get_data_bridge()
            self.data_bridge.register_listener('characters', self._on_characters_updated)
        else:
            self.data_bridge = None

        # 角色数据
        self.characters = []
        self.current_character = None

        # 组件引用
        self.characters_listbox = None
        self.character_form = None
        self.detail_frame = None
        self.character_info_text = None
        self.character_state_text = None

        # 回调函数
        self.character_changed_callback = None

        # 初始化组件
        self._create_characters_layout()
        self._load_characters_data()

        logger.debug("CharactersTab 组件初始化完成")

    def _create_characters_layout(self):
        """创建角色管理布局"""
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

        # 构建左侧面板 - 角色列表
        self._build_character_list_panel()

        # 构建右侧面板 - 角色详情
        self._build_character_detail_panel()

    def _build_character_list_panel(self):
        """构建角色列表面板"""
        # 标题栏 - 包含标题和刷新按钮
        title_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        title_frame.pack(fill="x", padx=10, pady=(10, 15))

        # 标题
        title_label = ctk.CTkLabel(
            title_frame,
            text="角色列表",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(side="left", padx=(0, 10))

        # 刷新按钮
        refresh_button = ctk.CTkButton(
            title_frame,
            text="🔄",
            width=35,
            height=35,
            command=self._refresh_characters,
            fg_color="#2196F3",
            hover_color="#1976D2",
            font=ctk.CTkFont(size=14)
        )
        refresh_button.pack(side="right", padx=(0, 5))

        # 搜索框
        search_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        search_frame.pack(fill="x", padx=10, pady=(0, 10))

        search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="搜索角色..."
        )
        search_entry.pack(fill="x")
        search_entry.bind("<KeyRelease>", self._on_character_search)

        # 角色列表
        list_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # 使用ScrollableFrame来显示角色列表
        self.characters_scroll = ctk.CTkScrollableFrame(
            list_frame,
            height=400
        )
        self.characters_scroll.pack(fill="both", expand=True)

        # 添加新角色按钮
        add_button = ctk.CTkButton(
            self.left_panel,
            text="+ 添加新角色",
            command=self._add_new_character,
            fg_color="#2E7D32",
            hover_color="#388E3C",
            height=40
        )
        add_button.pack(fill="x", padx=10, pady=(0, 10))

    def _build_character_detail_panel(self):
        """构建角色详情面板"""
        # 创建标签页视图
        self.detail_tabview = ctk.CTkTabview(
            self.right_panel,
            segmented_button_fg_color="#2A2A2A",
            segmented_button_selected_color="#404040",
            segmented_button_unselected_color="#1E1E1E"
        )
        self.detail_tabview.pack(fill="both", expand=True)

        # 添加标签页
        self.info_tab = self.detail_tabview.add("基本信息")
        self.state_tab = self.detail_tabview.add("角色状态")
        self.relationships_tab = self.detail_tabview.add("关系网络")

        # 构建各个标签页内容
        self._build_character_info_tab()
        self._build_character_state_tab()
        self._build_character_relationships_tab()

        # 底部操作按钮
        self._create_action_buttons()

    def _build_character_info_tab(self):
        """构建角色基本信息标签页"""
        # 主容器
        info_frame = ctk.CTkFrame(self.info_tab, fg_color="transparent")
        info_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 角色名称
        name_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        name_frame.pack(fill="x", pady=5)

        name_label = ctk.CTkLabel(
            name_frame,
            text="角色名称:",
            width=100,
            anchor="w"
        )
        name_label.pack(side="left", padx=(0, 10))

        self.character_name_entry = ctk.CTkEntry(
            name_frame,
            placeholder_text="输入角色名称"
        )
        self.character_name_entry.pack(side="left", fill="x", expand=True)

        # 角色类型
        type_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        type_frame.pack(fill="x", pady=5)

        type_label = ctk.CTkLabel(
            type_frame,
            text="角色类型:",
            width=100,
            anchor="w"
        )
        type_label.pack(side="left", padx=(0, 10))

        self.character_type_var = ctk.StringVar(value="主角")
        self.character_type_combo = ctk.CTkComboBox(
            type_frame,
            variable=self.character_type_var,
            values=["主角", "配角", "反派", "中立", "其他"]
        )
        self.character_type_combo.pack(side="left", fill="x", expand=True)

        # 角色描述
        desc_label = ctk.CTkLabel(
            info_frame,
            text="角色描述:",
            anchor="w"
        )
        desc_label.pack(fill="x", pady=(15, 5))

        self.character_desc_text = ctk.CTkTextbox(
            info_frame,
            height=120
        )
        self.character_desc_text.pack(fill="x", pady=(0, 10))

        # 角色特征
        traits_label = ctk.CTkLabel(
            info_frame,
            text="角色特征:",
            anchor="w"
        )
        traits_label.pack(fill="x", pady=(10, 5))

        self.character_traits_text = ctk.CTkTextbox(
            info_frame,
            height=100
        )
        self.character_traits_text.pack(fill="x", pady=(0, 10))

    def _build_character_state_tab(self):
        """构建角色状态标签页"""
        # 主容器
        state_frame = ctk.CTkFrame(self.state_tab, fg_color="transparent")
        state_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 状态标签
        state_label = ctk.CTkLabel(
            state_frame,
            text="角色状态详情",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        state_label.pack(fill="x", pady=(0, 10))

        # 状态文本框
        self.character_state_text = ctk.CTkTextbox(
            state_frame,
            height=400
        )
        self.character_state_text.pack(fill="both", expand=True, pady=(0, 10))

        # 状态更新时间
        self.update_time_label = ctk.CTkLabel(
            state_frame,
            text="最后更新: --",
            text_color="gray"
        )
        self.update_time_label.pack(fill="x")

    def _build_character_relationships_tab(self):
        """构建角色关系网络标签页"""
        # 主容器
        rel_frame = ctk.CTkFrame(self.relationships_tab, fg_color="transparent")
        rel_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 关系网络标题
        rel_label = ctk.CTkLabel(
            rel_frame,
            text="角色关系网络",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        rel_label.pack(fill="x", pady=(0, 10))

        # 添加关系区域
        add_rel_frame = ctk.CTkFrame(rel_frame, fg_color="transparent")
        add_rel_frame.pack(fill="x", pady=(0, 10))

        target_label = ctk.CTkLabel(
            add_rel_frame,
            text="关联角色:",
            width=80,
            anchor="w"
        )
        target_label.pack(side="left", padx=(0, 10))

        self.relationship_target_var = ctk.StringVar()
        self.relationship_target_combo = ctk.CTkComboBox(
            add_rel_frame,
            variable=self.relationship_target_var,
            values=[]
        )
        self.relationship_target_combo.pack(side="left", fill="x", expand=True, padx=(0, 10))

        relation_type_label = ctk.CTkLabel(
            add_rel_frame,
            text="关系类型:",
            width=80,
            anchor="w"
        )
        relation_type_label.pack(side="left", padx=(0, 10))

        self.relationship_type_var = ctk.StringVar(value="朋友")
        self.relationship_type_combo = ctk.CTkComboBox(
            add_rel_frame,
            variable=self.relationship_type_var,
            values=["朋友", "敌人", "家人", "恋人", "师徒", "同事", "其他"]
        )
        self.relationship_type_combo.pack(side="left", fill="x", expand=True)

        # 添加关系按钮
        add_rel_button = ctk.CTkButton(
            add_rel_frame,
            text="添加",
            command=self._add_relationship,
            width=60
        )
        add_rel_button.pack(side="left", padx=(10, 0))

        # 关系列表
        self.relationships_frame = ctk.CTkScrollableFrame(
            rel_frame,
            height=300
        )
        self.relationships_frame.pack(fill="both", expand=True, pady=(10, 0))

    def _create_action_buttons(self):
        """创建操作按钮"""
        button_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        button_frame.pack(fill="x", padx=10, pady=(0, 10))

        # 保存当前角色按钮
        save_button = ctk.CTkButton(
            button_frame,
            text="保存角色",
            command=self._save_current_character,
            fg_color="#1976D2",
            hover_color="#2196F3",
            height=40
        )
        save_button.pack(side="left", fill="x", expand=True, padx=(0, 5))

        # 删除角色按钮
        delete_button = ctk.CTkButton(
            button_frame,
            text="删除角色",
            command=self._delete_current_character,
            fg_color="#D32F2F",
            hover_color="#F44336",
            height=40
        )
        delete_button.pack(side="left", fill="x", expand=True, padx=(5, 5))

        # 导出/导入按钮
        export_button = ctk.CTkButton(
            button_frame,
            text="导出",
            command=self._export_character,
            fg_color="#388E3C",
            hover_color="#4CAF50",
            height=40
        )
        export_button.pack(side="left", fill="x", expand=True, padx=(5, 0))

    def _on_characters_updated(self, characters: List[Dict[str, Any]]):
        """角色数据更新回调"""
        try:
            self.characters = characters
            self._refresh_characters_display()

            # 如果有当前选中的角色，更新显示
            if hasattr(self, 'current_character_index') and self.current_character_index < len(characters):
                self._update_character_display(characters[self.current_character_index])

            logger.info(f"角色数据更新完成，共 {len(characters)} 个角色")
        except Exception as e:
            logger.error(f"角色数据更新回调失败: {e}")

    def _load_characters_data(self):
        """加载角色数据"""
        try:
            # 优先使用传递的项目管理器
            if self.project_manager:
                # 使用智能文件读取
                content = self.project_manager.read_file_smart("character_state.txt")
                if content:
                    logger.info(f"通过项目管理器成功加载角色数据")
                    self._parse_character_data(content)
                    return

            # 如果没有传递项目管理器，尝试获取全局项目管理器
            try:
                from .project_manager import get_project_manager
                project_manager = get_project_manager()

                # 使用智能文件读取
                content = project_manager.read_file_smart("character_state.txt")
                if content:
                    logger.info(f"通过全局项目管理器成功加载角色数据")
                    self._parse_character_data(content)
                    return

            except ImportError:
                logger.debug("项目管理器不可用，使用传统方式")
            except Exception as e:
                logger.debug(f"项目管理器加载失败: {e}")

            # 传统方式：从多个可能的路径加载角色状态文件
            possible_paths = [
                "character_state.txt",
                "./novel_output/character_state.txt",
                "./test_output/character_state.txt"
            ]

            # 如果有状态管理器，尝试获取配置的输出路径
            if self.state_manager:
                try:
                    config = self.state_manager.get_state('config', {})
                    if config and 'other_params' in config and 'filepath' in config['other_params']:
                        output_path = config['other_params']['filepath']
                        possible_paths.insert(0, f"{output_path}/character_state.txt")
                except Exception as e:
                    logger.debug(f"获取输出路径配置失败: {e}")

            content = None
            for path in possible_paths:
                try:
                    content = read_file(path)
                    if content:
                        logger.info(f"成功从 {path} 加载角色数据")
                        break
                except FileNotFoundError:
                    continue
                except Exception as e:
                    logger.debug(f"从 {path} 读取角色数据失败: {e}")
                    continue

            if content:
                # 解析角色数据
                self._parse_character_data(content)
            else:
                # 创建默认角色
                logger.info("未找到角色状态文件，创建默认角色")
                self._create_default_characters()

        except Exception as e:
            logger.error(f"加载角色数据失败: {e}")
            self._create_default_characters()

    def _parse_character_data(self, content: str):
        """解析角色数据"""
        try:
            characters = []
            lines = content.split('\n')
            current_character = None
            current_section = None

            for line in lines:
                line = line.rstrip()
                if not line:
                    continue

                # 检测角色名称行（以：结尾，不是以空格或├开头）
                if line.endswith('：') and not line.startswith(' ') and not line.startswith('├'):
                    # 保存前一个角色
                    if current_character:
                        characters.append(current_character)

                    # 创建新角色
                    name = line.rstrip('：')
                    current_character = {
                        'name': name,
                        'type': self._determine_character_type(name),
                        'description': '',
                        'traits': '',
                        'state': '',
                        'relationships': [],
                        'items': [],
                        'abilities': []
                    }
                    current_section = None

                # 检测章节标题
                elif line.startswith('新出场角色：') or line.startswith('主要角色间关系网') or line.startswith('触发或加深的事件'):
                    current_section = line.strip('：')
                    if current_character:
                        # 添加特殊信息到描述中
                        if current_section not in current_character:
                            current_character[current_section] = []

                # 检测具体信息项
                elif line.startswith('├──') or line.startswith('└──'):
                    if current_character:
                        item_info = line.lstrip('├── ').lstrip('└── ')
                        if '：' in item_info:
                            key, value = item_info.split('：', 1)
                            key = key.strip()
                            value = value.strip()

                            # 根据键分类存储信息
                            if '物品' in key or '道具' in key or '武器' in key or '饰品' in key or '遗物' in key:
                                current_character['items'].append(f"{key}: {value}")
                            elif '能力' in key:
                                current_character['abilities'].append(f"{key}: {value}")
                            elif '状态' in key:
                                current_character['state'] = value
                            elif '关系' in key:
                                current_character['relationships'].append(value)
                            else:
                                # 通用信息添加到描述
                                if current_character['description']:
                                    current_character['description'] += f"\n{key}: {value}"
                                else:
                                    current_character['description'] = f"{key}: {value}"

                # 处理段落信息（多行文本）
                elif line.startswith('│  ') and current_character:
                    info_text = line.lstrip('│  ')
                    if current_section:
                        if current_section not in current_character:
                            current_character[current_section] = []
                        current_character[current_section].append(info_text)
                    else:
                        # 添加到描述
                        if current_character['description']:
                            current_character['description'] += f"\n{info_text}"
                        else:
                            current_character['description'] = info_text

            # 添加最后一个角色
            if current_character:
                characters.append(current_character)

            # 如果解析成功，使用解析的数据
            if characters:
                self.characters = characters
                logger.info(f"成功解析出 {len(characters)} 个角色")
            else:
                # 解析失败，使用示例数据
                logger.warning("角色数据解析失败，使用示例数据")
                self._create_sample_characters()

        except Exception as e:
            logger.error(f"解析角色数据时出错: {e}")
            # 出错时使用示例数据
            self._create_sample_characters()

    def _determine_character_type(self, name: str) -> str:
        """根据角色名称判断角色类型"""
        name_lower = name.lower()
        if '格洛克' in name_lower:
            return '主角'
        elif any(keyword in name_lower for keyword in ['莉亚', '石拳', '腐爪', '铁颚', '柯尔']):
            return '主要角色'
        elif '新出场' in name_lower:
            return '新角色'
        else:
            return '配角'

    def _create_default_characters(self):
        """创建默认角色"""
        self._create_sample_characters()

    def _create_sample_characters(self):
        """创建示例角色"""
        sample_characters = [
            {
                "name": "主角",
                "type": "主角",
                "description": "故事的主要角色，经历各种冒险和成长",
                "traits": "勇敢、善良、有责任心",
                "state": "初始状态：准备开始冒险之旅",
                "relationships": []
            },
            {
                "name": "导师",
                "type": "配角",
                "description": "智慧和经验丰富的前辈角色",
                "traits": "智慧、耐心、神秘",
                "state": "当前状态：在暗中观察主角的成长",
                "relationships": []
            }
        ]

        for char_data in sample_characters:
            self._add_character_to_list(char_data)

    def _add_character_to_list(self, char_data: Dict[str, Any]):
        """添加角色到列表"""
        self.characters.append(char_data)
        self._create_character_item(char_data)

    def _create_character_item(self, char_data: Dict[str, Any]):
        """创建角色列表项"""
        # 创建角色项框架
        item_frame = ctk.CTkFrame(
            self.characters_scroll,
            fg_color="#333333",
            corner_radius=8
        )
        item_frame.pack(fill="x", padx=5, pady=3)

        # 角色名称
        name_label = ctk.CTkLabel(
            item_frame,
            text=char_data["name"],
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        name_label.pack(fill="x", padx=10, pady=(8, 2))

        # 角色类型
        type_label = ctk.CTkLabel(
            item_frame,
            text=char_data["type"],
            font=ctk.CTkFont(size=12),
            text_color="gray",
            anchor="w"
        )
        type_label.pack(fill="x", padx=10, pady=(0, 2))

        # 角色描述（截取前50字符）
        desc = char_data.get("description", "")
        if len(desc) > 50:
            desc = desc[:50] + "..."

        desc_label = ctk.CTkLabel(
            item_frame,
            text=desc,
            font=ctk.CTkFont(size=11),
            text_color="#CCCCCC",
            anchor="w",
            wraplength=250
        )
        desc_label.pack(fill="x", padx=10, pady=(0, 8))

        # 绑定点击事件
        def on_item_click(event=None):
            self._select_character(char_data)

        item_frame.bind("<Button-1>", on_item_click)
        name_label.bind("<Button-1>", on_item_click)
        type_label.bind("<Button-1>", on_item_click)
        desc_label.bind("<Button-1>", on_item_click)

        # 存储框架引用
        char_data["frame"] = item_frame

    def _select_character(self, char_data: Dict[str, Any]):
        """选择角色"""
        self.current_character = char_data

        # 更新角色信息
        self.character_name_entry.delete(0, "end")
        self.character_name_entry.insert(0, char_data["name"])

        self.character_type_var.set(char_data["type"])

        self.character_desc_text.delete("1.0", "end")
        self.character_desc_text.insert("1.0", char_data.get("description", ""))

        self.character_traits_text.delete("1.0", "end")
        self.character_traits_text.insert("1.0", char_data.get("traits", ""))

        self.character_state_text.delete("1.0", "end")
        self.character_state_text.insert("1.0", char_data.get("state", ""))

        # 更新关系列表
        self._update_relationships_list()

        # 高亮选中的角色项
        self._highlight_selected_character(char_data)

        # 触发回调
        if self.character_changed_callback:
            self.character_changed_callback(char_data)

    def _highlight_selected_character(self, selected_char: Dict[str, Any]):
        """高亮选中的角色项"""
        for char in self.characters:
            if "frame" in char and char["frame"]:
                try:
                    # 检查组件是否仍然存在
                    if char["frame"].winfo_exists():
                        if char == selected_char:
                            char["frame"].configure(fg_color="#404040")
                        else:
                            char["frame"].configure(fg_color="#333333")
                except Exception as e:
                    logger.debug(f"高亮角色项失败，组件可能已销毁: {e}")
                    # 如果组件已不存在，清理引用
                    char["frame"] = None

    def _add_new_character(self):
        """添加新角色"""
        # 创建新角色数据
        new_char = {
            "name": f"新角色{len(self.characters) + 1}",
            "type": "配角",
            "description": "",
            "traits": "",
            "state": "",
            "relationships": []
        }

        self._add_character_to_list(new_char)
        self._select_character(new_char)

        # 聚焦到名称输入框
        self.character_name_entry.focus_set()
        self.character_name_entry.select_range(0, "end")

    def _save_current_character(self):
        """保存当前角色"""
        if not self.current_character:
            messagebox.showwarning("警告", "请先选择一个角色")
            return

        try:
            # 更新角色数据
            self.current_character.update({
                "name": self.character_name_entry.get(),
                "type": self.character_type_var.get(),
                "description": self.character_desc_text.get("1.0", "end-1c"),
                "traits": self.character_traits_text.get("1.0", "end-1c"),
                "state": self.character_state_text.get("1.0", "end-1c")
            })

            # 更新列表显示
            self._update_character_display(self.current_character)

            # 保存到文件
            self._save_characters_to_file()

            messagebox.showinfo("成功", "角色保存成功！")

        except Exception as e:
            logger.error(f"保存角色失败: {e}")
            messagebox.showerror("错误", f"保存角色失败: {e}")

    def _delete_current_character(self):
        """删除当前角色"""
        if not self.current_character:
            messagebox.showwarning("警告", "请先选择一个角色")
            return

        if messagebox.askyesno("确认", f"确定要删除角色 '{self.current_character['name']}' 吗？"):
            try:
                # 从列表中移除
                if self.current_character in self.characters:
                    self.characters.remove(self.current_character)
                else:
                    logger.warning("要删除的角色不在列表中")
                    self._clear_character_form()
                    return

                # 安全地销毁UI框架
                if "frame" in self.current_character and self.current_character["frame"]:
                    try:
                        if self.current_character["frame"].winfo_exists():
                            self.current_character["frame"].destroy()
                    except Exception as e:
                        logger.debug(f"销毁角色UI框架失败: {e}")

                # 清空当前选择
                self.current_character = None
                self._clear_character_form()

                # 保存到文件
                self._save_characters_to_file()

                messagebox.showinfo("成功", "角色删除成功！")

            except Exception as e:
                logger.error(f"删除角色失败: {e}")
                messagebox.showerror("错误", f"删除角色失败: {e}")

    def _refresh_characters(self):
        """刷新角色数据"""
        try:
            self._log("🔄 开始刷新角色数据...")

            # 重新加载角色数据
            self._load_characters_data()

            # 刷新角色列表显示
            self._refresh_characters_display()

            # 如果使用数据桥接器，通知数据更新
            if self.data_bridge:
                try:
                    # 通知数据桥接器更新
                    success = self.data_bridge.update_characters(self.characters)
                    if success:
                        self._log("✅ 角色数据刷新完成")
                    else:
                        self._log("⚠️ 数据桥接器更新失败")
                except Exception as e:
                    self._log(f"⚠️ 刷新角色数据时出现错误: {e}")
                    logger.error(f"数据桥接器更新失败: {e}")
            else:
                # 传统刷新方式
                self._log("✅ 角色显示刷新完成")

        except Exception as e:
            self._log(f"❌ 刷新角色数据失败: {e}")
            logger.error(f"刷新角色数据失败: {e}")

    def _refresh_characters_display(self):
        """刷新角色显示"""
        try:
            # 清理角色的frame引用
            for char in self.characters:
                if "frame" in char:
                    char["frame"] = None

            # 清空现有的角色列表显示
            for widget in self.characters_scroll.winfo_children():
                widget.destroy()

            # 重新创建角色列表项
            for char_data in self.characters:
                self._create_character_item(char_data)

            logger.info(f"角色显示刷新完成，共 {len(self.characters)} 个角色")
        except Exception as e:
            logger.error(f"刷新角色显示失败: {e}")

    def _log(self, message: str):
        """记录日志信息到生成日志标签页"""
        try:
            # 尝试获取主窗口的生成日志标签页
            import logging
            logger = logging.getLogger(__name__)
            logger.info(message)
        except Exception:
            # 如果日志记录失败，静默处理
            pass

    def _create_character_display_item(self, character: Dict[str, Any], index: int):
        """创建角色显示项"""
        try:
            if not hasattr(self, 'characters_display_frame'):
                return

            # 创建角色框架
            char_frame = ctk.CTkFrame(self.characters_display_frame)
            char_frame.pack(fill="x", padx=5, pady=2)

            # 角色名称
            name = character.get('name', f'角色{index+1}')
            name_label = ctk.CTkLabel(char_frame, text=name, font=ctk.CTkFont(size=12, weight="bold"))
            name_label.pack(side="left", padx=10, pady=5)

            # 角色描述
            description = character.get('description', '暂无描述')
            desc_label = ctk.CTkLabel(char_frame, text=description, font=ctk.CTkFont(size=10))
            desc_label.pack(side="left", padx=5, pady=5)

        except Exception as e:
            logger.error(f"创建角色显示项失败: {e}")

    def _update_character_display(self, char_data: Dict[str, Any]):
        """更新角色显示"""
        if "frame" not in char_data:
            return

        frame = char_data["frame"]
        widgets = frame.winfo_children()

        # 更新名称
        if widgets:
            widgets[0].configure(text=char_data["name"])

        # 更新类型
        if len(widgets) > 1:
            widgets[1].configure(text=char_data["type"])

        # 更新描述
        if len(widgets) > 2:
            desc = char_data.get("description", "")
            if len(desc) > 50:
                desc = desc[:50] + "..."
            widgets[2].configure(text=desc)

    def _clear_character_form(self):
        """清空角色表单"""
        self.character_name_entry.delete(0, "end")
        self.character_type_var.set("配角")
        self.character_desc_text.delete("1.0", "end")
        self.character_traits_text.delete("1.0", "end")
        self.character_state_text.delete("1.0", "end")

    def _save_characters_to_file(self):
        """保存角色到文件"""
        try:
            # 这里实现角色数据保存逻辑
            # 暂时保存为简单的文本格式
            content = "角色状态文件\n\n"
            for char in self.characters:
                content += f"角色: {char['name']}\n"
                content += f"类型: {char['type']}\n"
                content += f"描述: {char.get('description', '')}\n"
                content += f"特征: {char.get('traits', '')}\n"
                content += f"状态: {char.get('state', '')}\n"
                content += "-" * 50 + "\n\n"

            save_string_to_txt(content, "character_state.txt")

        except Exception as e:
            logger.error(f"保存角色文件失败: {e}")

    def _on_character_search(self, event):
        """角色搜索处理"""
        search_text = event.widget.get().lower()

        for char in self.characters:
            if "frame" in char:
                # 检查是否匹配搜索
                name_match = search_text in char["name"].lower()
                desc_match = search_text in char.get("description", "").lower()
                type_match = search_text in char["type"].lower()

                if name_match or desc_match or type_match:
                    char["frame"].pack(fill="x", padx=5, pady=3)
                else:
                    char["frame"].pack_forget()

    def _add_relationship(self):
        """添加角色关系"""
        if not self.current_character:
            messagebox.showwarning("警告", "请先选择一个角色")
            return

        target = self.relationship_target_var.get()
        rel_type = self.relationship_type_var.get()

        if not target:
            messagebox.showwarning("警告", "请选择关联角色")
            return

        # 添加关系
        if "relationships" not in self.current_character:
            self.current_character["relationships"] = []

        self.current_character["relationships"].append({
            "target": target,
            "type": rel_type
        })

        # 更新关系显示
        self._update_relationships_list()

        # 清空选择
        self.relationship_target_var.set("")

    def _update_relationships_list(self):
        """更新关系列表"""
        # 清空现有关系项
        for widget in self.relationships_frame.winfo_children():
            widget.destroy()

        if not self.current_character:
            return

        relationships = self.current_character.get("relationships", [])

        for rel in relationships:
            rel_frame = ctk.CTkFrame(
                self.relationships_frame,
                fg_color="#333333",
                corner_radius=6
            )
            rel_frame.pack(fill="x", padx=5, pady=3)

            # 关系显示
            rel_text = f"{self.current_character['name']} → {rel['target']} ({rel['type']})"
            rel_label = ctk.CTkLabel(
                rel_frame,
                text=rel_text,
                anchor="w"
            )
            rel_label.pack(fill="x", padx=10, pady=8)

            # 删除按钮
            delete_btn = ctk.CTkButton(
                rel_frame,
                text="×",
                width=30,
                height=30,
                fg_color="#D32F2F",
                hover_color="#F44336",
                command=lambda r=rel: self._delete_relationship(r)
            )
            delete_btn.pack(side="right", padx=(5, 10))

    def _delete_relationship(self, relationship: Dict[str, str]):
        """删除关系"""
        if self.current_character and "relationships" in self.current_character:
            self.current_character["relationships"].remove(relationship)
            self._update_relationships_list()

    def _export_character(self):
        """导出角色"""
        if not self.current_character:
            messagebox.showwarning("警告", "请先选择一个角色")
            return

        try:
            # 生成导出内容
            content = f"角色: {self.current_character['name']}\n"
            content += f"类型: {self.current_character['type']}\n"
            content += f"描述: {self.current_character.get('description', '')}\n"
            content += f"特征: {self.current_character.get('traits', '')}\n"
            content += f"状态: {self.current_character.get('state', '')}\n"

            # 保存到文件
            filename = f"character_{self.current_character['name']}.txt"
            save_string_to_txt(content, filename)

            messagebox.showinfo("成功", f"角色已导出到 {filename}")

        except Exception as e:
            logger.error(f"导出角色失败: {e}")
            messagebox.showerror("错误", f"导出角色失败: {e}")

    def set_character_changed_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """设置角色变化回调函数"""
        self.character_changed_callback = callback

    def get_current_character(self) -> Optional[Dict[str, Any]]:
        """获取当前选中的角色"""
        return self.current_character

    def get_all_characters(self) -> List[Dict[str, Any]]:
        """获取所有角色"""
        return self.characters

    def apply_theme_style(self, theme_data: Dict[str, Any]):
        """应用主题样式"""
        try:
            colors = theme_data.get('colors', {})

            # 更新标签页样式
            if hasattr(self, 'detail_tabview'):
                self.detail_tabview.configure(
                    segmented_button_fg_color=colors.get('surface', '#2A2A2A'),
                    segmented_button_selected_color=colors.get('primary', '#404040'),
                    segmented_button_unselected_color=colors.get('background', '#1E1E1E')
                )

        except Exception as e:
            logger.error(f"应用主题到角色标签页失败: {e}")

    def get_characters_info(self) -> Dict[str, Any]:
        """获取角色标签页信息"""
        return {
            'total_characters': len(self.characters),
            'current_character': self.current_character['name'] if self.current_character else None,
            'has_callback': self.character_changed_callback is not None
        }