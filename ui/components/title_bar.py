"""
现代化标题栏组件 - AI小说生成器的主界面顶部区域
包含应用标题、搜索框、用户区域和操作按钮
"""

import logging
from typing import Dict, Any, Optional, Callable, List
import customtkinter as ctk
from .base_components import StyledComponent

logger = logging.getLogger(__name__)


class TitleBar(ctk.CTkFrame):
    """
    现代化标题栏组件

    功能：
    - 应用标题和logo
    - 全局搜索框
    - 用户操作区域
    - 窗口控制按钮
    - 响应式布局支持
    """

    def __init__(self, parent: ctk.CTk, theme_manager, state_manager=None, **kwargs):
        """
        初始化标题栏

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

        # 回调函数
        self.search_callback = None
        self.user_menu_callback = None
        self.settings_callback = None

        # 组件引用
        self.app_title_label = None
        self.search_entry = None
        self.user_button = None
        self.settings_button = None

        # 响应式状态
        self.is_compact = False
        self.search_visible = True

        # 初始化组件
        self._create_title_bar_layout()
        self._create_app_title_section()
        self._create_search_section()
        self._create_user_section()
        self._bind_custom_events()

        logger.debug("TitleBar 组件初始化完成")

    def _create_title_bar_layout(self):
        """创建标题栏布局"""
        # 配置主框架布局
        self.configure(
            corner_radius=0,
            height=60,
            fg_color="transparent"
        )

        # 创建内容框架
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # 配置网格布局
        self.content_frame.grid_columnconfigure(0, weight=0)  # 左侧标题
        self.content_frame.grid_columnconfigure(1, weight=1)  # 中间搜索
        self.content_frame.grid_columnconfigure(2, weight=0)  # 右侧用户区域

    def _create_app_title_section(self):
        """创建应用标题区域"""
        # 左侧标题区域
        self.title_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.title_frame.grid(row=0, column=0, sticky="w", padx=(0, 10))

        # 应用标题
        self.app_title_label = ctk.CTkLabel(
            self.title_frame,
            text="AI小说生成器",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w"
        )
        self.app_title_label.pack(side="left", padx=(0, 5))

        # 版本标签
        self.version_label = ctk.CTkLabel(
            self.title_frame,
            text="v2.0",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.version_label.pack(side="left")

    def _create_search_section(self):
        """创建搜索区域"""
        # 搜索容器
        self.search_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.search_frame.grid(row=0, column=1, sticky="ew", padx=10)

        # 搜索框
        self.search_entry = ctk.CTkEntry(
            self.search_frame,
            placeholder_text="搜索功能、设置或帮助...",
            width=300,
            height=32,
            corner_radius=16,
            font=ctk.CTkFont(size=12)
        )
        self.search_entry.pack(fill="x", expand=True)

        # 绑定搜索事件
        self.search_entry.bind("<Return>", self._on_search_enter)
        self.search_entry.bind("<FocusIn>", self._on_search_focus_in)
        self.search_entry.bind("<FocusOut>", self._on_search_focus_out)

    def _create_user_section(self):
        """创建用户操作区域"""
        # 右侧用户区域
        self.user_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.user_frame.grid(row=0, column=2, sticky="e", padx=(10, 0))

        # 设置按钮
        self.settings_button = ctk.CTkButton(
            self.user_frame,
            text="⚙",
            width=36,
            height=36,
            corner_radius=18,
            font=ctk.CTkFont(size=16),
            fg_color="transparent",
            text_color="gray"
        )
        self.settings_button.pack(side="left", padx=2)

        # 用户按钮
        self.user_button = ctk.CTkButton(
            self.user_frame,
            text="👤",
            width=36,
            height=36,
            corner_radius=18,
            font=ctk.CTkFont(size=16),
            fg_color="transparent",
            text_color="gray"
        )
        self.user_button.pack(side="left", padx=2)

        # 主题切换按钮
        self.theme_button = ctk.CTkButton(
            self.user_frame,
            text="🌙",
            width=36,
            height=36,
            corner_radius=18,
            font=ctk.CTkFont(size=16),
            fg_color="transparent",
            text_color="gray"
        )
        self.theme_button.pack(side="left", padx=2)

    def _bind_custom_events(self):
        """绑定自定义事件"""
        # 设置按钮事件
        self.settings_button.configure(command=self._on_settings_clicked)

        # 用户按钮事件
        self.user_button.configure(command=self._on_user_clicked)

        # 主题切换事件
        self.theme_button.configure(command=self._on_theme_toggle)

    def _on_search_enter(self, event):
        """搜索框回车事件"""
        search_text = self.search_entry.get().strip()
        if search_text and self.search_callback:
            self.search_callback(search_text)

    def _on_search_focus_in(self, event):
        """搜索框获得焦点"""
        if self.search_entry.get() == "搜索功能、设置或帮助...":
            self.search_entry.delete(0, "end")

    def _on_search_focus_out(self, event):
        """搜索框失去焦点"""
        if not self.search_entry.get().strip():
            self.search_entry.insert(0, "搜索功能、设置或帮助...")

    def _on_settings_clicked(self):
        """设置按钮点击事件"""
        if self.settings_callback:
            self.settings_callback()
        else:
            logger.debug("设置按钮被点击，但未设置回调函数")

    def _on_user_clicked(self):
        """用户按钮点击事件"""
        if self.user_menu_callback:
            self.user_menu_callback()
        else:
            logger.debug("用户按钮被点击，但未设置回调函数")

    def _on_theme_toggle(self):
        """主题切换事件"""
        if self.state_manager:
            current_theme = self.state_manager.get_state('app.theme', 'dark')
            new_theme = 'light' if current_theme == 'dark' else 'dark'
            self.state_manager.set_state('app.theme', new_theme)

            # 更新按钮图标
            new_icon = '☀️' if new_theme == 'light' else '🌙'
            self.theme_button.configure(text=new_icon)

            logger.info(f"主题切换: {current_theme} -> {new_theme}")

    def apply_theme_style(self, theme_data: Dict[str, Any]):
        """应用主题样式"""
        try:
            # 更新搜索框样式
            if self.search_entry:
                colors = theme_data.get('colors', {})
                self.search_entry.configure(
                    fg_color=colors.get('surface', '#2A2A2A'),
                    border_color=colors.get('border', '#404040'),
                    text_color=colors.get('text', '#FFFFFF')
                )

            # 更新按钮样式
            for button in [self.settings_button, self.user_button, self.theme_button]:
                if button:
                    colors = theme_data.get('colors', {})
                    button.configure(
                        text_color=colors.get('text_secondary', '#CCCCCC')
                    )

        except Exception as e:
            logger.error(f"应用主题到标题栏失败: {e}")

    def set_search_callback(self, callback: Callable[[str], None]):
        """设置搜索回调函数"""
        self.search_callback = callback

    def set_settings_callback(self, callback: Callable[[], None]):
        """设置设置回调函数"""
        self.settings_callback = callback

    def set_user_menu_callback(self, callback: Callable[[], None]):
        """设置用户菜单回调函数"""
        self.user_menu_callback = callback

    def update_layout_for_size(self, width: int, height: int):
        """根据窗口大小更新布局"""
        try:
            # 响应式布局调整
            if width < 800:
                # 紧凑模式
                self._apply_compact_layout()
            elif width < 1200:
                # 标准模式
                self._apply_standard_layout()
            else:
                # 宽屏模式
                self._apply_wide_layout()

        except Exception as e:
            logger.error(f"更新标题栏布局失败: {e}")

    def _apply_compact_layout(self):
        """应用紧凑布局"""
        if self.is_compact:
            return

        self.is_compact = True

        # 隐藏版本标签
        if self.version_label:
            self.version_label.pack_forget()

        # 缩小搜索框
        if self.search_entry:
            self.search_entry.configure(width=200)

        # 隐藏部分按钮
        if self.settings_button:
            self.settings_button.pack_forget()

    def _apply_standard_layout(self):
        """应用标准布局"""
        if self.is_compact == False and self.search_visible:
            return

        self.is_compact = False
        self.search_visible = True

        # 显示版本标签
        if self.version_label:
            self.version_label.pack(side="left")

        # 恢复搜索框大小
        if self.search_entry:
            self.search_entry.configure(width=300)

        # 显示所有按钮
        if self.settings_button:
            self.settings_button.pack(side="left", padx=2, after=self.user_frame.winfo_children()[0] if self.user_frame.winfo_children() else None)

    def _apply_wide_layout(self):
        """应用宽屏布局"""
        self._apply_standard_layout()

        # 增大搜索框
        if self.search_entry:
            self.search_entry.configure(width=400)

    def get_search_text(self) -> str:
        """获取搜索框文本"""
        return self.search_entry.get().strip() if self.search_entry else ""

    def clear_search(self):
        """清空搜索框"""
        if self.search_entry:
            self.search_entry.delete(0, "end")
            self.search_entry.insert(0, "搜索功能、设置或帮助...")

    def set_title(self, title: str):
        """设置应用标题"""
        if self.app_title_label:
            self.app_title_label.configure(text=title)

    def get_title(self) -> str:
        """获取应用标题"""
        return self.app_title_label.cget("text") if self.app_title_label else ""

    def show_search(self, show: bool = True):
        """显示或隐藏搜索框"""
        if self.search_frame:
            if show:
                self.search_frame.grid(row=0, column=1, sticky="ew", padx=10)
                self.search_visible = True
            else:
                self.search_frame.grid_forget()
                self.search_visible = False

    def enable_user_controls(self, enable: bool = True):
        """启用或禁用用户控件"""
        state = "normal" if enable else "disabled"
        for button in [self.settings_button, self.user_button, self.theme_button]:
            if button:
                button.configure(state=state)

    def get_title_info(self) -> Dict[str, Any]:
        """获取标题栏信息"""
        return {
            'title': self.get_title(),
            'search_visible': self.search_visible,
            'is_compact': self.is_compact,
            'has_search_callback': self.search_callback is not None,
            'has_settings_callback': self.settings_callback is not None,
            'has_user_menu_callback': self.user_menu_callback is not None
        }