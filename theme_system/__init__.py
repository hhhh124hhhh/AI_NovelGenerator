"""
AI小说生成器主题系统
提供现代化主题管理和样式应用功能
"""

from .theme_manager import ThemeManager
from .style_utils import StyleUtils
from .styled_component import StyledComponent, StyledFrame, StyledButton, StyledLabel, StyledEntry
from .theme_config import ThemeConfig

__version__ = "1.0.0"
__all__ = [
    'ThemeManager',
    'StyleUtils',
    'StyledComponent',
    'StyledFrame',
    'StyledButton',
    'StyledLabel',
    'StyledEntry',
    'ThemeConfig'
]