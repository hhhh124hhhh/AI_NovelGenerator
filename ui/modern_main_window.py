"""
现代化主窗口 - AI小说生成器的新一代主界面
基于BMAD方法构建，集成主题系统和响应式布局
"""

import os
import logging
import customtkinter as ctk
import tkinter as tk
from typing import Dict, Any, Optional

# 导入主题系统（STORY-001的成果）
from theme_system.theme_manager import ThemeManager

# 导入新的状态管理和布局系统
from .state.state_manager import StateManager
from .layout.responsive_manager import ResponsiveLayoutManager

logger = logging.getLogger(__name__)


class ModernMainWindow(ctk.CTk):
    """
    现代化主窗口

    特性：
    - 集成主题系统 (STORY-001)
    - 响应式布局支持
    - 状态管理
    - 现代化UI组件
    - 高性能渲染
    """

    def __init__(self, theme_manager: Optional[ThemeManager] = None):
        """
        初始化现代化主窗口

        Args:
            theme_manager: 主题管理器实例，如果不提供则创建新实例
        """
        super().__init__()

        # 初始化核心管理器
        self.theme_manager = theme_manager or ThemeManager()
        self.state_manager = StateManager()
        self.layout_manager = ResponsiveLayoutManager()

        # 初始化窗口属性
        self._window_state = {
            'initialized': False,
            'components_created': False,
            'layout_applied': False
        }

        # 设置窗口基本属性
        self._setup_window_properties()

        # 创建窗口组件
        self._create_components()

        # 设置布局
        self._setup_layout()

        # 绑定事件
        self._bind_events()

        # 应用初始主题
        self._apply_initial_theme()

        # 标记初始化完成
        self._window_state['initialized'] = True
        logger.info("ModernMainWindow 初始化完成")

    def _setup_window_properties(self):
        """设置窗口基本属性"""
        try:
            # 设置窗口标题和基本信息
            self.title("AI小说生成器 v2.0 - 现代化界面")

            # 设置窗口几何属性
            initial_geometry = self.state_manager.get_state('app.window_state')
            self.geometry(f"{initial_geometry['width']}x{initial_geometry['height']}")

            # 设置最小尺寸
            self.minsize(1024, 768)

            # 设置窗口位置
            if initial_geometry.get('position'):
                x = initial_geometry['position']['x']
                y = initial_geometry['position']['y']
                self.geometry(f"+{x}+{y}")

            # 尝试设置窗口图标
            if os.path.exists("icon.ico"):
                try:
                    self.iconbitmap("icon.ico")
                except Exception as e:
                    logger.warning(f"设置窗口图标失败: {e}")

            # 设置关闭协议
            self.protocol("WM_DELETE_WINDOW", self._on_closing)

            logger.info("窗口基本属性设置完成")

        except Exception as e:
            logger.error(f"设置窗口属性失败: {e}")
            # 设置默认属性作为后备
            self.title("AI小说生成器 v2.0")
            self.geometry("1200x800")
            self.minsize(1024, 768)

    def _create_components(self):
        """创建窗口组件"""
        try:
            # 标题栏 (将在后续任务中实现)
            self.title_bar = None  # TODO: 实现TitleBar组件

            # 侧边栏 (将在后续任务中实现)
            self.sidebar = None    # TODO: 实现Sidebar组件

            # 主内容区域 (将在后续任务中实现)
            self.main_content = None  # TODO: 实现MainContent组件

            # 状态栏 (将在后续任务中实现)
            self.status_bar = None    # TODO: 实现StatusBar组件

            # 临时内容框架 - 用于显示初始化状态
            self.temp_content = ctk.CTkFrame(self)
            self.temp_label = ctk.CTkLabel(
                self.temp_content,
                text="AI小说生成器 v2.0\n现代化界面正在构建中...\n\nBUILD阶段 Day 1 - 任务1.1完成",
                font=ctk.CTkFont(size=16, weight="bold")
            )
            self.temp_label.pack(expand=True, fill="both", padx=20, pady=20)

            self._window_state['components_created'] = True
            logger.info("窗口组件创建完成")

        except Exception as e:
            logger.error(f"创建窗口组件失败: {e}")
            # 创建错误提示
            self._create_error_display(str(e))

    def _setup_layout(self):
        """设置布局"""
        try:
            # 配置主窗口网格布局
            self.grid_columnconfigure(0, weight=1)
            self.grid_rowconfigure(0, weight=1)

            # 临时放置内容框架
            if hasattr(self, 'temp_content'):
                self.temp_content.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

            # 订阅布局变化
            self.layout_manager.subscribe_layout_changes(self._on_layout_changed)

            self._window_state['layout_applied'] = True
            logger.info("窗口布局设置完成")

        except Exception as e:
            logger.error(f"设置布局失败: {e}")

    def _bind_events(self):
        """绑定事件"""
        try:
            # 窗口大小变化事件
            self.bind('<Configure>', self._on_window_configure)

            # 窗口状态变化事件
            self.bind('<FocusIn>', self._on_focus_in)
            self.bind('<FocusOut>', self._on_focus_out)

            # 键盘事件
            self.bind('<Control-q>', lambda e: self._on_closing())
            self.bind('<F11>', self._toggle_fullscreen)

            # 订阅状态变化
            self.state_manager.subscribe('app', self._on_app_state_changed)
            self.state_manager.subscribe('ui', self._on_ui_state_changed)

            # 订阅主题变化
            if self.theme_manager:
                self.theme_manager.subscribe(self._on_theme_changed)

            logger.info("事件绑定完成")

        except Exception as e:
            logger.error(f"绑定事件失败: {e}")

    def _apply_initial_theme(self):
        """应用初始主题"""
        try:
            if self.theme_manager:
                current_theme = self.state_manager.get_state('app.theme', 'dark')
                self.theme_manager.apply_theme(current_theme)

                # 应用主题到窗口
                theme_data = self.theme_manager.get_theme_info(current_theme)
                self._apply_theme_to_window(theme_data)

                logger.info(f"应用初始主题: {current_theme}")

        except Exception as e:
            logger.error(f"应用初始主题失败: {e}")

    def _apply_theme_to_window(self, theme_data: Dict[str, Any]):
        """应用主题到窗口"""
        try:
            colors = theme_data.get('colors', {})

            # 应用主窗口背景色
            bg_color = colors.get('background', '#1E1E1E')
            self.configure(fg_color=bg_color)

            # 应用到临时内容
            if hasattr(self, 'temp_content'):
                self.temp_content.configure(fg_color=colors.get('surface', '#252526'))
                self.temp_label.configure(text_color=colors.get('text', '#CCCCCC'))

        except Exception as e:
            logger.error(f"应用主题到窗口失败: {e}")

    def _on_window_configure(self, event):
        """窗口大小变化事件处理"""
        try:
            if event.widget == self:  # 确保是主窗口的事件
                width = event.width
                height = event.height

                # 更新响应式布局
                layout_changed = self.layout_manager.update_layout(width, height)

                if layout_changed:
                    logger.info(f"布局类型变更为: {self.layout_manager.get_current_layout_type().value}")

                # 保存窗口状态
                self._save_window_state(width, height)

        except Exception as e:
            logger.error(f"处理窗口配置变化失败: {e}")

    def _on_layout_changed(self, layout_type, config):
        """布局变化回调"""
        try:
            logger.info(f"布局变更为: {layout_type.value}")

            # 更新状态管理器中的布局信息
            self.state_manager.update_state({
                'app.layout': layout_type.value,
                'ui': config
            })

            # 根据布局类型调整界面
            self._adjust_ui_for_layout(layout_type, config)

        except Exception as e:
            logger.error(f"处理布局变化失败: {e}")

    def _adjust_ui_for_layout(self, layout_type, config):
        """根据布局类型调整UI"""
        try:
            # 这里将在后续任务中实现具体的UI调整逻辑
            # 目前只记录日志
            layout_adjustments = {
                'sidebar_visible': config.get('sidebar_visible', True),
                'sidebar_width': config.get('sidebar_width', 250),
                'compact_mode': config.get('compact_mode', False),
                'font_scale': config.get('font_scale', 1.0)
            }

            logger.debug(f"布局调整参数: {layout_adjustments}")

        except Exception as e:
            logger.error(f"调整UI失败: {e}")

    def _on_app_state_changed(self, key, new_value, old_value):
        """应用状态变化回调"""
        try:
            if key == 'app.theme':
                # 主题变化
                if self.theme_manager:
                    self.theme_manager.apply_theme(new_value)

            elif key == 'app.active_tab':
                # 活动标签页变化
                logger.debug(f"活动标签页变更为: {new_value}")

        except Exception as e:
            logger.error(f"处理应用状态变化失败: {e}")

    def _on_ui_state_changed(self, key, new_value, old_value):
        """UI状态变化回调"""
        try:
            logger.debug(f"UI状态变化: {key} = {new_value}")

        except Exception as e:
            logger.error(f"处理UI状态变化失败: {e}")

    def _on_theme_changed(self, theme_name: str, theme_data: Dict[str, Any]):
        """主题变化回调"""
        try:
            logger.info(f"主题变更为: {theme_name}")
            self._apply_theme_to_window(theme_data)

        except Exception as e:
            logger.error(f"处理主题变化失败: {e}")

    def _on_focus_in(self, event):
        """窗口获得焦点"""
        try:
            # 可以在这里添加窗口激活时的逻辑
            pass
        except Exception as e:
            logger.error(f"处理窗口获得焦点失败: {e}")

    def _on_focus_out(self, event):
        """窗口失去焦点"""
        try:
            # 可以在这里添加窗口失焦时的逻辑
            pass
        except Exception as e:
            logger.error(f"处理窗口失去焦点失败: {e}")

    def _toggle_fullscreen(self, event=None):
        """切换全屏模式"""
        try:
            current_state = self.attributes('-fullscreen')
            self.attributes('-fullscreen', not current_state)
            logger.info(f"全屏模式: {'开启' if not current_state else '关闭'}")
        except Exception as e:
            logger.error(f"切换全屏模式失败: {e}")

    def _save_window_state(self, width: int, height: int):
        """保存窗口状态"""
        try:
            window_state = {
                'width': width,
                'height': height,
                'maximized': self.attributes('-zoomed') if self.winfo_toplevel() == self else False
            }

            # 保存位置信息（如果不是最大化状态）
            if not window_state['maximized']:
                try:
                    x = self.winfo_x()
                    y = self.winfo_y()
                    window_state['position'] = {'x': x, 'y': y}
                except:
                    # 获取位置失败时使用默认值
                    window_state['position'] = {'x': 100, 'y': 100}

            self.state_manager.update_state({'app.window_state': window_state})

        except Exception as e:
            logger.error(f"保存窗口状态失败: {e}")

    def _on_closing(self):
        """窗口关闭事件处理"""
        try:
            logger.info("正在关闭主窗口...")

            # 保存当前状态
            self.state_manager.save_state('config/window_state.json')

            # 清理资源
            self._cleanup_resources()

            # 销毁窗口
            self.destroy()

            logger.info("主窗口已关闭")

        except Exception as e:
            logger.error(f"关闭窗口时出错: {e}")
            # 强制关闭
            self.destroy()

    def _cleanup_resources(self):
        """清理资源"""
        try:
            # 取消订阅
            if hasattr(self, 'state_manager'):
                # StateManager目前没有取消订阅方法，这里可以扩展
                pass

            if hasattr(self, 'layout_manager'):
                # LayoutManager目前没有取消订阅方法，这里可以扩展
                pass

            if hasattr(self, 'theme_manager'):
                # ThemeManager目前没有取消订阅方法，这里可以扩展
                pass

        except Exception as e:
            logger.error(f"清理资源失败: {e}")

    def _create_error_display(self, error_message: str):
        """创建错误显示"""
        try:
            error_frame = ctk.CTkFrame(self)
            error_frame.pack(expand=True, fill="both", padx=20, pady=20)

            error_label = ctk.CTkLabel(
                error_frame,
                text=f"初始化错误:\n{error_message}",
                font=ctk.CTkFont(size=14),
                text_color="#FF6B6B"
            )
            error_label.pack(expand=True, fill="both", padx=20, pady=20)

        except Exception as e:
            logger.error(f"创建错误显示失败: {e}")

    # 公共接口方法

    def get_theme_manager(self) -> Optional[ThemeManager]:
        """获取主题管理器"""
        return self.theme_manager

    def get_state_manager(self) -> StateManager:
        """获取状态管理器"""
        return self.state_manager

    def get_layout_manager(self) -> ResponsiveLayoutManager:
        """获取布局管理器"""
        return self.layout_manager

    def is_initialized(self) -> bool:
        """检查窗口是否已初始化完成"""
        return self._window_state.get('initialized', False)

    def get_window_info(self) -> Dict[str, Any]:
        """获取窗口信息"""
        try:
            return {
                'title': self.title(),
                'geometry': self.geometry(),
                'minsize': self.minsize(),
                'layout_type': self.layout_manager.get_current_layout_type().value,
                'theme': self.theme_manager.get_current_theme() if self.theme_manager else 'unknown',
                'initialized': self.is_initialized(),
                'window_state': self._window_state
            }
        except Exception as e:
            logger.error(f"获取窗口信息失败: {e}")
            return {
                'title': self.title() if hasattr(self, 'title') else 'Unknown',
                'layout_type': 'unknown',
                'theme': 'unknown',
                'initialized': self.is_initialized(),
                'error': str(e)
            }

    def refresh_layout(self):
        """刷新布局"""
        try:
            current_width = self.winfo_width()
            current_height = self.winfo_height()

            if current_width > 1 and current_height > 1:
                self.layout_manager.update_layout(current_width, current_height, force=True)
                logger.info("布局已刷新")

        except Exception as e:
            logger.error(f"刷新布局失败: {e}")