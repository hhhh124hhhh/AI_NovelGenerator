"""
现代化侧边栏组件 - AI小说生成器的导航和快速操作区域
包含快速操作、项目列表和导航菜单
"""

import logging
from typing import Dict, Any, Optional, Callable, List
import customtkinter as ctk
from .base_components import StyledComponent

logger = logging.getLogger(__name__)


class Sidebar(ctk.CTkFrame):
    """
    现代化侧边栏组件

    功能：
    - 快速操作按钮
    - 项目/文件列表
    - 导航菜单
    - 响应式折叠
    - 拖拽调整宽度
    """

    def __init__(self, parent: ctk.CTkFrame, theme_manager, state_manager=None, main_window=None, **kwargs):
        """
        初始化侧边栏

        Args:
            parent: 父组件
            theme_manager: 主题管理器
            state_manager: 状态管理器
            main_window: 主窗口引用
            **kwargs: 其他参数
        """
        # 初始化CustomTkinter Frame
        super().__init__(parent, **kwargs)

        # 存储管理器引用
        self.theme_manager = theme_manager
        self.state_manager = state_manager
        self.main_window = main_window

        # 回调函数
        self.navigation_callback = None
        self.quick_action_callback = None
        self.project_select_callback = None

        # 组件引用
        self.quick_actions_frame = None
        self.navigation_frame = None
        self.projects_frame = None
        self.collapse_button = None

        # 状态
        self.is_collapsed = False
        self.current_width = 280
        self.min_width = 200
        self.max_width = 400

        # 导航项目
        self.nav_items = []
        self.quick_actions = []
        self.projects = []

        # 初始化组件
        self._create_sidebar_layout()
        self._create_collapse_button()
        self._create_quick_actions_section()
        self._create_navigation_section()
        self._create_projects_section()
        self._bind_custom_events()

        logger.debug("Sidebar 组件初始化完成")

    def _create_sidebar_layout(self):
        """创建侧边栏布局"""
        # 配置主框架 - 修复min_width参数错误
        self.configure(
            width=self.current_width,
            corner_radius=8,
            fg_color=("#f0f0f0", "#1a1a1a")  # 可见的背景色
        )

        # 创建滚动框架 - 修复显示问题
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            width=self.current_width - 20,
            corner_radius=6,
            fg_color=("#f8f8f8", "#2a2a2a"),  # 可见的背景色
            scrollbar_button_color=("#c0c0c0", "#404040")
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 配置滚动框架布局
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        # 设置最小宽度的备用方案
        self.bind("<Configure>", self._on_sidebar_configure)

    def _on_sidebar_configure(self, event):
        """处理侧边栏配置事件，确保最小宽度"""
        if event.width < self.min_width:
            # 如果宽度小于最小宽度，重新设置
            self.configure(width=self.min_width)
            logger.debug(f"侧边栏宽度重置为最小值: {self.min_width}")

    def _create_collapse_button(self):
        """创建折叠按钮"""
        self.collapse_button = ctk.CTkButton(
            self,
            text="◀",
            width=20,
            height=30,
            corner_radius=0,
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
            hover_color="#404040"
        )
        self.collapse_button.place(relx=1.0, rely=0.0, anchor="ne")

    def _create_quick_actions_section(self):
        """创建快速操作区域"""
        # 快速操作标题
        quick_title = ctk.CTkLabel(
            self.scroll_frame,
            text="快速操作",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        quick_title.grid(row=0, column=0, sticky="ew", padx=(0, 10), pady=(0, 5))

        # 快速操作容器
        self.quick_actions_frame = ctk.CTkFrame(
            self.scroll_frame,
            corner_radius=8,
            fg_color="#2A2A2A"
        )
        self.quick_actions_frame.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(0, 15))

        # 添加默认快速操作
        self._add_default_quick_actions()

    def _create_navigation_section(self):
        """创建导航区域"""
        # 导航标题
        nav_title = ctk.CTkLabel(
            self.scroll_frame,
            text="主要功能",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        nav_title.grid(row=2, column=0, sticky="ew", padx=(0, 10), pady=(0, 5))

        # 导航容器
        self.navigation_frame = ctk.CTkFrame(
            self.scroll_frame,
            corner_radius=8,
            fg_color="#2A2A2A"
        )
        self.navigation_frame.grid(row=3, column=0, sticky="ew", padx=(0, 10), pady=(0, 15))

        # 添加默认导航项目
        self._add_default_navigation_items()

    def _create_projects_section(self):
        """创建项目区域"""
        # 项目标题
        projects_title = ctk.CTkLabel(
            self.scroll_frame,
            text="最近项目",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        projects_title.grid(row=4, column=0, sticky="ew", padx=(0, 10), pady=(0, 5))

        # 项目容器
        self.projects_frame = ctk.CTkFrame(
            self.scroll_frame,
            corner_radius=8,
            fg_color="#2A2A2A"
        )
        self.projects_frame.grid(row=5, column=0, sticky="ew", padx=(0, 10), pady=(0, 15))

        # 添加示例项目
        self._add_sample_projects()

    def _add_default_quick_actions(self):
        """添加默认快速操作"""
        default_actions = [
            {"name": "新建小说", "icon": "📝", "action": "new_novel"},
            {"name": "快速加载", "icon": "⚡", "action": "quick_load"},
            {"name": "打开项目", "icon": "📁", "action": "open_project"},
            {"name": "保存", "icon": "💾", "action": "save"},
            {"name": "导出", "icon": "📤", "action": "export"}
        ]

        for action in default_actions:
            self.add_quick_action(action["name"], action["icon"], action["action"])

    def _add_default_navigation_items(self):
        """添加默认导航项目"""
        default_nav_items = [
            {"name": "主页", "icon": "🏠", "target": "main", "active": True},
            {"name": "配置", "icon": "⚙", "target": "config", "active": False},
            {"name": "设定", "icon": "🛠", "target": "setting", "active": False},
            {"name": "生成", "icon": "🚀", "target": "generate", "active": False},
            {"name": "角色", "icon": "👥", "target": "characters", "active": False},
            {"name": "章节", "icon": "📖", "target": "chapters", "active": False},
            {"name": "摘要", "icon": "📋", "target": "summary", "active": False},
            {"name": "目录", "icon": "📚", "target": "directory", "active": False}
        ]

        for item in default_nav_items:
            self.add_navigation_item(item["name"], item["icon"], item["target"], item["active"])

    def _add_sample_projects(self):
        """添加示例项目"""
        # 不再添加示例项目，避免混淆用户
        pass

    def add_quick_action(self, name: str, icon: str, action: str):
        """添加快速操作按钮"""
        button = ctk.CTkButton(
            self.quick_actions_frame,
            text=f"{icon} {name}",
            height=36,
            corner_radius=6,
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
            hover_color="#404040",
            anchor="w",
            command=lambda: self._on_quick_action(action)
        )
        button.pack(fill="x", padx=5, pady=2)

        self.quick_actions.append({
            "name": name,
            "icon": icon,
            "action": action,
            "button": button
        })

    def add_navigation_item(self, name: str, icon: str, target: str, active: bool = False):
        """添加导航项目"""
        # 创建导航按钮
        nav_frame = ctk.CTkFrame(
            self.navigation_frame,
            corner_radius=6,
            fg_color="#404040" if active else "transparent"
        )
        nav_frame.pack(fill="x", padx=5, pady=2)

        # 导航标签
        nav_label = ctk.CTkLabel(
            nav_frame,
            text=f"{icon} {name}",
            font=ctk.CTkFont(size=12, weight="bold" if active else "normal"),
            anchor="w"
        )
        nav_label.pack(fill="x", padx=10, pady=8)

        # 绑定点击事件
        def on_nav_frame_click(event=None):
            self._on_navigation_click(target, name)

        nav_frame.bind("<Button-1>", on_nav_frame_click)
        # 也绑定到标签，确保点击文字也能触发
        nav_label.bind("<Button-1>", on_nav_frame_click)

        self.nav_items.append({
            "name": name,
            "icon": icon,
            "target": target,
            "active": active,
            "frame": nav_frame,
            "label": nav_label
        })

    def clear_projects(self):
        """清空项目列表"""
        # 销毁所有项目框架
        for project in self.projects:
            if "frame" in project and project["frame"]:
                project["frame"].destroy()

        # 清空项目列表
        self.projects.clear()

    def add_project(self, name: str, modified: str, status: str, project_path: Optional[str] = None):
        """添加项目"""
        # 项目框架
        project_frame = ctk.CTkFrame(
            self.projects_frame,
            corner_radius=6,
            fg_color="transparent"
        )
        project_frame.pack(fill="x", padx=5, pady=2)

        # 项目名称
        name_label = ctk.CTkLabel(
            project_frame,
            text=name,
            font=ctk.CTkFont(size=11, weight="bold"),
            anchor="w"
        )
        name_label.pack(fill="x", padx=10, pady=(8, 2))

        # 项目信息
        info_label = ctk.CTkLabel(
            project_frame,
            text=f"{modified} • {status}",
            font=ctk.CTkFont(size=10),
            text_color="gray",
            anchor="w"
        )
        info_label.pack(fill="x", padx=10, pady=(0, 6))

        # 绑定点击事件
        def on_project_frame_click(event=None):
            self._on_project_select(name, project_path)

        project_frame.bind("<Button-1>", on_project_frame_click)
        name_label.bind("<Button-1>", on_project_frame_click)
        info_label.bind("<Button-1>", on_project_frame_click)

        self.projects.append({
            "name": name,
            "modified": modified,
            "status": status,
            "path": project_path,
            "frame": project_frame
        })

    def update_recent_projects(self, project_path: str):
        """更新最近项目列表"""
        import os
        from datetime import datetime

        # 获取项目名称
        project_name = os.path.basename(project_path)
        if os.path.isdir(project_path):
            # 文件夹项目
            project_name = f"📁 {project_name}"
        else:
            # JSON文件项目
            project_name = f"📄 {project_name}"

        # 获取修改时间
        modified_time = datetime.fromtimestamp(os.path.getmtime(project_path))
        modified_str = modified_time.strftime("%Y-%m-%d %H:%M")

        # 清空现有项目列表
        self.clear_projects()

        # 添加新的项目到列表顶部
        self.add_project(project_name, modified_str, "最近打开", project_path)

        # 如果主窗口有状态管理器，保存到状态中
        if hasattr(self, 'main_window') and self.main_window and hasattr(self.main_window, 'state_manager'):
            recent_projects = self.main_window.state_manager.get_state('app.recent_projects', [])

            # 更新最近项目列表
            if project_path not in recent_projects:
                recent_projects.insert(0, project_path)
                # 只保留最近10个项目
                recent_projects = recent_projects[:10]
                self.main_window.state_manager.set_state('app.recent_projects', recent_projects)

            # 添加其他最近项目（最多显示5个）
            for i, recent_path in enumerate(recent_projects[1:6]):
                if os.path.exists(recent_path) and recent_path != project_path:
                    recent_name = os.path.basename(recent_path)
                    if os.path.isdir(recent_path):
                        recent_name = f"📁 {recent_name}"
                    else:
                        recent_name = f"📄 {recent_name}"

                    recent_modified = datetime.fromtimestamp(os.path.getmtime(recent_path))
                    recent_modified_str = recent_modified.strftime("%Y-%m-%d %H:%M")

                    self.add_project(recent_name, recent_modified_str, "历史项目", recent_path)

    def _bind_custom_events(self):
        """绑定自定义事件"""
        # 折叠按钮事件
        if self.collapse_button:
            self.collapse_button.configure(command=self._toggle_collapse)

        # 绑定主题变化事件以更新图标
        if self.theme_manager:
            self.theme_manager.subscribe(self._on_theme_changed)

    def _toggle_collapse(self):
        """切换折叠状态"""
        self.is_collapsed = not self.is_collapsed

        if self.is_collapsed:
            self._collapse_sidebar()
        else:
            self._expand_sidebar()

        # 通知父组件（如果设置了回调）
        # sidebar_toggle_callback未定义，跳过

    def _collapse_sidebar(self):
        """折叠侧边栏"""
        # 更新按钮方向
        if self.collapse_button:
            self.collapse_button.configure(text="▶")

        # 隐藏内容框架
        if self.scroll_frame:
            self.scroll_frame.pack_forget()

        # 调整宽度
        self.configure(width=50)

        logger.debug("侧边栏已折叠")

    def _expand_sidebar(self):
        """展开侧边栏"""
        # 更新按钮方向
        if self.collapse_button:
            self.collapse_button.configure(text="◀")

        # 显示内容框架
        if self.scroll_frame:
            self.scroll_frame.pack(fill="both", expand=True, padx=(10, 0), pady=10)

        # 调整宽度
        self.configure(width=self.current_width)

        logger.debug("侧边栏已展开")

    def _on_quick_action(self, action: str):
        """快速操作事件处理"""
        if self.quick_action_callback:
            self.quick_action_callback(action)
        else:
            logger.debug(f"快速操作: {action}")

    def _on_navigation_click(self, target: str, name: str):
        """导航点击事件处理"""
        # 更新活动状态
        for item in self.nav_items:
            is_active = item["target"] == target
            item["active"] = is_active

            # 更新样式
            if is_active:
                item["frame"].configure(fg_color="#404040")
                item["label"].configure(font=ctk.CTkFont(size=12, weight="bold"))
            else:
                item["frame"].configure(fg_color="transparent")
                item["label"].configure(font=ctk.CTkFont(size=12, weight="normal"))

        # 触发回调
        if self.navigation_callback:
            self.navigation_callback(target, name)
        else:
            logger.debug(f"导航到: {target} ({name})")

        # 更新状态
        if self.state_manager:
            self.state_manager.set_state('app.active_tab', target)

    def _on_project_select(self, project_name: str, project_path: Optional[str] = None):
        """项目选择事件处理"""
        # 只有当确实存在项目时才处理
        if project_name and project_name != "未选择项目":
            if project_path and self.main_window:
                # 直接加载项目
                try:
                    self.main_window._load_project_from_path(project_path)
                except Exception as e:
                    logger.error(f"加载项目失败: {e}")
            elif self.project_select_callback:
                self.project_select_callback(project_name)
            else:
                logger.debug(f"选择项目: {project_name}")

    def _on_theme_changed(self, theme_name: str, theme_data: Dict[str, Any]):
        """主题变化回调"""
        try:
            # 检查组件是否仍然存在
            if not (hasattr(self, 'winfo_exists') and self.winfo_exists()):
                return
                
            # 更新折叠按钮样式
            if (self.collapse_button and 
                hasattr(self.collapse_button, 'configure') and
                hasattr(self.collapse_button, 'winfo_exists') and 
                self.collapse_button.winfo_exists()):
                try:
                    colors = theme_data.get('colors', {})
                    if isinstance(colors, dict):
                        text_color = colors.get('text_secondary', '#CCCCCC')
                        # 确保text_color是有效的颜色值
                        if isinstance(text_color, str) and len(text_color) > 0:
                            self.collapse_button.configure(text_color=text_color)
                except Exception as button_e:
                    # 在测试环境中，这可能是正常现象，降级为debug级别
                    logger.debug(f"更新折叠按钮样式失败: {button_e}")
        except Exception as e:
            # 在测试环境中，这可能是正常现象，降级为warning级别
            logger.debug(f"更新侧边栏主题失败: {e}")

    def apply_theme_style(self, theme_data: Dict[str, Any]):
        """应用主题样式"""
        self._on_theme_changed("", theme_data)

    def set_navigation_callback(self, callback: Callable[[str, str], None]):
        """设置导航回调函数"""
        self.navigation_callback = callback

    def set_quick_action_callback(self, callback: Callable[[str], None]):
        """设置快速操作回调函数"""
        self.quick_action_callback = callback

    def set_project_select_callback(self, callback: Callable[[str], None]):
        """设置项目选择回调函数"""
        self.project_select_callback = callback

    def set_active_navigation(self, target: str):
        """设置活动导航项目"""
        for item in self.nav_items:
            if item["target"] == target:
                self._on_navigation_click(target, item["name"])
                break

    def collapse(self):
        """折叠侧边栏"""
        if not self.is_collapsed:
            self._toggle_collapse()

    def expand(self):
        """展开侧边栏"""
        if self.is_collapsed:
            self._toggle_collapse()

    def is_collapsed_state(self) -> bool:
        """获取折叠状态"""
        return self.is_collapsed

    def update_layout_for_size(self, width: int, height: int):
        """根据窗口大小更新布局"""
        try:
            # 在小屏幕上自动折叠
            if width < 900 and not self.is_collapsed:
                self.collapse()
            elif width >= 900 and self.is_collapsed:
                self.expand()

        except Exception as e:
            logger.error(f"更新侧边栏布局失败: {e}")

    def get_sidebar_info(self) -> Dict[str, Any]:
        """获取侧边栏信息"""
        return {
            'is_collapsed': self.is_collapsed,
            'current_width': self.current_width,
            'nav_items_count': len(self.nav_items),
            'quick_actions_count': len(self.quick_actions),
            'projects_count': len(self.projects),
            'has_navigation_callback': self.navigation_callback is not None,
            'has_quick_action_callback': self.quick_action_callback is not None,
            'has_project_select_callback': self.project_select_callback is not None
        }