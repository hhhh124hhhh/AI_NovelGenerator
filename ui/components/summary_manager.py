"""
现代化摘要管理组件 - AI小说生成器的摘要和角色状态管理
迁移自1.0版本的summary_tab.py和character_tab.py功能，采用2.0架构重构
"""

import logging
import os
from typing import Dict, Any, Optional, Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from config_manager import load_config
import customtkinter as ctk
from tkinter import messagebox, filedialog
from config_manager import load_config

logger = logging.getLogger(__name__)


class SummaryManager(ctk.CTkFrame):
    """
    现代化摘要管理组件

    功能：
    - 全局摘要编辑和管理
    - 角色状态跟踪和管理
    - 摘要和角色状态的加载/保存
    - 字数统计和状态同步
    - 导出功能
    """

    def __init__(self, parent: ctk.CTkFrame, theme_manager, state_manager=None, **kwargs):
        """
        初始化摘要管理器

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

        # 配置数据
        self.config_data: Dict[str, Any] = load_config("config.json")
        self.project_data = {}

        # 组件引用
        self.summary_tabview = None
        self.global_summary_text = None
        self.character_state_text = None
        self.word_count_labels = {}

        # 回调函数
        self.summary_changed_callback = None
        self.character_changed_callback = None

        # 初始化组件
        self._create_summary_layout()
        self._initialize_data()
        self._setup_event_handlers()

        logger.debug("SummaryManager 组件初始化完成")

    def _create_summary_layout(self):
        """创建摘要管理布局"""
        # 配置主框架
        self.configure(
            corner_radius=8,
            fg_color="transparent"
        )

        # 创建摘要选项卡
        self.summary_tabview = ctk.CTkTabview(
            self,
            segmented_button_fg_color="#2A2A2A",
            segmented_button_selected_color="#404040",
            segmented_button_unselected_color="#1E1E1E"
        )
        self.summary_tabview.pack(fill="both", expand=True, padx=10, pady=10)

        # 添加选项卡
        global_summary_tab = self.summary_tabview.add("📋 全局摘要")
        character_state_tab = self.summary_tabview.add("👥 角色状态")

        # 构建各个页面
        self._build_global_summary_tab(global_summary_tab)
        self._build_character_state_tab(character_state_tab)

    def _build_global_summary_tab(self, parent: ctk.CTkFrame):
        """构建全局摘要页面"""
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)

        # 摘要标题区域
        header_frame = ctk.CTkFrame(parent, corner_radius=8)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        header_frame.grid_columnconfigure(1, weight=1)

        # 标题标签
        title_label = ctk.CTkLabel(
            header_frame,
            text="📋 全局摘要",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # 字数统计
        self.word_count_labels['summary'] = ctk.CTkLabel(
            header_frame,
            text="字数: 0",
            font=ctk.CTkFont(size=12)
        )
        self.word_count_labels['summary'].grid(row=0, column=1, padx=10, pady=10, sticky="e")

        # 摘要编辑区域
        self.global_summary_text = ctk.CTkTextbox(
            parent,
            wrap="word",
            font=ctk.CTkFont(size=14),
            height=400
        )
        self.global_summary_text.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

        # 绑定字数统计
        self.global_summary_text.bind("<KeyRelease>", lambda e: self._update_word_count('summary'))
        self.global_summary_text.bind("<ButtonRelease>", lambda e: self._update_word_count('summary'))

        # 操作按钮区域
        self._create_action_buttons(parent, "summary", row=2)

    def _build_character_state_tab(self, parent: ctk.CTkFrame):
        """构建角色状态页面"""
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)

        # 角色标题区域
        header_frame = ctk.CTkFrame(parent, corner_radius=8)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        header_frame.grid_columnconfigure(1, weight=1)

        # 标题标签
        title_label = ctk.CTkLabel(
            header_frame,
            text="👥 角色状态",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # 字数统计
        self.word_count_labels['character'] = ctk.CTkLabel(
            header_frame,
            text="字数: 0",
            font=ctk.CTkFont(size=12)
        )
        self.word_count_labels['character'].grid(row=0, column=1, padx=10, pady=10, sticky="e")

        # 角色状态编辑区域
        self.character_state_text = ctk.CTkTextbox(
            parent,
            wrap="word",
            font=ctk.CTkFont(size=14),
            height=400
        )
        self.character_state_text.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

        # 绑定字数统计
        self.character_state_text.bind("<KeyRelease>", lambda e: self._update_word_count('character'))
        self.character_state_text.bind("<ButtonRelease>", lambda e: self._update_word_count('character'))

        # 操作按钮区域
        self._create_action_buttons(parent, "character", row=2)

    def _create_action_buttons(self, parent: ctk.CTkFrame, content_type: str, row: int):
        """创建操作按钮区域"""
        # 按钮容器
        btn_frame = ctk.CTkFrame(parent, corner_radius=8)
        btn_frame.grid(row=row, column=0, sticky="ew", padx=10, pady=(5, 10))
        btn_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # 按钮定义
        buttons = [
            ("🔄 刷新", self._load_content, content_type),
            ("💾 保存", self._save_content, content_type),
            ("📤 导出", self._export_content, content_type),
            ("🗑️ 清空", self._clear_content, content_type)
        ]

        for i, (text, command, cmd_type) in enumerate(buttons):
            btn = ctk.CTkButton(
                btn_frame,
                text=text,
                command=lambda ct=cmd_type, func=command: func(ct),
                font=ctk.CTkFont(size=12),
                height=35
            )
            btn.grid(row=0, column=i, padx=2, pady=8, sticky="ew")

    def _initialize_data(self):
        """初始化数据"""
        try:
            # 从配置中获取保存路径
            self.save_path = self.config_data.get("other_params", {}).get("filepath", "")

            # 尝试加载现有数据
            self._load_content("summary")
            self._load_content("character")

        except Exception as e:
            logger.error(f"初始化数据失败: {e}")

    def _setup_event_handlers(self):
        """设置事件处理器"""
        # 绑定内容变化事件
        if self.global_summary_text:
            self.global_summary_text.bind("<KeyRelease>", lambda e: self._on_content_changed("summary"))
            self.global_summary_text.bind("<ButtonRelease>", lambda e: self._on_content_changed("summary"))

        if self.character_state_text:
            self.character_state_text.bind("<KeyRelease>", lambda e: self._on_content_changed("character"))
            self.character_state_text.bind("<ButtonRelease>", lambda e: self._on_content_changed("character"))

    def _update_word_count(self, content_type: str):
        """更新字数统计"""
        try:
            if content_type == "summary" and self.global_summary_text:
                text = self.global_summary_text.get("0.0", "end")
                count = len(text) - 1
                self.word_count_labels['summary'].configure(text=f"字数: {count}")
            elif content_type == "character" and self.character_state_text:
                text = self.character_state_text.get("0.0", "end")
                count = len(text) - 1
                self.word_count_labels['character'].configure(text=f"字数: {count}")
        except Exception as e:
            logger.error(f"更新字数统计失败: {e}")

    def _on_content_changed(self, content_type: str):
        """内容变化回调"""
        try:
            # 通知状态管理器内容变化
            if self.state_manager:
                content = self.get_content(content_type)
                self.state_manager.update_state({
                    f'summary.{content_type}': content,
                    'summary.modified': True
                })

            # 调用外部回调
            if content_type == "summary" and self.summary_changed_callback:
                self.summary_changed_callback(self.get_content("summary"))
            elif content_type == "character" and self.character_changed_callback:
                self.character_changed_callback(self.get_content("character"))

        except Exception as e:
            logger.error(f"处理内容变化失败: {e}")

    def _load_content(self, content_type: str):
        """加载内容"""
        try:
            content = ""

            if content_type == "summary":
                filename = "global_summary.txt"
                text_widget = self.global_summary_text
            elif content_type == "character":
                filename = "character_state.txt"
                text_widget = self.character_state_text
            else:
                return

            # 构建文件路径
            if self.save_path:
                full_path = os.path.join(self.save_path, filename)
            else:
                full_path = filename

            # 读取文件内容
            if os.path.exists(full_path):
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()

            # 更新文本框
            if text_widget:
                text_widget.delete("0.0", "end")
                text_widget.insert("0.0", content)
                self._update_word_count(content_type)

            logger.info(f"已加载{content_type}内容")

        except Exception as e:
            logger.error(f"加载{content_type}内容失败: {e}")

    def _save_content(self, content_type: str):
        """保存内容"""
        try:
            if content_type == "summary":
                filename = "global_summary.txt"
                text_widget = self.global_summary_text
            elif content_type == "character":
                filename = "character_state.txt"
                text_widget = self.character_state_text
            else:
                return

            # 获取内容
            if text_widget:
                content = text_widget.get("0.0", "end").strip()
            else:
                content = ""

            # 构建文件路径
            if self.save_path:
                full_path = os.path.join(self.save_path, filename)
            else:
                full_path = filename

            # 确保目录存在
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            # 保存文件
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"已保存{content_type}内容到 {full_path}")

        except Exception as e:
            logger.error(f"保存{content_type}内容失败: {e}")

    def _export_content(self, content_type: str):
        """导出内容"""
        try:
            if content_type == "summary":
                content = self.get_content("summary")
                default_name = "global_summary_export"
                text_widget = self.global_summary_text
            elif content_type == "character":
                content = self.get_content("character")
                default_name = "character_state_export"
                text_widget = self.character_state_text
            else:
                return

            if not content.strip():
                messagebox.showwarning("导出提示", "没有内容可以导出")
                return

            # 选择保存位置
            export_path = filedialog.asksaveasfilename(
                title=f"导出{content_type}",
                defaultextension=".txt",
                initialfile=default_name,
                filetypes=[
                    ("文本文件", "*.txt"),
                    ("Markdown文件", "*.md"),
                    ("JSON文件", "*.json"),
                    ("所有文件", "*.*")
                ]
            )

            if export_path:
                # 根据文件扩展名处理内容
                file_ext = os.path.splitext(export_path)[1].lower()

                if file_ext == '.json':
                    # 导出为JSON格式
                    export_data = {
                        'type': content_type,
                        'content': content,
                        'created_at': str(os.path.getctime(export_path) if os.path.exists(export_path) else ''),
                        'word_count': len(content)
                    }
                    import json
                    with open(export_path, 'w', encoding='utf-8') as f:
                        json.dump(export_data, f, ensure_ascii=False, indent=2)
                else:
                    # 导出为文本格式
                    with open(export_path, 'w', encoding='utf-8') as f:
                        f.write(content)

                logger.info(f"已导出{content_type}内容到 {export_path}")

        except Exception as e:
            logger.error(f"导出{content_type}内容失败: {e}")

    def _clear_content(self, content_type: str):
        """清空内容"""
        try:
            # 确认对话框
            if content_type == "summary":
                confirm_text = "确定要清空全局摘要吗？"
                text_widget = self.global_summary_text
            elif content_type == "character":
                confirm_text = "确定要清空角色状态吗？"
                text_widget = self.character_state_text
            else:
                return

            if messagebox.askyesno("确认清空", confirm_text):
                # 清空文本框
                if text_widget:
                    text_widget.delete("0.0", "end")
                    self._update_word_count(content_type)

                logger.info(f"已清空{content_type}内容")

        except Exception as e:
            logger.error(f"清空{content_type}内容失败: {e}")

    # 公共接口方法
    def get_content(self, content_type: str) -> str:
        """获取内容"""
        try:
            if content_type == "summary" and self.global_summary_text:
                return self.global_summary_text.get("0.0", "end").strip()
            elif content_type == "character" and self.character_state_text:
                return self.character_state_text.get("0.0", "end").strip()
            return ""
        except Exception as e:
            logger.error(f"获取{content_type}内容失败: {e}")
            return ""

    def set_content(self, content_type: str, content: str):
        """设置内容"""
        try:
            if content_type == "summary" and self.global_summary_text:
                self.global_summary_text.delete("0.0", "end")
                self.global_summary_text.insert("0.0", content)
                self._update_word_count("summary")
            elif content_type == "character" and self.character_state_text:
                self.character_state_text.delete("0.0", "end")
                self.character_state_text.insert("0.0", content)
                self._update_word_count("character")
        except Exception as e:
            logger.error(f"设置{content_type}内容失败: {e}")

    def get_summary_data(self) -> Dict[str, Any]:
        """获取摘要数据"""
        return {
            'global_summary': self.get_content("summary"),
            'character_state': self.get_content("character"),
            'word_counts': {
                'summary': len(self.get_content("summary")),
                'character': len(self.get_content("character"))
            }
        }

    def save_all(self):
        """保存所有内容"""
        self._save_content("summary")
        self._save_content("character")

    def load_all(self):
        """加载所有内容"""
        self._load_content("summary")
        self._load_content("character")

    def set_summary_changed_callback(self, callback: Callable):
        """设置摘要变化回调"""
        self.summary_changed_callback = callback

    def set_character_changed_callback(self, callback: Callable):
        """设置角色变化回调"""
        self.character_changed_callback = callback