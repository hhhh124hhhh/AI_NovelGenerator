"""
样式化组件基类
提供主题感知的组件基类
"""

import tkinter as tk
import customtkinter as ctk
from typing import Dict, Any, Optional, Callable
import logging

from .theme_manager import ThemeManager
from .style_utils import StyleUtils

logger = logging.getLogger(__name__)


class StyledComponent:
    """
    样式化组件基类
    为组件提供主题感知能力
    """

    def __init__(self, theme_manager: Optional[ThemeManager] = None,
                 widget_type: str = 'default', auto_apply_theme: bool = True):
        """
        初始化样式化组件

        Args:
            theme_manager: 主题管理器实例
            widget_type: 组件类型标识
            auto_apply_theme: 是否自动应用主题
        """
        self.theme_manager = theme_manager or ThemeManager()
        self.widget_type = widget_type
        self.auto_apply_theme = auto_apply_theme
        self._theme_applied = False
        self._custom_styles = {}
        self._widget = None  # 初始化_widget属性

        # 订阅主题变化
        self.theme_manager.subscribe(self.on_theme_changed)

        # 存储原始样式属性
        self._original_styles = {}

        logger.debug(f"初始化样式化组件: {widget_type}")

    def on_theme_changed(self, theme_name: str, theme_data: Dict[str, Any]) -> None:
        """
        主题变化回调

        Args:
            theme_name: 新主题名称
            theme_data: 主题数据
        """
        if self.auto_apply_theme:
            self.apply_styles()
            logger.debug(f"组件 {self.widget_type} 已应用新主题: {theme_name}")

    def apply_styles(self, state: str = 'normal') -> None:
        """
        应用当前主题样式

        Args:
            state: 组件状态
        """
        try:
            if hasattr(self, '_widget') and self._widget:
                # 应用主题样式
                StyleUtils.apply_theme_to_widget(
                    self._widget,
                    self.theme_manager,
                    self.widget_type,
                    state
                )

                # 应用自定义样式
                self._apply_custom_styles()

                self._theme_applied = True

        except Exception as e:
            logger.error(f"应用样式失败: {e}")

    def _apply_custom_styles(self) -> None:
        """应用自定义样式"""
        if hasattr(self, '_widget') and self._widget:
            for property_name, value in self._custom_styles.items():
                try:
                    if hasattr(self._widget, 'configure'):
                        self._widget.configure(**{property_name: value})
                except Exception as e:
                    logger.warning(f"应用自定义样式失败 {property_name}: {e}")

    def set_custom_style(self, property_name: str, value: Any) -> None:
        """
        设置自定义样式

        Args:
            property_name: 样式属性名
            value: 样式值
        """
        self._custom_styles[property_name] = value
        self._apply_custom_styles()

    def remove_custom_style(self, property_name: str) -> None:
        """
        移除自定义样式

        Args:
            property_name: 样式属性名
        """
        if property_name in self._custom_styles:
            del self._custom_styles[property_name]
            self.apply_styles()

    def clear_custom_styles(self) -> None:
        """清除所有自定义样式"""
        self._custom_styles.clear()
        self.apply_styles()

    def get_theme_color(self, color_name: str) -> str:
        """
        获取主题颜色

        Args:
            color_name: 颜色名称

        Returns:
            str: 颜色值
        """
        return self.theme_manager.get_color(color_name)

    def get_theme_font(self, size_name: str = 'md') -> Dict[str, Any]:
        """
        获取主题字体

        Args:
            size_name: 字体大小名称

        Returns:
            Dict[str, Any]: 字体配置
        """
        return self.theme_manager.get_font(size_name)

    def get_theme_spacing(self, size_name: str = 'md') -> int:
        """
        获取主题间距

        Args:
            size_name: 间距名称

        Returns:
            int: 间距值
        """
        return self.theme_manager.get_spacing(size_name)

    def is_dark_theme(self) -> bool:
        """
        判断当前主题是否为深色主题

        Returns:
            bool: 是否为深色主题
        """
        return StyleUtils.is_dark_theme(self.theme_manager)

    def destroy(self) -> None:
        """销毁组件，清理资源"""
        try:
            # 取消订阅主题变化
            if hasattr(self, 'theme_manager'):
                self.theme_manager.unsubscribe(self.on_theme_changed)

            # 清理自定义样式
            self._custom_styles.clear()
            self._original_styles.clear()

            # 销毁组件
            if hasattr(self, '_widget') and self._widget:
                self._widget.destroy()

        except Exception as e:
            logger.error(f"销毁组件失败: {e}")


class StyledFrame(ctk.CTkFrame, StyledComponent):
    """样式化框架组件"""

    def __init__(self, parent, **kwargs):
        # 提取样式相关参数
        theme_manager = kwargs.pop('theme_manager', None)
        widget_type = kwargs.pop('widget_type', 'frame')
        auto_apply_theme = kwargs.pop('auto_apply_theme', True)

        # 初始化CustomTkinter框架
        super().__init__(parent, **kwargs)

        # 初始化样式化组件
        StyledComponent.__init__(self, theme_manager, widget_type, auto_apply_theme)
        self._widget = self  # 设置_widget引用

        # 应用初始样式
        if auto_apply_theme:
            self.apply_styles()


class StyledButton(ctk.CTkButton, StyledComponent):
    """样式化按钮组件"""

    def __init__(self, parent, **kwargs):
        # 提取样式相关参数
        theme_manager = kwargs.pop('theme_manager', None)
        widget_type = kwargs.pop('widget_type', 'button')
        auto_apply_theme = kwargs.pop('auto_apply_theme', True)
        button_style = kwargs.pop('button_style', 'primary')

        # 初始化CustomTkinter按钮
        super().__init__(parent, **kwargs)

        # 初始化样式化组件
        StyledComponent.__init__(self, theme_manager, widget_type, auto_apply_theme)
        self._widget = self  # 设置_widget引用
        self.button_style = button_style

        # 应用按钮样式
        if auto_apply_theme:
            self._apply_button_style()

    def _apply_button_style(self) -> None:
        """应用按钮样式"""
        try:
            style = StyleUtils.create_button_style(self.theme_manager, self.button_style)
            if hasattr(self, 'configure'):
                # 只应用配置中存在的属性
                try:
                    configurable_attrs = self.configure()
                    if configurable_attrs is not None:
                        # 对于字典类型的配置结果
                        if isinstance(configurable_attrs, dict):
                            for attr, value in style.items():
                                if attr in configurable_attrs:
                                    self.configure(**{attr: value})
                        # 对于其他情况，直接尝试配置
                        else:
                            for attr, value in style.items():
                                try:
                                    self.configure(**{attr: value})
                                except Exception:
                                    pass  # 忽略不支持的属性
                    else:
                        # 如果configure()返回None，直接尝试配置
                        for attr, value in style.items():
                            try:
                                self.configure(**{attr: value})
                            except Exception:
                                pass  # 忽略不支持的属性
                except Exception:
                    # 如果configure()调用失败，直接尝试配置
                    for attr, value in style.items():
                        try:
                            self.configure(**{attr: value})
                        except Exception:
                            pass  # 忽略不支持的属性
        except Exception as e:
            logger.error(f"应用按钮样式失败: {e}")

    def on_theme_changed(self, theme_name: str, theme_data: Dict[str, Any]) -> None:
        """重写主题变化回调"""
        super().on_theme_changed(theme_name, theme_data)
        self._apply_button_style()


class StyledLabel(ctk.CTkLabel, StyledComponent):
    """样式化标签组件"""

    def __init__(self, parent, **kwargs):
        # 提取样式相关参数
        theme_manager = kwargs.pop('theme_manager', None)
        widget_type = kwargs.pop('widget_type', 'label')
        auto_apply_theme = kwargs.pop('auto_apply_theme', True)
        text_size = kwargs.pop('text_size', 'md')

        # 初始化CustomTkinter标签
        super().__init__(parent, **kwargs)

        # 初始化样式化组件
        StyledComponent.__init__(self, theme_manager, widget_type, auto_apply_theme)
        self._widget = self  # 设置_widget引用
        self.text_size = text_size

        # 应用标签样式
        if auto_apply_theme:
            self._apply_label_style()

    def _apply_label_style(self) -> None:
        """应用标签样式"""
        try:
            font = self.theme_manager.get_font(self.text_size)
            text_color = self.theme_manager.get_color('text')

            if hasattr(self, 'configure'):
                try:
                    configurable_attrs = self.configure()
                    if configurable_attrs is not None:
                        # 对于字典类型的配置结果
                        if isinstance(configurable_attrs, dict):
                            if 'font' in configurable_attrs:
                                self.configure(font=ctk.CTkFont(**font))
                            if 'text_color' in configurable_attrs:
                                self.configure(text_color=text_color)
                        # 对于其他情况，直接尝试配置
                        else:
                            try:
                                self.configure(font=ctk.CTkFont(**font))
                            except Exception:
                                pass
                            try:
                                self.configure(text_color=text_color)
                            except Exception:
                                pass
                    else:
                        # 如果configure()返回None，直接尝试配置
                        try:
                            self.configure(font=ctk.CTkFont(**font))
                        except Exception:
                            pass
                        try:
                            self.configure(text_color=text_color)
                        except Exception:
                            pass
                except Exception:
                    # 如果configure()调用失败，直接尝试配置
                    try:
                        self.configure(font=ctk.CTkFont(**font))
                    except Exception:
                        pass
                    try:
                        self.configure(text_color=text_color)
                    except Exception:
                        pass
        except Exception as e:
            logger.error(f"应用标签样式失败: {e}")

    def on_theme_changed(self, theme_name: str, theme_data: Dict[str, Any]) -> None:
        """重写主题变化回调"""
        super().on_theme_changed(theme_name, theme_data)
        self._apply_label_style()


class StyledEntry(ctk.CTkEntry, StyledComponent):
    """样式化输入框组件"""

    def __init__(self, parent, **kwargs):
        # 提取样式相关参数
        theme_manager = kwargs.pop('theme_manager', None)
        widget_type = kwargs.pop('widget_type', 'entry')
        auto_apply_theme = kwargs.pop('auto_apply_theme', True)

        # 初始化CustomTkinter输入框
        super().__init__(parent, **kwargs)

        # 初始化样式化组件
        StyledComponent.__init__(self, theme_manager, widget_type, auto_apply_theme)
        self._widget = self  # 设置_widget引用

        # 应用输入框样式
        if auto_apply_theme:
            self._apply_entry_style()

    def _apply_entry_style(self) -> None:
        """应用输入框样式"""
        try:
            style = StyleUtils.create_input_style(self.theme_manager)
            if hasattr(self, 'configure'):
                try:
                    configurable_attrs = self.configure()
                    if configurable_attrs is not None:
                        # 对于字典类型的配置结果
                        if isinstance(configurable_attrs, dict):
                            for attr, value in style.items():
                                if attr in configurable_attrs:
                                    self.configure(**{attr: value})
                        # 对于其他情况，直接尝试配置
                        else:
                            for attr, value in style.items():
                                try:
                                    self.configure(**{attr: value})
                                except Exception:
                                    pass  # 忽略不支持的属性
                    else:
                        # 如果configure()返回None，直接尝试配置
                        for attr, value in style.items():
                            try:
                                self.configure(**{attr: value})
                            except Exception:
                                pass  # 忽略不支持的属性
                except Exception:
                    # 如果configure()调用失败，直接尝试配置
                    for attr, value in style.items():
                        try:
                            self.configure(**{attr: value})
                        except Exception:
                            pass  # 忽略不支持的属性
        except Exception as e:
            logger.error(f"应用输入框样式失败: {e}")

    def on_theme_changed(self, theme_name: str, theme_data: Dict[str, Any]) -> None:
        """重写主题变化回调"""
        super().on_theme_changed(theme_name, theme_data)
        self._apply_entry_style()


class StyledTextbox(ctk.CTkTextbox, StyledComponent):
    """样式化文本框组件"""

    def __init__(self, parent, **kwargs):
        # 提取样式相关参数
        theme_manager = kwargs.pop('theme_manager', None)
        widget_type = kwargs.pop('widget_type', 'textbox')
        auto_apply_theme = kwargs.pop('auto_apply_theme', True)

        # 初始化CustomTkinter文本框
        super().__init__(parent, **kwargs)

        # 初始化样式化组件
        StyledComponent.__init__(self, theme_manager, widget_type, auto_apply_theme)
        self._widget = self  # 设置_widget引用

        # 应用文本框样式
        if auto_apply_theme:
            self._apply_textbox_style()

    def _apply_textbox_style(self) -> None:
        """应用文本框样式"""
        try:
            style = StyleUtils.create_input_style(self.theme_manager)
            if hasattr(self, 'configure'):
                try:
                    configurable_attrs = self.configure()
                    if configurable_attrs is not None:
                        # 对于字典类型的配置结果
                        if isinstance(configurable_attrs, dict):
                            for attr, value in style.items():
                                if attr in configurable_attrs:
                                    self.configure(**{attr: value})
                        # 对于其他情况，直接尝试配置
                        else:
                            for attr, value in style.items():
                                try:
                                    self.configure(**{attr: value})
                                except Exception:
                                    pass  # 忽略不支持的属性
                    else:
                        # 如果configure()返回None，直接尝试配置
                        for attr, value in style.items():
                            try:
                                self.configure(**{attr: value})
                            except Exception:
                                pass  # 忽略不支持的属性
                except Exception:
                    # 如果configure()调用失败，直接尝试配置
                    for attr, value in style.items():
                        try:
                            self.configure(**{attr: value})
                        except Exception:
                            pass  # 忽略不支持的属性
        except Exception as e:
            logger.error(f"应用文本框样式失败: {e}")

    def on_theme_changed(self, theme_name: str, theme_data: Dict[str, Any]) -> None:
        """重写主题变化回调"""
        super().on_theme_changed(theme_name, theme_data)
        self._apply_textbox_style()


class StyledScrollableFrame(ctk.CTkScrollableFrame, StyledComponent):
    """样式化滚动框架组件"""

    def __init__(self, parent, **kwargs):
        # 提取样式相关参数
        theme_manager = kwargs.pop('theme_manager', None)
        widget_type = kwargs.pop('widget_type', 'scrollable_frame')
        auto_apply_theme = kwargs.pop('auto_apply_theme', True)

        # 初始化CustomTkinter滚动框架
        super().__init__(parent, **kwargs)

        # 初始化样式化组件
        StyledComponent.__init__(self, theme_manager, widget_type, auto_apply_theme)
        self._widget = self  # 设置_widget引用

        # 应用滚动框架样式
        if auto_apply_theme:
            self.apply_styles()


class StyledProgressBar(ctk.CTkProgressBar, StyledComponent):
    """样式化进度条组件"""

    def __init__(self, parent, **kwargs):
        # 提取样式相关参数
        theme_manager = kwargs.pop('theme_manager', None)
        widget_type = kwargs.pop('widget_type', 'progressbar')
        auto_apply_theme = kwargs.pop('auto_apply_theme', True)

        # 初始化CustomTkinter进度条
        super().__init__(parent, **kwargs)

        # 初始化样式化组件
        StyledComponent.__init__(self, theme_manager, widget_type, auto_apply_theme)
        self._widget = self  # 设置_widget引用

        # 应用进度条样式
        if auto_apply_theme:
            self._apply_progressbar_style()

    def _apply_progressbar_style(self) -> None:
        """应用进度条样式"""
        try:
            progress_color = self.theme_manager.get_color('primary')
            if hasattr(self, 'configure'):
                try:
                    configurable_attrs = self.configure()
                    if configurable_attrs is not None:
                        # 对于字典类型的配置结果
                        if isinstance(configurable_attrs, dict) and 'progress_color' in configurable_attrs:
                            self.configure(progress_color=progress_color)
                        # 对于其他情况，直接尝试配置
                        else:
                            try:
                                self.configure(progress_color=progress_color)
                            except Exception:
                                pass
                    else:
                        # 如果configure()返回None，直接尝试配置
                        try:
                            self.configure(progress_color=progress_color)
                        except Exception:
                            pass
                except Exception:
                    # 如果configure()调用失败，直接尝试配置
                    try:
                        self.configure(progress_color=progress_color)
                    except Exception:
                        pass
        except Exception as e:
            logger.error(f"应用进度条样式失败: {e}")

    def on_theme_changed(self, theme_name: str, theme_data: Dict[str, Any]) -> None:
        """重写主题变化回调"""
        super().on_theme_changed(theme_name, theme_data)
        self._apply_progressbar_style()