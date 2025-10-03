"""
响应式布局断点定义
定义不同屏幕尺寸的布局策略
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any


class LayoutType(Enum):
    """布局类型枚举"""
    MOBILE = "mobile"
    TABLET = "tablet"
    DESKTOP = "desktop"
    LARGE = "large"


@dataclass
class Breakpoint:
    """断点定义"""
    name: str
    min_width: int
    layout_type: LayoutType
    config: Dict[str, Any]


class Breakpoints:
    """响应式布局断点管理"""

    # 断点定义
    BREAKPOINTS = {
        LayoutType.MOBILE: Breakpoint(
            name="Mobile",
            min_width=0,
            layout_type=LayoutType.MOBILE,
            config={
                'sidebar_width': 0,
                'sidebar_visible': False,
                'show_toolbar': False,
                'compact_mode': True,
                'font_scale': 0.9
            }
        ),
        LayoutType.TABLET: Breakpoint(
            name="Tablet",
            min_width=768,
            layout_type=LayoutType.TABLET,
            config={
                'sidebar_width': 200,
                'sidebar_visible': True,
                'sidebar_collapsible': True,
                'show_toolbar': True,
                'compact_mode': True,
                'font_scale': 0.95
            }
        ),
        LayoutType.DESKTOP: Breakpoint(
            name="Desktop",
            min_width=1024,
            layout_type=LayoutType.DESKTOP,
            config={
                'sidebar_width': 250,
                'sidebar_visible': True,
                'sidebar_collapsible': True,
                'show_toolbar': True,
                'compact_mode': False,
                'font_scale': 1.0
            }
        ),
        LayoutType.LARGE: Breakpoint(
            name="Large",
            min_width=1600,
            layout_type=LayoutType.LARGE,
            config={
                'sidebar_width': 280,
                'sidebar_visible': True,
                'sidebar_collapsible': True,
                'show_toolbar': True,
                'compact_mode': False,
                'font_scale': 1.1,
                'show_extra_info': True
            }
        )
    }

    @classmethod
    def get_layout_type(cls, width: int) -> LayoutType:
        """
        根据屏幕宽度获取布局类型

        Args:
            width: 屏幕宽度

        Returns:
            布局类型
        """
        # 从大到小检查断点
        for layout_type in [LayoutType.LARGE, LayoutType.DESKTOP,
                          LayoutType.TABLET, LayoutType.MOBILE]:
            if width >= cls.BREAKPOINTS[layout_type].min_width:
                return layout_type

        return LayoutType.MOBILE

    @classmethod
    def get_breakpoint(cls, layout_type: LayoutType) -> Breakpoint:
        """
        获取断点配置

        Args:
            layout_type: 布局类型

        Returns:
            断点配置
        """
        return cls.BREAKPOINTS.get(layout_type, cls.BREAKPOINTS[LayoutType.DESKTOP])

    @classmethod
    def get_config(cls, width: int) -> Dict[str, Any]:
        """
        根据屏幕宽度获取布局配置

        Args:
            width: 屏幕宽度

        Returns:
            布局配置
        """
        layout_type = cls.get_layout_type(width)
        breakpoint = cls.get_breakpoint(layout_type)
        return breakpoint.config

    @classmethod
    def get_all_breakpoints(cls) -> Dict[LayoutType, Breakpoint]:
        """获取所有断点定义"""
        return cls.BREAKPOINTS.copy()

    @classmethod
    def is_mobile(cls, width: int) -> bool:
        """判断是否为移动端布局"""
        return cls.get_layout_type(width) == LayoutType.MOBILE

    @classmethod
    def is_tablet(cls, width: int) -> bool:
        """判断是否为平板布局"""
        return cls.get_layout_type(width) == LayoutType.TABLET

    @classmethod
    def is_desktop(cls, width: int) -> bool:
        """判断是否为桌面布局"""
        layout_type = cls.get_layout_type(width)
        return layout_type in [LayoutType.DESKTOP, LayoutType.LARGE]

    @classmethod
    def is_large(cls, width: int) -> bool:
        """判断是否为大屏布局"""
        return cls.get_layout_type(width) == LayoutType.LARGE