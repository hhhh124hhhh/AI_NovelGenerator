"""
状态管理器 - 负责应用状态的统一管理
提供状态订阅、更新和持久化功能
"""

import json
import threading
from typing import Dict, Any, Callable, Optional, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class StateManager:
    """
    状态管理器

    负责管理应用的全局状态，提供：
    - 状态存储和获取
    - 状态更新和通知
    - 状态订阅和取消订阅
    - 状态持久化
    """

    def __init__(self):
        """初始化状态管理器"""
        self._state: Dict[str, Any] = {}
        self._observers: Dict[str, List[Callable]] = {}
        self._lock = threading.RLock()
        self._history: List[Dict[str, Any]] = []
        self._max_history = 100

        # 初始化默认状态
        self._initialize_default_state()

    def _initialize_default_state(self):
        """初始化默认状态"""
        default_state = {
            'app': {
                'window_state': {
                    'width': 1200,
                    'height': 800,
                    'maximized': False,
                    'position': {'x': 100, 'y': 100}
                },
                'active_tab': 'config',
                'theme': 'dark',
                'layout': 'desktop'
            },
            'user': {
                'preferences': {
                    'auto_save': True,
                    'show_tips': True,
                    'language': 'zh_CN'
                },
                'recent_files': [],
                'current_project': None
            },
            'ui': {
                'sidebar_visible': True,
                'sidebar_width': 250,
                'status_bar_visible': True,
                'toolbar_visible': True
            }
        }

        with self._lock:
            self._state.update(default_state)
            self._add_to_history(default_state)

    def get_state(self, key: str, default: Any = None) -> Any:
        """
        获取状态值

        Args:
            key: 状态键，支持点号分隔的嵌套键 (如 'app.theme')
            default: 默认值

        Returns:
            状态值
        """
        with self._lock:
            try:
                keys = key.split('.')
                value = self._state

                for k in keys:
                    if isinstance(value, dict) and k in value:
                        value = value[k]
                    else:
                        return default

                return value
            except Exception as e:
                logger.error(f"获取状态失败: {key}, 错误: {e}")
                return default

    def update_state(self, updates: Dict[str, Any]) -> None:
        """
        更新状态

        Args:
            updates: 要更新的状态字典
        """
        with self._lock:
            old_state = self._deep_copy(self._state)

            # 应用更新
            self._deep_update(self._state, updates)

            # 添加到历史记录
            self._add_to_history(self._state)

            # 通知观察者
            self._notify_observers(updates, old_state)

            logger.debug(f"状态更新: {updates}")

    def set_state(self, key: str, value: Any) -> None:
        """
        设置单个状态值

        Args:
            key: 状态键
            value: 状态值
        """
        self.update_state({key: value})

    def subscribe(self, key: str, callback: Callable[[str, Any, Any], None]) -> str:
        """
        订阅状态变化

        Args:
            key: 要订阅的状态键
            callback: 回调函数，参数为 (key, new_value, old_value)

        Returns:
            订阅ID
        """
        with self._lock:
            if key not in self._observers:
                self._observers[key] = []

            subscription_id = f"{key}_{len(self._observers[key])}_{datetime.now().timestamp()}"
            self._observers[key].append({
                'id': subscription_id,
                'callback': callback
            })

            logger.debug(f"添加状态订阅: {key}, ID: {subscription_id}")
            return subscription_id

    def unsubscribe(self, subscription_id: str) -> None:
        """
        取消订阅

        Args:
            subscription_id: 订阅ID
        """
        with self._lock:
            for key, observers in self._observers.items():
                self._observers[key] = [
                    obs for obs in observers
                    if obs['id'] != subscription_id
                ]

                if not self._observers[key]:
                    del self._observers[key]

                logger.debug(f"取消状态订阅: {subscription_id}")
                break

    def get_all_state(self) -> Dict[str, Any]:
        """获取所有状态"""
        with self._lock:
            return self._deep_copy(self._state)

    def reset_state(self, key: Optional[str] = None) -> None:
        """
        重置状态

        Args:
            key: 要重置的状态键，None表示重置所有状态
        """
        if key is None:
            # 重置所有状态
            self._state.clear()
            self._initialize_default_state()
            logger.info("已重置所有状态")
        else:
            # 重置特定状态
            with self._lock:
                if '.' in key:
                    keys = key.split('.')
                    self._reset_nested_state(self._state, keys)
                else:
                    if key in self._state:
                        del self._state[key]

                logger.info(f"已重置状态: {key}")

    def save_state(self, file_path: str) -> bool:
        """
        保存状态到文件

        Args:
            file_path: 文件路径

        Returns:
            是否保存成功
        """
        try:
            with self._lock:
                state_data = {
                    'state': self._state,
                    'timestamp': datetime.now().isoformat(),
                    'version': '1.0'
                }

                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(state_data, f, indent=2, ensure_ascii=False)

                logger.info(f"状态已保存到: {file_path}")
                return True

        except Exception as e:
            logger.error(f"保存状态失败: {e}")
            return False

    def load_state(self, file_path: str) -> bool:
        """
        从文件加载状态

        Args:
            file_path: 文件路径

        Returns:
            是否加载成功
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                state_data = json.load(f)

            with self._lock:
                old_state = self._deep_copy(self._state)
                self._state = state_data.get('state', {})
                self._add_to_history(self._state)
                self._notify_observers(self._state, old_state)

            logger.info(f"状态已从文件加载: {file_path}")
            return True

        except Exception as e:
            logger.error(f"加载状态失败: {e}")
            return False

    def get_state_history(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        获取状态历史记录

        Args:
            count: 返回的记录数量

        Returns:
            状态历史记录列表
        """
        with self._lock:
            return self._history[-count:] if count > 0 else self._history.copy()

    def _deep_update(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """深度更新字典"""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_update(target[key], value)
            else:
                target[key] = value

    def _deep_copy(self, obj: Any) -> Any:
        """深度复制对象"""
        if isinstance(obj, dict):
            return {k: self._deep_copy(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._deep_copy(item) for item in obj]
        else:
            return obj

    def _add_to_history(self, state: Dict[str, Any]) -> None:
        """添加状态到历史记录"""
        self._history.append(self._deep_copy(state))

        # 限制历史记录数量
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

    def _notify_observers(self, updates: Dict[str, Any], old_state: Dict[str, Any]) -> None:
        """通知观察者"""
        for key, new_value in updates.items():
            if key in self._observers:
                old_value = self._get_nested_value(old_state, key)

                for observer in self._observers[key]:
                    try:
                        observer['callback'](key, new_value, old_value)
                    except Exception as e:
                        logger.error(f"状态观察者回调失败: {e}")

    def _get_nested_value(self, state: Dict[str, Any], key: str) -> Any:
        """获取嵌套状态值"""
        keys = key.split('.')
        value = state

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None

        return value

    def _reset_nested_state(self, state: Dict[str, Any], keys: List[str]) -> None:
        """重置嵌套状态"""
        if len(keys) == 1:
            key = keys[0]
            if key in state:
                del state[key]
        else:
            key = keys[0]
            if key in state and isinstance(state[key], dict):
                self._reset_nested_state(state[key], keys[1:])