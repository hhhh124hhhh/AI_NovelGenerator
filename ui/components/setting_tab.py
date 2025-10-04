"""
现代化设定标签页组件 - AI小说生成器的小说设定编辑界面
包含小说架构编辑、保存、加载等功能
"""

import logging
import os
from typing import Dict, Any, Optional, Callable
import customtkinter as ctk
from tkinter import messagebox, scrolledtext
from datetime import datetime

logger = logging.getLogger(__name__)


class SettingTab(ctk.CTkFrame):
    """
    现代化设定标签页组件

    功能：
    - 小说架构编辑
    - 设定文件保存和加载
    - 实时字数统计
    - 自动保存功能
    """

    def __init__(self, parent: ctk.CTkFrame, theme_manager, state_manager=None, main_window=None, **kwargs):
        """
        初始化设定标签页

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

        # 当前项目路径
        self.current_project_path = ""
        self.auto_save_enabled = True

        # 回调函数
        self.setting_changed_callback = None

        # 创建界面
        self._create_layout()

        # 加载当前项目设定
        self._load_current_setting()

        logger.info("设定标签页初始化完成")

    def _create_layout(self):
        """创建布局"""
        # 配置主框架
        self.configure(
            corner_radius=8,
            fg_color="transparent"
        )

        # 创建标题区域
        self._create_header_area()

        # 创建工具栏
        self._create_toolbar()

        # 创建编辑区域
        self._create_editor_area()

        # 创建状态栏
        self._create_status_bar()

    def _create_header_area(self):
        """创建标题区域"""
        header_frame = ctk.CTkFrame(self, fg_color="#2A2A2A", corner_radius=8)
        header_frame.pack(fill="x", padx=10, pady=(10, 5))

        # 标题
        title_label = ctk.CTkLabel(
            header_frame,
            text="📚 小说设定编辑器",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=15)

        # 描述
        desc_label = ctk.CTkLabel(
            header_frame,
            text="编辑小说的世界观、角色设定、背景设定等核心内容",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        desc_label.pack(pady=(0, 15))

    def _create_toolbar(self):
        """创建工具栏"""
        toolbar_frame = ctk.CTkFrame(self, fg_color="#2A2A2A", corner_radius=8)
        toolbar_frame.pack(fill="x", padx=10, pady=5)

        # 左侧按钮组
        left_buttons = ctk.CTkFrame(toolbar_frame, fg_color="transparent")
        left_buttons.pack(side="left", fill="x", expand=True, padx=10, pady=10)

        # 刷新按钮
        refresh_btn = ctk.CTkButton(
            left_buttons,
            text="🔄 刷新",
            command=self._refresh_setting,
            width=100,
            fg_color="#1976D2",
            hover_color="#2196F3"
        )
        refresh_btn.pack(side="left", padx=(0, 5))

        # 保存按钮
        save_btn = ctk.CTkButton(
            left_buttons,
            text="💾 保存",
            command=self._save_setting,
            width=100,
            fg_color="#2E7D32",
            hover_color="#388E3C"
        )
        save_btn.pack(side="left", padx=5)

        # 清空按钮
        clear_btn = ctk.CTkButton(
            left_buttons,
            text="🗑️ 清空",
            command=self._clear_setting,
            width=100,
            fg_color="#D32F2F",
            hover_color="#F44336"
        )
        clear_btn.pack(side="left", padx=5)

        # 右侧选项组
        right_options = ctk.CTkFrame(toolbar_frame, fg_color="transparent")
        right_options.pack(side="right", padx=10, pady=10)

        # 自动保存选项
        self.auto_save_var = ctk.BooleanVar(value=True)
        auto_save_check = ctk.CTkCheckBox(
            right_options,
            text="自动保存",
            variable=self.auto_save_var,
            command=self._toggle_auto_save
        )
        auto_save_check.pack(side="right", padx=5)

    def _create_editor_area(self):
        """创建编辑区域"""
        editor_frame = ctk.CTkFrame(self, fg_color="#2A2A2A", corner_radius=8)
        editor_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # 创建文本编辑器
        self.setting_text = ctk.CTkTextbox(
            editor_frame,
            font=ctk.CTkFont(family="Microsoft YaHei", size=12),
            wrap="word",
            undo=True
        )
        self.setting_text.pack(fill="both", expand=True, padx=10, pady=10)

        # 绑定文本变化事件
        self.setting_text.bind("<KeyRelease>", self._on_text_changed)
        self.setting_text.bind("<Button-1>", self._on_text_changed)

    def _create_status_bar(self):
        """创建状态栏"""
        status_frame = ctk.CTkFrame(self, fg_color="#2A2A2A", corner_radius=8)
        status_frame.pack(fill="x", padx=10, pady=(5, 10))

        # 字数统计
        self.word_count_label = ctk.CTkLabel(
            status_frame,
            text="字数: 0",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.word_count_label.pack(side="left", padx=10, pady=5)

        # 文件路径
        self.file_path_label = ctk.CTkLabel(
            status_frame,
            text="文件: 未加载",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.file_path_label.pack(side="left", padx=10, pady=5)

        # 最后保存时间
        self.last_save_label = ctk.CTkLabel(
            status_frame,
            text="最后保存: 从未",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.last_save_label.pack(side="right", padx=10, pady=5)

    def _update_word_count(self):
        """更新字数统计"""
        try:
            content = self.setting_text.get("0.0", "end").strip()
            word_count = len(content)
            self.word_count_label.configure(text=f"字数: {word_count:,}")
        except Exception as e:
            logger.error(f"更新字数统计失败: {e}")

    def _update_file_path(self):
        """更新文件路径显示"""
        if self.current_project_path:
            file_path = os.path.join(self.current_project_path, "Novel_architecture.txt")
            self.file_path_label.configure(text=f"文件: {os.path.basename(file_path)}")
        else:
            self.file_path_label.configure(text="文件: 未设置项目路径")

    def _update_last_save_time(self):
        """更新最后保存时间"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.last_save_label.configure(text=f"最后保存: {current_time}")

    def _on_text_changed(self, event=None):
        """文本变化事件处理"""
        self._update_word_count()

        # 通知设定变化
        if self.setting_changed_callback:
            content = self.setting_text.get("0.0", "end").strip()
            self.setting_changed_callback(content)

        # 自动保存
        if self.auto_save_enabled and self.current_project_path:
            # 延迟自动保存，避免频繁保存
            if hasattr(self, '_auto_save_timer'):
                self.after_cancel(self._auto_save_timer)
            self._auto_save_timer = self.after(3000, self._auto_save)  # 3秒后自动保存

    def _toggle_auto_save(self):
        """切换自动保存"""
        self.auto_save_enabled = self.auto_save_var.get()
        logger.info(f"自动保存: {'启用' if self.auto_save_enabled else '禁用'}")

    def _auto_save(self):
        """自动保存"""
        if self.auto_save_enabled and self.current_project_path:
            try:
                self._save_setting_internal()
                logger.debug("自动保存完成")
            except Exception as e:
                logger.error(f"自动保存失败: {e}")

    def _get_current_project_path(self):
        """获取当前项目路径"""
        # 尝试从状态管理器获取
        if self.state_manager:
            path = self.state_manager.get_state('last_project_path', '')
            if path and os.path.exists(path):
                return path

        # 尝试从主窗口获取
        if self.main_window and hasattr(self.main_window, 'main_workspace'):
            workspace = self.main_window.main_workspace
            if hasattr(workspace, 'filepath_var'):
                path = workspace.filepath_var.get()
                if path and os.path.exists(path):
                    return path

        return ""

    def _load_current_setting(self):
        """加载当前项目设定"""
        try:
            self.current_project_path = self._get_current_project_path()

            if not self.current_project_path:
                logger.info("未设置项目路径，跳过加载设定")
                return

            # 构建文件路径
            setting_file = os.path.join(self.current_project_path, "Novel_architecture.txt")

            if os.path.exists(setting_file):
                with open(setting_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                self.setting_text.delete("0.0", "end")
                self.setting_text.insert("0.0", content)

                self._update_file_path()
                self._update_word_count()

                logger.info(f"成功加载设定文件: {setting_file}")
            else:
                logger.info(f"设定文件不存在: {setting_file}")
                # 创建默认内容
                default_content = self._get_default_setting_content()
                self.setting_text.insert("0.0", default_content)

        except Exception as e:
            logger.error(f"加载设定文件失败: {e}")
            messagebox.showerror("错误", f"加载设定文件失败: {e}")

    def _get_default_setting_content(self):
        """获取默认设定内容"""
        return """# 小说设定

## 世界观设定
请在此处描述小说的世界观背景...

## 主要角色
请在此处描述主要角色设定...

## 故事背景
请在此处描述故事背景设定...

## 核心设定
请在此处描述核心设定和规则...
"""

    def _refresh_setting(self):
        """刷新设定"""
        try:
            # 保存当前内容
            current_content = self.setting_text.get("0.0", "end").strip()

            # 重新加载
            self._load_current_setting()

            messagebox.showinfo("成功", "设定已刷新")
            logger.info("设定刷新完成")

        except Exception as e:
            logger.error(f"刷新设定失败: {e}")
            messagebox.showerror("错误", f"刷新设定失败: {e}")

    def _save_setting(self):
        """保存设定"""
        try:
            self._save_setting_internal()
            messagebox.showinfo("成功", "设定已保存")
            logger.info("手动保存设定完成")

        except Exception as e:
            logger.error(f"保存设定失败: {e}")
            messagebox.showerror("错误", f"保存设定失败: {e}")

    def _save_setting_internal(self):
        """内部保存方法"""
        # 获取当前项目路径
        if not self.current_project_path:
            self.current_project_path = self._get_current_project_path()

        if not self.current_project_path:
            raise Exception("未设置项目路径，无法保存设定")

        # 确保项目目录存在
        os.makedirs(self.current_project_path, exist_ok=True)

        # 构建文件路径
        setting_file = os.path.join(self.current_project_path, "Novel_architecture.txt")

        # 保存内容
        content = self.setting_text.get("0.0", "end").strip()
        with open(setting_file, 'w', encoding='utf-8') as f:
            f.write(content)

        # 更新状态
        self._update_file_path()
        self._update_last_save_time()

    def _clear_setting(self):
        """清空设定"""
        if messagebox.askyesno("确认", "确定要清空所有设定内容吗？此操作不可撤销。"):
            self.setting_text.delete("0.0", "end")
            self._update_word_count()
            logger.info("设定内容已清空")

    def set_setting_changed_callback(self, callback: Callable):
        """设置设定变化回调"""
        self.setting_changed_callback = callback

    def set_save_path(self, path: str):
        """设置保存路径"""
        self.current_project_path = path
        self._update_file_path()
        logger.info(f"设定页面保存路径已更新: {path}")

    def refresh_content(self):
        """刷新内容"""
        self._load_current_setting()