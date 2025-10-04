"""
现代化通知系统 - 用于替代简单的状态栏
提供持续状态显示和临时通知功能
"""

import customtkinter as ctk
import logging
from typing import Optional, Callable
from enum import Enum
import time

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """通知类型枚举"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    DEBUG = "debug"
    STATUS = "status"  # 新增状态类型


class NotificationSystem(ctk.CTkFrame):
    """
    现代化通知系统组件

    功能：
    - 持续状态显示
    - 临时通知功能
    - 多种通知类型
    - 主题适配
    """

    def __init__(self, parent, theme_manager=None, state_manager=None, **kwargs):
        """
        初始化通知系统

        Args:
            parent: 父组件
            theme_manager: 主题管理器
            state_manager: 状态管理器
            **kwargs: 其他参数
        """
        super().__init__(parent, **kwargs)

        # 存储管理器引用
        self.theme_manager = theme_manager
        self.state_manager = state_manager

        # 通知队列
        self.notifications = []
        self.notification_widgets = {}
        
        # 状态显示
        self.status_widget = None

        # 配置框架
        self.configure(
            fg_color="transparent",
            corner_radius=0,
            height=30
        )

        # 创建状态显示区域
        self.status_frame = ctk.CTkFrame(
            self,
            fg_color=self._get_status_color(),
            corner_radius=0,
            height=25
        )
        self.status_frame.pack(fill="x", expand=False, padx=5, pady=2)
        self.status_frame.pack_propagate(False)

        # 状态文本
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="就绪 | 主题: 深色模式 | 布局: 桌面版",
            font=ctk.CTkFont(size=11),
            anchor="w"
        )
        self.status_label.pack(side="left", padx=10, pady=3)

        # 通知容器（用于临时通知）
        self.notification_container = ctk.CTkFrame(
            self,
            fg_color="transparent",
            height=0  # 初始高度为0，只在有通知时显示
        )
        self.notification_container.pack(fill="x", expand=False, padx=5, pady=0)
        self.notification_container.pack_propagate(False)

        # 应用主题
        self._apply_theme()

        logger.debug("通知系统初始化完成")

    def _apply_theme(self):
        """应用主题到通知系统"""
        try:
            if self.theme_manager:
                # 获取主题颜色
                bg_color = self.theme_manager.get_color('background')
                
                # 应用到组件
                self.configure(fg_color=bg_color)
                if self.status_frame:
                    self.status_frame.configure(fg_color=self._get_status_color())
        except Exception as e:
            logger.error(f"应用主题到通知系统失败: {e}")

    def _get_status_color(self) -> str:
        """获取状态栏背景颜色"""
        if self.theme_manager:
            return self.theme_manager.get_color('surface')
        else:
            return "#252526"

    def _get_border_color(self) -> str:
        """获取边框颜色"""
        if self.theme_manager:
            return self.theme_manager.get_color('border')
        else:
            return "#3E3E42"

    def update_status(self, message: str):
        """更新状态显示（持续显示）"""
        try:
            if self.status_label:
                # 添加时间戳
                timestamp = time.strftime("%H:%M:%S")
                full_message = f"[{timestamp}] {message}"
                self.status_label.configure(text=full_message)
                logger.debug(f"状态更新: {message}")
        except Exception as e:
            logger.error(f"更新状态显示失败: {e}")

    def show_notification(self, message: str, notification_type: NotificationType = NotificationType.INFO,
                         duration: int = 5000, callback: Optional[Callable] = None):
        """
        显示临时通知

        Args:
            message: 通知消息
            notification_type: 通知类型
            duration: 显示持续时间（毫秒）
            callback: 点击回调函数
        """
        try:
            # 如果是状态类型，直接更新状态栏
            if notification_type == NotificationType.STATUS:
                self.update_status(message)
                return

            # 创建通知ID
            notification_id = f"notification_{int(time.time() * 1000)}"

            # 扩展通知容器
            self.notification_container.configure(height=40)
            self.configure(height=65)  # 总高度 = 状态栏25 + 通知栏40

            # 创建通知框架
            notification_frame = ctk.CTkFrame(
                self.notification_container,
                fg_color=self._get_notification_color(notification_type),
                corner_radius=6,
                border_width=1,
                border_color=self._get_border_color()
            )
            notification_frame.pack(fill="x", pady=2, padx=2)

            # 创建通知内容
            content_frame = ctk.CTkFrame(notification_frame, fg_color="transparent")
            content_frame.pack(fill="x", padx=8, pady=6)

            # 图标
            icon = self._get_notification_icon(notification_type)
            icon_label = ctk.CTkLabel(
                content_frame,
                text=icon,
                font=ctk.CTkFont(size=14),
                width=18
            )
            icon_label.pack(side="left", padx=(0, 8))

            # 消息文本
            message_label = ctk.CTkLabel(
                content_frame,
                text=message,
                font=ctk.CTkFont(size=11),
                anchor="w",
                wraplength=350
            )
            message_label.pack(side="left", fill="x", expand=True)

            # 关闭按钮
            close_button = ctk.CTkButton(
                content_frame,
                text="×",
                width=18,
                height=18,
                fg_color="transparent",
                hover_color="#FF0000",
                text_color="#FFFFFF",
                command=lambda: self._dismiss_notification(notification_id)
            )
            close_button.pack(side="right", padx=(8, 0))

            # 绑定点击事件
            if callback:
                notification_frame.bind("<Button-1>", lambda e: callback())
                content_frame.bind("<Button-1>", lambda e: callback())
                icon_label.bind("<Button-1>", lambda e: callback())
                message_label.bind("<Button-1>", lambda e: callback())

            # 记录通知
            self.notification_widgets[notification_id] = {
                'frame': notification_frame,
                'content': content_frame,
                'message': message_label,
                'close_button': close_button,
                'type': notification_type,
                'callback': callback
            }

            # 添加到通知队列
            self.notifications.append(notification_id)

            # 设置自动消失
            if duration > 0:
                self.after(duration, lambda: self._dismiss_notification(notification_id))

            logger.debug(f"显示通知: {message}")

        except Exception as e:
            logger.error(f"显示通知失败: {e}")

    def _get_notification_color(self, notification_type: NotificationType) -> str:
        """获取通知背景颜色"""
        if self.theme_manager:
            color_map = {
                NotificationType.INFO: self.theme_manager.get_color('info'),
                NotificationType.SUCCESS: self.theme_manager.get_color('success'),
                NotificationType.WARNING: self.theme_manager.get_color('warning'),
                NotificationType.ERROR: self.theme_manager.get_color('error'),
                NotificationType.DEBUG: self.theme_manager.get_color('secondary')
            }
            return color_map.get(notification_type, self.theme_manager.get_color('surface'))
        else:
            # 默认颜色
            color_map = {
                NotificationType.INFO: "#0078D4",
                NotificationType.SUCCESS: "#107C10",
                NotificationType.WARNING: "#FF8C00",
                NotificationType.ERROR: "#D13438",
                NotificationType.DEBUG: "#6C757D"
            }
            return color_map.get(notification_type, "#252526")

    def _get_notification_icon(self, notification_type: NotificationType) -> str:
        """获取通知图标"""
        icon_map = {
            NotificationType.INFO: "ℹ️",
            NotificationType.SUCCESS: "✅",
            NotificationType.WARNING: "⚠️",
            NotificationType.ERROR: "❌",
            NotificationType.DEBUG: "🐛",
            NotificationType.STATUS: "ℹ️"
        }
        return icon_map.get(notification_type, "ℹ️")

    def _dismiss_notification(self, notification_id: str):
        """消除通知"""
        try:
            if notification_id in self.notification_widgets:
                widget_info = self.notification_widgets[notification_id]
                
                # 销毁组件
                try:
                    widget_info['frame'].destroy()
                except:
                    pass
                
                # 从记录中移除
                del self.notification_widgets[notification_id]

                # 从队列中移除
                if notification_id in self.notifications:
                    self.notifications.remove(notification_id)

                # 如果没有更多通知，收缩容器
                if len(self.notification_widgets) == 0:
                    self.notification_container.configure(height=0)
                    self.configure(height=30)  # 只显示状态栏

                logger.debug(f"消除通知: {notification_id}")
        except Exception as e:
            logger.error(f"消除通知失败: {e}")

    def clear_all_notifications(self):
        """清除所有临时通知"""
        try:
            notification_ids = list(self.notification_widgets.keys())
            for notification_id in notification_ids:
                try:
                    self._dismiss_notification(notification_id)
                except:
                    pass
            logger.debug("清除所有通知")
        except Exception as e:
            logger.error(f"清除所有通知失败: {e}")

    def show_info(self, message: str, duration: int = 5000):
        """显示信息通知"""
        self.show_notification(message, NotificationType.INFO, duration)

    def show_success(self, message: str, duration: int = 5000):
        """显示成功通知"""
        self.show_notification(message, NotificationType.SUCCESS, duration)

    def show_warning(self, message: str, duration: int = 5000):
        """显示警告通知"""
        self.show_notification(message, NotificationType.WARNING, duration)

    def show_error(self, message: str, duration: int = 5000):
        """显示错误通知"""
        self.show_notification(message, NotificationType.ERROR, duration)

    def show_status(self, message: str):
        """显示状态信息（持续显示）"""
        self.show_notification(message, NotificationType.STATUS, 0)  # duration=0表示不自动消失

    def show_debug(self, message: str, duration: int = 5000):
        """显示调试通知"""
        self.show_notification(message, NotificationType.DEBUG, duration)