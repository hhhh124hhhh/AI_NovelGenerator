"""
主内容区域组件 - AI小说生成器的核心内容显示区域
包含标签页系统和内容管理功能
"""

import logging
from typing import Dict, Any, Optional, List, Callable
import customtkinter as ctk

logger = logging.getLogger(__name__)


class MainContentArea(ctk.CTkFrame):
    """
    主内容区域组件

    功能：
    - 标签页容器
    - 内容显示管理
    - 响应式布局支持
    - 状态栏集成
    - 内容切换动画
    """

    def __init__(self, parent: ctk.CTk, theme_manager, state_manager=None, **kwargs):
        """
        初始化主内容区域

        Args:
            parent: 父组件
            theme_manager: 主题管理器
            state_manager: 状态管理器
            **kwargs: 其他参数
        """
        # 初始化CustomTkinter Frame
        super().__init__(parent, **kwargs)

        # 存储管理器引用
        self.theme_manager = theme_manager
        self.state_manager = state_manager

        # 标签页相关
        self.tab_view = None
        self.tabs = {}
        self.current_tab = None

        # 内容管理
        self.content_frames = {}
        self.tab_callbacks = {}

        # 响应式状态
        self.current_width = 800
        self.current_height = 600

        # 初始化组件
        self._create_main_content_layout()
        self._create_tab_view()

        logger.debug("MainContentArea 组件初始化完成")

    def _create_main_content_layout(self):
        """创建主内容布局"""
        # 配置主框架
        self.configure(
            corner_radius=8,
            fg_color="transparent"
        )

        # 配置网格布局
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def _create_tab_view(self):
        """创建标签页视图"""
        # 标签页容器
        self.tab_view = ctk.CTkTabview(
            self,
            segmented_button_fg_color="#2A2A2A",
            segmented_button_selected_color="#404040",
            segmented_button_unselected_color="#1E1E1E"
        )
        self.tab_view.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # 禁用标签页导航 - 用户通过左侧导航栏进行切换
        try:
            if hasattr(self.tab_view, '_segmented_button'):
                # 隐藏分段按钮
                self.tab_view._segmented_button.pack_forget()
                logger.info("标签页导航已禁用，使用左侧导航栏")

            # 或者设置标签页为不可交互状态
            if hasattr(self.tab_view, 'configure'):
                # 让标签页看起来只是装饰性的
                logger.debug("标签页样式已配置为非交互式")

        except Exception as e:
            logger.warning(f"禁用标签页导航失败: {e}")

        # 注意：不再绑定标签页切换事件，因为用户通过左侧导航栏切换

    def _bind_tab_events(self):
        """绑定标签页事件"""
        try:
            if self.tab_view:
                # 方法1: 尝试绑定到分段按钮
                if hasattr(self.tab_view, '_segmented_button'):
                    self.tab_view._segmented_button.configure(
                        command=self._on_tab_changed
                    )
                    logger.info("标签页切换事件绑定成功（分段按钮方式）")
                    return

                # 方法2: 尝试直接绑定到tab_view
                elif hasattr(self.tab_view, 'configure'):
                    # CustomTkinter TabView的内置事件绑定
                    def tab_changed(*args):
                        try:
                            current_tab = self.tab_view.get()
                            logger.info(f"检测到标签页变化: {current_tab}")
                            self._on_tab_changed(current_tab)
                        except Exception as e:
                            logger.error(f"处理标签页变化失败: {e}")

                    # 重写tab选择变化的方法
                    original_set = self.tab_view.set

                    def new_set(value):
                        result = original_set(value)
                        tab_changed(value)
                        return result

                    self.tab_view.set = new_set
                    logger.info("标签页切换事件绑定成功（重写set方法）")
                    return

                # 方法3: 使用轮询检查标签页变化
                else:
                    self._start_tab_polling()
                    logger.info("标签页切换事件绑定成功（轮询方式）")
                    return
            else:
                logger.warning("标签页视图未初始化")

        except Exception as e:
            logger.error(f"绑定标签页事件失败: {e}")
            # 安排重试
            self.after(500, self._bind_tab_events)

    def _start_tab_polling(self):
        """开始轮询检查标签页变化"""
        try:
            if not hasattr(self, '_last_tab'):
                self._last_tab = None

            def check_tab_change():
                try:
                    if self.tab_view:
                        current_tab = self.tab_view.get()
                        if current_tab != self._last_tab:
                            self._last_tab = current_tab
                            logger.info(f"检测到标签页变化（轮询）: {current_tab}")
                            self._on_tab_changed(current_tab)

                    # 继续轮询
                    if hasattr(self, '_tab_polling_active') and self._tab_polling_active:
                        self.after(200, check_tab_change)

                except Exception as e:
                    logger.error(f"轮询检查标签页变化失败: {e}")

            self._tab_polling_active = True
            self.after(100, check_tab_change)

        except Exception as e:
            logger.error(f"启动标签页轮询失败: {e}")

    def _bind_click_events(self):
        """绑定点击事件作为备用方案"""
        try:
            if self.tab_view and hasattr(self.tab_view, '_segmented_button'):
                # 获取分段按钮的所有子组件
                segmented_button = self.tab_view._segmented_button

                # 遍历所有标签按钮并绑定点击事件
                for i, tab_name in enumerate(self.tabs.keys()):
                    try:
                        # 尝试获取对应的按钮组件
                        if hasattr(segmented_button, '_buttons') and i < len(segmented_button._buttons):
                            button = segmented_button._buttons[i]

                            def on_click(event, tab=tab_name):
                                logger.info(f"点击了标签页: {tab}")
                                # 切换到对应的标签页
                                self.tab_view.set(self.tabs[tab]['title'])
                                self._on_tab_changed(self.tabs[tab]['title'])

                            button.bind("<Button-1>", on_click)
                            logger.info(f"为标签页 {tab_name} 绑定了点击事件")

                    except Exception as button_error:
                        logger.warning(f"为标签页 {tab_name} 绑定点击事件失败: {button_error}")

        except Exception as e:
            logger.warning(f"绑定点击事件失败: {e}")

    def _bind_click_events_for_tab(self, tab_name: str):
        """为特定标签页绑定点击事件"""
        try:
            if not (self.tab_view and hasattr(self.tab_view, '_segmented_button')):
                return

            segmented_button = self.tab_view._segmented_button

            # 找到对应标签页的索引
            tab_names = list(self.tabs.keys())
            if tab_name in tab_names:
                tab_index = tab_names.index(tab_name)

                # 尝试获取对应的按钮组件
                if hasattr(segmented_button, '_buttons') and tab_index < len(segmented_button._buttons):
                    button = segmented_button._buttons[tab_index]

                    def on_click(event, tab=tab_name):
                        logger.info(f"点击了标签页: {tab}")
                        # 切换到对应的标签页
                        try:
                            self.tab_view.set(self.tabs[tab]['title'])
                            self._on_tab_changed(self.tabs[tab]['title'])
                        except Exception as set_error:
                            logger.error(f"切换标签页失败: {set_error}")

                    # 移除旧的绑定（如果有）
                    button.unbind("<Button-1>")
                    # 绑定新的事件
                    button.bind("<Button-1>", on_click)
                    logger.info(f"为标签页 {tab_name} 重新绑定了点击事件")

        except Exception as e:
            logger.warning(f"为标签页 {tab_name} 绑定点击事件失败: {e}")

    def _on_tab_changed(self, selected_value=None):
        """标签页切换事件处理"""
        try:
            if not self.tab_view:
                logger.warning("标签页视图未初始化")
                return

            # 获取当前选中的标签页标题
            if selected_value:
                current_title = selected_value
            else:
                current_title = self.tab_view.get()

            logger.info(f"标签页切换事件触发，当前标题: {current_title}")

            # 查找对应的标签页名称
            for tab_name, tab_info in self.tabs.items():
                if tab_info['title'] == current_title:
                    self.current_tab = tab_name
                    logger.info(f"找到匹配标签页: {tab_name}")

                    # 确保内容框架可见
                    if 'padding_frame' in tab_info and tab_info['padding_frame']:
                        try:
                            # 确保内容框架被提升到顶部
                            tab_info['padding_frame'].lift()
                            logger.debug(f"提升内容框架: {tab_name}")
                        except Exception as lift_error:
                            logger.warning(f"提升内容框架失败: {lift_error}")

                    # 调用回调
                    if tab_info['callback']:
                        try:
                            tab_info['callback'](tab_name)
                            logger.info(f"标签页回调执行成功: {tab_name}")
                        except Exception as callback_error:
                            logger.error(f"标签页回调执行失败 {tab_name}: {callback_error}")
                    else:
                        logger.warning(f"标签页 {tab_name} 没有设置回调函数")

                    # 更新状态
                    if self.state_manager:
                        try:
                            self.state_manager.set_state('app.active_tab', tab_name)
                            logger.debug(f"状态更新成功: {tab_name}")
                        except Exception as state_error:
                            logger.warning(f"状态更新失败: {state_error}")

                    logger.info(f"标签页切换完成: {tab_name}")
                    return
            else:
                logger.warning(f"未找到匹配的标签页: {current_title}")
                # 尝试直接使用selected_value作为tab_name
                if selected_value and selected_value in self.tabs:
                    self.current_tab = selected_value
                    logger.info(f"直接使用标签页名称: {selected_value}")
                elif selected_value:
                    logger.warning(f"未知标签页名称: {selected_value}")

        except Exception as e:
            logger.error(f"处理标签页切换事件失败: {e}")
            import traceback
            logger.error(f"详细错误: {traceback.format_exc()}")

    def add_tab(self, tab_name: str, tab_title: Optional[str] = None, callback: Optional[Callable] = None):
        """
        添加标签页

        Args:
            tab_name: 标签页名称（内部标识）
            tab_title: 标签页显示标题
            callback: 标签页切换回调
        """
        try:
            if tab_title is None:
                tab_title = tab_name

            # 创建标签页
            if self.tab_view is None:
                raise RuntimeError("标签页视图未初始化")
            tab = self.tab_view.add(tab_title)

            # 创建内容框架
            content_frame = ctk.CTkFrame(tab, fg_color="transparent")
            content_frame.pack(fill="both", expand=True)

            # 使用内嵌框架来实现内边距
            padding_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            padding_frame.pack(fill="both", expand=True, padx=10, pady=10)

            # 存储标签页信息
            self.tabs[tab_name] = {
                'name': tab_name,
                'title': tab_title,
                'tab': tab,
                'content_frame': content_frame,
                'callback': callback,
                'padding_frame': padding_frame
            }

            self.content_frames[tab_name] = padding_frame
            self.tab_callbacks[tab_name] = callback

            logger.info(f"添加标签页: {tab_name} ({tab_title})")

            # 重新绑定点击事件（针对新添加的标签页）
            self.after(300, lambda: self._bind_click_events_for_tab(tab_name))

        except Exception as e:
            logger.error(f"添加标签页失败 {tab_name}: {e}")

    def get_tab_content_frame(self, tab_name: str) -> Optional[ctk.CTkFrame]:
        """
        获取标签页内容框架

        Args:
            tab_name: 标签页名称

        Returns:
            标签页内容框架或None
        """
        return self.content_frames.get(tab_name)

    def switch_to_tab(self, tab_name: str):
        """
        切换到指定标签页

        Args:
            tab_name: 标签页名称
        """
        try:
            if tab_name in self.tabs:
                tab_info = self.tabs[tab_name]
                if self.tab_view is None:
                    raise RuntimeError("标签页视图未初始化")
                self.tab_view.set(tab_info['title'])

                # 调用回调
                if tab_info['callback']:
                    tab_info['callback'](tab_name)

                logger.info(f"切换到标签页: {tab_name}")
            else:
                logger.warning(f"标签页不存在: {tab_name}")

        except Exception as e:
            logger.error(f"切换标签页失败 {tab_name}: {e}")

    def set_active_tab(self, tab_name: str):
        """设置活动标签页"""
        self.switch_to_tab(tab_name)

    def get_current_tab(self) -> Optional[str]:
        """获取当前活动标签页"""
        try:
            if self.tab_view:
                current_title = self.tab_view.get()
                # 查找对应的标签页名称
                for tab_name, tab_info in self.tabs.items():
                    if tab_info['title'] == current_title:
                        return tab_name
        except Exception as e:
            logger.error(f"获取当前标签页失败: {e}")
        return None

    def remove_tab(self, tab_name: str):
        """
        移除标签页

        Args:
            tab_name: 标签页名称
        """
        try:
            if tab_name in self.tabs:
                tab_info = self.tabs[tab_name]
                if self.tab_view is None:
                    raise RuntimeError("标签页视图未初始化")
                self.tab_view.delete(tab_info['title'])

                # 清理内容框架
                if tab_name in self.content_frames:
                    del self.content_frames[tab_name]
                if tab_name in self.tab_callbacks:
                    del self.tab_callbacks[tab_name]

                del self.tabs[tab_name]

                logger.info(f"移除标签页: {tab_name}")
            else:
                logger.warning(f"标签页不存在: {tab_name}")

        except Exception as e:
            logger.error(f"移除标签页失败 {tab_name}: {e}")

    def get_all_tabs(self) -> List[str]:
        """获取所有标签页名称"""
        return list(self.tabs.keys())

    def tab_exists(self, tab_name: str) -> bool:
        """检查标签页是否存在"""
        return tab_name in self.tabs

    def update_layout_for_size(self, width: int, height: int):
        """
        根据窗口大小更新布局

        Args:
            width: 窗口宽度
            height: 窗口高度
        """
        try:
            self.current_width = width
            self.current_height = height

            # 响应式布局调整
            if width < 800:
                self._apply_compact_layout()
            elif width < 1200:
                self._apply_standard_layout()
            else:
                self._apply_wide_layout()

        except Exception as e:
            logger.error(f"更新主内容布局失败: {e}")

    def _apply_compact_layout(self):
        """应用紧凑布局"""
        try:
            if self.tab_view:
                # 减小内边距 - 通过更新padding_frame的pack配置
                for tab_name, tab_info in self.tabs.items():
                    if 'padding_frame' in tab_info:
                        padding_frame = tab_info['padding_frame']
                        if padding_frame and hasattr(padding_frame, 'pack'):
                            # 重新配置pack参数以减小内边距
                            padding_frame.pack_forget()
                            padding_frame.pack(fill="both", expand=True, padx=5, pady=5)

        except Exception as e:
            logger.error(f"应用紧凑布局失败: {e}")

    def _apply_standard_layout(self):
        """应用标准布局"""
        try:
            if self.tab_view:
                # 标准内边距 - 通过更新padding_frame的pack配置
                for tab_name, tab_info in self.tabs.items():
                    if 'padding_frame' in tab_info:
                        padding_frame = tab_info['padding_frame']
                        if padding_frame and hasattr(padding_frame, 'pack'):
                            # 重新配置pack参数以设置标准内边距
                            padding_frame.pack_forget()
                            padding_frame.pack(fill="both", expand=True, padx=10, pady=10)

        except Exception as e:
            logger.error(f"应用标准布局失败: {e}")

    def _apply_wide_layout(self):
        """应用宽屏布局"""
        try:
            if self.tab_view:
                # 增大内边距 - 通过更新padding_frame的pack配置
                for tab_name, tab_info in self.tabs.items():
                    if 'padding_frame' in tab_info:
                        padding_frame = tab_info['padding_frame']
                        if padding_frame and hasattr(padding_frame, 'pack'):
                            # 重新配置pack参数以增大内边距
                            padding_frame.pack_forget()
                            padding_frame.pack(fill="both", expand=True, padx=15, pady=15)

        except Exception as e:
            logger.error(f"应用宽屏布局失败: {e}")

    def apply_theme_style(self, theme_data: Dict[str, Any]):
        """应用主题样式"""
        try:
            colors = theme_data.get('colors', {})

            # 更新标签页样式
            if self.tab_view:
                self.tab_view.configure(
                    segmented_button_fg_color=colors.get('surface', '#2A2A2A'),
                    segmented_button_selected_color=colors.get('primary', '#404040'),
                    segmented_button_unselected_color=colors.get('background', '#1E1E1E')
                )

        except Exception as e:
            logger.error(f"应用主题到主内容区域失败: {e}")

    def set_tab_callback(self, tab_name: str, callback: Callable[[str], None]):
        """
        设置标签页回调函数

        Args:
            tab_name: 标签页名称
            callback: 回调函数
        """
        if tab_name in self.tab_callbacks:
            self.tab_callbacks[tab_name] = callback

        if tab_name in self.tabs:
            self.tabs[tab_name]['callback'] = callback

    def show_loading_indicator(self, tab_name: Optional[str] = None, message: str = "加载中..."):
        """
        显示加载指示器

        Args:
            tab_name: 标签页名称，None表示当前标签页
            message: 加载消息
        """
        try:
            if tab_name is None:
                tab_name = self.get_current_tab()

            if tab_name and tab_name in self.content_frames:
                content_frame = self.content_frames[tab_name]

                # 清除现有内容
                for widget in content_frame.winfo_children():
                    widget.destroy()

                # 创建加载指示器
                loading_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
                loading_frame.pack(expand=True, fill="both")

                progress_bar = ctk.CTkProgressBar(loading_frame)
                progress_bar.pack(pady=20)
                progress_bar.start()

                loading_label = ctk.CTkLabel(
                    loading_frame,
                    text=message,
                    font=ctk.CTkFont(size=14)
                )
                loading_label.pack(pady=10)

        except Exception as e:
            logger.error(f"显示加载指示器失败: {e}")

    def hide_loading_indicator(self, tab_name: Optional[str] = None):
        """
        隐藏加载指示器

        Args:
            tab_name: 标签页名称，None表示当前标签页
        """
        try:
            if tab_name is None:
                tab_name = self.get_current_tab()

            if tab_name and tab_name in self.content_frames:
                content_frame = self.content_frames[tab_name]

                # 清除加载指示器
                for widget in content_frame.winfo_children():
                    widget.destroy()

        except Exception as e:
            logger.error(f"隐藏加载指示器失败: {e}")

    def clear_tab_content(self, tab_name: Optional[str] = None):
        """
        清空标签页内容

        Args:
            tab_name: 标签页名称，None表示当前标签页
        """
        try:
            if tab_name is None:
                tab_name = self.get_current_tab()

            if tab_name and tab_name in self.content_frames:
                content_frame = self.content_frames[tab_name]

                # 清除所有内容
                for widget in content_frame.winfo_children():
                    widget.destroy()

        except Exception as e:
            logger.error(f"清空标签页内容失败: {e}")

    def get_content_info(self) -> Dict[str, Any]:
        """获取主内容区域信息"""
        return {
            'current_tab': self.get_current_tab(),
            'total_tabs': len(self.tabs),
            'tab_names': list(self.tabs.keys()),
            'current_width': self.current_width,
            'current_height': self.current_height,
            'has_tab_view': self.tab_view is not None
        }