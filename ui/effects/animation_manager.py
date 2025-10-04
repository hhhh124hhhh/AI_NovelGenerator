"""
动画效果管理器 - AI小说生成器的交互动画系统
提供各种UI动画效果和过渡动画，增强用户体验
"""

import logging
import time
import threading
import math
from typing import Dict, Any, Optional, Callable, List
from enum import Enum
import customtkinter as ctk

logger = logging.getLogger(__name__)


class AnimationType(Enum):
    """动画类型枚举"""
    FADE_IN = "fade_in"
    FADE_OUT = "fade_out"
    SLIDE_IN = "slide_in"
    SLIDE_OUT = "slide_out"
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    HIGHLIGHT = "highlight"
    PULSE = "pulse"
    BOUNCE = "bounce"


class AnimationDirection(Enum):
    """动画方向枚举"""
    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    DOWN = "down"
    CENTER = "center"


class AnimationManager:
    """
    动画效果管理器

    功能：
    - 淡入淡出效果
    - 滑动动画
    - 缩放动画
    - 高亮效果
    - 脉冲动画
    - 弹跳动画
    - 自定义动画序列
    """

    def __init__(self, root_widget: ctk.CTk):
        """
        初始化动画管理器

        Args:
            root_widget: 根组件，用于调度动画
        """
        self.root_widget = root_widget

        # 动画配置
        self.default_duration = 300  # 默认动画时长（毫秒）
        self.default_fps = 60  # 默认帧率
        self.animation_step = 16  # 动画步长（毫秒）

        # 动画状态
        self.active_animations = {}  # 活动动画
        self.animation_queue = []  # 动画队列
        self.is_animation_running = False

        # 缓动函数
        self.easing_functions = {
            'linear': self._easing_linear,
            'ease_in': self._easing_ease_in,
            'ease_out': self._easing_ease_out,
            'ease_in_out': self._easing_ease_in_out,
            'bounce': self._easing_bounce,
            'elastic': self._easing_elastic
        }

        logger.debug("AnimationManager 初始化完成")

    def fade_in(self, widget: ctk.CTkBaseClass, duration: Optional[int] = None,
                callback: Optional[Callable] = None, easing: str = 'ease_out') -> str:
        """
        淡入动画

        Args:
            widget: 目标组件
            duration: 动画时长（毫秒）
            callback: 动画完成回调
            easing: 缓动函数

        Returns:
            animation_id: 动画ID
        """
        return self._animate_property(
            widget, 'opacity', 0.0, 1.0, duration, callback, easing
        )

    def fade_out(self, widget: ctk.CTkBaseClass, duration: Optional[int] = None,
                 callback: Optional[Callable] = None, easing: str = 'ease_in') -> str:
        """
        淡出动画

        Args:
            widget: 目标组件
            duration: 动画时长（毫秒）
            callback: 动画完成回调
            easing: 缓动函数

        Returns:
            animation_id: 动画ID
        """
        return self._animate_property(
            widget, 'opacity', 1.0, 0.0, duration, callback, easing
        )

    def slide_in(self, widget: ctk.CTkBaseClass, direction: AnimationDirection = AnimationDirection.LEFT,
                 duration: Optional[int] = None, callback: Optional[Callable] = None, easing: str = 'ease_out') -> str:
        """
        滑入动画

        Args:
            widget: 目标组件
            direction: 滑动方向
            duration: 动画时长（毫秒）
            callback: 动画完成回调
            easing: 缓动函数

        Returns:
            animation_id: 动画ID
        """
        # 获取组件当前位置
        current_x = widget.winfo_x() if widget.winfo_exists() else 0
        current_y = widget.winfo_y() if widget.winfo_exists() else 0

        # 根据方向设置起始位置
        screen_width = widget.winfo_screenwidth() if widget.winfo_exists() else 1920
        screen_height = widget.winfo_screenheight() if widget.winfo_exists() else 1080

        start_positions = {
            AnimationDirection.LEFT: (-screen_width, current_y),
            AnimationDirection.RIGHT: (screen_width, current_y),
            AnimationDirection.UP: (current_x, -screen_height),
            AnimationDirection.DOWN: (current_x, screen_height),
            AnimationDirection.CENTER: (0, 0)
        }

        start_x, start_y = start_positions[direction]

        # 创建位移动画
        animation_id = self._generate_animation_id()
        self._start_animation(animation_id, {
            'widget': widget,
            'type': 'slide',
            'start_x': start_x,
            'start_y': start_y,
            'end_x': current_x,
            'end_y': current_y,
            'duration': duration or self.default_duration,
            'callback': callback,
            'easing': easing,
            'start_time': time.time()
        })

        return animation_id

    def slide_out(self, widget: ctk.CTkBaseClass, direction: AnimationDirection = AnimationDirection.RIGHT,
                  duration: Optional[int] = None, callback: Optional[Callable] = None, easing: str = 'ease_in') -> str:
        """
        滑出动画

        Args:
            widget: 目标组件
            direction: 滑动方向
            duration: 动画时长（毫秒）
            callback: 动画完成回调
            easing: 缓动函数

        Returns:
            animation_id: 动画ID
        """
        # 获取组件当前位置
        current_x = widget.winfo_x() if widget.winfo_exists() else 0
        current_y = widget.winfo_y() if widget.winfo_exists() else 0

        # 根据方向设置结束位置
        screen_width = widget.winfo_screenwidth() if widget.winfo_exists() else 1920
        screen_height = widget.winfo_screenheight() if widget.winfo_exists() else 1080

        end_positions = {
            AnimationDirection.LEFT: (-screen_width, current_y),
            AnimationDirection.RIGHT: (screen_width, current_y),
            AnimationDirection.UP: (current_x, -screen_height),
            AnimationDirection.DOWN: (current_x, screen_height),
            AnimationDirection.CENTER: (0, 0)
        }

        end_x, end_y = end_positions[direction]

        # 创建位移动画
        animation_id = self._generate_animation_id()
        self._start_animation(animation_id, {
            'widget': widget,
            'type': 'slide',
            'start_x': current_x,
            'start_y': current_y,
            'end_x': end_x,
            'end_y': end_y,
            'duration': duration or self.default_duration,
            'callback': callback,
            'easing': easing,
            'start_time': time.time()
        })

        return animation_id

    def scale_up(self, widget: ctk.CTkBaseClass, from_scale: float = 0.8, to_scale: float = 1.0,
                 duration: Optional[int] = None, callback: Optional[Callable] = None, easing: str = 'ease_out') -> str:
        """
        放大动画

        Args:
            widget: 目标组件
            from_scale: 起始缩放比例
            to_scale: 结束缩放比例
            duration: 动画时长（毫秒）
            callback: 动画完成回调
            easing: 缓动函数

        Returns:
            animation_id: 动画ID
        """
        return self._animate_property(
            widget, 'scale', from_scale, to_scale, duration, callback, easing
        )

    def scale_down(self, widget: ctk.CTkBaseClass, from_scale: float = 1.0, to_scale: float = 0.8,
                   duration: Optional[int] = None, callback: Optional[Callable] = None, easing: str = 'ease_in') -> str:
        """
        缩小动画

        Args:
            widget: 目标组件
            from_scale: 起始缩放比例
            to_scale: 结束缩放比例
            duration: 动画时长（毫秒）
            callback: 动画完成回调
            easing: 缓动函数

        Returns:
            animation_id: 动画ID
        """
        return self._animate_property(
            widget, 'scale', from_scale, to_scale, duration, callback, easing
        )

    def highlight(self, widget: ctk.CTkBaseClass, highlight_color: str = "#007ACC",
                  duration: Optional[int] = None, callback: Optional[Callable] = None) -> str:
        """
        高亮动画

        Args:
            widget: 目标组件
            highlight_color: 高亮颜色
            duration: 动画时长（毫秒）
            callback: 动画完成回调

        Returns:
            animation_id: 动画ID
        """
        animation_id = self._generate_animation_id()

        # 获取原始边框颜色
        original_border_color = getattr(widget, '_original_border_color', None)
        if original_border_color is None:
            original_border_color = widget.cget('border_color') if widget.winfo_exists() else "#1E1E1E"
            setattr(widget, '_original_border_color', original_border_color)

        self._start_animation(animation_id, {
            'widget': widget,
            'type': 'highlight',
            'highlight_color': highlight_color,
            'original_color': original_border_color,
            'duration': duration or 600,
            'callback': callback,
            'start_time': time.time()
        })

        return animation_id

    def pulse(self, widget: ctk.CTkBaseClass, scale_factor: float = 1.05,
              duration: Optional[int] = None, callback: Optional[Callable] = None) -> str:
        """
        脉冲动画

        Args:
            widget: 目标组件
            scale_factor: 缩放因子
            duration: 动画时长（毫秒）
            callback: 动画完成回调

        Returns:
            animation_id: 动画ID
        """
        animation_id = self._generate_animation_id()

        self._start_animation(animation_id, {
            'widget': widget,
            'type': 'pulse',
            'scale_factor': scale_factor,
            'duration': duration or 800,
            'callback': callback,
            'start_time': time.time()
        })

        return animation_id

    def bounce(self, widget: ctk.CTkBaseClass, bounce_height: int = 20,
               duration: Optional[int] = None, callback: Optional[Callable] = None) -> str:
        """
        弹跳动画

        Args:
            widget: 目标组件
            bounce_height: 弹跳高度
            duration: 动画时长（毫秒）
            callback: 动画完成回调

        Returns:
            animation_id: 动画ID
        """
        animation_id = self._generate_animation_id()

        self._start_animation(animation_id, {
            'widget': widget,
            'type': 'bounce',
            'bounce_height': bounce_height,
            'duration': duration or 1000,
            'callback': callback,
            'start_time': time.time()
        })

        return animation_id

    def create_sequence(self, animations: List[Dict[str, Any]], callback: Optional[Callable] = None) -> str:
        """
        创建动画序列

        Args:
            animations: 动画列表，每个元素包含动画类型和参数
            callback: 序列完成回调

        Returns:
            sequence_id: 序列ID
        """
        sequence_id = self._generate_animation_id()

        def run_sequence():
            for i, animation_config in enumerate(animations):
                try:
                    # 获取动画类型和参数
                    animation_type = animation_config.get('type', '')
                    animation_params = animation_config.get('params', {})

                    # 设置最后一个动画的回调
                    if i == len(animations) - 1:
                        animation_params['callback'] = callback
                    else:
                        # 创建一个简单的等待回调
                        animation_params['callback'] = lambda: None

                    # 执行动画
                    self._execute_animation(animation_type, **animation_params)

                    # 等待动画完成
                    duration = animation_params.get('duration', self.default_duration)
                    time.sleep(duration / 1000.0)

                except Exception as e:
                    logger.error(f"执行序列动画 {i} 失败: {e}")

        # 在新线程中运行序列
        sequence_thread = threading.Thread(target=run_sequence, daemon=True)
        sequence_thread.start()

        return sequence_id

    def stop_animation(self, animation_id: str):
        """停止指定的动画"""
        if animation_id in self.active_animations:
            del self.active_animations[animation_id]
            logger.debug(f"动画 {animation_id} 已停止")

    def stop_all_animations(self):
        """停止所有动画"""
        self.active_animations.clear()
        logger.debug("所有动画已停止")

    def _animate_property(self, widget: ctk.CTkBaseClass, property_name: str,
                         from_value: float, to_value: float, duration: Optional[int],
                         callback: Optional[Callable], easing: str) -> str:
        """
        属性动画

        Args:
            widget: 目标组件
            property_name: 属性名称
            from_value: 起始值
            to_value: 结束值
            duration: 动画时长
            callback: 完成回调
            easing: 缓动函数

        Returns:
            animation_id: 动画ID
        """
        animation_id = self._generate_animation_id()

        self._start_animation(animation_id, {
            'widget': widget,
            'type': 'property',
            'property': property_name,
            'from_value': from_value,
            'to_value': to_value,
            'duration': duration or self.default_duration,
            'callback': callback,
            'easing': easing,
            'start_time': time.time()
        })

        return animation_id

    def _start_animation(self, animation_id: str, animation_data: Dict[str, Any]):
        """开始动画"""
        self.active_animations[animation_id] = animation_data

        # 如果动画循环未运行，启动它
        if not self.is_animation_running:
            self._start_animation_loop()

    def _start_animation_loop(self):
        """启动动画循环"""
        self.is_animation_running = True

        def animation_loop():
            while self.active_animations:
                try:
                    current_time = time.time()
                    completed_animations = []

                    # 创建副本以避免在迭代时修改字典
                    animations_copy = dict(self.active_animations)
                    for animation_id, animation_data in animations_copy.items():
                        # 检查动画是否仍然存在（因为在创建副本后可能已被删除）
                        if animation_id not in self.active_animations:
                            continue
                            
                        # 计算进度
                        elapsed = (current_time - animation_data['start_time']) * 1000
                        duration = animation_data['duration']
                        progress = min(elapsed / duration, 1.0)

                        # 应用缓动函数
                        easing_name = animation_data.get('easing', 'linear')
                        easing_func = self.easing_functions.get(easing_name, self._easing_linear)
                        eased_progress = easing_func(progress)

                        # 更新动画
                        if self._update_animation(animation_data, eased_progress):
                            completed_animations.append(animation_id)

                    # 移除完成的动画
                    for animation_id in completed_animations:
                        self._complete_animation(animation_id)

                    # 等待下一帧
                    time.sleep(self.animation_step / 1000.0)

                except Exception as e:
                    logger.error(f"动画循环错误: {e}")

            self.is_animation_running = False

        # 在新线程中运行动画循环
        animation_thread = threading.Thread(target=animation_loop, daemon=True)
        animation_thread.start()

    def _update_animation(self, animation_data: Dict[str, Any], progress: float) -> bool:
        """
        更新动画

        Args:
            animation_data: 动画数据
            progress: 动画进度（0.0-1.0）

        Returns:
            bool: 动画是否完成
        """
        try:
            widget = animation_data['widget']
            animation_type = animation_data['type']

            # 检查组件是否仍然存在
            if not widget.winfo_exists():
                return True

            if animation_type == 'property':
                return self._update_property_animation(animation_data, progress)
            elif animation_type == 'slide':
                return self._update_slide_animation(animation_data, progress)
            elif animation_type == 'highlight':
                return self._update_highlight_animation(animation_data, progress)
            elif animation_type == 'pulse':
                return self._update_pulse_animation(animation_data, progress)
            elif animation_type == 'bounce':
                return self._update_bounce_animation(animation_data, progress)

            return progress >= 1.0

        except Exception as e:
            logger.error(f"更新动画失败: {e}")
            return True

    def _update_property_animation(self, animation_data: Dict[str, Any], progress: float) -> bool:
        """更新属性动画"""
        widget = animation_data['widget']
        property_name = animation_data['property']
        from_value = animation_data['from_value']
        to_value = animation_data['to_value']

        # 计算当前值
        current_value = from_value + (to_value - from_value) * progress

        # 应用属性变化
        if property_name == 'opacity':
            # CustomTkinter不直接支持透明度，这里简化处理
            if progress < 0.5:
                widget.pack_forget()
            else:
                widget.pack(fill="both", expand=True)
        elif property_name == 'scale':
            # 简化的缩放处理
            if hasattr(widget, 'configure'):
                try:
                    current_font = widget.cget('font')
                    if isinstance(current_font, tuple):
                        font_size = int(current_font[1] * current_value)
                        new_font = (current_font[0], font_size) + current_font[2:]
                        widget.configure(font=new_font)
                except:
                    pass

        return progress >= 1.0

    def _update_slide_animation(self, animation_data: Dict[str, Any], progress: float) -> bool:
        """更新滑动动画"""
        widget = animation_data['widget']
        start_x = animation_data['start_x']
        start_y = animation_data['start_y']
        end_x = animation_data['end_x']
        end_y = animation_data['end_y']

        # 计算当前位置
        current_x = start_x + (end_x - start_x) * progress
        current_y = start_y + (end_y - start_y) * progress

        # 简化的位置处理（使用pack布局）
        if hasattr(widget, 'pack'):
            if progress < 1.0:
                widget.pack_forget()
            else:
                widget.pack(fill="both", expand=True)

        return progress >= 1.0

    def _update_highlight_animation(self, animation_data: Dict[str, Any], progress: float) -> bool:
        """更新高亮动画"""
        widget = animation_data['widget']
        highlight_color = animation_data['highlight_color']
        original_color = animation_data['original_color']

        if hasattr(widget, 'configure'):
            try:
                # 前半段：高亮
                if progress < 0.5:
                    widget.configure(border_color=highlight_color)
                # 后半段：恢复原始颜色
                else:
                    widget.configure(border_color=original_color)
            except:
                pass

        return progress >= 1.0

    def _update_pulse_animation(self, animation_data: Dict[str, Any], progress: float) -> bool:
        """更新脉冲动画"""
        widget = animation_data['widget']
        scale_factor = animation_data['scale_factor']

        # 计算脉冲缩放
        pulse_progress = (progress % 0.5) * 2  # 0-1的脉冲周期
        current_scale = 1.0 + (scale_factor - 1.0) * pulse_progress

        # 简化的缩放处理
        if hasattr(widget, 'configure'):
            try:
                current_font = widget.cget('font')
                if isinstance(current_font, tuple):
                    font_size = int(current_font[1] * current_scale)
                    new_font = (current_font[0], font_size) + current_font[2:]
                    widget.configure(font=new_font)
            except:
                pass

        return progress >= 1.0

    def _update_bounce_animation(self, animation_data: Dict[str, Any], progress: float) -> bool:
        """更新弹跳动画"""
        widget = animation_data['widget']
        bounce_height = animation_data['bounce_height']

        # 计算弹跳位置（使用简化的正弦波）
        bounce_progress = progress * 3.14159  # 0到π
        current_bounce = abs(bounce_height * (1 - progress) * (bounce_progress / 3.14159))

        # 简化的位置处理
        if hasattr(widget, 'pack'):
            # 这里只是模拟，实际弹跳效果需要更复杂的布局管理
            pass

        return progress >= 1.0

    def _complete_animation(self, animation_id: str):
        """完成动画"""
        if animation_id in self.active_animations:
            animation_data = self.active_animations[animation_id]
            callback = animation_data.get('callback')

            # 移除动画
            del self.active_animations[animation_id]

            # 调用完成回调
            if callback:
                try:
                    callback()
                except Exception as e:
                    logger.error(f"动画完成回调失败: {e}")

    def _execute_animation(self, animation_type: str, **kwargs):
        """执行动画"""
        try:
            if animation_type == 'fade_in':
                self.fade_in(**kwargs)
            elif animation_type == 'fade_out':
                self.fade_out(**kwargs)
            elif animation_type == 'slide_in':
                self.slide_in(**kwargs)
            elif animation_type == 'slide_out':
                self.slide_out(**kwargs)
            elif animation_type == 'scale_up':
                self.scale_up(**kwargs)
            elif animation_type == 'scale_down':
                self.scale_down(**kwargs)
            elif animation_type == 'highlight':
                self.highlight(**kwargs)
            elif animation_type == 'pulse':
                self.pulse(**kwargs)
            elif animation_type == 'bounce':
                self.bounce(**kwargs)
            else:
                logger.warning(f"未知的动画类型: {animation_type}")

        except Exception as e:
            logger.error(f"执行动画失败: {e}")

    def _generate_animation_id(self) -> str:
        """生成动画ID"""
        return f"animation_{int(time.time() * 1000)}_{len(self.active_animations)}"

    # 缓动函数
    def _easing_linear(self, t: float) -> float:
        """线性缓动"""
        return t

    def _easing_ease_in(self, t: float) -> float:
        """加速缓动"""
        return t * t

    def _easing_ease_out(self, t: float) -> float:
        """减速缓动"""
        return 1 - (1 - t) * (1 - t)

    def _easing_ease_in_out(self, t: float) -> float:
        """加速减速缓动"""
        if t < 0.5:
            return 2 * t * t
        else:
            return 1 - 2 * (1 - t) * (1 - t)

    def _easing_bounce(self, t: float) -> float:
        """弹跳缓动"""
        if t < 1 / 2.75:
            return 7.5625 * t * t
        elif t < 2 / 2.75:
            t -= 1.5 / 2.75
            return 7.5625 * t * t + 0.75
        elif t < 2.5 / 2.75:
            t -= 2.25 / 2.75
            return 7.5625 * t * t + 0.9375
        else:
            t -= 2.625 / 2.75
            return 7.5625 * t * t + 0.984375

    def _easing_elastic(self, t: float) -> float:
        """弹性缓动"""
        if t == 0:
            return 0
        if t == 1:
            return 1

        p = 0.3
        s = p / 4
        return -pow(2, 10 * (t - 1)) * math.sin((t - s) * (2 * 3.14159) / p)