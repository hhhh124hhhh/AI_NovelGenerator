"""
样式工具类
提供样式应用和转换的工具函数
"""

import tkinter as tk
import customtkinter as ctk
from typing import Dict, Any, Union, Tuple
import logging

logger = logging.getLogger(__name__)


class StyleUtils:
    """样式工具类 - 提供样式应用的静态方法"""

    @staticmethod
    def apply_color(widget: Union[tk.Widget, ctk.CTkBaseClass],
                   color_name: str, color_value: str) -> None:
        """
        应用颜色样式到组件

        Args:
            widget: 目标组件
            color_name: 颜色属性名称
            color_value: 颜色值
        """
        try:
            if hasattr(widget, 'configure'):
                # CustomTkinter组件
                config_dict = {}
                if color_name.lower() in ['fg', 'foreground', 'text_color']:
                    config_dict['text_color'] = color_value
                elif color_name.lower() in ['bg', 'background']:
                    # 尝试设置背景色的不同属性
                    config_dict['bg_color'] = color_value
                elif color_name.lower() in ['border_color']:
                    config_dict['border_color'] = color_value
                elif color_name.lower() in ['hover_color']:
                    config_dict['hover_color'] = color_value
                elif color_name.lower() in ['fg_color']:
                    config_dict['fg_color'] = color_value

                # 只传递组件支持的参数
                StyleUtils._safe_configure(widget, config_dict)
            else:
                logger.warning(f"组件不支持颜色配置: {widget}")

        except Exception as e:
            logger.error(f"应用颜色样式失败: {e}")

    @staticmethod
    def _safe_configure(widget, config_dict: Dict[str, Any]) -> None:
        """
        安全地配置组件参数，忽略不支持的参数

        Args:
            widget: 目标组件
            config_dict: 配置字典
        """
        try:
            # 尝试一次性配置所有参数
            widget.configure(**config_dict)
        except Exception:
            # 如果一次性配置失败，尝试逐个参数配置
            for key, value in config_dict.items():
                try:
                    widget.configure(**{key: value})
                except Exception:
                    pass  # 忽略不支持的参数

    @staticmethod
    def apply_font(widget: Union[tk.Widget, ctk.CTkBaseClass],
                  font_config: Dict[str, Any]) -> None:
        """
        应用字体样式到组件

        Args:
            widget: 目标组件
            font_config: 字体配置
        """
        try:
            if hasattr(widget, 'configure'):
                family = font_config.get('family', 'Arial')
                size = font_config.get('size', 12)
                weight = font_config.get('weight', 'normal')
                slant = font_config.get('slant', 'roman')

                # 创建字体对象
                font = ctk.CTkFont(family=family, size=size, weight=weight)

                # 只传递组件支持的参数
                StyleUtils._safe_configure(widget, {'font': font})

        except Exception as e:
            logger.error(f"应用字体样式失败: {e}")

    @staticmethod
    def apply_spacing(widget: Union[tk.Widget, ctk.CTkBaseClass],
                     spacing_config: Dict[str, Any]) -> None:
        """
        应用间距样式到组件

        Args:
            widget: 目标组件
            spacing_config: 间距配置
        """
        try:
            if hasattr(widget, 'configure'):
                padx_x = spacing_config.get('x', 0)
                padx_y = spacing_config.get('y', 0)
                pady = spacing_config.get('pad', 0)

                # 对于有grid配置的组件
                if hasattr(widget, 'grid_info') and widget.grid_info():
                    # 这里需要在父组件上设置grid的padx和pady
                    pass
                elif hasattr(widget, 'pack_info') and widget.pack_info():
                    widget.pack(padx=(padx_x, padx_y), pady=pady)

        except Exception as e:
            logger.error(f"应用间距样式失败: {e}")

    @staticmethod
    def apply_shadow(widget: Union[tk.Widget, ctk.CTkBaseClass],
                    shadow_config: str) -> None:
        """
        应用阴影效果 (CustomTkinter有限支持)

        Args:
            widget: 目标组件
            shadow_config: 阴影配置字符串
        """
        try:
            # CustomTkinter对阴影的支持有限
            # 这里主要处理边框和圆角来模拟阴影效果
            StyleUtils._safe_configure(widget, {'border_width': 1})

        except Exception as e:
            logger.error(f"应用阴影效果失败: {e}")

    @staticmethod
    def parse_color(color_str: str) -> str:
        """
        解析颜色字符串

        Args:
            color_str: 颜色字符串

        Returns:
            str: 标准化的颜色值
        """
        if color_str.startswith('#'):
            return color_str
        elif color_str.startswith('rgb'):
            # 转换rgb颜色到hex
            import re
            match = re.match(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', color_str)
            if match:
                r, g, b = map(int, match.groups())
                return f'#{r:02x}{g:02x}{b:02x}'
        return color_str

    @staticmethod
    def get_contrast_color(background_color: str) -> str:
        """
        根据背景色获取对比色

        Args:
            background_color: 背景颜色

        Returns:
            str: 对比色 (黑色或白色)
        """
        try:
            # 移除#号
            color = background_color.lstrip('#')

            # 转换为RGB
            r = int(color[0:2], 16)
            g = int(color[2:4], 16)
            b = int(color[4:6], 16)

            # 计算亮度
            luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255

            # 根据亮度返回对比色
            return '#000000' if luminance > 0.5 else '#FFFFFF'

        except Exception:
            return '#000000'

    @staticmethod
    def blend_colors(color1: str, color2: str, ratio: float = 0.5) -> str:
        """
        混合两种颜色

        Args:
            color1: 第一种颜色
            color2: 第二种颜色
            ratio: 混合比例 (0.0-1.0)

        Returns:
            str: 混合后的颜色
        """
        try:
            # 移除#号
            c1 = color1.lstrip('#')
            c2 = color2.lstrip('#')

            # 转换为RGB
            r1, g1, b1 = int(c1[0:2], 16), int(c1[2:4], 16), int(c1[4:6], 16)
            r2, g2, b2 = int(c2[0:2], 16), int(c2[2:4], 16), int(c2[4:6], 16)

            # 混合
            r = int(r1 * (1 - ratio) + r2 * ratio)
            g = int(g1 * (1 - ratio) + g2 * ratio)
            b = int(b1 * (1 - ratio) + b2 * ratio)

            return f'#{r:02x}{g:02x}{b:02x}'

        except Exception:
            return color1

    @staticmethod
    def lighten_color(color: str, amount: float = 0.2) -> str:
        """
        使颜色变亮

        Args:
            color: 原始颜色
            amount: 变亮程度 (0.0-1.0)

        Returns:
            str: 变亮后的颜色
        """
        return StyleUtils.blend_colors(color, '#FFFFFF', amount)

    @staticmethod
    def darken_color(color: str, amount: float = 0.2) -> str:
        """
        使颜色变暗

        Args:
            color: 原始颜色
            amount: 变暗程度 (0.0-1.0)

        Returns:
            str: 变暗后的颜色
        """
        return StyleUtils.blend_colors(color, '#000000', amount)

    @staticmethod
    def create_button_style(theme_manager, button_type: str = 'primary') -> Dict[str, Any]:
        """
        创建按钮样式

        Args:
            theme_manager: 主题管理器
            button_type: 按钮类型

        Returns:
            Dict[str, Any]: 按钮样式配置
        """
        base_style = {
            'corner_radius': 8,
            'border_width': 0,
            'font': theme_manager.get_font('md')
        }

        if button_type == 'primary':
            base_style.update({
                'fg_color': theme_manager.get_color('primary'),
                'hover_color': StyleUtils.darken_color(theme_manager.get_color('primary')),
                'text_color': '#FFFFFF'
            })
        elif button_type == 'secondary':
            base_style.update({
                'fg_color': 'transparent',
                'border_width': 2,
                'border_color': theme_manager.get_color('primary'),
                'text_color': theme_manager.get_color('primary'),
                'hover_color': theme_manager.get_color('primary'),
                'hover': True
            })
        elif button_type == 'success':
            base_style.update({
                'fg_color': theme_manager.get_color('success'),
                'hover_color': StyleUtils.darken_color(theme_manager.get_color('success')),
                'text_color': '#FFFFFF'
            })
        elif button_type == 'warning':
            base_style.update({
                'fg_color': theme_manager.get_color('warning'),
                'hover_color': StyleUtils.darken_color(theme_manager.get_color('warning')),
                'text_color': '#FFFFFF'
            })
        elif button_type == 'danger':
            base_style.update({
                'fg_color': theme_manager.get_color('error'),
                'hover_color': StyleUtils.darken_color(theme_manager.get_color('error')),
                'text_color': '#FFFFFF'
            })

        return base_style

    @staticmethod
    def create_input_style(theme_manager, input_type: str = 'default') -> Dict[str, Any]:
        """
        创建输入框样式

        Args:
            theme_manager: 主题管理器
            input_type: 输入框类型

        Returns:
            Dict[str, Any]: 输入框样式配置
        """
        base_style = {
            'corner_radius': 6,
            'border_width': 2,
            'font': theme_manager.get_font('md'),
            'text_color': theme_manager.get_color('text'),
            'fg_color': theme_manager.get_color('surface'),
            'border_color': theme_manager.get_color('border')
        }

        if input_type == 'focused':
            base_style['border_color'] = theme_manager.get_color('primary')
        elif input_type == 'error':
            base_style['border_color'] = theme_manager.get_color('error')

        return base_style

    @staticmethod
    def create_card_style(theme_manager) -> Dict[str, Any]:
        """
        创建卡片样式

        Args:
            theme_manager: 主题管理器

        Returns:
            Dict[str, Any]: 卡片样式配置
        """
        return {
            'corner_radius': 12,
            'border_width': 1,
            'fg_color': theme_manager.get_color('surface'),
            'border_color': theme_manager.get_color('border'),
            'font': theme_manager.get_font('md')
        }

    @staticmethod
    def apply_theme_to_widget(widget: Union[tk.Widget, ctk.CTkBaseClass],
                             theme_manager,
                             widget_type: str = 'default',
                             state: str = 'normal') -> None:
        """
        应用主题到组件

        Args:
            widget: 目标组件
            theme_manager: 主题管理器
            widget_type: 组件类型
            state: 组件状态
        """
        try:
            # 获取主题样式
            style = theme_manager.get_theme_style(widget_type, state)

            if not style:
                return

            # 应用颜色
            colors = style.get('colors', {})
            for color_name, color_value in colors.items():
                StyleUtils.apply_color(widget, color_name, color_value)

            # 应用字体
            typography = style.get('typography', {})
            if typography:
                StyleUtils.apply_font(widget, typography)

            # 应用间距
            spacing = style.get('spacing', {})
            if spacing:
                StyleUtils.apply_spacing(widget, spacing)

            # 应用阴影
            shadows = style.get('shadows', {})
            if shadows:
                StyleUtils.apply_shadow(widget, shadows.get('md', ''))

        except Exception as e:
            logger.error(f"应用主题到组件失败: {e}")

    @staticmethod
    def convert_hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        """
        将十六进制颜色转换为RGB

        Args:
            hex_color: 十六进制颜色值

        Returns:
            Tuple[int, int, int]: RGB值
        """
        hex_color = hex_color.lstrip('#')
        return (int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16))

    @staticmethod
    def is_dark_theme(theme_manager) -> bool:
        """
        判断当前主题是否为深色主题

        Args:
            theme_manager: 主题管理器

        Returns:
            bool: 是否为深色主题
        """
        background_color = theme_manager.get_color('background')
        return StyleUtils.get_contrast_color(background_color) == '#FFFFFF'