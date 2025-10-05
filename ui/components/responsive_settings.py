# ui/components/responsive_settings.py
# -*- coding: utf-8 -*-
"""
响应式设置管理器 - BMAD方法的Adapt组件
解决窗口大小和字体自适应问题
"""

import logging
import os
import tkinter as tk
from typing import Dict, Any, Optional, Callable, List
import customtkinter as ctk
from tkinter import messagebox, font as tk_font
from datetime import datetime

logger = logging.getLogger(__name__)


class ResponsiveSettingsManager:
    """
    响应式设置管理器

    功能：
    - 自适应窗口大小
    - 动态字体调整
    - 响应式布局
    - 设置持久化
    """

    def __init__(self):
        """初始化响应式设置管理器"""
        # 默认设置
        self.default_settings = {
            'window': {
                'min_width': 1200,
                'min_height': 800,
                'default_width': 1400,
                'default_height': 900
            },
            'fonts': {
                'base_size': 12,
                'title_size': 16,
                'small_size': 10,
                'family': 'Microsoft YaHei'
            },
            'layout': {
                'sidebar_width': 280,
                'content_padding': 20,
                'element_spacing': 10,
                'corner_radius': 8
            },
            'dialog': {
                'min_width': 600,
                'min_height': 500,
                'default_width': 800,
                'default_height': 600
            }
        }

        # 当前设置
        self.settings = self._load_settings()

        # 字体缓存
        self.font_cache = {}

        logger.debug("ResponsiveSettingsManager 初始化完成")

    def _load_settings(self) -> Dict[str, Any]:
        """加载设置"""
        settings_file = 'ui_settings.json'

        try:
            if os.path.exists(settings_file):
                import json
                with open(settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)

                # 合并默认设置和加载的设置
                settings = self._deep_merge(self.default_settings.copy(), loaded_settings)
                logger.info("设置加载成功")
                return settings
            else:
                logger.info("使用默认设置")
                return self.default_settings.copy()

        except Exception as e:
            logger.error(f"加载设置失败: {e}")
            return self.default_settings.copy()

    def _deep_merge(self, base: Dict, update: Dict) -> Dict:
        """深度合并字典"""
        result = base.copy()
        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def save_settings(self):
        """保存设置"""
        try:
            settings_file = 'ui_settings.json'
            import json
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
            logger.info("设置保存成功")
            return True
        except Exception as e:
            logger.error(f"保存设置失败: {e}")
            return False

    def get_font(self, style: str = 'base', size_delta: int = 0, weight: str = 'normal') -> ctk.CTkFont:
        """
        获取字体对象

        Args:
            style: 字体样式 ('base', 'title', 'small')
            size_delta: 大小调整
            weight: 字体粗细 ('normal', 'bold')

        Returns:
            CustomTkinter字体对象
        """
        font_key = f"{style}_{size_delta}_{weight}"

        if font_key not in self.font_cache:
            base_size = self.settings['fonts']['base_size']

            if style == 'title':
                font_size = self.settings['fonts']['title_size']
            elif style == 'small':
                font_size = self.settings['fonts']['small_size']
            else:
                font_size = base_size

            font_size += size_delta

            self.font_cache[font_key] = ctk.CTkFont(
                family=self.settings['fonts']['family'],
                size=font_size,
                weight=weight
            )

        return self.font_cache[font_key]

    def update_font_size(self, delta: int):
        """更新字体大小"""
        self.settings['fonts']['base_size'] = max(8, self.settings['fonts']['base_size'] + delta)
        self.settings['fonts']['title_size'] = self.settings['fonts']['base_size'] + 4
        self.settings['fonts']['small_size'] = max(8, self.settings['fonts']['base_size'] - 2)

        # 清空字体缓存
        self.font_cache.clear()

        # 保存设置
        self.save_settings()

        logger.info(f"字体大小更新: {delta}")

    def update_font_family(self, family: str):
        """更新字体族"""
        self.settings['fonts']['family'] = family

        # 清空字体缓存
        self.font_cache.clear()

        # 保存设置
        self.save_settings()

        logger.info(f"字体族更新: {family}")

    def get_window_size(self, window_type: str = 'main') -> tuple:
        """
        获取窗口大小

        Args:
            window_type: 窗口类型 ('main', 'dialog')

        Returns:
            (width, height)
        """
        if window_type == 'dialog':
            return (
                self.settings['dialog']['default_width'],
                self.settings['dialog']['default_height']
            )
        else:
            return (
                self.settings['window']['default_width'],
                self.settings['window']['default_height']
            )

    def get_min_window_size(self, window_type: str = 'main') -> tuple:
        """
        获取最小窗口大小

        Args:
            window_type: 窗口类型 ('main', 'dialog')

        Returns:
            (width, height)
        """
        if window_type == 'dialog':
            return (
                self.settings['dialog']['min_width'],
                self.settings['dialog']['min_height']
            )
        else:
            return (
                self.settings['window']['min_width'],
                self.settings['window']['min_height']
            )

    def create_responsive_dialog(self, parent, title: str, content_func: Callable) -> ctk.CTkToplevel:
        """
        创建响应式对话框

        Args:
            parent: 父窗口
            title: 对话框标题
            content_func: 内容创建函数

        Returns:
            对话框窗口
        """
        dialog = ctk.CTkToplevel(parent)
        dialog.title(title)

        # 设置窗口大小
        width, height = self.get_window_size('dialog')
        min_width, min_height = self.get_min_window_size('dialog')

        dialog.geometry(f"{width}x{height}")
        dialog.minsize(min_width, min_height)

        # 居中显示
        dialog.transient(parent)
        dialog.grab_set()

        # 创建内容
        content_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=self.settings['layout']['content_padding'],
                         pady=self.settings['layout']['content_padding'])

        # 调用内容创建函数
        if content_func:
            content_func(content_frame, dialog)

        # 绑定窗口大小变化事件
        def on_resize(event):
            # 可以在这里添加响应式逻辑
            pass

        dialog.bind("<Configure>", on_resize)

        return dialog

    def create_responsive_settings_dialog(self, parent) -> ctk.CTkToplevel:
        """
        创建响应式设置对话框

        Args:
            parent: 父窗口

        Returns:
            设置对话框
        """
        def create_settings_content(content_frame, dialog):
            # 创建设置标签页
            settings_tabview = ctk.CTkTabview(
                content_frame,
                segmented_button_fg_color="#2A2A2A",
                segmented_button_selected_color="#3B82F6",
                text_color="#FFFFFF"
            )
            settings_tabview.pack(fill="both", expand=True)

            # 添加标签页
            settings_tabview.add("通用设置")
            settings_tabview.add("字体设置")
            settings_tabview.add("界面设置")
            settings_tabview.add("主题设置")

            # 构建各标签页内容
            self._build_general_settings(settings_tabview.tab("通用设置"))
            self._build_font_settings(settings_tabview.tab("字体设置"), dialog)
            self._build_interface_settings(settings_tabview.tab("界面设置"))
            self._build_theme_settings(settings_tabview.tab("主题设置"))

            # 底部按钮
            button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            button_frame.pack(fill="x", pady=(10, 0))

            save_button = ctk.CTkButton(
                button_frame,
                text="保存设置",
                command=lambda: self._save_all_settings(dialog),
                fg_color="#2E7D32",
                hover_color="#388E3C"
            )
            save_button.pack(side="right", padx=5)

            cancel_button = ctk.CTkButton(
                button_frame,
                text="取消",
                command=dialog.destroy
            )
            cancel_button.pack(side="right", padx=5)

            reset_button = ctk.CTkButton(
                button_frame,
                text="重置默认",
                command=lambda: self._reset_settings(dialog),
                fg_color="#FF9800",
                hover_color="#F57C00"
            )
            reset_button.pack(side="left", padx=5)

        return self.create_responsive_dialog(parent, "应用设置", create_settings_content)

    def _build_general_settings(self, parent):
        """构建通用设置"""
        # 语言设置
        lang_frame = ctk.CTkFrame(parent, fg_color="transparent")
        lang_frame.pack(fill="x", pady=10)

        lang_label = ctk.CTkLabel(
            lang_frame,
            text="界面语言:",
            font=self.get_font('base'),
            width=120
        )
        lang_label.pack(side="left", padx=(0, 10))

        lang_combo = ctk.CTkComboBox(
            lang_frame,
            values=["简体中文", "English"],
            font=self.get_font('base')
        )
        lang_combo.pack(side="left", fill="x", expand=True)
        lang_combo.set("简体中文")

        # 自动保存设置
        autosave_frame = ctk.CTkFrame(parent, fg_color="transparent")
        autosave_frame.pack(fill="x", pady=10)

        autosave_label = ctk.CTkLabel(
            autosave_frame,
            text="自动保存:",
            font=self.get_font('base'),
            width=120
        )
        autosave_label.pack(side="left", padx=(0, 10))

        autosave_switch = ctk.CTkSwitch(
            autosave_frame,
            text="启用自动保存"
        )
        autosave_switch.pack(side="left")

    def _build_font_settings(self, parent, dialog):
        """构建字体设置"""
        # 字体族设置
        family_frame = ctk.CTkFrame(parent, fg_color="transparent")
        family_frame.pack(fill="x", pady=10)

        family_label = ctk.CTkLabel(
            family_frame,
            text="字体:",
            font=self.get_font('base'),
            width=120
        )
        family_label.pack(side="left", padx=(0, 10))

        family_combo = ctk.CTkComboBox(
            family_frame,
            values=["Microsoft YaHei", "SimHei", "Arial", "Helvetica", "Times New Roman"],
            font=self.get_font('base'),
            command=lambda choice: self.update_font_family(choice)
        )
        family_combo.pack(side="left", fill="x", expand=True)
        family_combo.set(self.settings['fonts']['family'])

        # 字体大小设置
        size_frame = ctk.CTkFrame(parent, fg_color="transparent")
        size_frame.pack(fill="x", pady=10)

        size_label = ctk.CTkLabel(
            size_frame,
            text="基础字体大小:",
            font=self.get_font('base'),
            width=120
        )
        size_label.pack(side="left", padx=(0, 10))

        size_slider = ctk.CTkSlider(
            size_frame,
            from_=8,
            to=20,
            number_of_steps=13,
            command=lambda value: self._update_font_size_display(value)
        )
        size_slider.pack(side="left", fill="x", expand=True)
        size_slider.set(self.settings['fonts']['base_size'])

        self.font_size_label = ctk.CTkLabel(
            size_frame,
            text=str(self.settings['fonts']['base_size']),
            font=self.get_font('base'),
            width=30
        )
        self.font_size_label.pack(side="right", padx=(10, 0))

        # 预览区域
        preview_frame = ctk.CTkFrame(parent, fg_color="#333333", corner_radius=8)
        preview_frame.pack(fill="both", expand=True, pady=20)

        preview_label = ctk.CTkLabel(
            preview_frame,
            text="字体预览",
            font=self.get_font('title')
        )
        preview_label.pack(pady=10)

        preview_text = ctk.CTkTextbox(
            preview_frame,
            height=100,
            font=self.get_font('base')
        )
        preview_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        preview_text.insert('1.0', "这是一段预览文本，用于显示字体效果。\nThis is a preview text to show font effect.")
        preview_text.configure(state='disabled')

    def _build_interface_settings(self, parent):
        """构建界面设置"""
        # 侧边栏宽度
        sidebar_frame = ctk.CTkFrame(parent, fg_color="transparent")
        sidebar_frame.pack(fill="x", pady=10)

        sidebar_label = ctk.CTkLabel(
            sidebar_frame,
            text="侧边栏宽度:",
            font=self.get_font('base'),
            width=120
        )
        sidebar_label.pack(side="left", padx=(0, 10))

        sidebar_slider = ctk.CTkSlider(
            sidebar_frame,
            from_=200,
            to=400,
            number_of_steps=21,
            command=lambda value: self._update_sidebar_width(value)
        )
        sidebar_slider.pack(side="left", fill="x", expand=True)
        sidebar_slider.set(self.settings['layout']['sidebar_width'])

        self.sidebar_width_label = ctk.CTkLabel(
            sidebar_frame,
            text=str(self.settings['layout']['sidebar_width']),
            font=self.get_font('base'),
            width=40
        )
        self.sidebar_width_label.pack(side="right", padx=(10, 0))

        # 圆角大小
        corner_frame = ctk.CTkFrame(parent, fg_color="transparent")
        corner_frame.pack(fill="x", pady=10)

        corner_label = ctk.CTkLabel(
            corner_frame,
            text="圆角大小:",
            font=self.get_font('base'),
            width=120
        )
        corner_label.pack(side="left", padx=(0, 10))

        corner_slider = ctk.CTkSlider(
            corner_frame,
            from_=0,
            to=20,
            number_of_steps=21,
            command=lambda value: self._update_corner_radius(value)
        )
        corner_slider.pack(side="left", fill="x", expand=True)
        corner_slider.set(self.settings['layout']['corner_radius'])

        self.corner_radius_label = ctk.CTkLabel(
            corner_frame,
            text=str(self.settings['layout']['corner_radius']),
            font=self.get_font('base'),
            width=30
        )
        self.corner_radius_label.pack(side="right", padx=(10, 0))

    def _build_theme_settings(self, parent):
        """构建主题设置"""
        # 主题选择
        theme_frame = ctk.CTkFrame(parent, fg_color="transparent")
        theme_frame.pack(fill="x", pady=10)

        theme_label = ctk.CTkLabel(
            theme_frame,
            text="主题模式:",
            font=self.get_font('base'),
            width=120
        )
        theme_label.pack(side="left", padx=(0, 10))

        theme_segmented = ctk.CTkSegmentedButton(
            theme_frame,
            values=["浅色", "深色", "系统"],
            font=self.get_font('base')
        )
        theme_segmented.pack(side="left", fill="x", expand=True)
        theme_segmented.set("深色")

        # 颜色方案
        color_frame = ctk.CTkFrame(parent, fg_color="transparent")
        color_frame.pack(fill="x", pady=10)

        color_label = ctk.CTkLabel(
            color_frame,
            text="颜色方案:",
            font=self.get_font('base'),
            width=120
        )
        color_label.pack(side="left", padx=(0, 10))

        color_combo = ctk.CTkComboBox(
            color_frame,
            values=["蓝色", "绿色", "暗色", "自定义"],
            font=self.get_font('base')
        )
        color_combo.pack(side="left", fill="x", expand=True)
        color_combo.set("蓝色")

    def _update_font_size_display(self, value):
        """更新字体大小显示"""
        size = int(value)
        self.font_size_label.configure(text=str(size))

    def _update_sidebar_width(self, value):
        """更新侧边栏宽度显示"""
        width = int(value)
        self.sidebar_width_label.configure(text=str(width))
        self.settings['layout']['sidebar_width'] = width

    def _update_corner_radius(self, value):
        """更新圆角大小显示"""
        radius = int(value)
        self.corner_radius_label.configure(text=str(radius))
        self.settings['layout']['corner_radius'] = radius

    def _save_all_settings(self, dialog):
        """保存所有设置"""
        if self.save_settings():
            messagebox.showinfo("成功", "设置已保存")
            dialog.destroy()
        else:
            messagebox.showerror("错误", "设置保存失败")

    def _reset_settings(self, dialog):
        """重置设置"""
        if messagebox.askyesno("确认重置", "确定要重置所有设置为默认值吗？"):
            self.settings = self.default_settings.copy()
            self.font_cache.clear()
            self.save_settings()
            dialog.destroy()
            messagebox.showinfo("成功", "设置已重置为默认值")

    def apply_font_to_widget(self, widget, style: str = 'base', size_delta: int = 0):
        """
        应用字体到组件

        Args:
            widget: 组件
            style: 字体样式
            size_delta: 大小调整
        """
        font = self.get_font(style, size_delta)

        try:
            if hasattr(widget, 'configure'):
                if hasattr(widget, 'cget') and widget.cget('font'):
                    widget.configure(font=font)
                elif 'font' in widget.keys():
                    widget.configure(font=font)
        except Exception as e:
            logger.warning(f"应用字体失败: {e}")


# 全局设置管理器实例
_settings_manager = None

def get_responsive_settings() -> ResponsiveSettingsManager:
    """获取全局响应式设置管理器实例"""
    global _settings_manager
    if _settings_manager is None:
        _settings_manager = ResponsiveSettingsManager()
    return _settings_manager