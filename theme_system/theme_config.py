"""
主题配置管理
负责主题配置的加载、验证和持久化
"""

import json
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class ColorScheme:
    """颜色配置方案"""
    primary: str = "#0078D4"
    secondary: str = "#6C757D"
    background: str = "#1E1E1E"
    surface: str = "#252526"
    text: str = "#CCCCCC"
    text_secondary: str = "#969696"
    border: str = "#3E3E42"
    success: str = "#107C10"
    warning: str = "#FF8C00"
    error: str = "#D13438"
    info: str = "#0078D4"


@dataclass
class TypographyConfig:
    """字体配置"""
    font_family: str = "Microsoft YaHei UI"
    font_size: Dict[str, int] = None
    line_height: float = 1.5

    def __post_init__(self):
        if self.font_size is None:
            self.font_size = {
                "xs": 10,
                "sm": 12,
                "md": 14,
                "lg": 16,
                "xl": 18,
                "xxl": 24
            }


@dataclass
class SpacingConfig:
    """间距配置"""
    xs: int = 2
    sm: int = 4
    md: int = 8
    lg: int = 16
    xl: int = 24
    xxl: int = 32


@dataclass
class ShadowConfig:
    """阴影配置"""
    sm: str = "0 1px 2px rgba(0,0,0,0.3)"
    md: str = "0 4px 6px rgba(0,0,0,0.3)"
    lg: str = "0 10px 15px rgba(0,0,0,0.3)"


@dataclass
class ComponentStyle:
    """组件样式配置"""
    corner_radius: int = 8
    border_width: int = 1
    hover_color: Optional[str] = None
    states: Dict[str, Dict[str, Any]] = None

    def __post_init__(self):
        if self.states is None:
            self.states = {}


@dataclass
class ThemeConfig:
    """完整主题配置"""
    name: str
    description: str = ""
    colors: ColorScheme = None
    typography: TypographyConfig = None
    spacing: SpacingConfig = None
    shadows: ShadowConfig = None
    components: Dict[str, ComponentStyle] = None
    is_custom: bool = False
    base_theme: Optional[str] = None

    def __post_init__(self):
        if self.colors is None:
            self.colors = ColorScheme()
        if self.typography is None:
            self.typography = TypographyConfig()
        if self.spacing is None:
            self.spacing = SpacingConfig()
        if self.shadows is None:
            self.shadows = ShadowConfig()
        if self.components is None:
            self.components = {}

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = asdict(self)
        # 确保颜色方案正确序列化
        if isinstance(result['colors'], ColorScheme):
            result['colors'] = asdict(result['colors'])
        if isinstance(result['typography'], TypographyConfig):
            result['typography'] = asdict(result['typography'])
        if isinstance(result['spacing'], SpacingConfig):
            result['spacing'] = asdict(result['spacing'])
        if isinstance(result['shadows'], ShadowConfig):
            result['shadows'] = asdict(result['shadows'])
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ThemeConfig':
        """从字典创建主题配置"""
        # 处理嵌套对象
        if 'colors' in data and isinstance(data['colors'], dict):
            data['colors'] = ColorScheme(**data['colors'])
        if 'typography' in data and isinstance(data['typography'], dict):
            data['typography'] = TypographyConfig(**data['typography'])
        if 'spacing' in data and isinstance(data['spacing'], dict):
            data['spacing'] = SpacingConfig(**data['spacing'])
        if 'shadows' in data and isinstance(data['shadows'], dict):
            data['shadows'] = ShadowConfig(**data['shadows'])

        # 处理组件样式
        if 'components' in data and isinstance(data['components'], dict):
            components = {}
            for comp_name, comp_data in data['components'].items():
                if isinstance(comp_data, dict):
                    components[comp_name] = ComponentStyle(**comp_data)
            data['components'] = components

        return cls(**data)


class ThemeConfigManager:
    """主题配置管理器"""

    def __init__(self, config_dir: str = "config/themes"):
        """
        初始化主题配置管理器

        Args:
            config_dir: 配置目录
        """
        self.config_dir = config_dir
        self._ensure_config_dir()

    def _ensure_config_dir(self) -> None:
        """确保配置目录存在"""
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(os.path.join(self.config_dir, 'user'), exist_ok=True)

    def create_dark_theme(self) -> ThemeConfig:
        """创建深色主题配置"""
        colors = ColorScheme(
            primary="#0078D4",
            secondary="#6C757D",
            background="#1E1E1E",
            surface="#252526",
            text="#CCCCCC",
            text_secondary="#969696",
            border="#3E3E42",
            success="#107C10",
            warning="#FF8C00",
            error="#D13438",
            info="#0078D4"
        )

        typography = TypographyConfig(
            font_family="Microsoft YaHei UI",
            font_size={"xs": 10, "sm": 12, "md": 14, "lg": 16, "xl": 18, "xxl": 24},
            line_height=1.5
        )

        spacing = SpacingConfig()
        shadows = ShadowConfig()

        # 组件样式
        components = {
            "button": ComponentStyle(
                corner_radius=8,
                border_width=0,
                hover_color="#106ebe",
                states={
                    "primary": {"fg_color": "#0078D4", "text_color": "#FFFFFF"},
                    "secondary": {"fg_color": "transparent", "border_width": 2, "border_color": "#0078D4"},
                    "success": {"fg_color": "#107C10", "text_color": "#FFFFFF"},
                    "warning": {"fg_color": "#FF8C00", "text_color": "#FFFFFF"},
                    "danger": {"fg_color": "#D13438", "text_color": "#FFFFFF"}
                }
            ),
            "frame": ComponentStyle(
                corner_radius=12,
                border_width=1,
                fg_color="#252526",
                border_color="#3E3E42"
            ),
            "entry": ComponentStyle(
                corner_radius=6,
                border_width=2,
                fg_color="#2D2D2D",
                border_color="#3E3E42",
                states={
                    "focused": {"border_color": "#0078D4"},
                    "error": {"border_color": "#D13438"}
                }
            )
        }

        return ThemeConfig(
            name="深色主题",
            description="适合夜间使用的深色主题",
            colors=colors,
            typography=typography,
            spacing=spacing,
            shadows=shadows,
            components=components
        )

    def create_light_theme(self) -> ThemeConfig:
        """创建浅色主题配置"""
        colors = ColorScheme(
            primary="#0078D4",
            secondary="#6C757D",
            background="#FFFFFF",
            surface="#F8F9FA",
            text="#212529",
            text_secondary="#6C757D",
            border="#DEE2E6",
            success="#28A745",
            warning="#FFC107",
            error="#DC3545",
            info="#17A2B8"
        )

        typography = TypographyConfig(
            font_family="Microsoft YaHei UI",
            font_size={"xs": 10, "sm": 12, "md": 14, "lg": 16, "xl": 18, "xxl": 24},
            line_height=1.5
        )

        spacing = SpacingConfig()
        shadows = ShadowConfig(
            sm="0 1px 2px rgba(0,0,0,0.1)",
            md="0 4px 6px rgba(0,0,0,0.1)",
            lg="0 10px 15px rgba(0,0,0,0.1)"
        )

        # 组件样式
        components = {
            "button": ComponentStyle(
                corner_radius=8,
                border_width=0,
                hover_color="#005a9e",
                states={
                    "primary": {"fg_color": "#0078D4", "text_color": "#FFFFFF"},
                    "secondary": {"fg_color": "transparent", "border_width": 2, "border_color": "#0078D4"},
                    "success": {"fg_color": "#28A745", "text_color": "#FFFFFF"},
                    "warning": {"fg_color": "#FFC107", "text_color": "#212529"},
                    "danger": {"fg_color": "#DC3545", "text_color": "#FFFFFF"}
                }
            ),
            "frame": ComponentStyle(
                corner_radius=12,
                border_width=1,
                fg_color="#F8F9FA",
                border_color="#DEE2E6"
            ),
            "entry": ComponentStyle(
                corner_radius=6,
                border_width=2,
                fg_color="#FFFFFF",
                border_color="#DEE2E6",
                states={
                    "focused": {"border_color": "#0078D4"},
                    "error": {"border_color": "#DC3545"}
                }
            )
        }

        return ThemeConfig(
            name="浅色主题",
            description="适合白天使用的浅色主题",
            colors=colors,
            typography=typography,
            spacing=spacing,
            shadows=shadows,
            components=components
        )

    def save_theme(self, theme: ThemeConfig, filename: str = None) -> bool:
        """
        保存主题配置到文件

        Args:
            theme: 主题配置
            filename: 文件名 (可选)

        Returns:
            bool: 保存是否成功
        """
        try:
            if filename is None:
                filename = f"{theme.name.replace(' ', '_')}_theme.json"

            # 自定义主题保存到用户目录
            if theme.is_custom:
                filepath = os.path.join(self.config_dir, 'user', filename)
            else:
                filepath = os.path.join(self.config_dir, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(theme.to_dict(), f, indent=2, ensure_ascii=False)

            logger.info(f"主题配置已保存: {filepath}")
            return True

        except Exception as e:
            logger.error(f"保存主题配置失败: {e}")
            return False

    def load_theme(self, filename: str) -> Optional[ThemeConfig]:
        """
        从文件加载主题配置

        Args:
            filename: 文件名

        Returns:
            ThemeConfig: 主题配置，失败返回None
        """
        try:
            # 先尝试主配置目录
            filepath = os.path.join(self.config_dir, filename)
            if not os.path.exists(filepath):
                # 尝试用户配置目录
                filepath = os.path.join(self.config_dir, 'user', filename)

            if not os.path.exists(filepath):
                logger.error(f"主题配置文件不存在: {filename}")
                return None

            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            theme = ThemeConfig.from_dict(data)
            logger.info(f"主题配置已加载: {filepath}")
            return theme

        except Exception as e:
            logger.error(f"加载主题配置失败: {e}")
            return None

    def validate_theme(self, theme: ThemeConfig) -> List[str]:
        """
        验证主题配置

        Args:
            theme: 主题配置

        Returns:
            List[str]: 验证错误列表
        """
        errors = []

        # 验证必需字段
        if not theme.name:
            errors.append("主题名称不能为空")

        # 验证颜色格式
        if theme.colors:
            color_fields = asdict(theme.colors)
            for field_name, color_value in color_fields.items():
                if not self._is_valid_color(color_value):
                    errors.append(f"无效的颜色值: {field_name} = {color_value}")

        # 验证字体大小
        if theme.typography and theme.typography.font_size:
            for size_name, size_value in theme.typography.font_size.items():
                if not isinstance(size_value, int) or size_value <= 0:
                    errors.append(f"无效的字体大小: {size_name} = {size_value}")

        # 验证间距值
        if theme.spacing:
            spacing_fields = asdict(theme.spacing)
            for field_name, spacing_value in spacing_fields.items():
                if not isinstance(spacing_value, int) or spacing_value < 0:
                    errors.append(f"无效的间距值: {field_name} = {spacing_value}")

        return errors

    def _is_valid_color(self, color: str) -> bool:
        """验证颜色格式"""
        if not color or not isinstance(color, str):
            return False

        # 检查十六进制颜色格式
        if color.startswith('#') and len(color) in [4, 7]:  # #RGB 或 #RRGGBB
            hex_part = color[1:]
            return all(c in '0123456789abcdefABCDEF' for c in hex_part)

        # 检查RGB颜色格式
        if color.startswith('rgb(') and color.endswith(')'):
            try:
                rgb_part = color[4:-1]
                values = [int(x.strip()) for x in rgb_part.split(',')]
                return len(values) == 3 and all(0 <= v <= 255 for v in values)
            except:
                return False

        return False

    def get_available_themes(self) -> List[str]:
        """获取所有可用的主题文件"""
        themes = []

        # 扫描主配置目录
        for filename in os.listdir(self.config_dir):
            if filename.endswith('_theme.json'):
                themes.append(filename)

        # 扫描用户配置目录
        user_dir = os.path.join(self.config_dir, 'user')
        if os.path.exists(user_dir):
            for filename in os.listdir(user_dir):
                if filename.endswith('_theme.json'):
                    themes.append(f"user/{filename}")

        return themes

    def export_theme(self, theme: ThemeConfig, export_path: str) -> bool:
        """
        导出主题配置

        Args:
            theme: 主题配置
            export_path: 导出路径

        Returns:
            bool: 导出是否成功
        """
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(theme.to_dict(), f, indent=2, ensure_ascii=False)

            logger.info(f"主题已导出: {export_path}")
            return True

        except Exception as e:
            logger.error(f"导出主题失败: {e}")
            return False

    def import_theme(self, import_path: str, theme_name: str = None) -> Optional[ThemeConfig]:
        """
        导入主题配置

        Args:
            import_path: 导入路径
            theme_name: 主题名称 (可选)

        Returns:
            ThemeConfig: 主题配置，失败返回None
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            theme = ThemeConfig.from_dict(data)

            # 设置导入的主题名称
            if theme_name:
                theme.name = theme_name
                theme.is_custom = True

            # 验证主题
            errors = self.validate_theme(theme)
            if errors:
                logger.error(f"主题配置验证失败: {errors}")
                return None

            logger.info(f"主题已导入: {import_path}")
            return theme

        except Exception as e:
            logger.error(f"导入主题失败: {e}")
            return None

    def create_theme_from_base(self, base_theme: ThemeConfig,
                             new_name: str, overrides: Dict[str, Any]) -> ThemeConfig:
        """
        基于现有主题创建新主题

        Args:
            base_theme: 基础主题
            new_name: 新主题名称
            overrides: 覆盖配置

        Returns:
            ThemeConfig: 新主题配置
        """
        # 复制基础主题
        new_theme = ThemeConfig.from_dict(base_theme.to_dict())

        # 设置新主题信息
        new_theme.name = new_name
        new_theme.is_custom = True
        new_theme.base_theme = base_theme.name

        # 应用覆盖配置
        self._apply_overrides(new_theme, overrides)

        return new_theme

    def _apply_overrides(self, theme: ThemeConfig, overrides: Dict[str, Any]) -> None:
        """应用覆盖配置到主题"""
        for key, value in overrides.items():
            if hasattr(theme, key):
                setattr(theme, key, value)
            else:
                logger.warning(f"未知的主题配置项: {key}")