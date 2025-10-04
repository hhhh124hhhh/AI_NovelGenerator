"""
现代化角色管理标签页组件 - AI小说生成器的角色管理界面
包含角色创建、编辑、状态跟踪等功能
"""

import logging
import os
from typing import Dict, Any, Optional, Callable, List
import customtkinter as ctk
from tkinter import messagebox
from utils import read_file, save_string_to_txt

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

    def __init__(self, parent: ctk.CTkFrame, theme_manager, state_manager=None, **kwargs):
        """
        初始化角色管理标签页

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

        # 角色数据
        self.characters = []
        self.current_character = None

        # 组件引用
        self.characters_listbox = None
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
        # 标题
        title_label = ctk.CTkLabel(
            self.left_panel,
            text="角色列表",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(10, 15))

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

    def _load_characters_data(self):
        """加载角色数据"""
        try:
            # 尝试从文件加载角色状态
            content = read_file("character_state.txt")
            if content:
                # 解析角色数据（这里简化处理，实际应该解析JSON或其他格式）
                self._parse_character_data(content)
            else:
                # 创建默认角色
                self._create_default_characters()

        except FileNotFoundError:
            logger.info("未找到角色状态文件，创建默认角色")
            self._create_default_characters()
        except Exception as e:
            logger.error(f"加载角色数据失败: {e}")
            self._create_default_characters()

    def _parse_character_data(self, content: str):
        """解析角色数据"""
        # 这里实现角色数据解析逻辑
        # 暂时创建示例数据
        self._create_sample_characters()

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
            if "frame" in char:
                if char == selected_char:
                    char["frame"].configure(fg_color="#404040")
                else:
                    char["frame"].configure(fg_color="#333333")

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
                self.characters.remove(self.current_character)

                # 销毁UI框架
                if "frame" in self.current_character:
                    self.current_character["frame"].destroy()

                # 清空当前选择
                self.current_character = None
                self._clear_character_form()

                # 保存到文件
                self._save_characters_to_file()

                messagebox.showinfo("成功", "角色删除成功！")

            except Exception as e:
                logger.error(f"删除角色失败: {e}")
                messagebox.showerror("错误", f"删除角色失败: {e}")

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