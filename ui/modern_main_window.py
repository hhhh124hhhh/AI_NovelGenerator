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

# 导入UI组件
from .components.title_bar import TitleBar
from .components.sidebar import Sidebar
from .components.main_content import MainContentArea

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
        self.theme_manager: ThemeManager = theme_manager or ThemeManager()
        self.state_manager: StateManager = StateManager()
        self.layout_manager: ResponsiveLayoutManager = ResponsiveLayoutManager()

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
            # 标题栏
            from .components.title_bar import TitleBar
            self.title_bar = TitleBar(self, self.theme_manager, self.state_manager)
            self.title_bar.pack(fill="x", padx=5, pady=(5, 0))

            # 主要内容容器
            self.main_container = ctk.CTkFrame(self, fg_color="transparent")
            self.main_container.pack(fill="both", expand=True, padx=5, pady=5)

            # 配置主容器网格布局
            self.main_container.grid_columnconfigure(1, weight=1)
            self.main_container.grid_rowconfigure(0, weight=1)

            # 侧边栏
            from .components.sidebar import Sidebar
            self.sidebar = Sidebar(self.main_container, self.theme_manager, self.state_manager)
            self.sidebar.grid(row=0, column=0, sticky="ns", padx=(0, 5))

            # 主内容区域
            from .components.main_content import MainContentArea
            self.main_content = MainContentArea(
                self,  # 使用主窗口作为父级而不是main_container
                self.theme_manager,
                self.state_manager
            )
            self.main_content.pack(fill="both", expand=True, padx=5, pady=5)

            # 添加默认标签页
            self._setup_default_tabs()

            # 临时内容标签（用于初始显示）
            config_frame = self.main_content.get_tab_content_frame("config")
            if config_frame:
                self.temp_label = ctk.CTkLabel(
                    config_frame,
                    text="AI小说生成器 v2.0\n\nBUILD阶段 Day 3 - 任务3.1进行中\n\n📋 已完成:\n✅ 现代化标题栏\n✅ 侧边栏导航\n✅ 主内容区域\n✅ 标签页系统\n\n🚧 下一步:\n内容迁移和功能集成",
                    font=ctk.CTkFont(size=16, weight="bold"),
                    justify="center"
                )
                self.temp_label.pack(expand=True, fill="both", padx=20, pady=20)

            # 状态栏 (简单版本)
            self.status_bar = ctk.CTkFrame(self, height=30, corner_radius=0)
            self.status_bar.pack(fill="x", side="bottom", padx=5, pady=(0, 5))

            self.status_label = ctk.CTkLabel(
                self.status_bar,
                text="就绪 | 主题: 深色模式 | 布局: 桌面版",
                font=ctk.CTkFont(size=11),
                anchor="w"
            )
            self.status_label.pack(side="left", padx=10, pady=5)

            # 设置组件回调
            self._setup_component_callbacks()

            self._window_state['components_created'] = True
            logger.info("窗口组件创建完成")

        except Exception as e:
            logger.error(f"创建窗口组件失败: {e}")
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
                ("config", "配置"),
                ("generate", "生成"),
                ("characters", "角色"),
                ("chapters", "章节"),
                ("summary", "摘要"),
                ("directory", "目录")
            ]

            for tab_name, tab_title in default_tabs:
                self.main_content.add_tab(tab_name, tab_title, self._on_tab_callback)

            # 初始化配置和生成标签页
            self._setup_config_tab()
            self._setup_generate_tab()
            self._setup_characters_tab()
            self._setup_chapters_tab()

            # 设置默认活动标签页
            current_active = self.state_manager.get_state('app.active_tab', 'config')
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
                    self.state_manager
                )
                self.config_tab.pack(fill="both", expand=True)

                # 设置配置变化回调
                self.config_tab.set_config_changed_callback(self._on_config_changed)

                logger.info("配置标签页初始化完成")

        except Exception as e:
            logger.error(f"设置配置标签页失败: {e}")

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

    def _on_tab_callback(self, tab_name: str):
        """标签页切换回调"""
        try:
            logger.info(f"标签页切换到: {tab_name}")

            # 对于已有实际内容的标签页，不需要更新临时标签页
            # config、generate、characters、chapters标签页现在有实际内容
            if tab_name in ["config", "generate", "characters", "chapters"]:
                return

            # 更新其他标签页的临时内容
            if hasattr(self, 'temp_label') and self.temp_label:
                tab_titles = {
                    "summary": "摘要",
                    "directory": "目录"
                }

                if tab_name in tab_titles:
                    tab_title = tab_titles[tab_name]
                    self.temp_label.configure(
                        text=f"AI小说生成器 v2.0\n\n当前页面: {tab_title}\n\n功能正在开发中...\n\n📋 已完成:\n✅ 现代化标题栏\n✅ 侧边栏导航\n✅ 主内容区域\n✅ 标签页系统\n✅ 配置管理\n✅ 生成功能\n✅ 角色管理\n✅ 章节管理\n\n🚧 下一步:\n{tab_title}功能集成"
                    )

        except Exception as e:
            logger.error(f"标签页回调处理失败: {e}")

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
        self._update_status(f"搜索: {search_text}")

    def _on_settings(self):
        """设置回调"""
        logger.info("打开设置")
        self._update_status("打开设置面板")

    def _on_user_menu(self):
        """用户菜单回调"""
        logger.info("打开用户菜单")
        self._update_status("打开用户菜单")

    def _on_navigation(self, target: str, name: str):
        """导航回调"""
        logger.info(f"导航到: {target} ({name})")

        # 切换到对应的标签页
        if hasattr(self, 'main_content') and self.main_content:
            self.main_content.switch_to_tab(target)

        self._update_status(f"当前页面: {name}")

    def _on_quick_action(self, action: str):
        """快速操作回调"""
        logger.info(f"快速操作: {action}")
        action_names = {
            "new_novel": "新建小说",
            "open_project": "打开项目",
            "save": "保存",
            "export": "导出"
        }
        action_name = action_names.get(action, action)
        self._update_status(f"执行: {action_name}")

    def _on_project_select(self, project_name: str):
        """项目选择回调"""
        logger.info(f"选择项目: {project_name}")
        self._update_status(f"当前项目: {project_name}")

    def _update_status(self, message: str):
        """更新状态栏"""
        try:
            if hasattr(self, 'status_label'):
                current_theme = self.state_manager.get_state('app.theme', 'dark')
                layout_type = self.layout_manager.get_current_layout_type().value
                self.status_label.configure(
                    text=f"{message} | 主题: {current_theme} | 布局: {layout_type}"
                )
        except Exception as e:
            logger.error(f"更新状态栏失败: {e}")