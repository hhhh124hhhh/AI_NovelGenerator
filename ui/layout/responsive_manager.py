"""
响应式布局管理器 - 负责动态调整界面布局
根据窗口大小自动适配最合适的布局策略
"""

import logging
from typing import Dict, Any, Callable, Optional, Set
from .breakpoints import Breakpoints, LayoutType

logger = logging.getLogger(__name__)


class ResponsiveLayoutManager:
    """
    响应式布局管理器

    负责：
    - 监听窗口大小变化
    - 自动切换布局策略
    - 管理组件的响应式行为
    - 提供布局变化通知
    """

    def __init__(self):
        """初始化响应式布局管理器"""
        self._current_layout_type = LayoutType.DESKTOP
        self._current_width = 1200
        self._current_height = 800
        self._observers: Set[Callable[[LayoutType, Dict[str, Any]], None]] = set()
        self._layout_cache: Dict[str, Any] = {}
        self._debounce_timer = None

        # 初始化默认布局
        self._apply_default_layout()

    def _apply_default_layout(self):
        """应用默认布局"""
        self.update_layout(1200, 800)

    def update_layout(self, width: int, height: int, force: bool = False) -> bool:
        """
        更新布局

        Args:
            width: 窗口宽度
            height: 窗口高度
            force: 是否强制更新

        Returns:
            布局是否发生变化
        """
        if not force and self._is_same_size(width, height):
            return False

        old_layout_type = self._current_layout_type
        new_layout_type = Breakpoints.get_layout_type(width)

        self._current_width = width
        self._current_height = height

        layout_changed = old_layout_type != new_layout_type

        if layout_changed:
            self._current_layout_type = new_layout_type
            logger.info(f"布局类型变更: {old_layout_type.value} -> {new_layout_type.value}")

            # 获取新的布局配置
            new_config = Breakpoints.get_config(width)
            self._layout_cache = new_config.copy()

            # 通知观察者
            self._notify_layout_changed(new_layout_type, new_config)

        return layout_changed

    def get_current_layout_type(self) -> LayoutType:
        """获取当前布局类型"""
        return self._current_layout_type

    def get_current_config(self) -> Dict[str, Any]:
        """获取当前布局配置"""
        if not self._layout_cache:
            self._layout_cache = Breakpoints.get_config(self._current_width)
        return self._layout_cache.copy()

    def is_mobile_layout(self) -> bool:
        """判断当前是否为移动端布局"""
        return self._current_layout_type == LayoutType.MOBILE

    def is_tablet_layout(self) -> bool:
        """判断当前是否为平板布局"""
        return self._current_layout_type == LayoutType.TABLET

    def is_desktop_layout(self) -> bool:
        """判断当前是否为桌面布局"""
        return self._current_layout_type in [LayoutType.DESKTOP, LayoutType.LARGE]

    def is_large_layout(self) -> bool:
        """判断当前是否为大屏布局"""
        return self._current_layout_type == LayoutType.LARGE

    def get_sidebar_config(self) -> Dict[str, Any]:
        """获取侧边栏配置"""
        config = self.get_current_config()
        return {
            'visible': config.get('sidebar_visible', True),
            'width': config.get('sidebar_width', 250),
            'collapsible': config.get('sidebar_collapsible', True)
        }

    def get_toolbar_config(self) -> Dict[str, Any]:
        """获取工具栏配置"""
        config = self.get_current_config()
        return {
            'visible': config.get('show_toolbar', True),
            'compact': config.get('compact_mode', False)
        }

    def get_font_config(self) -> Dict[str, Any]:
        """获取字体配置"""
        config = self.get_current_config()
        return {
            'scale': config.get('font_scale', 1.0),
            'compact': config.get('compact_mode', False)
        }

    def subscribe_layout_changes(self, callback: Callable[[LayoutType, Dict[str, Any]], None]) -> str:
        """
        订阅布局变化

        Args:
            callback: 回调函数，参数为 (layout_type, config)

        Returns:
            订阅ID
        """
        self._observers.add(callback)
        subscription_id = f"layout_{len(self._observers)}_{hash(callback)}"
        logger.debug(f"添加布局变化订阅: {subscription_id}")
        return subscription_id

    def unsubscribe_layout_changes(self, callback: Callable) -> None:
        """
        取消订阅布局变化

        Args:
            callback: 回调函数
        """
        if callback in self._observers:
            self._observers.remove(callback)
            logger.debug("取消布局变化订阅")

    def optimize_layout_for_content(self, content_type: str, content_size: Dict[str, int]) -> Dict[str, Any]:
        """
        根据内容类型和大小优化布局

        Args:
            content_type: 内容类型 (如 'text', 'image', 'table')
            content_size: 内容尺寸 {'width': int, 'height': int}

        Returns:
            优化建议
        """
        current_config = self.get_current_config()
        suggestions = {}

        # 根据内容类型提供建议
        if content_type == 'table':
            if self.is_mobile_layout():
                suggestions['use_horizontal_scroll'] = True
                suggestions['compact_font'] = True
            elif self.is_tablet_layout():
                suggestions['reduce_column_padding'] = True

        elif content_type == 'image':
            available_width = self._current_width
            if current_config.get('sidebar_visible', True):
                available_width -= current_config.get('sidebar_width', 250)

            if content_size['width'] > available_width:
                suggestions['scale_image'] = True
                suggestions['max_width'] = available_width - 40

        elif content_type == 'text':
            if content_size['width'] < 400:
                suggestions['increase_font_size'] = True
            elif content_size['width'] > 1200 and not self.is_large_layout():
                suggestions['use_columns'] = True

        return suggestions

    def get_responsive_class(self, base_class: str) -> str:
        """
        获取响应式CSS类名

        Args:
            base_class: 基础类名

        Returns:
            响应式类名
        """
        layout_suffix = {
            LayoutType.MOBILE: 'mobile',
            LayoutType.TABLET: 'tablet',
            LayoutType.DESKTOP: 'desktop',
            LayoutType.LARGE: 'large'
        }

        suffix = layout_suffix.get(self._current_layout_type, 'desktop')
        return f"{base_class}-{suffix}"

    def simulate_layout_change(self, width: int, height: int) -> Dict[str, Any]:
        """
        模拟布局变化（不实际应用）

        Args:
            width: 模拟的窗口宽度
            height: 模拟的窗口高度

        Returns:
            模拟的布局配置
        """
        layout_type = Breakpoints.get_layout_type(width)
        config = Breakpoints.get_config(width)

        return {
            'layout_type': layout_type,
            'config': config,
            'changes_from_current': self._calculate_changes(config)
        }

    def _is_same_size(self, width: int, height: int) -> bool:
        """检查尺寸是否相同"""
        return self._current_width == width and self._current_height == height

    def _notify_layout_changed(self, layout_type: LayoutType, config: Dict[str, Any]) -> None:
        """通知布局变化"""
        for callback in self._observers:
            try:
                callback(layout_type, config)
            except Exception as e:
                logger.error(f"布局变化通知失败: {e}")

    def _calculate_changes(self, new_config: Dict[str, Any]) -> Dict[str, Any]:
        """计算配置变化"""
        changes = {}
        current_config = self.get_current_config()

        for key, value in new_config.items():
            if key not in current_config or current_config[key] != value:
                changes[key] = {
                    'old': current_config.get(key),
                    'new': value
                }

        return changes

    def get_layout_info(self) -> Dict[str, Any]:
        """获取当前布局信息"""
        return {
            'layout_type': self._current_layout_type.value,
            'window_size': {
                'width': self._current_width,
                'height': self._current_height
            },
            'config': self.get_current_config(),
            'is_mobile': self.is_mobile_layout(),
            'is_tablet': self.is_tablet_layout(),
            'is_desktop': self.is_desktop_layout(),
            'is_large': self.is_large_layout()
        }