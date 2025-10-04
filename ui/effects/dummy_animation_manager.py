"""
虚拟动画管理器 - 用于禁用动画功能
根据用户反馈，动画系统影响用户体验，因此提供这个空实现
"""

from enum import Enum
from typing import Optional, Callable, Dict, Any, List
import customtkinter as ctk


class AnimationDirection(Enum):
    """动画方向枚举"""
    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    DOWN = "down"
    CENTER = "center"


class DummyAnimationManager:
    """虚拟动画管理器 - 所有方法都是空实现"""

    def __init__(self, *args, **kwargs):
        pass

    def fade_in(self, widget: ctk.CTkBaseClass, duration: Optional[int] = None,
                callback: Optional[Callable] = None, easing: str = 'ease_out') -> str:
        """淡入动画 - 空实现"""
        return ""

    def fade_out(self, widget: ctk.CTkBaseClass, duration: Optional[int] = None,
                 callback: Optional[Callable] = None, easing: str = 'ease_in') -> str:
        """淡出动画 - 空实现"""
        return ""

    def slide_in(self, widget: ctk.CTkBaseClass, direction: AnimationDirection = AnimationDirection.LEFT,
                 duration: Optional[int] = None, callback: Optional[Callable] = None, easing: str = 'ease_out') -> str:
        """滑入动画 - 空实现"""
        return ""

    def slide_out(self, widget: ctk.CTkBaseClass, direction: AnimationDirection = AnimationDirection.RIGHT,
                  duration: Optional[int] = None, callback: Optional[Callable] = None, easing: str = 'ease_in') -> str:
        """滑出动画 - 空实现"""
        return ""

    def scale_up(self, widget: ctk.CTkBaseClass, from_scale: float = 0.8, to_scale: float = 1.0,
                 duration: Optional[int] = None, callback: Optional[Callable] = None, easing: str = 'ease_out') -> str:
        """放大动画 - 空实现"""
        return ""

    def scale_down(self, widget: ctk.CTkBaseClass, from_scale: float = 1.0, to_scale: float = 0.8,
                   duration: Optional[int] = None, callback: Optional[Callable] = None, easing: str = 'ease_in') -> str:
        """缩小动画 - 空实现"""
        return ""

    def bounce(self, widget: ctk.CTkBaseClass, bounce_height: int = 20,
               duration: Optional[int] = None, callback: Optional[Callable] = None) -> str:
        """弹跳动画 - 空实现"""
        return ""

    def pulse(self, widget: ctk.CTkBaseClass, scale_factor: float = 1.05,
              duration: Optional[int] = None, callback: Optional[Callable] = None) -> str:
        """脉冲动画 - 空实现"""
        return ""

    def highlight(self, widget: ctk.CTkBaseClass, highlight_color: str = "#007ACC",
                  duration: Optional[int] = None, callback: Optional[Callable] = None) -> str:
        """高亮动画 - 空实现"""
        return ""

    def shake(self, *args, **kwargs):
        """震动动画 - 空实现"""
        pass

    def rotate(self, *args, **kwargs):
        """旋转动画 - 空实现"""
        pass

    def create_sequence(self, animations: List[Dict[str, Any]], callback: Optional[Callable] = None) -> str:
        """创建动画序列 - 空实现"""
        return ""

    def stop_animation(self, animation_id: str):
        """停止指定的动画 - 空实现"""
        pass

    def stop_all_animations(self):
        """停止所有动画 - 空实现"""
        pass


# 创建一个单例实例
_dummy_manager = DummyAnimationManager()

def get_animation_manager():
    """获取动画管理器 - 返回虚拟实例"""
    return _dummy_manager