"""
现代化主窗口 - AI小说生成器的新一代主界面
基于BMAD方法构建，集成主题系统和响应式布局
"""

import os
import logging
import sys
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from typing import Dict, Any, Optional, List

# 导入高级日志系统
try:
    from advanced_logger import setup_logger, ui_logger, main_logger
    ADVANCED_LOGGING_AVAILABLE = True
except ImportError:
    ADVANCED_LOGGING_AVAILABLE = False
    ui_logger = logging.getLogger("ui")
    main_logger = logging.getLogger("main")

# 导入主题系统（STORY-001的成果）
from theme_system.theme_manager import ThemeManager

# 导入新的状态管理和布局系统
from .state.state_manager import StateManager
from .layout.responsive_manager import ResponsiveLayoutManager

# 导入UI组件
from .components.title_bar import TitleBar
from .components.sidebar import Sidebar
from .components.main_content import MainContentArea
from .components.main_workspace import MainWorkspace
from .components.summary_manager import SummaryManager
from .components.directory_manager import DirectoryManager

# 导入动画效果系统
from .effects.animation_manager import AnimationManager, AnimationType, AnimationDirection

# 导入性能监控系统
from .performance.performance_monitor import PerformanceMonitor, PerformanceProfiler

# 导入文件监控器
from .file_watcher import get_file_watcher

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

    def __init__(self, parent=None, theme_manager: Optional[ThemeManager] = None):
        """
        初始化现代化主窗口

        Args:
            parent: 父窗口（兼容性参数）
            theme_manager: 主题管理器实例，如果不提供则创建新实例
        """
        super().__init__()

        # 初始化核心管理器
        self.theme_manager: ThemeManager = theme_manager or ThemeManager()
        self.state_manager: StateManager = StateManager()
        self.layout_manager: ResponsiveLayoutManager = ResponsiveLayoutManager()

        # 关闭性能监控和动画系统 - 根据用户反馈
        try:
            from .effects.dummy_animation_manager import get_animation_manager
            self.animation_manager = get_animation_manager()
            main_logger.info("使用虚拟动画管理器 - 所有动画已禁用")
        except Exception as e:
            self.animation_manager = None
            main_logger.warning(f"动画管理器设置失败: {e}")

        self.performance_monitor = None
        self.performance_profiler = None

        main_logger.info("性能监控已关闭 - 用户反馈影响体验")

        # 初始化文件监控器
        self.file_watcher = get_file_watcher()
        self.file_watcher.start_watching()

        # 初始化窗口属性
        self._window_state = {
            'initialized': False,
            'components_created': False,
            'layout_applied': False
        }

        # 组件引用
        self.title_bar: Optional[TitleBar] = None
        self.sidebar: Optional[Sidebar] = None
        self.main_content: Optional[MainContentArea] = None
        self.status_bar: Optional[ctk.CTkFrame] = None
        self.temp_label: Optional[ctk.CTkLabel] = None

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

        # 性能监控已关闭
        main_logger.info("性能监控已禁用")

        # 标记初始化完成
        self._window_state['initialized'] = True
        main_logger.info("ModernMainWindow 初始化完成")
        ui_logger.info("UI主窗口初始化完成")

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
            self._setup_window_icon()

            # 设置关闭协议
            self.protocol("WM_DELETE_WINDOW", self._on_closing)

            logger.info("窗口基本属性设置完成")

        except Exception as e:
            logger.error(f"设置窗口属性失败: {e}")
            # 设置默认属性作为后备
            self.title("AI小说生成器 v2.0")
            self.geometry("1200x800")
            self.minsize(1024, 768)

    def _setup_window_icon(self):
        """设置窗口图标"""
        try:
            # 尝试多种图标文件路径
            icon_paths = [
                "icon.ico",
                os.path.join(os.path.dirname(__file__), "..", "..", "icon.ico"),
                os.path.join(os.path.dirname(__file__), "..", "..", "icon.ico.bak"),
                os.path.join(os.getcwd(), "icon.ico")
            ]
            
            icon_set = False
            for icon_path in icon_paths:
                if os.path.exists(icon_path):
                    try:
                        self.iconbitmap(icon_path)
                        logger.info(f"窗口图标设置成功: {icon_path}")
                        icon_set = True
                        break
                    except Exception as icon_e:
                        logger.warning(f"设置窗口图标失败 {icon_path}: {icon_e}")
                        continue
            
            if not icon_set:
                logger.warning("未找到有效的窗口图标文件")
                
        except Exception as e:
            logger.warning(f"设置窗口图标时出现异常: {e}")

    def _create_components(self):
        """创建窗口组件"""
        try:
            main_logger.info("开始创建窗口组件")

            # 开始性能分析
            if self.performance_profiler:
                try:
                    self.performance_profiler.start_profiling("window_creation")
                    self.performance_profiler.record_event("window_creation", "开始创建组件")
                except Exception as e:
                    main_logger.warning(f"性能分析启动失败: {e}")

            # 标题栏
            try:
                main_logger.info("创建标题栏")
                self.title_bar = TitleBar(self, self.theme_manager, self.state_manager)
                self.title_bar.pack(fill="x", padx=5, pady=(5, 0))

                # 动画系统已关闭
                main_logger.info("标题栏显示完成")

            except Exception as e:
                main_logger.error(f"创建标题栏失败: {e}")
                raise

            # 主要内容容器 - 修复布局问题
            try:
                main_logger.info("创建主容器")
                self.main_container = ctk.CTkFrame(self, fg_color="transparent")
                self.main_container.pack(fill="both", expand=True, padx=5, pady=5)

                # 配置主容器网格布局 - 修复侧边栏布局
                self.main_container.grid_columnconfigure(0, weight=0, minsize=280)  # 侧边栏固定宽度
                self.main_container.grid_columnconfigure(1, weight=1)  # 主内容区域自适应
                self.main_container.grid_rowconfigure(0, weight=1)

                # 动画系统已关闭
                main_logger.info("主容器显示完成")

            except Exception as e:
                main_logger.error(f"创建主容器失败: {e}")
                raise

            # 侧边栏 - 修复显示问题
            try:
                main_logger.info("创建侧边栏")
                from .components.sidebar import Sidebar
                self.sidebar = Sidebar(self.main_container, self.theme_manager, self.state_manager, main_window=self)
                self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(5, 5), pady=(5, 5))
                main_logger.info("侧边栏创建并放置成功")

                # 动画系统已关闭
                main_logger.info("侧边栏显示完成")

            except Exception as e:
                main_logger.error(f"创建侧边栏失败: {e}")
                # 继续创建其他组件，侧边栏可选

            # 主内容区域 - 修复父容器问题
            try:
                main_logger.info("创建主内容区域")
                from .components.main_content import MainContentArea
                self.main_content = MainContentArea(
                    self.main_container,  # 使用main_container作为父级
                    self.theme_manager,
                    self.state_manager
                )
                self.main_content.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
                main_logger.info("主内容区域创建并放置成功")

                # 动画系统已关闭
                main_logger.info("主内容区域显示完成")

            except Exception as e:
                main_logger.error(f"创建主内容区域失败: {e}")
                raise

            # 添加默认标签页
            try:
                main_logger.info("设置默认标签页")
                self._setup_default_tabs()
            except Exception as e:
                main_logger.error(f"设置默认标签页失败: {e}")

            # 配置标签页初始化后，显示欢迎信息
            try:
                main_logger.info("显示欢迎信息")
                self._show_welcome_message()
            except Exception as e:
                main_logger.warning(f"显示欢迎信息失败: {e}")

            # 状态栏 (简单版本)
            try:
                main_logger.info("创建状态栏")
                # 创建通知系统替代原有的简单状态栏
                try:
                    from ui.components.notification_system import NotificationSystem
                    self.notification_system = NotificationSystem(self, self.theme_manager, self.state_manager)
                    self.notification_system.pack(fill="x", side="bottom", padx=0, pady=0)
                    
                    # 显示初始状态
                    self.notification_system.update_status("应用已启动 | 主题: 深色模式 | 布局: 桌面版")
                    main_logger.info("通知系统创建成功")
                except Exception as e:
                    main_logger.warning(f"创建通知系统失败，使用传统状态栏: {e}")
                    # 回退到简单状态栏
                    self.status_bar = ctk.CTkFrame(self, height=30, corner_radius=0)
                    self.status_bar.pack(fill="x", side="bottom", padx=5, pady=(0, 5))

                    self.status_label = ctk.CTkLabel(
                        self.status_bar,
                        text="就绪 | 主题: 深色模式 | 布局: 桌面版",
                        font=ctk.CTkFont(size=11),
                        anchor="w"
                    )
                    self.status_label.pack(side="left", padx=10, pady=5)
                    main_logger.info("传统状态栏创建成功")

                main_logger.info("状态栏创建成功")
            except Exception as e:
                main_logger.warning(f"创建状态栏失败: {e}")

            # 设置组件回调
            try:
                main_logger.info("设置组件回调")
                self._setup_component_callbacks()
            except Exception as e:
                main_logger.warning(f"设置组件回调失败: {e}")

            self._window_state['components_created'] = True
            main_logger.info("窗口组件创建完成")

        except Exception as e:
            main_logger.error(f"创建窗口组件失败: {e}")
            import traceback
            main_logger.error(f"详细错误: {traceback.format_exc()}")
            self._window_state['components_created'] = False

    def _setup_default_tabs(self):
        """设置默认标签页"""
        try:
            # 确保main_content已初始化
            if not self.main_content:
                logger.warning("MainContentArea未初始化")
                return
                
            # 添加默认标签页
            default_tabs = [
                ("main", "主页"),
                ("config", "配置"),
                ("setting", "设定"),
                ("generate", "生成"),
                ("characters", "角色"),
                ("chapters", "章节"),
                ("summary", "摘要"),
                ("directory", "目录")
            ]

            for tab_name, tab_title in default_tabs:
                self.main_content.add_tab(tab_name, tab_title, self._on_tab_callback)

            # 初始化所有标签页
            self._setup_main_tab()
            self._setup_config_tab()
            self._setup_setting_tab()
            self._setup_generate_tab()
            self._setup_characters_tab()
            self._setup_chapters_tab()
            self._setup_summary_tab()
            self._setup_directory_tab()

            # 设置默认活动标签页
            current_active = self.state_manager.get_state('app.active_tab', 'main')
            if current_active in [t[0] for t in default_tabs]:
                self.main_content.switch_to_tab(current_active)

            logger.info(f"默认标签页设置完成，共{len(default_tabs)}个标签页")

        except Exception as e:
            logger.error(f"设置默认标签页失败: {e}")

    def _setup_config_tab(self):
        """设置配置标签页"""
        try:
            # 确保main_content已初始化
            if not self.main_content:
                logger.warning("MainContentArea未初始化")
                return
                
            from .components.config_tab import ConfigTab

            # 获取配置标签页的内容框架
            config_frame = self.main_content.get_tab_content_frame("config")
            if config_frame:
                # 创建配置标签页组件
                self.config_tab = ConfigTab(
                    config_frame,
                    self.theme_manager,
                    self.state_manager,
                    main_window=self
                )
                self.config_tab.pack(fill="both", expand=True)

                # 设置配置变化回调
                self.config_tab.set_config_changed_callback(self._on_config_changed)

                logger.info("配置标签页初始化完成")

        except Exception as e:
            logger.error(f"设置配置标签页失败: {e}")

    def _setup_setting_tab(self):
        """设置设定标签页"""
        try:
            # 确保main_content已初始化
            if not self.main_content:
                logger.warning("MainContentArea未初始化")
                return

            from .components.setting_tab import SettingTab

            # 获取设定标签页的内容框架
            setting_frame = self.main_content.get_tab_content_frame("setting")
            if setting_frame:
                # 创建设定标签页组件
                self.setting_tab = SettingTab(
                    setting_frame,
                    self.theme_manager,
                    self.state_manager,
                    main_window=self
                )
                self.setting_tab.pack(fill="both", expand=True)

                logger.info("设定标签页初始化完成")

        except Exception as e:
            logger.error(f"设置设定标签页失败: {e}")

    def _setup_generate_tab(self):
        """设置生成标签页"""
        try:
            # 确保main_content已初始化
            if not self.main_content:
                logger.warning("MainContentArea未初始化")
                return
                
            from .components.generate_tab import GenerateTab

            # 获取生成标签页的内容框架
            generate_frame = self.main_content.get_tab_content_frame("generate")
            if generate_frame:
                # 创建生成标签页组件
                self.generate_tab = GenerateTab(
                    generate_frame,
                    self.theme_manager,
                    self.state_manager
                )
                self.generate_tab.pack(fill="both", expand=True)

                # 设置生成回调
                self.generate_tab.set_generation_started_callback(self._on_generation_started)
                self.generate_tab.set_generation_completed_callback(self._on_generation_completed)

                logger.info("生成标签页初始化完成")

        except Exception as e:
            logger.error(f"设置生成标签页失败: {e}")

    def _setup_characters_tab(self):
        """设置角色管理标签页"""
        try:
            # 确保main_content已初始化
            if not self.main_content:
                logger.warning("MainContentArea未初始化")
                return
                
            from .components.characters_tab import CharactersTab

            # 获取角色标签页的内容框架
            characters_frame = self.main_content.get_tab_content_frame("characters")
            if characters_frame:
                # 创建角色管理标签页组件
                self.characters_tab = CharactersTab(
                    characters_frame,
                    self.theme_manager,
                    self.state_manager
                )
                self.characters_tab.pack(fill="both", expand=True)

                # 设置角色变化回调
                self.characters_tab.set_character_changed_callback(self._on_character_changed)

                logger.info("角色管理标签页初始化完成")

        except Exception as e:
            logger.error(f"设置角色管理标签页失败: {e}")

    def _setup_chapters_tab(self):
        """设置章节管理标签页"""
        try:
            # 确保main_content已初始化
            if not self.main_content:
                logger.warning("MainContentArea未初始化")
                return
                
            from .components.chapters_tab import ChaptersTab

            # 获取章节标签页的内容框架
            chapters_frame = self.main_content.get_tab_content_frame("chapters")
            if chapters_frame:
                # 创建章节管理标签页组件
                self.chapters_tab = ChaptersTab(
                    chapters_frame,
                    self.theme_manager,
                    self.state_manager
                )
                self.chapters_tab.pack(fill="both", expand=True)

                # 设置章节变化回调
                self.chapters_tab.set_chapter_changed_callback(self._on_chapter_changed)

                logger.info("章节管理标签页初始化完成")

        except Exception as e:
            logger.error(f"设置章节管理标签页失败: {e}")

    def _setup_main_tab(self):
        """设置主工作区标签页"""
        try:
            logger.info("开始设置主工作区标签页...")

            # 确保main_content已初始化
            if not self.main_content:
                logger.warning("MainContentArea未初始化")
                return

            logger.info("MainContentArea已初始化，获取主页标签页框架...")

            # 获取主页标签页的内容框架
            main_frame = self.main_content.get_tab_content_frame("main")
            logger.info(f"获取到主页框架: {main_frame is not None}")

            # 检查content_frames内容
            if hasattr(self.main_content, 'content_frames'):
                logger.info(f"可用标签页框架: {list(self.main_content.content_frames.keys())}")
            else:
                logger.warning("MainContentArea没有content_frames属性")

            if main_frame:
                logger.info("开始创建MainWorkspace组件...")
                # 创建主工作区组件
                self.main_workspace = MainWorkspace(
                    main_frame,
                    self.theme_manager,
                    self.state_manager
                )
                self.main_workspace.pack(fill="both", expand=True)
                logger.info("MainWorkspace组件已创建并打包")

                # 设置回调函数
                self.main_workspace.set_step_changed_callback(self._on_step_changed)
                self.main_workspace.set_generation_started_callback(self._on_generation_started)
                self.main_workspace.set_generation_completed_callback(self._on_generation_completed)
                logger.info("主工作区回调函数已设置")

                logger.info("主工作区标签页初始化完成")
            else:
                logger.error("无法获取主页标签页内容框架")

        except Exception as e:
            logger.error(f"设置主工作区标签页失败: {e}")
            import traceback
            logger.error(f"详细错误: {traceback.format_exc()}")

    def _setup_summary_tab(self):
        """设置摘要管理标签页"""
        try:
            # 确保main_content已初始化
            if not self.main_content:
                logger.warning("MainContentArea未初始化")
                return

            # 获取摘要标签页的内容框架
            summary_frame = self.main_content.get_tab_content_frame("summary")
            if summary_frame:
                # 创建摘要管理组件
                self.summary_manager = SummaryManager(
                    summary_frame,
                    self.theme_manager,
                    self.state_manager
                )
                self.summary_manager.pack(fill="both", expand=True)

                # 设置回调函数
                self.summary_manager.set_summary_changed_callback(self._on_summary_changed)
                self.summary_manager.set_character_changed_callback(self._on_character_state_changed)

                logger.info("摘要管理标签页初始化完成")

        except Exception as e:
            logger.error(f"设置摘要管理标签页失败: {e}")

    def _setup_directory_tab(self):
        """设置目录管理标签页"""
        try:
            # 确保main_content已初始化
            if not self.main_content:
                logger.warning("MainContentArea未初始化")
                return

            # 获取目录标签页的内容框架
            directory_frame = self.main_content.get_tab_content_frame("directory")
            if directory_frame:
                # 创建目录管理组件
                self.directory_manager = DirectoryManager(
                    directory_frame,
                    self.theme_manager,
                    self.state_manager
                )
                self.directory_manager.pack(fill="both", expand=True)

                # 设置回调函数
                self.directory_manager.set_chapter_selected_callback(self._on_directory_chapter_selected)
                self.directory_manager.set_chapter_modified_callback(self._on_directory_chapter_modified)

                logger.info("目录管理标签页初始化完成")

        except Exception as e:
            logger.error(f"设置目录管理标签页失败: {e}")

    def _on_tab_callback(self, tab_name: str):
        """标签页切换回调"""
        try:
            # 使用新的标签页切换逻辑
            self._on_tab_switched(tab_name)

        except Exception as e:
            logger.error(f"处理标签页切换回调失败: {e}")

    def _on_config_changed(self, config: dict):
        """配置变化回调"""
        try:
            logger.info("配置已更新")

            # 更新状态栏
            self._update_status(f"配置已更新 - {config.get('llm', {}).get('provider', 'Unknown')}")

            # 这里可以添加更多配置变化后的处理逻辑
            # 例如：重新初始化生成器、更新其他组件等

        except Exception as e:
            logger.error(f"配置变化处理失败: {e}")

    def _on_generation_started(self, generation_type: str):
        """生成开始回调"""
        try:
            logger.info(f"{generation_type} 生成已开始")

            # 更新状态栏
            type_names = {
                "architecture": "小说架构",
                "blueprint": "章节规划",
                "content": "章节内容"
            }
            type_name = type_names.get(generation_type, generation_type)
            self._update_status(f"正在生成{type_name}...")

        except Exception as e:
            logger.error(f"生成开始回调处理失败: {e}")

    def _on_generation_completed(self, generation_type: str, result: str):
        """生成完成回调"""
        try:
            logger.info(f"{generation_type} 生成已完成")

            # 更新状态栏
            type_names = {
                "architecture": "小说架构",
                "blueprint": "章节规划",
                "content": "章节内容"
            }
            type_name = type_names.get(generation_type, generation_type)
            self._update_status(f"{type_name}生成完成")

            # 这里可以添加更多生成完成后的处理逻辑
            # 例如：保存结果、更新其他标签页等

        except Exception as e:
            logger.error(f"生成完成回调处理失败: {e}")

    def _on_character_changed(self, character: dict):
        """角色变化回调"""
        try:
            logger.info(f"角色切换到: {character.get('name', 'Unknown')}")

            # 更新状态栏
            self._update_status(f"当前角色: {character.get('name', 'Unknown')}")

        except Exception as e:
            logger.error(f"角色变化处理失败: {e}")

    def _on_chapter_changed(self, chapter: dict):
        """章节变化回调"""
        try:
            logger.info(f"章节切换到: {chapter.get('title', 'Unknown')}")

            # 更新状态栏
            self._update_status(f"当前章节: {chapter.get('title', 'Unknown')}")

        except Exception as e:
            logger.error(f"章节变化处理失败: {e}")

    def _setup_component_callbacks(self):
        """设置组件回调函数"""
        try:
            # 标题栏回调
            if self.title_bar:
                self.title_bar.set_search_callback(self._on_search)
                self.title_bar.set_settings_callback(self._on_settings)
                self.title_bar.set_user_menu_callback(self._on_user_menu)

            # 侧边栏回调
            if self.sidebar:
                self.sidebar.set_navigation_callback(self._on_navigation)
                self.sidebar.set_quick_action_callback(self._on_quick_action)
                self.sidebar.set_project_select_callback(self._on_project_select)

            logger.debug("组件回调设置完成")

        except Exception as e:
            logger.error(f"设置组件回调失败: {e}")

    def _setup_layout(self):
        """设置布局"""
        try:
            # 配置主窗口网格布局
            self.grid_columnconfigure(0, weight=1)
            self.grid_rowconfigure(0, weight=1)

            # 临时放置内容框架
            # temp_content已被移除，使用main_content代替
            pass

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
            if self.state_manager:
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

    def _on_theme_changed(self, theme_name: str, theme_data: Dict[str, Any]):
        """主题变化回调"""
        try:
            # 确保窗口仍然存在
            if not (hasattr(self, 'winfo_exists') and self.winfo_exists()):
                return
                
            logger.info(f"主题变更为: {theme_name}")
            self._apply_theme_to_window(theme_data)

        except Exception as e:
            logger.debug(f"处理主题变化失败: {e}")

    def _apply_theme_to_window(self, theme_data: Dict[str, Any]):
        """应用主题到窗口"""
        try:
            # 确保窗口仍然存在
            if not (hasattr(self, 'winfo_exists') and self.winfo_exists()):
                return
                
            colors = theme_data.get('colors', {})

            # 应用主窗口背景色
            bg_color = colors.get('background', '#1E1E1E')
            self.configure(fg_color=bg_color)

            # 应用到主内容
            if (hasattr(self, 'main_content') and 
                self.main_content is not None and
                hasattr(self.main_content, 'winfo_exists') and
                self.main_content.winfo_exists()):
                self.main_content.configure(fg_color=colors.get('surface', '#252526'))
                
            if (hasattr(self, 'temp_label') and 
                self.temp_label is not None and
                hasattr(self.temp_label, 'winfo_exists') and
                self.temp_label.winfo_exists()):
                self.temp_label.configure(text_color=colors.get('text', '#CCCCCC'))

        except Exception as e:
            logger.debug(f"应用主题到窗口失败: {e}")

    def _on_window_configure(self, event):
        """窗口大小变化事件处理"""
        try:
            # 确保窗口仍然存在
            if not self.winfo_exists():
                return
                
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
            # 确保窗口仍然存在
            if not self.winfo_exists():
                return
                
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
            # 安全地检查窗口是否最大化
            maximized = False
            if hasattr(self, 'attributes') and callable(getattr(self, 'attributes', None)):
                try:
                    # 确保窗口仍然存在
                    if self.winfo_exists():
                        maximized = bool(self.attributes('-zoomed'))
                except:
                    maximized = False
            
            window_state = {
                'width': width if isinstance(width, int) and width > 0 else 800,
                'height': height if isinstance(height, int) and height > 0 else 600,
                'maximized': maximized
            }

            # 保存位置信息（如果不是最大化状态）
            if not window_state['maximized']:
                try:
                    x = self.winfo_x() if self.winfo_exists() else 100
                    y = self.winfo_y() if self.winfo_exists() else 100
                    # 确保x和y是有效数值
                    if isinstance(x, int) and isinstance(y, int):
                        window_state['position'] = {'x': x, 'y': y}
                    else:
                        window_state['position'] = {'x': 100, 'y': 100}
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

            # 停止性能监控
            if hasattr(self, 'performance_monitor'):
                self.performance_monitor.stop_monitoring()

            # 保存当前状态
            try:
                self.state_manager.save_state('config/window_state.json')
            except:
                pass

            # 清理资源
            self._cleanup_resources()

            # 销毁窗口
            if self.winfo_exists():
                self.destroy()

            logger.info("主窗口已关闭")

        except Exception as e:
            logger.error(f"关闭窗口时出错: {e}")
            # 强制关闭
            try:
                if self.winfo_exists():
                    self.destroy()
            except:
                pass

    def _cleanup_resources(self):
        """清理资源"""
        try:
            # 停止文件监控
            if hasattr(self, 'file_watcher'):
                self.file_watcher.stop_watching()
                
            # 清理组件引用
            if hasattr(self, 'title_bar'):
                self.title_bar = None
            if hasattr(self, 'sidebar'):
                self.sidebar = None
            if hasattr(self, 'main_content'):
                self.main_content = None
            if hasattr(self, 'status_bar'):
                self.status_bar = None

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
            # 安全地获取窗口信息
            title = 'Unknown'
            geometry = '0x0'
            minsize = (800, 600)
            
            try:
                if hasattr(self, 'title') and callable(getattr(self, 'title', None)) and self.winfo_exists():
                    title = self.title()
                else:
                    title = 'AI小说生成器 v2.0'
            except:
                title = 'AI小说生成器 v2.0'
                
            try:
                if hasattr(self, 'geometry') and callable(getattr(self, 'geometry', None)) and self.winfo_exists():
                    geometry = self.geometry()
                else:
                    geometry = '1200x800'
            except:
                geometry = '1200x800'
                
            try:
                if hasattr(self, 'minsize') and callable(getattr(self, 'minsize', None)) and self.winfo_exists():
                    minsize_result = self.minsize()
                    # 确保minsize_result是有效的元组
                    if isinstance(minsize_result, tuple) and len(minsize_result) == 2:
                        # 确保两个元素都是整数
                        if isinstance(minsize_result[0], int) and isinstance(minsize_result[1], int):
                            minsize = minsize_result
                        else:
                            minsize = (800, 600)
                    else:
                        minsize = (800, 600)
                else:
                    minsize = (800, 600)
            except:
                minsize = (800, 600)

            # 安全地获取布局类型
            layout_type = 'unknown'
            try:
                if hasattr(self, 'layout_manager') and self.layout_manager and self.winfo_exists():
                    layout_type = self.layout_manager.get_current_layout_type().value
            except:
                layout_type = 'unknown'

            # 安全地获取主题
            theme = 'unknown'
            try:
                if hasattr(self, 'theme_manager') and self.theme_manager and self.winfo_exists():
                    theme = self.theme_manager.get_current_theme()
            except:
                theme = 'unknown'

            return {
                'title': title,
                'geometry': geometry,
                'minsize': minsize,
                'layout_type': layout_type,
                'theme': theme,
                'initialized': self.is_initialized(),
                'window_state': self._window_state
            }
        except Exception as e:
            logger.error(f"获取窗口信息失败: {e}")
            return {
                'title': 'AI小说生成器 v2.0',
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

    # 组件回调方法

    def _on_search(self, search_text: str):
        """搜索回调"""
        logger.info(f"搜索: {search_text}")

        if not search_text.strip():
            self._update_status("请输入搜索内容")
            return

        # 执行智能搜索
        search_results = self._perform_search(search_text.strip())

        if search_results:
            self._update_status(f"找到 {len(search_results)} 个结果: {search_text}")
            self._show_search_results(search_text, search_results)
        else:
            self._update_status(f"未找到相关内容: {search_text}")

    def _perform_search(self, search_text: str) -> List[Dict[str, Any]]:
        """执行搜索操作"""
        results = []

        try:
            # 搜索功能映射
            search_actions = {
                # 配置相关
                'config': {'tab': 'config', 'description': 'LLM和嵌入模型配置'},
                'llm': {'tab': 'config', 'description': '大语言模型配置'},
                'openai': {'tab': 'config', 'description': 'OpenAI API配置'},
                'api': {'tab': 'config', 'description': 'API密钥配置'},
                '设置': {'tab': 'config', 'description': '应用配置设置'},

                # 生成相关
                'generate': {'tab': 'generate', 'description': '小说生成功能'},
                '生成': {'tab': 'generate', 'description': 'AI小说生成'},
                '小说': {'tab': 'main', 'description': '小说创作工作区'},
                '写作': {'tab': 'main', 'description': '小说写作界面'},

                # 角色相关
                'character': {'tab': 'characters', 'description': '角色管理'},
                '角色': {'tab': 'characters', 'description': '角色设定管理'},

                # 章节相关
                'chapter': {'tab': 'chapters', 'description': '章节管理'},
                '章节': {'tab': 'chapters', 'description': '章节目录管理'},

                # 摘要相关
                'summary': {'tab': 'summary', 'description': '故事摘要管理'},
                '摘要': {'tab': 'summary', 'description': '全局故事摘要'},

                # 目录相关
                'directory': {'tab': 'directory', 'description': '章节目录'},
                '目录': {'tab': 'directory', 'description': '小说章节目录'},

                # 帮助相关
                'help': {'action': 'show_help', 'description': '显示帮助信息'},
                '帮助': {'action': 'show_help', 'description': '显示使用帮助'},
                'tutorial': {'action': 'show_tutorial', 'description': '显示使用教程'},
                '教程': {'action': 'show_tutorial', 'description': '显示使用教程'},

                # 主题相关
                'theme': {'action': 'show_theme_settings', 'description': '主题设置'},
                '主题': {'action': 'show_theme_settings', 'description': '界面主题设置'},
                'dark': {'action': 'toggle_dark_theme', 'description': '切换到深色主题'},
                'light': {'action': 'toggle_light_theme', 'description': '切换到浅色主题'},

                # 新建相关
                'new': {'action': 'new_novel', 'description': '创建新小说'},
                '新建': {'action': 'new_novel', 'description': '新建小说项目'},
                'create': {'action': 'new_novel', 'description': '创建新项目'},
            }

            # 精确匹配
            if search_text.lower() in search_actions:
                action = search_actions[search_text.lower()]
                action['keyword'] = search_text
                results.append(action)

            # 模糊匹配
            for keyword, action in search_actions.items():
                if search_text.lower() in keyword.lower() or keyword.lower() in search_text.lower():
                    if search_text.lower() != keyword:  # 避免重复
                        action['keyword'] = keyword
                        results.append(action)

            # 如果没有找到任何结果，提供网络搜索选项
            if not results:
                results.append({
                    'keyword': search_text,
                    'action': 'web_search',
                    'description': f'在网络上搜索 "{search_text}"',
                    'query': search_text
                })

        except Exception as e:
            logger.error(f"搜索执行失败: {e}")
            results.append({
                'keyword': search_text,
                'action': 'search_error',
                'description': f'搜索出错: {str(e)}'
            })

        return results[:5]  # 限制最多5个结果

    def _show_search_results(self, search_text: str, results: List[Dict[str, Any]]):
        """显示搜索结果"""
        try:
            # 创建搜索结果窗口
            results_window = ctk.CTkToplevel(self)
            results_window.title(f"搜索结果: {search_text}")
            results_window.geometry("400x300")
            results_window.transient(self)
            results_window.grab_set()

            # 设置窗口在父窗口中央显示
            results_window.update_idletasks()
            x = (results_window.winfo_screenwidth() // 2) - (400 // 2)
            y = (results_window.winfo_screenheight() // 2) - (300 // 2)
            results_window.geometry(f"400x300+{x}+{y}")

            # 搜索结果标题
            title_label = ctk.CTkLabel(
                results_window,
                text=f"搜索结果: {search_text}",
                font=ctk.CTkFont(size=16, weight="bold")
            )
            title_label.pack(pady=20)

            # 搜索结果列表
            results_frame = ctk.CTkScrollableFrame(results_window, height=200)
            results_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

            # 显示结果
            for i, result in enumerate(results):
                result_btn = ctk.CTkButton(
                    results_frame,
                    text=f"🔍 {result.get('description', result['keyword'])}",
                    command=lambda r=result: self._execute_search_action(r),
                    height=40,
                    anchor="w",
                    font=ctk.CTkFont(size=12)
                )
                result_btn.pack(fill="x", pady=2)

            # 关闭按钮
            close_btn = ctk.CTkButton(
                results_window,
                text="关闭",
                command=results_window.destroy,
                height=35
            )
            close_btn.pack(pady=(0, 20))

        except Exception as e:
            logger.error(f"显示搜索结果失败: {e}")
            self._update_status("显示搜索结果失败")

    def _execute_search_action(self, action: Dict[str, Any]):
        """执行搜索操作"""
        try:
            action_type = action.get('action', 'tab')

            if action_type == 'tab':
                # 切换到指定标签页
                tab_name = action.get('tab')
                if tab_name and hasattr(self, 'main_content'):
                    self.main_content.switch_to_tab(tab_name)
                    self._update_status(f"已切换到: {action.get('description', tab_name)}")

            elif action_type == 'show_help':
                self._show_help_dialog()

            elif action_type == 'show_tutorial':
                self._show_tutorial_dialog()

            elif action_type == 'show_theme_settings':
                self._open_settings_dialog()
                # 切换到主题设置选项卡
                self._update_status("请在设置中选择主题设置选项卡")

            elif action_type in ['toggle_dark_theme', 'toggle_light_theme']:
                new_theme = 'dark' if action_type == 'toggle_dark_theme' else 'light'
                if self.state_manager:
                    self.state_manager.set_state('app.theme', new_theme)
                    self._update_status(f"已切换到{new_theme}主题")

            elif action_type == 'new_novel':
                self._create_new_novel()

            elif action_type == 'web_search':
                import webbrowser
                query = action.get('query', '')
                webbrowser.open(f"https://www.google.com/search?q={query}")
                self._update_status(f"已在浏览器中搜索: {query}")

            elif action_type == 'search_error':
                self._update_status(action.get('description', '搜索出错'))

        except Exception as e:
            logger.error(f"执行搜索操作失败: {e}")
            self._update_status("执行搜索操作失败")

    def _show_help_dialog(self):
        """显示帮助对话框"""
        try:
            help_window = ctk.CTkToplevel(self)
            help_window.title("使用帮助")
            help_window.geometry("600x400")
            help_window.transient(self)
            help_window.grab_set()

            # 设置窗口在父窗口中央显示
            help_window.update_idletasks()
            x = (help_window.winfo_screenwidth() // 2) - (600 // 2)
            y = (help_window.winfo_screenheight() // 2) - (400 // 2)
            help_window.geometry(f"600x400+{x}+{y}")

            # 帮助内容
            help_text = """
🎯 AI小说生成器 v2.0 使用帮助

📚 核心功能:
• 主页 - 小说创作工作区，包含生成步骤控制
• 配置 - LLM和嵌入模型API配置
• 生成 - AI驱动的内容生成功能
• 角色 - 角色设定和状态管理
• 章节 - 章节目录和内容管理
• 摘要 - 故事全局摘要管理
• 目录 - 章节大纲规划

🔧 快速开始:
1. 在配置页面设置API密钥
2. 在主页输入小说主题和参数
3. 点击生成按钮开始创作

💡 搜索提示:
• 搜索功能名称快速跳转
• 支持中文和英文搜索
• 输入"帮助"查看更多信息

⚙️ 高级功能:
• 主题切换 - 深色/浅色模式
• 项目管理 - 保存和加载项目
• 批量生成 - 自动化创作流程

📞 获取支持:
• 遇到问题请查看日志文件
• 提交Issue到项目仓库
            """

            help_textbox = ctk.CTkTextbox(help_window, wrap="word")
            help_textbox.pack(fill="both", expand=True, padx=20, pady=20)
            help_textbox.insert("0.0", help_text)
            help_textbox.configure(state="disabled")

            # 关闭按钮
            close_btn = ctk.CTkButton(
                help_window,
                text="关闭",
                command=help_window.destroy,
                height=35
            )
            close_btn.pack(pady=(0, 20))

        except Exception as e:
            logger.error(f"显示帮助对话框失败: {e}")

    def _show_tutorial_dialog(self):
        """显示教程对话框"""
        try:
            tutorial_window = ctk.CTkToplevel(self)
            tutorial_window.title("使用教程")
            tutorial_window.geometry("600x500")
            tutorial_window.transient(self)
            tutorial_window.grab_set()

            # 设置窗口在父窗口中央显示
            tutorial_window.update_idletasks()
            x = (tutorial_window.winfo_screenwidth() // 2) - (600 // 2)
            y = (tutorial_window.winfo_screenheight() // 2) - (500 // 2)
            tutorial_window.geometry(f"600x500+{x}+{y}")

            # 教程内容
            tutorial_text = """
📖 AI小说生成器使用教程

🎯 第一步：配置API
1. 切换到"配置"标签页
2. 选择LLM提供商（如OpenAI、智谱等）
3. 输入API密钥
4. 点击"测试连接"确保配置正确

✨ 第二步：设置小说参数
1. 切换到"主页"标签页
2. 在右侧配置面板输入：
   - 小说主题（必填）
   - 小说类型
   - 章节数量
   - 每章字数
   - 保存路径

🚀 第三步：生成小说
按照以下步骤生成小说：

1️⃣ 生成架构
   - 点击"🏗️ 生成架构"按钮
   - AI将创建世界观和基本设定
   - 结果保存到Novel_setting.txt

2️⃣ 生成目录
   - 点击"📋 生成目录"按钮
   - AI将规划章节大纲
   - 结果保存到Novel_directory.txt

3️⃣ 生成章节
   - 设置当前章节号
   - 点击"✍️ 生成草稿"按钮
   - AI将撰写具体章节内容

4️⃣ 完善章节
   - 点击"✨ 完善章节"按钮
   - AI将润色和优化内容

🎨 第四步：管理内容
• 使用"角色"标签页管理角色设定
• 使用"章节"标签页浏览所有章节
• 使用"摘要"标签页维护故事连贯性
• 使用"目录"标签页查看整体结构

💡 专业技巧：
• 批量生成：使用"🚀 批量生成"自动完成所有步骤
• 内容指导：在生成前输入具体要求，获得更好结果
• 角色设定：详细的角色设定让故事更生动
• 定期保存：使用项目菜单保存创作进度

🔍 搜索功能：
• 输入功能名称快速跳转
• 搜索"配置"、"生成"、"角色"等关键词
• 支持中英文混合搜索

❓ 常见问题：
Q: API测试失败怎么办？
A: 检查密钥是否正确，网络是否正常

Q: 生成内容不满意？
A: 尝试修改主题描述或内容指导

Q: 如何查看详细日志？
A: 查看项目目录下的logs文件夹

祝您创作愉快！ 🎉
            """

            tutorial_textbox = ctk.CTkTextbox(tutorial_window, wrap="word")
            tutorial_textbox.pack(fill="both", expand=True, padx=20, pady=20)
            tutorial_textbox.insert("0.0", tutorial_text)
            tutorial_textbox.configure(state="disabled")

            # 关闭按钮
            close_btn = ctk.CTkButton(
                tutorial_window,
                text="关闭",
                command=tutorial_window.destroy,
                height=35
            )
            close_btn.pack(pady=(0, 20))

        except Exception as e:
            logger.error(f"显示教程对话框失败: {e}")

    def _on_settings(self):
        """设置回调"""
        try:
            logger.info("打开设置面板")
            self._open_settings_dialog()
            self._update_status("打开设置面板")
        except Exception as e:
            logger.error(f"打开设置面板失败: {e}")
            messagebox.showerror("错误", f"打开设置面板失败: {e}")

    def _open_settings_dialog(self):
        """打开设置对话框"""
        # 创建设置窗口
        settings_window = ctk.CTkToplevel(self)
        settings_window.title("应用设置")
        settings_window.geometry("650x550")  # 增加窗口大小以适应中文界面
        settings_window.resizable(True, True)  # 允许调整大小
        settings_window.transient(self)
        settings_window.grab_set()

        # 设置窗口在父窗口中央显示
        settings_window.update_idletasks()
        x = (settings_window.winfo_screenwidth() // 2) - (650 // 2)
        y = (settings_window.winfo_screenheight() // 2) - (550 // 2)
        settings_window.geometry(f"650x550+{x}+{y}")

        # 创建设置选项卡
        settings_tabview = ctk.CTkTabview(
            settings_window,
            segmented_button_fg_color="#2A2A2A",
            segmented_button_selected_color="#404040",
            segmented_button_unselected_color="#1E1E1E",
            height=400  # 设置固定高度
        )
        settings_tabview.pack(fill="both", expand=True, padx=20, pady=20)

        # 添加设置选项卡
        general_tab = settings_tabview.add("🔧 通用设置")
        theme_tab = settings_tabview.add("🎨 主题设置")
        advanced_tab = settings_tabview.add("⚙️ 高级设置")

        # 构建各个设置页面
        self._build_general_settings(general_tab, settings_window)
        self._build_theme_settings(theme_tab, settings_window)
        self._build_advanced_settings(advanced_tab, settings_window)

        # 底部按钮区域
        button_frame = ctk.CTkFrame(settings_window, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 20))

        # 保存按钮
        save_btn = ctk.CTkButton(
            button_frame,
            text="💾 保存设置",
            command=lambda: self._save_settings(settings_window),
            width=120,
            height=35
        )
        save_btn.pack(side="right", padx=(10, 0))

        # 取消按钮
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="❌ 取消",
            command=settings_window.destroy,
            width=120,
            height=35,
            fg_color="transparent",
            border_color="#404040",
            border_width=2
        )
        cancel_btn.pack(side="right")

        logger.info("设置对话框已打开")

    def _build_general_settings(self, parent, window):
        """构建通用设置页面"""
        # 主框架
        main_frame = ctk.CTkFrame(parent, fg_color="#2A2A2A")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 标题
        title = ctk.CTkLabel(
            main_frame,
            text="通用设置",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=(20, 30))

        # 语言设置
        lang_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        lang_frame.pack(fill="x", padx=20, pady=10)

        lang_label = ctk.CTkLabel(
            lang_frame,
            text="界面语言:",
            width=120,
            anchor="w"
        )
        lang_label.pack(side="left", padx=(0, 10))

        lang_var = ctk.StringVar(value="简体中文")
        lang_combo = ctk.CTkComboBox(
            lang_frame,
            variable=lang_var,
            values=["简体中文", "English", "繁體中文"]
        )
        lang_combo.pack(side="left", fill="x", expand=True)

        # 自动保存设置
        autosave_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        autosave_frame.pack(fill="x", padx=20, pady=10)

        autosave_var = ctk.BooleanVar(value=True)
        autosave_check = ctk.CTkCheckBox(
            autosave_frame,
            text="自动保存项目",
            variable=autosave_var
        )
        autosave_check.pack(side="left")

        # 启动时打开上次项目
        restore_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        restore_frame.pack(fill="x", padx=20, pady=10)

        restore_var = ctk.BooleanVar(value=False)
        restore_check = ctk.CTkCheckBox(
            restore_frame,
            text="启动时恢复上次项目",
            variable=restore_var
        )
        restore_check.pack(side="left")

        # 保存设置变量到窗口
        window.lang_var = lang_var
        window.autosave_var = autosave_var
        window.restore_var = restore_var

    def _build_theme_settings(self, parent, window):
        """构建主题设置页面"""
        # 主框架
        main_frame = ctk.CTkFrame(parent, fg_color="#2A2A2A")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 标题
        title = ctk.CTkLabel(
            main_frame,
            text="主题设置",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=(20, 30))

        # 主题选择
        theme_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        theme_frame.pack(fill="x", padx=20, pady=10)

        theme_label = ctk.CTkLabel(
            theme_frame,
            text="界面主题:",
            width=120,
            anchor="w"
        )
        theme_label.pack(side="left", padx=(0, 10))

        theme_var = ctk.StringVar(value=self.state_manager.get_state('app.theme', 'dark'))
        theme_combo = ctk.CTkComboBox(
            theme_frame,
            variable=theme_var,
            values=["浅色", "深色", "蓝色", "绿色"],
            command=lambda x: self._preview_theme(theme_var.get())
        )
        theme_combo.pack(side="left", fill="x", expand=True)

        # 字体设置区域
        font_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        font_frame.pack(fill="x", padx=20, pady=10)

        font_title = ctk.CTkLabel(
            font_frame,
            text="字体设置",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        font_title.pack(fill="x", pady=(0, 10))

        # 字体族设置
        font_family_frame = ctk.CTkFrame(font_frame, fg_color="transparent")
        font_family_frame.pack(fill="x", pady=5)

        font_family_label = ctk.CTkLabel(
            font_family_frame,
            text="字体族:",
            width=120,
            anchor="w"
        )
        font_family_label.pack(side="left", padx=(0, 10))

        # 获取系统可用字体
        available_fonts = ["Microsoft YaHei UI", "Arial", "Helvetica", "Times New Roman", "Courier New", "Verdana", "Tahoma"]
        font_family_var = ctk.StringVar(value="Microsoft YaHei UI")
        font_family_combo = ctk.CTkComboBox(
            font_family_frame,
            variable=font_family_var,
            values=available_fonts
        )
        font_family_combo.pack(side="left", fill="x", expand=True)

        # 字体大小设置
        fontsize_frame = ctk.CTkFrame(font_frame, fg_color="transparent")
        fontsize_frame.pack(fill="x", pady=5)

        fontsize_label = ctk.CTkLabel(
            fontsize_frame,
            text="字体大小:",
            width=120,
            anchor="w"
        )
        fontsize_label.pack(side="left", padx=(0, 10))

        fontsize_var = ctk.StringVar(value="正常")
        fontsize_combo = ctk.CTkComboBox(
            fontsize_frame,
            variable=fontsize_var,
            values=["小", "正常", "大", "特大"]
        )
        fontsize_combo.pack(side="left", fill="x", expand=True)

        # 字体样式设置
        font_style_frame = ctk.CTkFrame(font_frame, fg_color="transparent")
        font_style_frame.pack(fill="x", pady=5)

        font_style_label = ctk.CTkLabel(
            font_style_frame,
            text="字体样式:",
            width=120,
            anchor="w"
        )
        font_style_label.pack(side="left", padx=(0, 10))

        font_style_var = ctk.StringVar(value="正常")
        font_style_combo = ctk.CTkComboBox(
            font_style_frame,
            variable=font_style_var,
            values=["正常", "粗体", "斜体", "粗斜体"]
        )
        font_style_combo.pack(side="left", fill="x", expand=True)

        # 字体预览区域
        preview_frame = ctk.CTkFrame(font_frame, fg_color="transparent")
        preview_frame.pack(fill="x", pady=(10, 5))

        preview_label = ctk.CTkLabel(
            preview_frame,
            text="预览:",
            anchor="w"
        )
        preview_label.pack(anchor="w")

        preview_text = ctk.CTkLabel(
            preview_frame,
            text="The quick brown fox jumps over the lazy dog\n快速的棕色狐狸跳过懒狗",
            fg_color="#404040",
            corner_radius=6,
            padx=10,
            pady=10
        )
        preview_text.pack(fill="x", pady=(5, 0))

        # 绑定预览更新事件
        def update_preview(*args):
            family = font_family_var.get()
            size_map = {"小": 10, "正常": 12, "大": 14, "特大": 16}
            size = size_map.get(fontsize_var.get(), 12)
            style_map = {"正常": "normal", "粗体": "bold", "斜体": "normal", "粗斜体": "bold"}
            style_value = style_map.get(font_style_var.get(), "normal")
            
            # 确保weight参数是合法值
            weight = "bold" if style_value == "bold" else "normal"
            preview_font = ctk.CTkFont(family=family, size=size, weight=weight)
            preview_text.configure(font=preview_font)

        font_family_var.trace("w", update_preview)
        fontsize_var.trace("w", update_preview)
        font_style_var.trace("w", update_preview)

        # 动画效果
        animation_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        animation_frame.pack(fill="x", padx=20, pady=10)

        animation_var = ctk.BooleanVar(value=False)
        animation_check = ctk.CTkCheckBox(
            animation_frame,
            text="启用界面动画效果",
            variable=animation_var
        )
        animation_check.pack(side="left")

        # 保存设置变量到窗口
        window.theme_var = theme_var
        window.font_family_var = font_family_var
        window.fontsize_var = fontsize_var
        window.font_style_var = font_style_var
        window.animation_var = animation_var

    def _build_advanced_settings(self, parent, window):
        """构建高级设置页面"""
        # 主框架
        main_frame = ctk.CTkFrame(parent, fg_color="#2A2A2A")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 标题
        title = ctk.CTkLabel(
            main_frame,
            text="高级设置",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=(20, 30))

        # 日志级别
        log_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        log_frame.pack(fill="x", padx=20, pady=10)

        log_label = ctk.CTkLabel(
            log_frame,
            text="日志级别:",
            width=120,
            anchor="w"
        )
        log_label.pack(side="left", padx=(0, 10))

        log_var = ctk.StringVar(value="INFO")
        log_combo = ctk.CTkComboBox(
            log_frame,
            variable=log_var,
            values=["DEBUG", "INFO", "WARNING", "ERROR"]
        )
        log_combo.pack(side="left", fill="x", expand=True)

        # 性能监控
        perf_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        perf_frame.pack(fill="x", padx=20, pady=10)

        perf_var = ctk.BooleanVar(value=False)
        perf_check = ctk.CTkCheckBox(
            perf_frame,
            text="启用性能监控",
            variable=perf_var
        )
        perf_check.pack(side="left")

        # 调试模式
        debug_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        debug_frame.pack(fill="x", padx=20, pady=10)

        debug_var = ctk.BooleanVar(value=False)
        debug_check = ctk.CTkCheckBox(
            debug_frame,
            text="启用调试模式",
            variable=debug_var
        )
        debug_check.pack(side="left")

        # 保存设置变量到窗口
        window.log_var = log_var
        window.perf_var = perf_var
        window.debug_var = debug_var

    def _preview_theme(self, theme_name: str):
        """预览主题"""
        try:
            theme_mapping = {
                "浅色": "light",
                "深色": "dark",
                "蓝色": "blue",
                "绿色": "green"
            }

            mapped_theme = theme_mapping.get(theme_name, "dark")
            if self.theme_manager:
                self.theme_manager.apply_theme(mapped_theme)
                logger.info(f"预览主题: {mapped_theme}")
        except Exception as e:
            logger.error(f"预览主题失败: {e}")

    def _save_settings(self, window):
        """保存设置"""
        try:
            # 保存主题设置
            if hasattr(window, 'theme_var'):
                theme_mapping = {
                    "浅色": "light",
                    "深色": "dark",
                    "蓝色": "blue",
                    "绿色": "green"
                }
                theme_name = window.theme_var.get()
                mapped_theme = theme_mapping.get(theme_name, "dark")
                self.state_manager.set_state('app.theme', mapped_theme)
                if self.theme_manager:
                    self.theme_manager.apply_theme(mapped_theme)

            # 保存其他设置到状态管理器
            settings = {
                'language': window.lang_var.get() if hasattr(window, 'lang_var') else "简体中文",
                'autosave': window.autosave_var.get() if hasattr(window, 'autosave_var') else True,
                'restore_last_project': window.restore_var.get() if hasattr(window, 'restore_var') else False,
                'fontsize': window.fontsize_var.get() if hasattr(window, 'fontsize_var') else "正常",
                'font_family': window.font_family_var.get() if hasattr(window, 'font_family_var') else "Microsoft YaHei UI",
                'font_style': window.font_style_var.get() if hasattr(window, 'font_style_var') else "正常",
                'animation': window.animation_var.get() if hasattr(window, 'animation_var') else False,
                'log_level': window.log_var.get() if hasattr(window, 'log_var') else "INFO",
                'performance_monitoring': window.perf_var.get() if hasattr(window, 'perf_var') else False,
                'debug_mode': window.debug_var.get() if hasattr(window, 'debug_var') else False
            }

            self.state_manager.update_state({'settings': settings})
            logger.info("设置已保存")

            # 应用字体设置
            self._apply_font_size_setting(settings.get('fontsize', '正常'))
            self._apply_font_family_setting(settings.get('font_family', 'Microsoft YaHei UI'))

            self._update_status("✅ 设置已保存！")
            window.destroy()

        except Exception as e:
            logger.error(f"保存设置失败: {e}")
            self._update_status(f"❌ 保存设置失败: {e}")

    def _apply_font_size_setting(self, font_size_setting: str):
        """应用字体大小设置"""
        try:
            # 字体大小映射
            font_size_map = {
                "小": 10,
                "正常": 12,
                "大": 14,
                "特大": 16
            }

            base_size = font_size_map.get(font_size_setting, 12)

            # 为全局设置默认字体大小
            ctk.set_appearance_mode("dark")  # 确保模式设置
            logger.info(f"应用字体大小设置: {font_size_setting} ({base_size}px)")

            # 如果有主题管理器，更新主题设置
            if hasattr(self, 'theme_manager') and self.theme_manager:
                # 这里可以扩展主题管理器以支持字体大小
                current_theme = self.theme_manager.get_current_theme()
                logger.info(f"当前主题: {current_theme}, 字体大小已更新")

            # 更新状态栏字体
            if hasattr(self, 'status_label'):
                self.status_label.configure(font=ctk.CTkFont(size=base_size - 1))

            logger.info("字体大小设置已应用到界面")

        except Exception as e:
            logger.error(f"应用字体设置失败: {e}")

    def _apply_font_family_setting(self, font_family: str):
        """应用字体族设置"""
        try:
            logger.info(f"应用字体族设置: {font_family}")
            # 这里可以扩展更多字体应用逻辑
            # 目前我们只记录日志，实际应用需要在各组件中实现
        except Exception as e:
            logger.error(f"应用字体族设置失败: {e}")

    def _on_user_menu(self):
        """用户菜单回调"""
        try:
            logger.info("打开用户菜单")
            self._open_user_menu_dialog()
            self._update_status("打开用户菜单")
        except Exception as e:
            logger.error(f"打开用户菜单失败: {e}")
            messagebox.showerror("错误", f"打开用户菜单失败: {e}")

    def _open_user_menu_dialog(self):
        """打开用户菜单对话框"""
        # 创建用户菜单窗口
        user_window = ctk.CTkToplevel(self)
        user_window.title("用户中心")
        user_window.geometry("400x500")
        user_window.transient(self)
        user_window.grab_set()

        # 设置窗口在父窗口中央显示
        user_window.update_idletasks()
        x = (user_window.winfo_screenwidth() // 2) - (400 // 2)
        y = (user_window.winfo_screenheight() // 2) - (500 // 2)
        user_window.geometry(f"400x500+{x}+{y}")

        # 用户信息框架
        user_info_frame = ctk.CTkFrame(user_window, corner_radius=8)
        user_info_frame.pack(fill="x", padx=20, pady=20)

        # 用户头像（使用图标代替）
        avatar_label = ctk.CTkLabel(
            user_info_frame,
            text="👤",
            font=ctk.CTkFont(size=48),
            width=80,
            height=80
        )
        avatar_label.pack(pady=20)

        # 用户名
        username_label = ctk.CTkLabel(
            user_info_frame,
            text="用户",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        username_label.pack(pady=(0, 5))

        # 用户状态
        status_label = ctk.CTkLabel(
            user_info_frame,
            text="🟢 在线",
            font=ctk.CTkFont(size=14),
            text_color="#4CAF50"
        )
        status_label.pack(pady=(0, 20))

        # 菜单选项框架
        menu_frame = ctk.CTkFrame(user_window, fg_color="#2A2A2A")
        menu_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # 菜单选项
        menu_items = [
            ("👤 个人资料", self._open_profile),
            ("📊 使用统计", self._open_usage_stats),
            ("💾 备份与恢复", self._open_backup_restore),
            ("📁 项目管理", self._open_project_management),
            ("⚙️ 高级设置", lambda: self._open_settings_dialog()),
            ("❓ 帮助与支持", self._open_help),
            ("📝 关于", self._open_about)
        ]

        for text, command in menu_items:
            btn = ctk.CTkButton(
                menu_frame,
                text=text,
                command=lambda cmd=command: self._execute_menu_action(cmd, user_window),
                height=40,
                corner_radius=6,
                fg_color="transparent",
                hover_color="#404040",
                anchor="w",
                font=ctk.CTkFont(size=14)
            )
            btn.pack(fill="x", padx=10, pady=2)

        # 底部按钮
        bottom_frame = ctk.CTkFrame(user_window)
        bottom_frame.pack(fill="x", padx=20, pady=(0, 20))

        # 退出登录按钮
        logout_btn = ctk.CTkButton(
            bottom_frame,
            text="退出登录",
            command=lambda: self._logout(user_window),
            fg_color="#FF6B6B",
            hover_color="#FF5252"
        )
        logout_btn.pack(side="left", padx=(0, 10))

        # 关闭按钮
        close_btn = ctk.CTkButton(
            bottom_frame,
            text="关闭",
            command=user_window.destroy
        )
        close_btn.pack(side="right")

        logger.info("用户菜单对话框已打开")

    def _execute_menu_action(self, command, parent_window):
        """执行菜单操作"""
        try:
            command()
            parent_window.destroy()
        except Exception as e:
            logger.error(f"执行菜单操作失败: {e}")
            messagebox.showerror("错误", f"操作失败: {e}")

    def _open_profile(self):
        """打开个人资料"""
        try:
            # 创建个人资料窗口
            profile_window = ctk.CTkToplevel(self)
            profile_window.title("个人资料")
            profile_window.geometry("500x600")
            profile_window.transient(self)
            profile_window.grab_set()

            # 设置窗口在父窗口中央显示
            profile_window.update_idletasks()
            x = (profile_window.winfo_screenwidth() // 2) - (500 // 2)
            y = (profile_window.winfo_screenheight() // 2) - (600 // 2)
            profile_window.geometry(f"500x600+{x}+{y}")

            # 主框架
            main_frame = ctk.CTkFrame(profile_window, fg_color="#2A2A2A")
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)

            # 标题
            title_label = ctk.CTkLabel(
                main_frame,
                text="👤 个人资料",
                font=ctk.CTkFont(size=18, weight="bold")
            )
            title_label.pack(pady=(0, 20))

            # 头像区域
            avatar_frame = ctk.CTkFrame(main_frame, fg_color="#404040")
            avatar_frame.pack(fill="x", pady=(0, 20))

            avatar_label = ctk.CTkLabel(
                avatar_frame,
                text="🎭",
                font=ctk.CTkFont(size=48),
                height=100
            )
            avatar_label.pack(pady=20)

            # 用户信息表单
            form_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            form_frame.pack(fill="x", pady=(0, 20))

            # 用户名
            username_label = ctk.CTkLabel(
                form_frame,
                text="用户名:",
                anchor="w"
            )
            username_label.pack(fill="x", pady=(5, 2))

            username_entry = ctk.CTkEntry(
                form_frame,
                placeholder_text="请输入用户名"
            )
            username_entry.pack(fill="x", pady=(0, 10))
            username_entry.insert(0, "AI创作者")  # 默认值

            # 邮箱
            email_label = ctk.CTkLabel(
                form_frame,
                text="邮箱:",
                anchor="w"
            )
            email_label.pack(fill="x", pady=(5, 2))

            email_entry = ctk.CTkEntry(
                form_frame,
                placeholder_text="请输入邮箱地址"
            )
            email_entry.pack(fill="x", pady=(0, 10))

            # 创作偏好
            preference_label = ctk.CTkLabel(
                form_frame,
                text="创作偏好:",
                anchor="w"
            )
            preference_label.pack(fill="x", pady=(5, 2))

            preference_text = ctk.CTkTextbox(
                form_frame,
                height=80
            )
            preference_text.pack(fill="x", pady=(0, 10))
            preference_text.insert("0.0", "科幻、玄幻、现实主义")

            # 使用统计
            stats_frame = ctk.CTkFrame(main_frame, fg_color="#404040")
            stats_frame.pack(fill="x", pady=(0, 20))

            stats_title = ctk.CTkLabel(
                stats_frame,
                text="📊 使用统计",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            stats_title.pack(pady=(10, 5))

            stats_content = ctk.CTkLabel(
                stats_frame,
                text="创作小说: 3部\n总字数: 50,000字\n使用天数: 15天",
                justify="left"
            )
            stats_content.pack(pady=(0, 10))

            # 按钮区域
            button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            button_frame.pack(fill="x")

            save_btn = ctk.CTkButton(
                button_frame,
                text="保存资料",
                command=lambda: self._save_profile(profile_window),
                height=40
            )
            save_btn.pack(side="left", padx=(0, 10), pady=10, expand=True, fill="x")

            cancel_btn = ctk.CTkButton(
                button_frame,
                text="取消",
                command=profile_window.destroy,
                height=40,
                fg_color="transparent",
                border_color="#404040",
                border_width=1
            )
            cancel_btn.pack(side="left", pady=10, expand=True, fill="x")

        except Exception as e:
            logger.error(f"打开个人资料失败: {e}")
            messagebox.showerror("错误", f"打开个人资料失败: {e}")

    def _save_profile(self, window):
        """保存个人资料"""
        try:
            # 这里可以实现保存逻辑
            self._update_status("✅ 个人资料已保存")
            window.destroy()
        except Exception as e:
            logger.error(f"保存个人资料失败: {e}")
            self._update_status("❌ 保存个人资料失败")

    def _open_usage_stats(self):
        """打开使用统计"""
        stats_window = ctk.CTkToplevel(self)
        stats_window.title("使用统计")
        stats_window.geometry("500x400")
        stats_window.transient(self)

        # 统计信息框架
        stats_frame = ctk.CTkFrame(stats_window, fg_color="#2A2A2A")
        stats_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 标题
        title = ctk.CTkLabel(
            stats_frame,
            text="📊 使用统计",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=(20, 30))

        # 统计数据
        stats = [
            ("总生成章节数:", "12"),
            ("总字数:", "48,520"),
            ("使用天数:", "7"),
            ("最爱模型:", "gpt-4"),
            ("最后使用:", "2025-10-04")
        ]

        for label, value in stats:
            stat_frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
            stat_frame.pack(fill="x", padx=20, pady=8)

            stat_label = ctk.CTkLabel(
                stat_frame,
                text=label,
                width=150,
                anchor="w",
                font=ctk.CTkFont(size=14)
            )
            stat_label.pack(side="left")

            value_label = ctk.CTkLabel(
                stat_frame,
                text=value,
                anchor="w",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            value_label.pack(side="left")

        # 关闭按钮
        close_btn = ctk.CTkButton(
            stats_frame,
            text="关闭",
            command=stats_window.destroy
        )
        close_btn.pack(pady=20)

    def _open_backup_restore(self):
        """打开备份与恢复"""
        messagebox.showinfo("备份与恢复", "备份与恢复功能正在开发中...")

    def _open_project_management(self):
        """打开项目管理"""
        try:
            # 创建项目管理窗口
            project_window = ctk.CTkToplevel(self)
            project_window.title("项目管理")
            project_window.geometry("700x500")
            project_window.transient(self)
            project_window.grab_set()

            # 设置窗口在父窗口中央显示
            project_window.update_idletasks()
            x = (project_window.winfo_screenwidth() // 2) - (700 // 2)
            y = (project_window.winfo_screenheight() // 2) - (500 // 2)
            project_window.geometry(f"700x500+{x}+{y}")

            # 主框架
            main_frame = ctk.CTkFrame(project_window, fg_color="#2A2A2A")
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)

            # 标题
            title_label = ctk.CTkLabel(
                main_frame,
                text="📁 项目管理",
                font=ctk.CTkFont(size=18, weight="bold")
            )
            title_label.pack(pady=(0, 20))

            # 工具栏
            toolbar_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            toolbar_frame.pack(fill="x", pady=(0, 10))

            new_project_btn = ctk.CTkButton(
                toolbar_frame,
                text="➕ 新建项目",
                command=self._create_new_novel,
                width=120
            )
            new_project_btn.pack(side="left", padx=(0, 10))

            open_project_btn = ctk.CTkButton(
                toolbar_frame,
                text="📂 打开项目",
                command=self._open_project,
                width=120
            )
            open_project_btn.pack(side="left", padx=(0, 10))

            # 项目列表
            list_frame = ctk.CTkFrame(main_frame, fg_color="#404040")
            list_frame.pack(fill="both", expand=True, pady=(0, 10))

            list_title = ctk.CTkLabel(
                list_frame,
                text="最近项目",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            list_title.pack(pady=(10, 5), anchor="w", padx=10)

            # 滚动框架
            scroll_frame = ctk.CTkScrollableFrame(list_frame, height=300)
            scroll_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

            # 示例项目列表
            projects = [
                {
                    "name": "星际旅行者",
                    "path": "/path/to/star_traveler",
                    "modified": "2025-10-03",
                    "status": "进行中",
                    "progress": 65
                },
                {
                    "name": "魔法学院",
                    "path": "/path/to/magic_academy",
                    "modified": "2025-10-01",
                    "status": "已完成",
                    "progress": 100
                },
                {
                    "name": "都市传说",
                    "path": "/path/to/urban_legend",
                    "modified": "2025-09-28",
                    "status": "草稿",
                    "progress": 30
                }
            ]

            for i, project in enumerate(projects):
                project_frame = ctk.CTkFrame(scroll_frame, fg_color="#2A2A2A")
                project_frame.pack(fill="x", pady=2)

                # 项目信息
                info_frame = ctk.CTkFrame(project_frame, fg_color="transparent")
                info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

                name_label = ctk.CTkLabel(
                    info_frame,
                    text=f"📚 {project['name']}",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    anchor="w"
                )
                name_label.pack(fill="x")

                details_label = ctk.CTkLabel(
                    info_frame,
                    text=f"📅 {project['modified']} | 📊 {project['status']} | 进度: {project['progress']}%",
                    font=ctk.CTkFont(size=10),
                    text_color="gray",
                    anchor="w"
                )
                details_label.pack(fill="x")

                # 操作按钮
                action_frame = ctk.CTkFrame(project_frame, fg_color="transparent")
                action_frame.pack(side="right", padx=10)

                load_btn = ctk.CTkButton(
                    action_frame,
                    text="加载",
                    width=60,
                    height=30,
                    command=lambda p=project: self._load_project_from_path(p['path'])
                )
                load_btn.pack(pady=5)

            # 底部按钮
            bottom_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            bottom_frame.pack(fill="x")

            quick_load_btn = ctk.CTkButton(
                bottom_frame,
                text="⚡ 快速加载上次项目",
                command=self._quick_load_last_project,
                height=40
            )
            quick_load_btn.pack(side="left", padx=(0, 10), pady=10, expand=True, fill="x")

            close_btn = ctk.CTkButton(
                bottom_frame,
                text="关闭",
                command=project_window.destroy,
                height=40,
                fg_color="transparent",
                border_color="#404040",
                border_width=1
            )
            close_btn.pack(side="left", pady=10, expand=True, fill="x")

        except Exception as e:
            logger.error(f"打开项目管理失败: {e}")
            messagebox.showerror("错误", f"打开项目管理失败: {e}")

    def _open_help(self):
        """打开帮助与支持"""
        help_window = ctk.CTkToplevel(self)
        help_window.title("帮助与支持")
        help_window.geometry("600x500")
        help_window.transient(self)

        # 帮助内容框架
        help_frame = ctk.CTkScrollableFrame(help_window, fg_color="#2A2A2A")
        help_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 标题
        title = ctk.CTkLabel(
            help_frame,
            text="❓ 帮助与支持",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=(20, 30))

        # 帮助内容
        help_content = """
🎯 快速开始

1. 配置API密钥：在"配置"标签页中输入您的LLM和嵌入API密钥
2. 设置小说参数：在主页中设置小说的主题、类型等参数
3. 生成小说架构：点击"生成架构"按钮创建世界观
4. 生成章节目录：点击"生成目录"按钮创建章节大纲
5. 生成章节内容：点击"生成草稿"按钮开始写作

🔧 常见问题

Q: 如何获取API密钥？
A: 请访问各LLM提供商的官方网站注册账号并获取API密钥。

Q: 支持哪些LLM提供商？
A: 目前支持OpenAI、DeepSeek、智谱、硅基流动等多个提供商。

Q: 如何备份我的项目？
A: 使用"导出"功能可以将项目保存为文件。

📞 联系支持

如需技术支持，请访问：
- GitHub项目主页
- 用户交流群组
- 邮件支持：support@example.com
        """

        help_text = ctk.CTkTextbox(
            help_frame,
            wrap="word",
            font=ctk.CTkFont(size=12),
            height=400
        )
        help_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        help_text.insert("0.0", help_content.strip())
        help_text.configure(state="disabled")

        # 关闭按钮
        close_btn = ctk.CTkButton(
            help_frame,
            text="关闭",
            command=help_window.destroy
        )
        close_btn.pack(pady=(0, 20))

    def _open_about(self):
        """打开关于"""
        about_window = ctk.CTkToplevel(self)
        about_window.title("关于")
        about_window.geometry("400x300")
        about_window.transient(self)

        # 关于内容框架
        about_frame = ctk.CTkFrame(about_window, fg_color="#2A2A2A")
        about_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 应用图标和名称
        app_label = ctk.CTkLabel(
            about_frame,
            text="🤖 AI小说生成器",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        app_label.pack(pady=(30, 10))

        # 版本信息
        version_label = ctk.CTkLabel(
            about_frame,
            text="版本 2.0",
            font=ctk.CTkFont(size=16)
        )
        version_label.pack(pady=(0, 20))

        # 描述
        desc_label = ctk.CTkLabel(
            about_frame,
            text="基于大语言模型的智能小说创作工具\n帮助创作者轻松构建精彩的小说世界",
            font=ctk.CTkFont(size=12),
            justify="center"
        )
        desc_label.pack(pady=(0, 20))

        # 版权信息
        copyright_label = ctk.CTkLabel(
            about_frame,
            text="© 2025 AI Novel Generator\nAll rights reserved",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        copyright_label.pack(pady=(0, 20))

        # 关闭按钮
        close_btn = ctk.CTkButton(
            about_frame,
            text="关闭",
            command=about_window.destroy
        )
        close_btn.pack(pady=(0, 20))

    def _logout(self, parent_window):
        """退出登录"""
        if messagebox.askyesno("确认退出", "确定要退出登录吗？"):
            logger.info("用户已退出登录")
            parent_window.destroy()
            # 这里可以添加退出登录的逻辑

    def _on_navigation(self, target: str, name: str):
        """导航回调"""
        logger.info(f"导航到: {target} ({name})")

        # 导航动画效果
        if hasattr(self, 'sidebar') and self.sidebar:
            self.animation_manager.bounce(self.sidebar, bounce_height=5, duration=200)

        # 切换到对应的标签页
        if hasattr(self, 'main_content') and self.main_content:
            self.main_content.switch_to_tab(target)

        self._update_status(f"当前页面: {name}")

    def _on_quick_action(self, action: str):
        """快速操作回调"""
        logger.info(f"快速操作: {action}")
        action_names = {
            "new_novel": "新建小说",
            "quick_load": "快速加载上次项目",
            "open_project": "打开项目",
            "save": "保存",
            "export": "导出"
        }
        action_name = action_names.get(action, action)

        # 快速操作动画效果
        if hasattr(self, 'title_bar') and self.title_bar:
            self.animation_manager.scale_up(self.title_bar, to_scale=1.02, duration=150)

        # 执行具体操作
        if action == "new_novel":
            self._create_new_novel()
        elif action == "quick_load":
            self._quick_load_last_project()
        elif action == "open_project":
            self._open_project()
        elif action == "save":
            self._save_project()
        elif action == "export":
            self._export_project()
        else:
            logger.warning(f"未知的快速操作: {action}")

        self._update_status(f"执行: {action_name}")

    def _on_project_select(self, project_name: str):
        """项目选择回调"""
        logger.info(f"选择项目: {project_name}")
        # 只有当确实存在项目时才更新状态
        if project_name and project_name != "未选择项目":
            self._update_status(f"当前项目: {project_name}")

    def _update_status(self, message: str):
        """更新状态栏"""
        try:
            # 优先使用通知系统
            if hasattr(self, 'notification_system') and self.notification_system:
                # 根据消息内容判断通知类型
                if "✅" in message or "成功" in message:
                    self.notification_system.show_success(message, duration=3000)
                elif "❌" in message or "失败" in message or "错误" in message:
                    self.notification_system.show_error(message, duration=5000)
                elif "⚠️" in message or "警告" in message:
                    self.notification_system.show_warning(message, duration=4000)
                else:
                    # 持续显示状态信息
                    self.notification_system.show_status(message)
            elif hasattr(self, 'status_label'):
                # 回退到传统状态栏
                current_theme = self.state_manager.get_state('app.theme', 'dark')
                layout_type = self.layout_manager.get_current_layout_type().value
                self.status_label.configure(
                    text=f"{message} | 主题: {current_theme} | 布局: {layout_type}"
                )
        except Exception as e:
            logger.error(f"更新状态栏失败: {e}")

    def _show_welcome_message(self):
        """显示欢迎信息"""
        try:
            # 在配置标签页显示欢迎信息
            config_frame = self.main_content.get_tab_content_frame("summary")
            if config_frame:
                welcome_text = """🎨 AI小说生成器 v2.0

📋 Day 4 ADAPT阶段 - 功能迁移进行中

✅ 已完成功能:
• 现代化主题系统
• 响应式主窗口布局
• 核心导航和标题栏
• 主内容区域和标签页系统
• 配置管理界面
• 生成功能界面
• 角色管理界面
• 章节管理界面

🚧 正在开发:
• 高级交互动画和过渡效果
• 性能优化和用户体验改进
• 摘要和目录功能集成

💡 使用提示:
• 使用左侧导航栏快速切换功能
• 通过顶部标题栏访问搜索和设置
• 在配置页面设置API密钥和生成参数
• 在生成页面开始创作您的小说

🎯 BMAD方法实践:
• BUILD: 现代化UI框架已完成 ✅
• MAINTAIN: 系统稳定性和维护性 ✅
• ADAPT: 功能迁移和适配中 🔄
• DEVELOP: 功能扩展和完善中 ⏳"""

                self.welcome_label = ctk.CTkLabel(
                    config_frame,
                    text=welcome_text,
                    font=ctk.CTkFont(size=14, weight="normal"),
                    justify="left",
                    wraplength=500
                )
                self.welcome_label.pack(expand=True, fill="both", padx=20, pady=20)

        except Exception as e:
            logger.error(f"显示欢迎信息失败: {e}")

    def _on_config_changed(self, config_data: Dict[str, Any]):
        """配置变化回调"""
        try:
            logger.info("配置已更新")
            self._update_status("配置已保存")

            # 配置保存动画效果
            if hasattr(self, 'config_tab') and self.config_tab:
                self.animation_manager.highlight(self.config_tab, "#4CAF50", duration=800)

            # 通知其他组件配置变化
            if self.state_manager:
                self.state_manager.update_state({'config': config_data})

        except Exception as e:
            logger.error(f"处理配置变化失败: {e}")

  
    def _on_generation_completed(self, result: Dict[str, Any]):
        """生成完成回调"""
        try:
            self._update_status("内容生成完成")

            # 生成完成动画效果
            if hasattr(self, 'generate_tab') and self.generate_tab:
                self.animation_manager.scale_up(self.generate_tab, duration=300)
                self.animation_manager.highlight(self.generate_tab, "#2196F3", duration=600)

        except Exception as e:
            logger.error(f"处理生成完成事件失败: {e}")

    def _on_tab_switching(self, from_tab: str, to_tab: str):
        """标签页切换前回调"""
        try:
            logger.debug(f"从 {from_tab} 切换到 {to_tab}")
            # 可以在这里添加切换前的逻辑
        except Exception as e:
            logger.error(f"处理标签页切换前事件失败: {e}")

    def _on_tab_switched(self, tab_name: str):
        """标签页切换后回调"""
        try:
            logger.info(f"已切换到标签页: {tab_name}")
            self.state_manager.update_state({'app.active_tab': tab_name})

            # 获取标签页内容框架
            tab_frame = self.main_content.get_tab_content_frame(tab_name)
            if tab_frame:
                # 标签页切换动画效果
                self.animation_manager.scale_up(tab_frame, from_scale=0.95, to_scale=1.0, duration=200)

                # 根据不同标签页添加特殊动画
                if tab_name == "main":
                    # 主页：滑入动画
                    self.animation_manager.slide_in(tab_frame, AnimationDirection.RIGHT, duration=400)
                elif tab_name == "generate":
                    # 生成页面：脉冲动画
                    self.animation_manager.pulse(tab_frame, duration=600)
                elif tab_name == "config":
                    # 配置页面：高亮动画
                    self.animation_manager.highlight(tab_frame, duration=400)

            # 更新状态栏
            tab_names = {
                "main": "主页",
                "config": "配置",
                "generate": "生成",
                "characters": "角色",
                "chapters": "章节",
                "summary": "摘要",
                "directory": "目录"
            }
            tab_display_name = tab_names.get(tab_name, tab_name)
            self._update_status(f"当前页面: {tab_display_name}")

        except Exception as e:
            logger.error(f"处理标签页切换后事件失败: {e}")

    def _on_character_changed(self, character_data: Dict[str, Any]):
        """角色变化回调"""
        try:
            logger.info("角色信息已更新")
            self._update_status("角色信息已保存")

            # 通知其他组件角色变化
            if self.state_manager:
                self.state_manager.update_state({'characters': character_data})

        except Exception as e:
            logger.error(f"处理角色变化失败: {e}")

    def _on_chapter_changed(self, chapter_data: Dict[str, Any]):
        """章节变化回调"""
        try:
            logger.info("章节信息已更新")
            self._update_status("章节内容已保存")

            # 通知其他组件章节变化
            if self.state_manager:
                self.state_manager.update_state({'chapters': chapter_data})

        except Exception as e:
            logger.error(f"处理章节变化失败: {e}")

    def _on_summary_changed(self, summary_content: str):
        """摘要变化回调"""
        try:
            logger.info("摘要内容已更新")
            self._update_status("摘要内容已保存")

            # 通知其他组件摘要变化
            if self.state_manager:
                self.state_manager.update_state({'summary': summary_content})

            # 添加保存动画效果
            if hasattr(self, 'summary_manager') and self.summary_manager:
                self.animation_manager.highlight(self.summary_manager, "#4CAF50", duration=400)

        except Exception as e:
            logger.error(f"处理摘要变化失败: {e}")

    def _on_character_state_changed(self, character_content: str):
        """角色状态变化回调"""
        try:
            logger.info("角色状态已更新")
            self._update_status("角色状态已保存")

            # 通知其他组件角色状态变化
            if self.state_manager:
                self.state_manager.update_state({'character_state': character_content})

            # 添加保存动画效果
            if hasattr(self, 'summary_manager') and self.summary_manager:
                self.animation_manager.highlight(self.summary_manager, "#2196F3", duration=400)

        except Exception as e:
            logger.error(f"处理角色状态变化失败: {e}")

    def _on_directory_chapter_selected(self, chapter: Dict[str, Any]):
        """目录章节选择回调"""
        try:
            logger.info(f"选择目录章节: {chapter.get('number', 'Unknown')} - {chapter.get('title', 'Unknown')}")

            # 更新状态栏
            self._update_status(f"当前章节: {chapter.get('title', 'Unknown')}")

            # 如果有主工作区，同步章节信息
            if hasattr(self, 'main_workspace') and self.main_workspace:
                chapter_num = chapter.get('number', 1)
                if hasattr(self.main_workspace, 'chapter_num_var'):
                    self.main_workspace.chapter_num_var.set(str(chapter_num))

        except Exception as e:
            logger.error(f"处理目录章节选择失败: {e}")

    def _on_directory_chapter_modified(self, chapter: Dict[str, Any]):
        """目录章节修改回调"""
        try:
            logger.info(f"目录章节已修改: {chapter.get('title', 'Unknown')}")

            # 更新状态栏
            self._update_status("章节目录已更新")

            # 添加保存动画效果
            if hasattr(self, 'directory_manager') and self.directory_manager:
                self.animation_manager.highlight(self.directory_manager, "#FF9800", duration=400)

        except Exception as e:
            logger.error(f"处理目录章节修改失败: {e}")

    def _create_new_novel(self):
        """新建小说项目"""
        try:
            logger.info("创建新小说项目")

            # 清空主工作区的内容
            if hasattr(self, 'main_workspace') and self.main_workspace:
                self.main_workspace.clear_log()
                self.main_workspace.set_chapter_content("")

                # 重置参数到默认值
                if hasattr(self.main_workspace, 'topic_text'):
                    self.main_workspace.topic_text.delete("0.0", "end")
                if hasattr(self.main_workspace, 'guidance_text'):
                    self.main_workspace.guidance_text.delete("0.0", "end")
                if hasattr(self.main_workspace, 'characters_text'):
                    self.main_workspace.characters_text.delete("0.0", "end")

                # 添加欢迎信息到日志
                self.main_workspace._log("🎉 新小说项目创建成功！")
                self.main_workspace._log("💡 请在右侧配置小说参数，然后点击生成按钮开始创作")

            # 切换到主页标签页
            if hasattr(self, 'main_content') and self.main_content:
                self.main_content.switch_to_tab("main")

            self._update_status("新项目创建成功")

        except Exception as e:
            logger.error(f"创建新小说失败: {e}")
            self._update_status("创建新项目失败")

    def _quick_load_last_project(self):
        """快速加载上次项目"""
        try:
            import os
            import json

            # 尝试从配置中获取上次项目路径
            last_project_path = None

            # 方法1: 从状态管理器获取
            if self.state_manager:
                last_project_path = self.state_manager.get_state('last_project_path')

            # 方法2: 从配置文件获取
            if not last_project_path:
                try:
                    config = load_config("config.json")
                    last_project_path = config.get('other_params', {}).get('last_project_path')
                except:
                    pass

            # 方法3: 检查当前工作目录中的项目文件
            if not last_project_path:
                current_dir = os.getcwd()
                potential_files = [
                    os.path.join(current_dir, "Novel_architecture.txt"),
                    os.path.join(current_dir, "Novel_directory.txt"),
                    os.path.join(current_dir, "global_summary.txt")
                ]
                if any(os.path.exists(f) for f in potential_files):
                    last_project_path = current_dir

            if last_project_path and os.path.exists(last_project_path):
                logger.info(f"快速加载项目: {last_project_path}")
                self._load_project_from_path(last_project_path)
                self._update_status("✅ 快速加载上次项目成功")
            else:
                self._update_status("❌ 没有找到上次的项目")
                logger.info("没有找到上次项目，打开项目选择器")
                self._open_project_chooser()

        except Exception as e:
            logger.error(f"快速加载项目失败: {e}")
            self._update_status(f"❌ 快速加载失败: {e}")

    def _open_project_chooser(self):
        """打开项目选择器（支持文件夹和JSON文件）"""
        try:
            import os
            from tkinter import filedialog
            from tkinter import messagebox

            # 创建选择对话框
            choice = messagebox.askyesnocancel(
                "选择项目加载方式",
                "选择加载方式：\n\n" +
                "【是】加载项目文件夹（推荐）\n" +
                "【否】加载JSON项目文件\n" +
                "【取消】不加载项目\n\n" +
                "文件夹方式支持直接加载包含小说文件的项目目录"
            )

            if choice is True:
                # 加载文件夹
                self._open_project_folder()
            elif choice is False:
                # 加载JSON文件
                self._open_project()
            else:
                # 取消
                self._update_status("用户取消了项目加载")

        except Exception as e:
            logger.error(f"打开项目选择器失败: {e}")
            self._update_status("❌ 项目选择器失败")

    def _open_project_folder(self):
        """打开项目文件夹选择"""
        try:
            from tkinter import filedialog
            import os

            # 选择项目文件夹
            folder_path = filedialog.askdirectory(
                title="选择项目文件夹"
            )

            if folder_path:
                # 检查项目文件并记录
                project_files = []
                expected_files = [
                    "Novel_architecture.txt",
                    "Novel_directory.txt",
                    "global_summary.txt",
                    "character_state.txt"
                ]


                found_files = []
                for file in project_files:
                    file_path = os.path.join(folder_path, file)
                    if os.path.exists(file_path):
                        found_files.append(file)

                if found_files:
                    logger.info(f"选择的项目文件夹包含文件: {found_files}")
                    self._load_project_from_path(folder_path)
                    self._update_status("✅ 项目文件夹加载成功")
                else:
                    self._update_status("❌ 选择的文件夹中没有找到项目文件")
                    logger.warning(f"文件夹中没有找到项目文件: {folder_path}")

        except Exception as e:
            logger.error(f"打开项目文件夹失败: {e}")
            self._update_status("❌ 打开项目文件夹失败")

    def _load_project_from_path(self, project_path: str):
        """从指定路径加载项目"""
        try:
            import os

            logger.info(f"开始加载项目: {project_path}")

            # 保存项目路径到配置和状态
            if self.state_manager:
                self.state_manager.set_state('last_project_path', project_path)

            # 更新配置文件中的项目路径
            try:
                config = load_config("config.json")
                if 'other_params' not in config:
                    config['other_params'] = {}
                config['other_params']['last_project_path'] = project_path
                config['other_params']['filepath'] = project_path

                from config_manager import save_config
                save_config(config, "config.json")
            except Exception as e:
                logger.warning(f"保存项目路径到配置失败: {e}")

            # 检查项目文件并记录
            project_files = []
            expected_files = [
                "Novel_setting.txt",
                "Novel_directory.txt",
                "global_summary.txt",
                "character_state.txt"
            ]

            for file in expected_files:
                file_path = os.path.join(project_path, file)
                if os.path.exists(file_path):
                    project_files.append(file)
                    logger.info(f"发现项目文件: {file}")

            if not project_files:
                self._update_status("⚠️ 项目文件夹为空，但已设置路径")
                logger.warning("项目文件夹中没有找到任何项目文件")
            else:
                self._update_status(f"✅ 发现项目文件: {len(project_files)}个")

                # 尝试从项目文件中读取参数并更新UI
                self._load_project_parameters_from_folder(project_path)

            # 延迟刷新各个组件的内容，确保文件已就绪
            self.after(500, self._refresh_all_components)
            self.after(1000, self._refresh_all_components)
            self.after(2000, self._refresh_all_components)

            logger.info(f"项目加载成功: {project_path}")

            # 更新侧边栏的最近项目列表
            if self.sidebar:
                self.sidebar.update_recent_projects(project_path)

        except Exception as e:
            logger.error(f"加载项目失败: {e}")
            self._update_status(f"❌ 加载项目失败: {e}")
            raise

    def _load_project_parameters_from_folder(self, folder_path: str):
        """从项目文件夹中读取参数并更新UI"""
        try:
            import os
            import re

            logger.info(f"开始从文件夹读取项目参数: {folder_path}")

            # 尝试从Novel_architecture.txt中读取参数
            novel_setting_path = os.path.join(folder_path, "Novel_architecture.txt")
            if os.path.exists(novel_setting_path):
                with open(novel_setting_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 解析参数
                params = {}

                # 使用正则表达式提取参数
                topic_match = re.search(r'主题[:：]\s*(.+?)(?=\n|$)', content, re.IGNORECASE)
                if topic_match:
                    params['topic'] = topic_match.group(1).strip()

                genre_match = re.search(r'类型[:：]\s*(.+?)(?=\n|$)', content, re.IGNORECASE)
                if genre_match:
                    params['genre'] = genre_match.group(1).strip()

                chapters_match = re.search(r'章节数[:：]\s*(\d+)', content, re.IGNORECASE)
                if chapters_match:
                    params['num_chapters'] = int(chapters_match.group(1))

                words_match = re.search(r'字数[:：]\s*(\d+)', content, re.IGNORECASE)
                if words_match:
                    params['word_number'] = int(words_match.group(1))

                # 更新main_workspace的UI
                if hasattr(self, 'main_workspace') and self.main_workspace and params:
                    logger.info(f"从项目文件中解析到参数: {params}")

                    if 'topic' in params and hasattr(self.main_workspace, 'topic_text'):
                        self.main_workspace.topic_text.delete("0.0", "end")
                        self.main_workspace.topic_text.insert("0.0", params['topic'])
                        logger.info(f"更新主题: {params['topic']}")

                    if 'genre' in params and hasattr(self.main_workspace, 'genre_var'):
                        self.main_workspace.genre_var.set(params['genre'])
                        logger.info(f"更新类型: {params['genre']}")

                    if 'num_chapters' in params and hasattr(self.main_workspace, 'num_chapters_var'):
                        self.main_workspace.num_chapters_var.set(str(params['num_chapters']))
                        logger.info(f"更新章节数: {params['num_chapters']}")

                    if 'word_number' in params and hasattr(self.main_workspace, 'word_number_var'):
                        self.main_workspace.word_number_var.set(str(params['word_number']))
                        logger.info(f"更新字数: {params['word_number']}")

                    if hasattr(self.main_workspace, 'filepath_var'):
                        self.main_workspace.filepath_var.set(folder_path)
                        logger.info(f"更新文件路径: {folder_path}")

                    self.main_workspace._log("📂 项目参数已从文件加载并更新到UI")
            else:
                logger.info("未找到Novel_setting.txt文件，尝试更新文件路径")
                # 至少更新文件路径
                if hasattr(self, 'main_workspace') and self.main_workspace:
                    if hasattr(self.main_workspace, 'filepath_var'):
                        self.main_workspace.filepath_var.set(folder_path)
                        self.main_workspace._log(f"📂 已设置项目路径: {folder_path}")

        except Exception as e:
            logger.error(f"从文件夹加载项目参数失败: {e}")

    def _refresh_all_components(self):
        """刷新所有组件的内容"""
        try:
            logger.info("开始刷新所有组件...")
            refreshed_count = 0

            # 获取当前项目路径
            current_project_path = self.state_manager.get_state('last_project_path', '') if self.state_manager else ''

            # 刷新主工作区
            if hasattr(self, 'main_workspace') and self.main_workspace:
                try:
                    # 更新保存路径
                    if current_project_path and hasattr(self.main_workspace, 'set_save_path'):
                        self.main_workspace.set_save_path(current_project_path)
                        logger.debug(f"主工作区路径更新为: {current_project_path}")

                    # 重新加载小说参数
                    self.main_workspace._initialize_parameters()
                    self.main_workspace._log("🔄 项目已加载，数据已刷新")
                    refreshed_count += 1
                    logger.debug("主工作区刷新成功")
                except Exception as e:
                    logger.error(f"主工作区刷新失败: {e}")

            # 刷新摘要管理器
            if hasattr(self, 'summary_manager') and self.summary_manager:
                try:
                    # 更新保存路径
                    if current_project_path and hasattr(self.summary_manager, 'set_save_path'):
                        self.summary_manager.set_save_path(current_project_path)
                        logger.debug(f"摘要管理器路径更新为: {current_project_path}")

                    self.summary_manager.load_all()
                    refreshed_count += 1
                    logger.debug("摘要管理器刷新成功")
                except Exception as e:
                    logger.error(f"摘要管理器刷新失败: {e}")

            # 刷新目录管理器
            if hasattr(self, 'directory_manager') and self.directory_manager:
                try:
                    # 更新保存路径
                    if current_project_path and hasattr(self.directory_manager, 'set_save_path'):
                        self.directory_manager.set_save_path(current_project_path)
                        logger.debug(f"目录管理器路径更新为: {current_project_path}")

                    self.directory_manager._load_chapters()
                    refreshed_count += 1
                    logger.debug("目录管理器刷新成功")
                except Exception as e:
                    logger.error(f"目录管理器刷新失败: {e}")

            # 刷新角色管理器
            if hasattr(self, 'characters_tab') and self.characters_tab:
                try:
                    # 更新保存路径
                    if current_project_path and hasattr(self.characters_tab, 'set_save_path'):
                        self.characters_tab.set_save_path(current_project_path)
                        logger.debug(f"角色管理器路径更新为: {current_project_path}")

                    if hasattr(self.characters_tab, 'refresh_characters'):
                        self.characters_tab.refresh_characters()
                        refreshed_count += 1
                        logger.debug("角色管理器刷新成功")
                except Exception as e:
                    logger.error(f"角色管理器刷新失败: {e}")

            # 刷新章节管理器
            if hasattr(self, 'chapters_tab') and self.chapters_tab:
                try:
                    # 更新保存路径
                    if current_project_path and hasattr(self.chapters_tab, 'set_save_path'):
                        self.chapters_tab.set_save_path(current_project_path)
                        logger.debug(f"章节管理器路径更新为: {current_project_path}")

                    if hasattr(self.chapters_tab, 'refresh_chapters'):
                        self.chapters_tab.refresh_chapters()
                        refreshed_count += 1
                        logger.debug("章节管理器刷新成功")
                except Exception as e:
                    logger.error(f"章节管理器刷新失败: {e}")

            # 刷新配置标签页
            if hasattr(self, 'config_tab') and self.config_tab:
                try:
                    self.config_tab._load_current_config()
                    refreshed_count += 1
                    logger.debug("配置标签页刷新成功")
                except Exception as e:
                    logger.error(f"配置标签页刷新失败: {e}")

            # 刷新设定标签页
            if hasattr(self, 'setting_tab') and self.setting_tab:
                try:
                    # 更新保存路径
                    if current_project_path and hasattr(self.setting_tab, 'set_save_path'):
                        self.setting_tab.set_save_path(current_project_path)
                        logger.debug(f"设定标签页路径更新为: {current_project_path}")

                    self.setting_tab.refresh_content()
                    refreshed_count += 1
                    logger.debug("设定标签页刷新成功")
                except Exception as e:
                    logger.error(f"设定标签页刷新失败: {e}")

            # 更新状态栏信息
            if self.state_manager:
                project_path = self.state_manager.get_state('last_project_path', '')
                if project_path:
                    self._update_status(f"✅ 项目已加载: {os.path.basename(project_path)} - {refreshed_count}个组件已更新")

            logger.info(f"组件刷新完成 - 共刷新 {refreshed_count} 个组件")

        except Exception as e:
            logger.error(f"刷新组件失败: {e}")
            self._update_status("⚠️ 部分组件刷新失败")

    def _open_project(self):
        """打开项目"""
        try:
            from tkinter import filedialog
            import os
            from tkinter import messagebox

            # 选择加载方式
            choice = messagebox.askyesnocancel(
                "选择项目加载方式",
                "选择加载方式：\n\n" +
                "【是】加载项目文件夹（推荐）\n" +
                "【否】加载JSON项目文件\n" +
                "【取消】取消操作\n\n" +
                "文件夹方式支持直接加载包含小说文件的目录"
            )

            if choice is True:
                # 加载文件夹
                self._open_project_folder()
            elif choice is False:
                # 加载JSON文件
                project_file = filedialog.askopenfilename(
                    title="选择项目文件",
                    filetypes=[("项目文件", "*.json"), ("所有文件", "*.*")]
                )

                if project_file and os.path.exists(project_file):
                    logger.info(f"打开项目文件: {project_file}")

                    # 读取项目配置
                    with open(project_file, 'r', encoding='utf-8') as f:
                        project_data = json.load(f)

                    # 加载项目数据到主工作区
                    if hasattr(self, 'main_workspace') and self.main_workspace:
                        # 加载参数
                        if 'parameters' in project_data:
                            params = project_data['parameters']
                            if hasattr(self.main_workspace, 'topic_text') and params.get('topic'):
                                self.main_workspace.topic_text.delete("0.0", "end")
                                self.main_workspace.topic_text.insert("0.0", params['topic'])

                        if hasattr(self.main_workspace, 'genre_var') and params.get('genre'):
                            self.main_workspace.genre_var.set(params['genre'])

                        if hasattr(self.main_workspace, 'num_chapters_var') and params.get('num_chapters'):
                            self.main_workspace.num_chapters_var.set(str(params['num_chapters']))

                        if hasattr(self.main_workspace, 'word_number_var') and params.get('word_number'):
                            self.main_workspace.word_number_var.set(str(params['word_number']))

                    # 加载章节内容
                    if 'chapters' in project_data and project_data['chapters']:
                        first_chapter = project_data['chapters'][0]
                        if hasattr(self.main_workspace, 'chapter_editor') and first_chapter.get('content'):
                            self.main_workspace.set_chapter_content(first_chapter['content'])

                    self.main_workspace._log(f"📂 项目加载成功: {os.path.basename(project_file)}")

                    # 更新侧边栏的最近项目列表
                    if self.sidebar:
                        self.sidebar.update_recent_projects(project_file)

                self._update_status(f"项目加载成功: {os.path.basename(project_file)}")
            else:
                logger.info("用户取消了项目打开")

        except Exception as e:
            logger.error(f"打开项目失败: {e}")
            self._update_status("打开项目失败")

    def _save_project(self):
        """保存项目"""
        try:
            from tkinter import filedialog
            import os
            import json
            from datetime import datetime

            if not hasattr(self, 'main_workspace') or not self.main_workspace:
                logger.warning("主工作区未初始化")
                return

            # 获取项目数据
            project_data = {
                'created_at': datetime.now().isoformat(),
                'version': '2.0',
                'parameters': self.main_workspace.get_novel_parameters(),
                'chapters': []
            }

            # 获取当前章节内容
            chapter_content = self.main_workspace.get_chapter_content()
            if chapter_content:
                project_data['chapters'].append({
                    'number': int(self.main_workspace.chapter_num_var.get()) if hasattr(self.main_workspace, 'chapter_num_var') else 1,
                    'content': chapter_content,
                    'word_count': len(chapter_content)
                })

            # 选择保存位置
            save_path = filedialog.asksaveasfilename(
                title="保存项目",
                defaultextension=".json",
                filetypes=[("项目文件", "*.json"), ("所有文件", "*.*")]
            )

            if save_path:
                # 保存项目数据
                with open(save_path, 'w', encoding='utf-8') as f:
                    json.dump(project_data, f, ensure_ascii=False, indent=2)

                logger.info(f"项目保存成功: {save_path}")
                self.main_workspace._log(f"💾 项目保存成功: {os.path.basename(save_path)}")
                self._update_status(f"项目保存成功")
            else:
                logger.info("用户取消了项目保存")

        except Exception as e:
            logger.error(f"保存项目失败: {e}")
            self._update_status("保存项目失败")

    def _export_project(self):
        """导出项目"""
        try:
            if not hasattr(self, 'main_workspace') or not self.main_workspace:
                logger.warning("主工作区未初始化")
                return

            chapter_content = self.main_workspace.get_chapter_content()
            if not chapter_content:
                logger.warning("没有内容可导出")
                self._update_status("没有内容可导出")
                return

            from tkinter import filedialog
            import os

            # 选择导出位置
            export_path = filedialog.asksaveasfilename(
                title="导出章节",
                defaultextension=".txt",
                filetypes=[("文本文件", "*.txt"), ("Markdown文件", "*.md"), ("所有文件", "*.*")]
            )

            if export_path:
                # 导出内容
                with open(export_path, 'w', encoding='utf-8') as f:
                    f.write(chapter_content)

                logger.info(f"内容导出成功: {export_path}")
                self.main_workspace._log(f"📤 内容导出成功: {os.path.basename(export_path)}")
                self._update_status("导出成功")
            else:
                logger.info("用户取消了导出")

        except Exception as e:
            logger.error(f"导出项目失败: {e}")
            self._update_status("导出失败")

    def _on_step_changed(self, step_id: str):
        """步骤变化回调"""
        try:
            logger.info(f"当前步骤: {step_id}")

            step_names = {
                "step1": "生成架构",
                "step2": "生成目录",
                "step3": "生成草稿",
                "step4": "完善章节",
                "batch": "批量生成"
            }

            step_name = step_names.get(step_id, step_id)
            self._update_status(f"当前步骤: {step_name}")

            # 添加步骤切换动画
            if hasattr(self, 'main_workspace') and self.main_workspace:
                self.animation_manager.pulse(self.main_workspace, duration=300)

        except Exception as e:
            logger.error(f"处理步骤变化失败: {e}")

    def _on_performance_warning(self, metric_name: str, value: float):
        """性能警告回调"""
        try:
            logger.warning(f"性能警告: {metric_name} = {value}")

            # 更新状态栏显示性能警告
            if hasattr(self, 'status_label'):
                self.status_label.configure(
                    text=f"⚠️ 性能警告: {metric_name} | 主题: {self.state_manager.get_state('app.theme', 'dark')}"
                )

            # 根据警告类型采取不同措施
            if "memory" in metric_name.lower():
                # 内存警告：自动清理
                self.performance_monitor.optimize_memory()
            elif "render" in metric_name.lower():
                # 渲染警告：优化UI组件
                self.performance_monitor.optimize_ui_components()

        except Exception as e:
            logger.error(f"处理性能警告失败: {e}")

    def get_performance_info(self) -> Dict[str, Any]:
        """获取性能信息"""
        try:
            if hasattr(self, 'performance_monitor'):
                return {
                    'summary': self.performance_monitor.get_performance_summary(),
                    'suggestions': self.performance_monitor.get_optimization_suggestions(),
                    'report': self.performance_monitor.get_performance_report()
                }
            return {}
        except Exception as e:
            logger.error(f"获取性能信息失败: {e}")
            return {}

    def optimize_performance(self):
        """优化性能"""
        try:
            if hasattr(self, 'performance_monitor'):
                # 内存优化
                memory_freed = self.performance_monitor.optimize_memory()

                # UI组件优化
                ui_optimized = self.performance_monitor.optimize_ui_components()

                logger.info(f"性能优化完成: 内存清理 {memory_freed} 个对象, UI优化 {ui_optimized} 个组件")
                self._update_status(f"性能优化完成: 清理内存 {memory_freed} 项")

        except Exception as e:
            logger.error(f"性能优化失败: {e}")