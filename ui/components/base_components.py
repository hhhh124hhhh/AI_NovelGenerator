"""
基础组件系统 - 现代化UI组件的基类和工厂
提供统一的样式应用、主题切换和状态管理功能
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable, Type
from threading import Lock
from enum import Enum

import customtkinter as ctk

logger = logging.getLogger(__name__)


class ComponentState(Enum):
    """组件状态枚举"""
    INITIALIZING = "initializing"
    READY = "ready"
    VISIBLE = "visible"
    HIDDEN = "hidden"
    DISABLED = "disabled"
    DESTROYED = "destroyed"


class StyledComponent(ABC):
    """
    样式化组件基类

    为所有UI组件提供：
    - 统一的样式应用机制
    - 主题变化响应
    - 状态管理
    - 生命周期管理
    - 性能监控
    """

    def __init__(self, parent: ctk.CTk, theme_manager, state_manager=None):
        """
        初始化样式化组件

        Args:
            parent: 父组件
            theme_manager: 主题管理器
            state_manager: 状态管理器
        """
        # 基本属性
        self.parent = parent
        self.theme_manager = theme_manager
        self.state_manager = state_manager

        # 添加tk和_w属性，以支持CustomTkinter的某些功能
        self.tk = parent.tk if hasattr(parent, 'tk') else None
        self._w = str(id(self))  # 添加widget ID

        # 组件状态
        self._state = ComponentState.INITIALIZING
        self._component_id = f"{self.__class__.__name__}_{id(self)}"
        self._style_cache = {}
        self._event_handlers = {}
        self._performance_metrics = {
            'creation_time': time.time(),
            'render_count': 0,
            'last_render_time': 0,
            'total_render_time': 0
        }

        # 线程安全锁
        self._lock = Lock()

        # 初始化组件
        self._initialize_component()

        # 应用样式
        self.apply_theme()

        # 绑定事件
        self._bind_events()

        # 设置状态为就绪
        self._set_state(ComponentState.READY)

        logger.debug(f"StyledComponent {self._component_id} 初始化完成")

    @abstractmethod
    def _initialize_component(self):
        """初始化组件 - 子类必须实现"""
        pass

    @abstractmethod
    def get_component_type(self) -> str:
        """获取组件类型 - 子类必须实现"""
        pass

    def apply_theme(self, theme_name: Optional[str] = None) -> None:
        """
        应用主题到组件

        Args:
            theme_name: 主题名称，None表示使用当前主题
        """
        try:
            start_time = time.time()

            if self.theme_manager:
                if theme_name is None:
                    theme_name = self.theme_manager.get_current_theme()

                # 获取主题样式
                style_data = self._get_theme_style(theme_name)

                # 应用样式
                self._apply_style(style_data)

                # 缓存样式
                self._style_cache[theme_name] = style_data

                render_time = time.time() - start_time
                self._update_performance_metrics(render_time)

                logger.debug(f"组件 {self._component_id} 应用主题 {theme_name} 耗时 {render_time:.3f}s")

        except Exception as e:
            logger.error(f"应用主题失败 {self._component_id}: {e}")

    def _get_theme_style(self, theme_name: str) -> Dict[str, Any]:
        """
        获取主题样式

        Args:
            theme_name: 主题名称

        Returns:
            样式数据
        """
        try:
            component_type = self.get_component_type()

            # 优先使用组件特定样式
            style = self.theme_manager.get_theme_style(component_type)

            # 如果没有组件特定样式，使用基础样式
            if not style:
                style = {
                    'fg_color': self.theme_manager.get_color('surface'),
                    'text_color': self.theme_manager.get_color('text'),
                    'border_color': self.theme_manager.get_color('border')
                }

            return style

        except Exception as e:
            logger.error(f"获取主题样式失败 {self._component_id}: {e}")
            return {}

    def _apply_style(self, style_data: Dict[str, Any]) -> None:
        """
        应用样式到组件

        Args:
            style_data: 样式数据
        """
        try:
            if hasattr(self, 'configure'):
                # 过滤有效的样式属性
                valid_styles = {}
                widget_info = self._get_widget_info()

                for key, value in style_data.items():
                    if key in widget_info['valid_properties']:
                        valid_styles[key] = value

                if valid_styles:
                    self.configure(**valid_styles)

        except Exception as e:
            logger.error(f"应用样式失败 {self._component_id}: {e}")

    def _get_widget_info(self) -> Dict[str, Any]:
        """获取组件信息"""
        try:
            return {
                'class_name': self.__class__.__name__,
                'valid_properties': self._get_valid_properties(),
                'current_style': self._get_current_style()
            }
        except Exception as e:
            logger.error(f"获取组件信息失败 {self._component_id}: {e}")
            return {}

    def _get_valid_properties(self) -> List[str]:
        """获取有效的样式属性"""
        try:
            if hasattr(self, 'configure'):
                import inspect
                sig = inspect.signature(self.configure)
                return list(sig.parameters.keys())
            return []
        except Exception:
            return ['fg_color', 'text_color', 'border_color', 'corner_radius']

    def _get_current_style(self) -> Dict[str, Any]:
        """获取当前样式"""
        try:
            if hasattr(self, 'cget'):
                valid_props = self._get_valid_properties()
                current_style = {}
                for prop in valid_props:
                    try:
                        value = self.cget(prop)
                        current_style[prop] = value
                    except:
                        pass
                return current_style
            return {}
        except Exception:
            return {}

    def _bind_events(self):
        """绑定事件"""
        try:
            # 绑定主题变化事件
            if self.theme_manager:
                self.theme_manager.subscribe(self._on_theme_changed)

            # 绑定自定义事件
            self._bind_custom_events()

        except Exception as e:
            logger.error(f"绑定事件失败 {self._component_id}: {e}")

    def _bind_custom_events(self):
        """绑定自定义事件 - 子类可重写"""
        pass

    def _on_theme_changed(self, theme_name: str, theme_data: Dict[str, Any]):
        """主题变化回调"""
        try:
            self.apply_theme(theme_name)
            self._on_theme_applied(theme_name, theme_data)
        except Exception as e:
            logger.error(f"处理主题变化失败 {self._component_id}: {e}")

    def _on_theme_applied(self, theme_name: str, theme_data: Dict[str, Any]):
        """主题应用后回调 - 子类可重写"""
        pass

    def _set_state(self, new_state: ComponentState):
        """设置组件状态"""
        with self._lock:
            old_state = self._state
            self._state = new_state
            logger.debug(f"组件状态变化 {self._component_id}: {old_state.value} -> {new_state.value}")
            self._on_state_changed(old_state, new_state)

    def _on_state_changed(self, old_state: ComponentState, new_state: ComponentState):
        """状态变化回调 - 子类可重写"""
        pass

    def get_state(self) -> ComponentState:
        """获取组件状态"""
        return self._state

    def is_ready(self) -> bool:
        """检查组件是否就绪"""
        return self._state == ComponentState.READY

    def is_visible(self) -> bool:
        """检查组件是否可见"""
        return self._state == ComponentState.VISIBLE

    def show(self):
        """显示组件"""
        try:
            if hasattr(self, 'grid'):
                self.grid()
            elif hasattr(self, 'pack'):
                self.pack()
            elif hasattr(self, 'place'):
                self.place()

            self._set_state(ComponentState.VISIBLE)

        except Exception as e:
            logger.error(f"显示组件失败 {self._component_id}: {e}")

    def hide(self):
        """隐藏组件"""
        try:
            if hasattr(self, 'grid_forget'):
                self.grid_forget()
            elif hasattr(self, 'pack_forget'):
                self.pack_forget()
            elif hasattr(self, 'place_forget'):
                self.place_forget()

            self._set_state(ComponentState.HIDDEN)

        except Exception as e:
            logger.error(f"隐藏组件失败 {self._component_id}: {e}")

    def enable(self):
        """启用组件"""
        try:
            if hasattr(self, 'configure'):
                self.configure(state="normal")
            self._set_state(ComponentState.READY)
        except Exception as e:
            logger.error(f"启用组件失败 {self._component_id}: {e}")

    def disable(self):
        """禁用组件"""
        try:
            if hasattr(self, 'configure'):
                self.configure(state="disabled")
            self._set_state(ComponentState.DISABLED)
        except Exception as e:
            logger.error(f"禁用组件失败 {self._component_id}: {e}")

    def add_event_handler(self, event: str, handler: Callable) -> None:
        """
        添加事件处理器

        Args:
            event: 事件名称
            handler: 处理函数
        """
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(handler)

    def remove_event_handler(self, event: str, handler: Callable) -> None:
        """
        移除事件处理器

        Args:
            event: 事件名称
            handler: 处理函数
        """
        if event in self._event_handlers:
            try:
                self._event_handlers[event].remove(handler)
            except ValueError:
                pass

    def trigger_event(self, event: str, *args, **kwargs) -> None:
        """
        触发事件

        Args:
            event: 事件名称
            *args: 位置参数
            **kwargs: 关键字参数
        """
        if event in self._event_handlers:
            for handler in self._event_handlers[event]:
                try:
                    handler(*args, **kwargs)
                except Exception as e:
                    logger.error(f"事件处理器执行失败 {self._component_id}.{event}: {e}")

    def _update_performance_metrics(self, render_time: float) -> None:
        """更新性能指标"""
        self._performance_metrics['render_count'] += 1
        self._performance_metrics['last_render_time'] = render_time
        self._performance_metrics['total_render_time'] += render_time

    def get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        metrics = self._performance_metrics.copy()
        if metrics['render_count'] > 0:
            metrics['average_render_time'] = metrics['total_render_time'] / metrics['render_count']
        else:
            metrics['average_render_time'] = 0
        return metrics

    def reset_performance_metrics(self) -> None:
        """重置性能指标"""
        self._performance_metrics = {
            'creation_time': time.time(),
            'render_count': 0,
            'last_render_time': 0,
            'total_render_time': 0
        }

    def get_component_info(self) -> Dict[str, Any]:
        """获取组件完整信息"""
        return {
            'id': self._component_id,
            'type': self.get_component_type(),
            'class': self.__class__.__name__,
            'state': self._state.value,
            'parent': str(self.parent),
            'style_cache': list(self._style_cache.keys()),
            'event_handlers': list(self._event_handlers.keys()),
            'performance': self.get_performance_metrics(),
            'widget_info': self._get_widget_info()
        }

    def destroy(self) -> None:
        """销毁组件"""
        try:
            self._set_state(ComponentState.DESTROYING)

            # 清理事件处理器
            self._event_handlers.clear()

            # 取消主题订阅
            if self.theme_manager:
                self.theme_manager.unsubscribe(self._on_theme_changed)

            # 销毁widget
            if hasattr(self, 'destroy'):
                self.destroy()

            self._set_state(ComponentState.DESTROYED)
            logger.debug(f"组件 {self._component_id} 已销毁")

        except Exception as e:
            logger.error(f"销毁组件失败 {self._component_id}: {e}")

    def __str__(self) -> str:
        return f"StyledComponent({self._component_id}, {self.get_component_type()})"

    def __repr__(self) -> str:
        return self.__str__()


class ComponentFactory:
    """
    组件工厂类

    负责：
    - 组件创建和管理
    - 组件注册和获取
    - 组件实例化
    - 组件生命周期管理
    """

    def __init__(self):
        """初始化组件工厂"""
        self._registered_components: Dict[str, Type[StyledComponent]] = {}
        self._component_instances: Dict[str, StyledComponent] = {}
        self._creation_stats = {
            'total_created': 0,
            'total_destroyed': 0,
            'active_count': 0
        }
        self._lock = Lock()

    def register_component(self, component_type: str, component_class: Type[StyledComponent]) -> bool:
        """
        注册组件类

        Args:
            component_type: 组件类型
            component_class: 组件类

        Returns:
            是否注册成功
        """
        try:
            if not issubclass(component_class, StyledComponent):
                logger.error(f"组件类必须继承StyledComponent: {component_class}")
                return False

            with self._lock:
                self._registered_components[component_type] = component_class
                logger.info(f"注册组件类型: {component_type} -> {component_class.__name__}")
                return True

        except Exception as e:
            logger.error(f"注册组件失败 {component_type}: {e}")
            return False

    def create_component(self, component_type: str, parent: ctk.CTk,
                        theme_manager, state_manager=None, **kwargs) -> Optional[StyledComponent]:
        """
        创建组件实例

        Args:
            component_type: 组件类型
            parent: 父组件
            theme_manager: 主题管理器
            state_manager: 状态管理器
            **kwargs: 其他参数

        Returns:
            组件实例或None
        """
        try:
            with self._lock:
                if component_type not in self._registered_components:
                    logger.error(f"未注册的组件类型: {component_type}")
                    return None

                component_class = self._registered_components[component_type]

                # 创建实例
                instance = component_class(
                    parent=parent,
                    theme_manager=theme_manager,
                    state_manager=state_manager,
                    **kwargs
                )

                # 记录实例
                self._component_instances[instance._component_id] = instance
                self._creation_stats['total_created'] += 1
                self._creation_stats['active_count'] += 1

                logger.debug(f"创建组件实例: {component_type} -> {instance._component_id}")
                return instance

        except Exception as e:
            logger.error(f"创建组件失败 {component_type}: {e}")
            return None

    def get_component(self, component_id: str) -> Optional[StyledComponent]:
        """
        获取组件实例

        Args:
            component_id: 组件ID

        Returns:
            组件实例或None
        """
        with self._lock:
            return self._component_instances.get(component_id)

    def get_components_by_type(self, component_type: str) -> List[StyledComponent]:
        """
        根据类型获取组件实例

        Args:
            component_type: 组件类型

        Returns:
            组件实例列表
        """
        with self._lock:
            return [
                comp for comp in self._component_instances.values()
                if comp.get_component_type() == component_type
            ]

    def destroy_component(self, component_id: str) -> bool:
        """
        销毁组件实例

        Args:
            component_id: 组件ID

        Returns:
            是否销毁成功
        """
        try:
            with self._lock:
                if component_id in self._component_instances:
                    instance = self._component_instances[component_id]
                    instance.destroy()
                    del self._component_instances[component_id]

                    self._creation_stats['total_destroyed'] += 1
                    self._creation_stats['active_count'] -= 1

                    logger.debug(f"销毁组件实例: {component_id}")
                    return True
                return False

        except Exception as e:
            logger.error(f"销毁组件失败 {component_id}: {e}")
            return False

    def get_registered_types(self) -> List[str]:
        """获取已注册的组件类型"""
        with self._lock:
            return list(self._registered_components.keys())

    def get_creation_stats(self) -> Dict[str, int]:
        """获取创建统计"""
        with self._lock:
            return self._creation_stats.copy()

    def clear_all_components(self) -> None:
        """销毁所有组件实例"""
        try:
            with self._lock:
                component_ids = list(self._component_instances.keys())
                for component_id in component_ids:
                    self.destroy_component(component_id)
                logger.info("已销毁所有组件实例")
        except Exception as e:
            logger.error(f"清空组件实例失败: {e}")

    def get_factory_info(self) -> Dict[str, Any]:
        """获取工厂信息"""
        with self._lock:
            return {
                'registered_components': {
                    comp_type: comp_class.__name__
                    for comp_type, comp_class in self._registered_components.items()
                },
                'active_instances': len(self._component_instances),
                'creation_stats': self._creation_stats.copy(),
                'instance_ids': list(self._component_instances.keys())
            }


# 全局组件工厂实例
_component_factory = ComponentFactory()

def get_component_factory() -> ComponentFactory:
    """获取全局组件工厂实例"""
    return _component_factory

def register_component(component_type: str, component_class: Type[StyledComponent]) -> bool:
    """注册组件的便捷函数"""
    return _component_factory.register_component(component_type, component_class)

def create_component(component_type: str, parent: ctk.CTk,
                   theme_manager, state_manager=None, **kwargs) -> Optional[StyledComponent]:
    """创建组件的便捷函数"""
    return _component_factory.create_component(
        component_type, parent, theme_manager, state_manager, **kwargs
    )