# ui/components/refresh_button.py
# -*- coding: utf-8 -*-
"""
统一刷新按钮组件 - 为角色、章节、目录标签页提供一致的刷新功能
"""

import logging
import customtkinter as ctk
from typing import Callable, Optional
import threading
import time

logger = logging.getLogger(__name__)


class RefreshButton(ctk.CTkFrame):
    """
    统一刷新按钮组件

    功能：
    - 标准化的刷新按钮样式
    - 加载状态指示
    - 异步刷新支持
    - 成功/失败反馈
    """

    def __init__(
        self,
        parent: ctk.CTkFrame,
        refresh_callback: Callable,
        button_text: str = "刷新",
        width: int = 100,
        height: int = 35,
        **kwargs
    ):
        """
        初始化刷新按钮组件

        Args:
            parent: 父组件
            refresh_callback: 刷新回调函数
            button_text: 按钮文本
            width: 按钮宽度
            height: 按钮高度
        """
        super().__init__(parent, fg_color="transparent", **kwargs)

        self.refresh_callback = refresh_callback
        self.button_text = button_text
        self.is_refreshing = False

        # 创建按钮
        self.create_refresh_button(width, height)

        logger.debug("RefreshButton 组件初始化完成")

    def create_refresh_button(self, width: int, height: int):
        """创建刷新按钮"""
        self.button = ctk.CTkButton(
            self,
            text=self.button_text,
            command=self.on_refresh_click,
            width=width,
            height=height,
            fg_color="#2196F3",  # 蓝色
            hover_color="#1976D2",  # 深蓝色
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=8
        )
        self.button.pack(expand=True)

    def on_refresh_click(self):
        """刷新按钮点击事件"""
        if self.is_refreshing:
            return  # 防止重复点击

        self.is_refreshing = True
        self.set_loading_state()

        # 在后台线程执行刷新
        def refresh_in_background():
            try:
                # 执行刷新回调
                if self.refresh_callback:
                    self.refresh_callback()

                # 在主线程更新UI
                self.after(0, self.set_success_state)

            except Exception as e:
                logger.error(f"刷新失败: {e}")
                self.after(0, self.set_error_state)
            finally:
                self.is_refreshing = False
                # 2秒后恢复正常状态
                self.after(2000, self.set_normal_state)

        # 启动后台线程
        refresh_thread = threading.Thread(target=refresh_in_background, daemon=True)
        refresh_thread.start()

    def set_loading_state(self):
        """设置加载状态"""
        self.button.configure(
            text="刷新中...",
            fg_color="#FF9800",  # 橙色
            hover_color="#F57C00",
            state="disabled"
        )

    def set_success_state(self):
        """设置成功状态"""
        self.button.configure(
            text="✓ 刷新成功",
            fg_color="#4CAF50",  # 绿色
            hover_color="#45A049",
            state="disabled"
        )

    def set_error_state(self):
        """设置错误状态"""
        self.button.configure(
            text="✗ 刷新失败",
            fg_color="#F44336",  # 红色
            hover_color="#D32F2F",
            state="disabled"
        )

    def set_normal_state(self):
        """设置正常状态"""
        self.button.configure(
            text=self.button_text,
            fg_color="#2196F3",  # 蓝色
            hover_color="#1976D2",
            state="normal"
        )

    def set_text(self, text: str):
        """设置按钮文本"""
        self.button_text = text
        if not self.is_refreshing:
            self.button.configure(text=text)

    def enable(self):
        """启用按钮"""
        self.button.configure(state="normal")

    def disable(self):
        """禁用按钮"""
        self.button.configure(state="disabled")


class RefreshableTabFrame(ctk.CTkFrame):
    """
    可刷新标签页框架基类

    为角色、章节、目录标签页提供统一的刷新功能
    """

    def __init__(
        self,
        parent: ctk.CTkFrame,
        tab_name: str,
        refresh_callback: Callable,
        **kwargs
    ):
        """
        初始化可刷新标签页框架

        Args:
            parent: 父组件
            tab_name: 标签页名称
            refresh_callback: 刷新回调函数
        """
        super().__init__(parent, fg_color="transparent", **kwargs)

        self.tab_name = tab_name
        self.refresh_callback = refresh_callback

        # 创建标题栏和刷新按钮
        self.create_header()

        # 创建内容区域
        self.create_content_area()

        logger.debug(f"RefreshableTabFrame ({self.tab_name}) 初始化完成")

    def create_header(self):
        """创建标题栏"""
        header_frame = ctk.CTkFrame(self, fg_color="#2A2A2A", height=50)
        header_frame.pack(fill="x", pady=(0, 10))
        header_frame.pack_propagate(False)

        # 标题标签
        self.title_label = ctk.CTkLabel(
            header_frame,
            text=self.tab_name,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#FFFFFF"
        )
        self.title_label.pack(side="left", padx=20, pady=15)

        # 右侧按钮区域
        button_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        button_frame.pack(side="right", padx=20, pady=10)

        # 刷新按钮
        self.refresh_button = RefreshButton(
            button_frame,
            refresh_callback=self.refresh_callback,
            button_text="刷新",
            width=80,
            height=35
        )
        self.refresh_button.pack(side="right", padx=(5, 0))

    def create_content_area(self):
        """创建内容区域"""
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def get_content_frame(self) -> ctk.CTkFrame:
        """获取内容框架"""
        return self.content_frame

    def set_title(self, title: str):
        """设置标题"""
        self.title_label.configure(text=title)

    def set_refresh_callback(self, callback: Callable):
        """设置刷新回调"""
        self.refresh_callback = callback

    def refresh(self):
        """手动触发刷新"""
        self.refresh_button.on_refresh_click()

    def show_refresh_success(self):
        """显示刷新成功状态"""
        self.refresh_button.set_success_state()
        # 2秒后恢复正常
        self.after(2000, self.refresh_button.set_normal_state)

    def show_refresh_error(self):
        """显示刷新失败状态"""
        self.refresh_button.set_error_state()
        # 2秒后恢复正常
        self.after(2000, self.refresh_button.set_normal_state)