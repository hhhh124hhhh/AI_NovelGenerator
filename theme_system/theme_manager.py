"""
主题管理器 - 核心主题管理功能
负责主题的加载、切换、应用和持久化
"""

import json
import os
from typing import Dict, Any, Callable, Optional, List
from threading import Lock
import logging

logger = logging.getLogger(__name__)


class ThemeManager:
    """
    主题管理器 - 单例模式
    负责管理应用的主题系统，包括主题加载、切换和应用
    """

    _instance = None
    _lock = Lock()

    def __new__(cls, config_path: Optional[str] = None):
        """单例模式实现"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化主题管理器

        Args:
            config_path: 主题配置文件路径
        """
        if hasattr(self, '_initialized'):
            return

        self._config_path = config_path or 'config/themes'
        self._current_theme = 'dark'
        self._themes: Dict[str, Dict[str, Any]] = {}
        self._observers: List[Callable[[str, Dict[str, Any]], None]] = []
        self._theme_preferences = {}

        # 确保配置目录存在
        os.makedirs(self._config_path, exist_ok=True)

        # 初始化系统
        self._load_themes()
        self._load_preferences()
        self._apply_default_theme()

        self._initialized = True
        logger.info("主题管理器初始化完成")

    def _load_themes(self) -> None:
        """加载所有可用的主题"""
        try:
            # 加载内置主题
            self._load_builtin_themes()

            # 加载用户自定义主题
            self._load_user_themes()

            logger.info(f"已加载 {len(self._themes)} 个主题")

        except Exception as e:
            logger.error(f"加载主题失败: {e}")
            # 加载默认主题作为后备
            self._load_fallback_theme()

    def _load_builtin_themes(self) -> None:
        """加载内置主题"""
        builtin_themes = ['dark', 'light', 'soft_light', 'neutral']

        for theme_name in builtin_themes:
            theme_file = os.path.join(self._config_path, f'{theme_name}_theme.json')
            if os.path.exists(theme_file):
                try:
                    with open(theme_file, 'r', encoding='utf-8') as f:
                        theme_data = json.load(f)
                    self._themes[theme_name] = theme_data
                    logger.debug(f"加载内置主题: {theme_name}")
                except Exception as e:
                    logger.error(f"加载主题 {theme_name} 失败: {e}")
            else:
                # 如果主题文件不存在，创建默认主题
                default_theme = self._create_default_theme(theme_name)
                self._themes[theme_name] = default_theme
                self._save_theme(theme_name, default_theme)

    def _load_user_themes(self) -> None:
        """加载用户自定义主题"""
        user_themes_dir = os.path.join(self._config_path, 'user')
        if not os.path.exists(user_themes_dir):
            return

        for filename in os.listdir(user_themes_dir):
            if filename.endswith('_theme.json'):
                theme_name = filename.replace('_theme.json', '')
                theme_file = os.path.join(user_themes_dir, filename)

                try:
                    with open(theme_file, 'r', encoding='utf-8') as f:
                        theme_data = json.load(f)
                    self._themes[theme_name] = theme_data
                    logger.debug(f"加载用户主题: {theme_name}")
                except Exception as e:
                    logger.error(f"加载用户主题 {theme_name} 失败: {e}")

    def _create_default_theme(self, theme_name: str) -> Dict[str, Any]:
        """创建默认主题配置"""
        if theme_name == 'dark':
            return {
                "name": "深色主题",
                "description": "适合夜间使用的深色主题",
                "colors": {
                    "primary": "#0078D4",
                    "secondary": "#6C757D",
                    "background": "#1E1E1E",
                    "surface": "#252526",
                    "text": "#CCCCCC",
                    "text_secondary": "#969696",
                    "border": "#3E3E42",
                    "success": "#107C10",
                    "warning": "#FF8C00",
                    "error": "#D13438",
                    "info": "#0078D4"
                },
                "typography": {
                    "font_family": "Microsoft YaHei UI",
                    "font_size": {
                        "xs": 10,
                        "sm": 12,
                        "md": 14,
                        "lg": 16,
                        "xl": 18,
                        "xxl": 24
                    },
                    "line_height": 1.5
                },
                "spacing": {
                    "xs": 2,
                    "sm": 4,
                    "md": 8,
                    "lg": 16,
                    "xl": 24,
                    "xxl": 32
                },
                "shadows": {
                    "sm": "0 1px 2px rgba(0,0,0,0.3)",
                    "md": "0 4px 6px rgba(0,0,0,0.3)",
                    "lg": "0 10px 15px rgba(0,0,0,0.3)"
                }
            }
        elif theme_name == 'light':
            return {
                "name": "浅色主题",
                "description": "适合白天使用的浅色主题",
                "colors": {
                    "primary": "#0078D4",
                    "secondary": "#6C757D",
                    "background": "#F8F9FA",
                    "surface": "#FFFFFF",
                    "text": "#333333",
                    "text_secondary": "#6C757D",
                    "border": "#E9ECEF",
                    "success": "#28A745",
                    "warning": "#FFC107",
                    "error": "#DC3545",
                    "info": "#17A2B8"
                },
                "typography": {
                    "font_family": "Microsoft YaHei UI",
                    "font_size": {
                        "xs": 10,
                        "sm": 12,
                        "md": 14,
                        "lg": 16,
                        "xl": 18,
                        "xxl": 24
                    },
                    "line_height": 1.5
                },
                "spacing": {
                    "xs": 2,
                    "sm": 4,
                    "md": 8,
                    "lg": 16,
                    "xl": 24,
                    "xxl": 32
                },
                "shadows": {
                    "sm": "0 1px 2px rgba(0,0,0,0.05)",
                    "md": "0 4px 6px rgba(0,0,0,0.05)",
                    "lg": "0 10px 15px rgba(0,0,0,0.05)"
                }
            }
        elif theme_name == 'soft_light':
            return {
                "name": "柔和浅色主题",
                "description": "更柔和舒适的浅色主题，减少眼部疲劳",
                "colors": {
                    "primary": "#0078D4",
                    "secondary": "#6C757D",
                    "background": "#FAFAFA",
                    "surface": "#FFFFFF",
                    "text": "#444444",
                    "text_secondary": "#777777",
                    "border": "#EEEEEE",
                    "success": "#28A745",
                    "warning": "#FFC107",
                    "error": "#DC3545",
                    "info": "#17A2B8"
                },
                "typography": {
                    "font_family": "Microsoft YaHei UI",
                    "font_size": {
                        "xs": 10,
                        "sm": 12,
                        "md": 14,
                        "lg": 16,
                        "xl": 18,
                        "xxl": 24
                    },
                    "line_height": 1.5
                },
                "spacing": {
                    "xs": 2,
                    "sm": 4,
                    "md": 8,
                    "lg": 16,
                    "xl": 24,
                    "xxl": 32
                },
                "shadows": {
                    "sm": "0 1px 2px rgba(0,0,0,0.03)",
                    "md": "0 4px 6px rgba(0,0,0,0.03)",
                    "lg": "0 10px 15px rgba(0,0,0,0.03)"
                }
            }
        elif theme_name == 'neutral':
            return {
                "name": "中性主题",
                "description": "舒适的中性主题，结合浅色和深色主题的优点，减少眼部疲劳",
                "colors": {
                    "primary": "#0078D4",
                    "secondary": "#6C757D",
                    "background": "#F5F5F5",
                    "surface": "#FFFFFF",
                    "text": "#333333",
                    "text_secondary": "#666666",
                    "border": "#DDDDDD",
                    "success": "#28A745",
                    "warning": "#FFC107",
                    "error": "#DC3545",
                    "info": "#17A2B8"
                },
                "typography": {
                    "font_family": "Microsoft YaHei UI",
                    "font_size": {
                        "xs": 10,
                        "sm": 12,
                        "md": 14,
                        "lg": 16,
                        "xl": 18,
                        "xxl": 24
                    },
                    "line_height": 1.5
                },
                "spacing": {
                    "xs": 2,
                    "sm": 4,
                    "md": 8,
                    "lg": 16,
                    "xl": 24,
                    "xxl": 32
                },
                "shadows": {
                    "sm": "0 1px 2px rgba(0,0,0,0.03)",
                    "md": "0 4px 6px rgba(0,0,0,0.03)",
                    "lg": "0 10px 15px rgba(0,0,0,0.03)"
                }
            }
        else:
            raise ValueError(f"未知的默认主题类型: {theme_name}")

    def _load_fallback_theme(self) -> None:
        """加载后备主题"""
        fallback_theme = self._create_default_theme('dark')
        self._themes['dark'] = fallback_theme
        logger.warning("使用后备深色主题")

    def _load_preferences(self) -> None:
        """加载用户主题偏好"""
        preferences_file = os.path.join(self._config_path, 'theme_preferences.json')

        try:
            if os.path.exists(preferences_file):
                with open(preferences_file, 'r', encoding='utf-8') as f:
                    self._theme_preferences = json.load(f)
                    self._current_theme = self._theme_preferences.get('preferred_theme', 'dark')
        except Exception as e:
            logger.error(f"加载主题偏好失败: {e}")
            self._theme_preferences = {'preferred_theme': 'dark'}

    def _save_preferences(self) -> None:
        """保存用户主题偏好"""
        preferences_file = os.path.join(self._config_path, 'theme_preferences.json')

        try:
            os.makedirs(os.path.dirname(preferences_file), exist_ok=True)
            with open(preferences_file, 'w', encoding='utf-8') as f:
                json.dump(self._theme_preferences, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存主题偏好失败: {e}")

    def _apply_default_theme(self) -> None:
        """应用默认主题"""
        if self._current_theme in self._themes:
            logger.info(f"应用默认主题: {self._current_theme}")
        else:
            # 如果当前主题不存在，使用第一个可用主题
            available_themes = list(self._themes.keys())
            if available_themes:
                self._current_theme = available_themes[0]
                logger.warning(f"主题 {self._current_theme} 不存在，使用主题: {self._current_theme}")
            else:
                logger.error("没有可用的主题")

    def register_theme(self, name: str, theme_config: Dict[str, Any]) -> bool:
        """
        注册新主题

        Args:
            name: 主题名称
            theme_config: 主题配置

        Returns:
            bool: 注册是否成功
        """
        try:
            # 验证主题配置
            self._validate_theme_config(theme_config)

            self._themes[name] = theme_config
            logger.info(f"注册主题成功: {name}")
            return True

        except Exception as e:
            logger.error(f"注册主题 {name} 失败: {e}")
            return False

    def _validate_theme_config(self, theme_config: Dict[str, Any]) -> None:
        """验证主题配置的有效性"""
        required_keys = ['colors', 'typography', 'spacing']

        for key in required_keys:
            if key not in theme_config:
                raise ValueError(f"主题配置缺少必需的键: {key}")

    def apply_theme(self, theme_name: str) -> bool:
        """
        应用指定主题

        Args:
            theme_name: 主题名称

        Returns:
            bool: 应用是否成功
        """
        if theme_name not in self._themes:
            logger.error(f"主题不存在: {theme_name}")
            return False

        old_theme = self._current_theme
        self._current_theme = theme_name

        # 保存用户偏好
        self._theme_preferences['preferred_theme'] = theme_name
        self._save_preferences()

        # 通知所有观察者
        self._notify_observers(theme_name, self._themes[theme_name])

        logger.info(f"主题切换成功: {old_theme} -> {theme_name}")
        return True

    def toggle_theme(self) -> str:
        """
        切换主题 (深色->浅色->柔和浅色->中性->深色)

        Returns:
            str: 新主题名称
        """
        # 定义主题切换顺序
        theme_order = ['dark', 'light', 'soft_light', 'neutral']
        
        # 获取当前主题索引
        try:
            current_index = theme_order.index(self._current_theme)
            # 切换到下一个主题
            new_index = (current_index + 1) % len(theme_order)
            new_theme = theme_order[new_index]
        except ValueError:
            # 如果当前主题不在列表中，默认切换到深色主题
            new_theme = 'dark'
        
        if self.apply_theme(new_theme):
            return new_theme
        else:
            return self._current_theme

    def get_current_theme(self) -> str:
        """获取当前主题名称"""
        return self._current_theme

    def get_theme_style(self, component_type: str, state: str = 'normal') -> Dict[str, Any]:
        """
        获取组件样式

        Args:
            component_type: 组件类型
            state: 组件状态

        Returns:
            Dict[str, Any]: 样式配置
        """
        if self._current_theme not in self._themes:
            return {}

        theme = self._themes[self._current_theme]

        # 获取基础样式
        base_style = {
            'colors': theme.get('colors', {}),
            'typography': theme.get('typography', {}),
            'spacing': theme.get('spacing', {}),
            'shadows': theme.get('shadows', {})
        }

        # 获取组件特定样式
        component_styles = theme.get('components', {})
        component_style = component_styles.get(component_type, {})

        # 获取状态特定样式
        state_styles = component_style.get('states', {})
        state_style = state_styles.get(state, {})

        # 合并样式
        final_style = {**base_style, **component_style}
        final_style.pop('states', None)  # 移除状态配置，只保留样式

        return {**final_style, **state_style}

    def get_color(self, color_name: str) -> str:
        """
        获取主题颜色

        Args:
            color_name: 颜色名称

        Returns:
            str: 颜色值
        """
        if self._current_theme not in self._themes:
            return '#000000'

        colors = self._themes[self._current_theme].get('colors', {})
        return colors.get(color_name, '#000000')

    def get_font(self, size_name: str = 'md') -> Dict[str, Any]:
        """
        获取字体配置

        Args:
            size_name: 字体大小名称

        Returns:
            Dict[str, Any]: 字体配置
        """
        if self._current_theme not in self._themes:
            return {'family': 'Arial', 'size': 12}

        typography = self._themes[self._current_theme].get('typography', {})
        font_sizes = typography.get('font_size', {})

        return {
            'family': typography.get('font_family', 'Arial'),
            'size': font_sizes.get(size_name, 12),
            'line_height': typography.get('line_height', 1.5)
        }

    def get_spacing(self, size_name: str = 'md') -> int:
        """
        获取间距值

        Args:
            size_name: 间距名称

        Returns:
            int: 间距值
        """
        if self._current_theme not in self._themes:
            return 8

        spacing = self._themes[self._current_theme].get('spacing', {})
        return spacing.get(size_name, 8)

    def subscribe(self, observer: Callable[[str, Dict[str, Any]], None]) -> None:
        """
        订阅主题变化事件

        Args:
            observer: 观察者回调函数
        """
        if observer not in self._observers:
            self._observers.append(observer)
            logger.debug(f"添加主题观察者: {observer.__name__}")

    def unsubscribe(self, observer: Callable[[str, Dict[str, Any]], None]) -> None:
        """
        取消订阅主题变化事件

        Args:
            observer: 观察者回调函数
        """
        if observer in self._observers:
            self._observers.remove(observer)
            logger.debug(f"移除主题观察者: {observer.__name__}")

    def _notify_observers(self, theme_name: str, theme_data: Dict[str, Any]) -> None:
        """通知所有观察者主题变化"""
        for observer in self._observers:
            try:
                observer(theme_name, theme_data)
            except Exception as e:
                logger.error(f"通知观察者 {observer.__name__} 失败: {e}")

    def get_available_themes(self) -> List[str]:
        """获取所有可用主题列表"""
        return list(self._themes.keys())

    def get_theme_info(self, theme_name: str) -> Dict[str, Any]:
        """
        获取主题信息

        Args:
            theme_name: 主题名称

        Returns:
            Dict[str, Any]: 主题信息
        """
        if theme_name not in self._themes:
            return {}

        theme = self._themes[theme_name]
        return {
            'name': theme.get('name', theme_name),
            'description': theme.get('description', ''),
            'is_current': theme_name == self._current_theme
        }

    def save_theme_preferences(self) -> None:
        """
        保存主题偏好设置
        """
        self._save_preferences()

    def _save_theme(self, theme_name: str, theme_config: Dict[str, Any]) -> None:
        """保存主题到文件"""
        theme_file = os.path.join(self._config_path, f'{theme_name}_theme.json')

        try:
            with open(theme_file, 'w', encoding='utf-8') as f:
                json.dump(theme_config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存主题 {theme_name} 失败: {e}")

    def create_custom_theme(self, base_theme: str, custom_name: str,
                          overrides: Dict[str, Any]) -> bool:
        """
        创建自定义主题

        Args:
            base_theme: 基础主题名称
            custom_name: 自定义主题名称
            overrides: 覆盖配置

        Returns:
            bool: 创建是否成功
        """
        if base_theme not in self._themes:
            logger.error(f"基础主题不存在: {base_theme}")
            return False

        try:
            # 复制基础主题
            base_config = self._themes[base_theme].copy()

            # 深度合并覆盖配置
            custom_theme = self._deep_merge(base_config, overrides)

            # 设置自定义主题信息
            custom_theme['name'] = custom_name
            custom_theme['base_theme'] = base_theme
            custom_theme['is_custom'] = True

            # 注册新主题
            self.register_theme(custom_name, custom_theme)

            logger.info(f"创建自定义主题成功: {custom_name}")
            return True

        except Exception as e:
            logger.error(f"创建自定义主题 {custom_name} 失败: {e}")
            return False

    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """深度合并字典"""
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def export_theme(self, theme_name: str, export_path: str) -> bool:
        """
        导出主题配置

        Args:
            theme_name: 主题名称
            export_path: 导出路径

        Returns:
            bool: 导出是否成功
        """
        if theme_name not in self._themes:
            logger.error(f"主题不存在: {theme_name}")
            return False

        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self._themes[theme_name], f, indent=2, ensure_ascii=False)
            logger.info(f"主题导出成功: {theme_name} -> {export_path}")
            return True

        except Exception as e:
            logger.error(f"导出主题 {theme_name} 失败: {e}")
            return False

    def import_theme(self, import_path: str, theme_name: Optional[str] = None) -> bool:
        """
        导入主题配置

        Args:
            import_path: 导入路径
            theme_name: 主题名称 (可选，使用文件中的名称)

        Returns:
            bool: 导入是否成功
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                theme_config = json.load(f)

            # 使用文件中的主题名称或指定名称
            final_name = theme_name or theme_config.get('name', 'imported_theme')

            # 注册主题
            self.register_theme(final_name, theme_config)

            logger.info(f"主题导入成功: {import_path} -> {final_name}")
            return True

        except Exception as e:
            logger.error(f"导入主题失败: {e}")
            return False