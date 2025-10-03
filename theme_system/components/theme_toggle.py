"""
主题切换按钮组件
提供用户友好的主题切换界面
"""

import customtkinter as ctk
from typing import Callable, Optional
import logging

from ..styled_component import StyledButton
from ..theme_manager import ThemeManager

logger = logging.getLogger(__name__)


class ThemeToggleButton(StyledButton):
    """主题切换按钮组件"""

    def __init__(self, parent, theme_manager: Optional[ThemeManager] = None,
                 on_theme_changed: Optional[Callable[[str], None]] = None, **kwargs):
        """
        初始化主题切换按钮

        Args:
            parent: 父组件
            theme_manager: 主题管理器
            on_theme_changed: 主题变化回调
            **kwargs: 其他按钮参数
        """
        # 设置默认参数
        default_kwargs = {
            'width': 40,
            'height': 40,
            'text': "🌙",
            'theme_manager': theme_manager,
            'widget_type': 'theme_toggle',
            'button_style': 'secondary'
        }
        default_kwargs.update(kwargs)

        # 初始化按钮
        super().__init__(parent, **default_kwargs)

        self.on_theme_changed_callback = on_theme_changed
        self._update_theme_state()

        # 绑定点击事件
        self.configure(command=self._toggle_theme)

        logger.debug("主题切换按钮初始化完成")

    def _toggle_theme(self) -> None:
        """切换主题"""
        try:
            new_theme = self.theme_manager.toggle_theme()
            self._update_theme_state()

            # 调用回调函数
            if self.on_theme_changed_callback:
                self.on_theme_changed_callback(new_theme)

            logger.info(f"主题已切换到: {new_theme}")

        except Exception as e:
            logger.error(f"切换主题失败: {e}")

    def _update_theme_state(self) -> None:
        """更新主题状态显示"""
        current_theme = self.theme_manager.get_current_theme()

        if current_theme == 'dark':
            self.configure(text="☀️")  # 太阳图标，切换到浅色
            self._tooltip_text = "切换到浅色主题"
        elif current_theme == 'light':
            self.configure(text="🌓")  # 半月图标，切换到柔和浅色
            self._tooltip_text = "切换到柔和浅色主题"
        elif current_theme == 'soft_light':
            self.configure(text="🌙")  # 月亮图标，切换到中性
            self._tooltip_text = "切换到中性主题"
        else:  # neutral theme
            self.configure(text="☀️")  # 太阳图标，切换到深色
            self._tooltip_text = "切换到深色主题"

        # 设置提示文本
        self._set_tooltip()

    def _set_tooltip(self) -> None:
        """设置提示文本"""
        if hasattr(self, '_tooltip_text'):
            # 简单的提示实现
            self.bind("<Enter>", lambda e: self._show_tooltip())
            self.bind("<Leave>", lambda e: self._hide_tooltip())

    def _show_tooltip(self) -> None:
        """显示提示"""
        if hasattr(self, '_tooltip') and self._tooltip:
            return

        try:
            self._tooltip = ctk.CTkLabel(
                self.winfo_toplevel(),
                text=self._tooltip_text,
                font=ctk.CTkFont(size=12),
                text_color=self.theme_manager.get_color('text'),
                fg_color=self.theme_manager.get_color('surface'),
                corner_radius=6,
                padx=8,
                pady=4
            )

            # 计算提示位置
            x = self.winfo_rootx() + self.winfo_width() + 10
            y = self.winfo_rooty() + (self.winfo_height() // 2) - 10

            self._tooltip.place(x=x, y=y)

        except Exception as e:
            logger.debug(f"显示提示失败: {e}")

    def _hide_tooltip(self) -> None:
        """隐藏提示"""
        if hasattr(self, '_tooltip') and self._tooltip:
            try:
                self._tooltip.destroy()
                self._tooltip = None
            except Exception:
                pass

    def destroy(self) -> None:
        """销毁组件"""
        self._hide_tooltip()
        super().destroy()


class ThemeSelector(ctk.CTkFrame):
    """主题选择器组件"""

    def __init__(self, parent, theme_manager: Optional[ThemeManager] = None,
                 on_theme_changed: Optional[Callable[[str], None]] = None, **kwargs):
        """
        初始化主题选择器

        Args:
            parent: 父组件
            theme_manager: 主题管理器
            on_theme_changed: 主题变化回调
            **kwargs: 其他框架参数
        """
        super().__init__(parent, **kwargs)

        self.theme_manager = theme_manager or ThemeManager()
        self.on_theme_changed_callback = on_theme_changed

        self._setup_ui()
        self._update_selection()

        logger.debug("主题选择器初始化完成")

    def _setup_ui(self) -> None:
        """设置用户界面"""
        # 配置布局
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 标题
        self.title_label = ctk.CTkLabel(
            self,
            text="主题选择",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.title_label.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))

        # 主题列表容器
        self.theme_container = ctk.CTkScrollableFrame(self)
        self.theme_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

        # 加载主题选项
        self._load_theme_options()

        # 主题切换按钮
        self.toggle_button = ThemeToggleButton(
            self,
            theme_manager=self.theme_manager,
            on_theme_changed=self._on_theme_changed
        )
        self.toggle_button.grid(row=2, column=0, pady=10)

    def _load_theme_options(self) -> None:
        """加载主题选项"""
        available_themes = self.theme_manager.get_available_themes()

        for i, theme_name in enumerate(available_themes):
            theme_info = self.theme_manager.get_theme_info(theme_name)

            # 主题选项按钮
            theme_button = ctk.CTkRadioButton(
                self.theme_container,
                text=theme_info.get('name', theme_name),
                value=theme_name,
                command=lambda t=theme_name: self._select_theme(t)
            )

            # 设置当前选中的主题
            if theme_info.get('is_current', False):
                theme_button.select()

            theme_button.grid(row=i, column=0, sticky="ew", padx=5, pady=2)

    def _select_theme(self, theme_name: str) -> None:
        """选择主题"""
        try:
            if self.theme_manager.apply_theme(theme_name):
                self._update_selection()
                if self.on_theme_changed_callback:
                    self.on_theme_changed_callback(theme_name)
                logger.info(f"主题已切换到: {theme_name}")
        except Exception as e:
            logger.error(f"选择主题失败: {e}")

    def _on_theme_changed(self, theme_name: str) -> None:
        """主题变化回调"""
        self._update_selection()

        if self.on_theme_changed_callback:
            self.on_theme_changed_callback(theme_name)

    def _update_selection(self) -> None:
        """更新选择状态"""
        # 清除现有选项
        for widget in self.theme_container.winfo_children():
            widget.destroy()

        # 重新加载主题选项
        self._load_theme_options()


class ThemeStatusBar(ctk.CTkFrame):
    """主题状态栏组件"""

    def __init__(self, parent, theme_manager: Optional[ThemeManager] = None, **kwargs):
        """
        初始化主题状态栏

        Args:
            parent: 父组件
            theme_manager: 主题管理器
            **kwargs: 其他框架参数
        """
        super().__init__(parent, **kwargs)

        self.theme_manager = theme_manager or ThemeManager()

        self._setup_ui()
        self._update_status()

        # 订阅主题变化
        self.theme_manager.subscribe(self._on_theme_changed)

        logger.debug("主题状态栏初始化完成")

    def _setup_ui(self) -> None:
        """设置用户界面"""
        # 配置布局
        self.grid_columnconfigure(1, weight=1)

        # 当前主题标签
        self.theme_label = ctk.CTkLabel(
            self,
            text="主题:",
            font=ctk.CTkFont(size=12)
        )
        self.theme_label.grid(row=0, column=0, sticky="w", padx=(10, 5), pady=5)

        # 主题名称
        self.theme_name_label = ctk.CTkLabel(
            self,
            text="深色主题",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.theme_name_label.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        # 快速切换按钮
        self.quick_toggle = ThemeToggleButton(
            self,
            theme_manager=self.theme_manager,
            width=30,
            height=30
        )
        self.quick_toggle.grid(row=0, column=2, sticky="e", padx=(0, 10), pady=5)

    def _update_status(self) -> None:
        """更新状态显示"""
        current_theme = self.theme_manager.get_current_theme()
        theme_info = self.theme_manager.get_theme_info(current_theme)

        theme_name = theme_info.get('name', current_theme)
        self.theme_name_label.configure(text=theme_name)

    def _on_theme_changed(self, theme_name: str, theme_data) -> None:
        """主题变化回调"""
        self._update_status()

    def destroy(self) -> None:
        """销毁组件"""
        # 取消订阅
        self.theme_manager.unsubscribe(self._on_theme_changed)
        super().destroy()