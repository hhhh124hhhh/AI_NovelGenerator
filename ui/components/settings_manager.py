"""
现代化设置管理器组件 - AI小说生成器的系统设置界面
集成响应式设置管理器，解决窗口大小和字体问题
包含字体设置、主题设置、界面设置等功能
"""

import logging
import os
from typing import Dict, Any, Optional, Callable, List
import customtkinter as ctk
from tkinter import messagebox, font as tk_font
from datetime import datetime

# 导入响应式设置管理器
try:
    from .responsive_settings import get_responsive_settings
    RESPONSIVE_SETTINGS_AVAILABLE = True
except ImportError:
    RESPONSIVE_SETTINGS_AVAILABLE = False

logger = logging.getLogger(__name__)


class SettingsManager(ctk.CTkFrame):
    """
    现代化设置管理器组件

    功能：
    - 字体设置（字体族、大小、粗细、行间距）
    - 主题设置（深色/浅色主题）
    - 界面设置（动画效果、布局选项）
    - 实时预览功能
    - 设置导入导出
    - 响应式布局
    """

    def __init__(self, parent: ctk.CTkFrame, theme_manager, state_manager=None, main_window=None, **kwargs):
        """
        初始化设置管理器

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

        # 响应式设置管理器
        if RESPONSIVE_SETTINGS_AVAILABLE:
            self.responsive_settings = get_responsive_settings()
        else:
            self.responsive_settings = None

        # 设置数据
        self.settings_data = {}
        self.default_settings = self._get_default_settings()

        # 预览回调
        self.preview_callback = None

        # 创建界面
        self._create_layout()
        self._load_settings()
        self._apply_settings_to_ui()

        logger.info("设置管理器初始化完成")

    def _get_default_settings(self) -> Dict[str, Any]:
        """获取默认设置"""
        return {
            "font": {
                "family": "Microsoft YaHei UI",
                "size": 12,
                "weight": "normal",
                "line_spacing": 1.5
            },
            "ui": {
                "theme": "dark",
                "animations": True,
                "auto_save": True,
                "show_status_bar": True
            },
            "editor": {
                "tab_size": 4,
                "word_wrap": True,
                "show_line_numbers": False
            }
        }

    def _create_layout(self):
        """创建布局"""
        # 配置主框架
        self.configure(
            corner_radius=8,
            fg_color="transparent"
        )

        # 创建标题区域
        self._create_header_area()

        # 创建设置选项卡
        self._create_settings_tabs()

        # 创建按钮区域
        self._create_button_area()

    def _create_header_area(self):
        """创建标题区域"""
        header_frame = ctk.CTkFrame(self, fg_color="#2A2A2A", corner_radius=8)
        header_frame.pack(fill="x", padx=10, pady=(10, 5))

        # 标题
        title_label = ctk.CTkLabel(
            header_frame,
            text="⚙️ 系统设置",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=15)

        # 描述
        desc_label = ctk.CTkLabel(
            header_frame,
            text="自定义字体、主题、界面等系统设置",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        desc_label.pack(pady=(0, 15))

    def _create_settings_tabs(self):
        """创建设置选项卡"""
        # 选项卡容器
        self.tabview = ctk.CTkTabview(
            self,
            segmented_button_fg_color="#2A2A2A",
            segmented_button_selected_color="#404040",
            segmented_button_unselected_color="#1E1E1E"
        )
        self.tabview.pack(fill="both", expand=True, padx=10, pady=5)

        # 创建各个选项卡
        self._create_font_tab()
        self._create_theme_tab()
        self._create_interface_tab()
        self._create_editor_tab()

    def _create_font_tab(self):
        """创建字体设置选项卡"""
        font_tab = self.tabview.add("字体设置")

        # 主滚动框架
        scroll_frame = ctk.CTkScrollableFrame(font_tab, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 字体族设置
        family_frame = ctk.CTkFrame(scroll_frame, fg_color="#2A2A2A", corner_radius=8)
        family_frame.pack(fill="x", pady=(0, 10))

        family_label = ctk.CTkLabel(
            family_frame,
            text="🔤 字体族",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        family_label.pack(pady=(10, 5), padx=10, anchor="w")

        # 获取系统字体
        system_fonts = self._get_system_fonts()

        self.font_family_var = ctk.StringVar(value="Microsoft YaHei UI")
        self.font_family_combo = ctk.CTkComboBox(
            family_frame,
            variable=self.font_family_var,
            values=system_fonts,
            command=self._on_font_changed
        )
        self.font_family_combo.pack(fill="x", padx=10, pady=(0, 10))

        # 字体大小设置
        size_frame = ctk.CTkFrame(scroll_frame, fg_color="#2A2A2A", corner_radius=8)
        size_frame.pack(fill="x", pady=(0, 10))

        size_label = ctk.CTkLabel(
            size_frame,
            text="📏 字体大小",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        size_label.pack(pady=(10, 5), padx=10, anchor="w")

        # 字体大小滑块
        self.font_size_var = ctk.IntVar(value=12)
        self.font_size_slider = ctk.CTkSlider(
            size_frame,
            from_=8,
            to=24,
            variable=self.font_size_var,
            command=self._on_font_size_changed
        )
        self.font_size_slider.pack(fill="x", padx=10, pady=5)

        # 字体大小显示
        self.font_size_label = ctk.CTkLabel(
            size_frame,
            text="12px",
            font=ctk.CTkFont(size=12)
        )
        self.font_size_label.pack(pady=(0, 10))

        # 字体粗细设置
        weight_frame = ctk.CTkFrame(scroll_frame, fg_color="#2A2A2A", corner_radius=8)
        weight_frame.pack(fill="x", pady=(0, 10))

        weight_label = ctk.CTkLabel(
            weight_frame,
            text="💪 字体粗细",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        weight_label.pack(pady=(10, 5), padx=10, anchor="w")

        self.font_weight_var = ctk.StringVar(value="normal")
        weight_options = ["正常", "粗体", "细体"]
        weight_buttons_frame = ctk.CTkFrame(weight_frame, fg_color="transparent")
        weight_buttons_frame.pack(fill="x", padx=10, pady=(0, 10))

        for i, option in enumerate(weight_options):
            radio = ctk.CTkRadioButton(
                weight_buttons_frame,
                text=option,
                variable=self.font_weight_var,
                value="normal" if option == "正常" else ("bold" if option == "粗体" else "light"),
                command=self._on_font_changed
            )
            radio.pack(side="left", padx=10)

        # 行间距设置
        spacing_frame = ctk.CTkFrame(scroll_frame, fg_color="#2A2A2A", corner_radius=8)
        spacing_frame.pack(fill="x", pady=(0, 10))

        spacing_label = ctk.CTkLabel(
            spacing_frame,
            text="📝 行间距",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        spacing_label.pack(pady=(10, 5), padx=10, anchor="w")

        self.line_spacing_var = ctk.DoubleVar(value=1.5)
        self.line_spacing_slider = ctk.CTkSlider(
            spacing_frame,
            from_=1.0,
            to=3.0,
            variable=self.line_spacing_var,
            command=self._on_line_spacing_changed
        )
        self.line_spacing_slider.pack(fill="x", padx=10, pady=5)

        self.line_spacing_label = ctk.CTkLabel(
            spacing_frame,
            text="1.5",
            font=ctk.CTkFont(size=12)
        )
        self.line_spacing_label.pack(pady=(0, 10))

        # 预览区域
        preview_frame = ctk.CTkFrame(scroll_frame, fg_color="#2A2A2A", corner_radius=8)
        preview_frame.pack(fill="x", pady=(0, 10))

        preview_label = ctk.CTkLabel(
            preview_frame,
            text="👁️ 预览效果",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        preview_label.pack(pady=(10, 5), padx=10, anchor="w")

        self.preview_text = ctk.CTkTextbox(
            preview_frame,
            height=100,
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=12)
        )
        self.preview_text.pack(fill="x", padx=10, pady=(0, 10))
        self.preview_text.insert("0.0", "这是字体预览文本\nThe quick brown fox jumps over the lazy dog\n1234567890!@#$%^&*()")
        self.preview_text.configure(state="disabled")

    def _create_theme_tab(self):
        """创建主题设置选项卡"""
        theme_tab = self.tabview.add("主题设置")

        # 主滚动框架
        scroll_frame = ctk.CTkScrollableFrame(theme_tab, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 主题选择
        theme_frame = ctk.CTkFrame(scroll_frame, fg_color="#2A2A2A", corner_radius=8)
        theme_frame.pack(fill="x", pady=(0, 10))

        theme_label = ctk.CTkLabel(
            theme_frame,
            text="🎨 主题模式",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        theme_label.pack(pady=(10, 5), padx=10, anchor="w")

        self.theme_var = ctk.StringVar(value="dark")
        theme_options = ["深色主题", "浅色主题", "跟随系统"]
        theme_buttons_frame = ctk.CTkFrame(theme_frame, fg_color="transparent")
        theme_buttons_frame.pack(fill="x", padx=10, pady=(0, 10))

        for i, option in enumerate(theme_options):
            radio = ctk.CTkRadioButton(
                theme_buttons_frame,
                text=option,
                variable=self.theme_var,
                value="dark" if option == "深色主题" else ("light" if option == "浅色主题" else "system"),
                command=self._on_theme_changed
            )
            radio.pack(side="left", padx=10)

        # 主题预览
        preview_frame = ctk.CTkFrame(scroll_frame, fg_color="#2A2A2A", corner_radius=8)
        preview_frame.pack(fill="x", pady=(0, 10))

        preview_label = ctk.CTkLabel(
            preview_frame,
            text="🎭 主题预览",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        preview_label.pack(pady=(10, 5), padx=10, anchor="w")

        # 这里可以添加主题预览组件

    def _create_interface_tab(self):
        """创建界面设置选项卡"""
        interface_tab = self.tabview.add("界面设置")

        # 主滚动框架
        scroll_frame = ctk.CTkScrollableFrame(interface_tab, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 动画效果
        animation_frame = ctk.CTkFrame(scroll_frame, fg_color="#2A2A2A", corner_radius=8)
        animation_frame.pack(fill="x", pady=(0, 10))

        animation_label = ctk.CTkLabel(
            animation_frame,
            text="✨ 动画效果",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        animation_label.pack(pady=(10, 5), padx=10, anchor="w")

        self.animations_var = ctk.BooleanVar(value=True)
        animation_check = ctk.CTkCheckBox(
            animation_frame,
            text="启用界面动画效果",
            variable=self.animations_var,
            command=self._on_interface_changed
        )
        animation_check.pack(pady=(0, 10), padx=10, anchor="w")

        # 自动保存
        autosave_frame = ctk.CTkFrame(scroll_frame, fg_color="#2A2A2A", corner_radius=8)
        autosave_frame.pack(fill="x", pady=(0, 10))

        autosave_label = ctk.CTkLabel(
            autosave_frame,
            text="💾 自动保存",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        autosave_label.pack(pady=(10, 5), padx=10, anchor="w")

        self.autosave_var = ctk.BooleanVar(value=True)
        autosave_check = ctk.CTkCheckBox(
            autosave_frame,
            text="启用自动保存功能",
            variable=self.autosave_var,
            command=self._on_interface_changed
        )
        autosave_check.pack(pady=(0, 10), padx=10, anchor="w")

    def _create_editor_tab(self):
        """创建编辑器设置选项卡"""
        editor_tab = self.tabview.add("编辑器设置")

        # 主滚动框架
        scroll_frame = ctk.CTkScrollableFrame(editor_tab, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 制表符大小
        tabsize_frame = ctk.CTkFrame(scroll_frame, fg_color="#2A2A2A", corner_radius=8)
        tabsize_frame.pack(fill="x", pady=(0, 10))

        tabsize_label = ctk.CTkLabel(
            tabsize_frame,
            text="📏 制表符大小",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        tabsize_label.pack(pady=(10, 5), padx=10, anchor="w")

        self.tabsize_var = ctk.IntVar(value=4)
        tabsize_options = [2, 4, 8]
        tabsize_buttons_frame = ctk.CTkFrame(tabsize_frame, fg_color="transparent")
        tabsize_buttons_frame.pack(fill="x", padx=10, pady=(0, 10))

        for option in tabsize_options:
            radio = ctk.CTkRadioButton(
                tabsize_buttons_frame,
                text=f"{option} 空格",
                variable=self.tabsize_var,
                value=option,
                command=self._on_editor_changed
            )
            radio.pack(side="left", padx=10)

        # 自动换行
        wordwrap_frame = ctk.CTkFrame(scroll_frame, fg_color="#2A2A2A", corner_radius=8)
        wordwrap_frame.pack(fill="x", pady=(0, 10))

        wordwrap_label = ctk.CTkLabel(
            wordwrap_frame,
            text="🔄 自动换行",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        wordwrap_label.pack(pady=(10, 5), padx=10, anchor="w")

        self.wordwrap_var = ctk.BooleanVar(value=True)
        wordwrap_check = ctk.CTkCheckBox(
            wordwrap_frame,
            text="启用自动换行",
            variable=self.wordwrap_var,
            command=self._on_editor_changed
        )
        wordwrap_check.pack(pady=(0, 10), padx=10, anchor="w")

    def _create_button_area(self):
        """创建按钮区域"""
        button_frame = ctk.CTkFrame(self, fg_color="#2A2A2A", corner_radius=8)
        button_frame.pack(fill="x", padx=10, pady=(5, 10))

        # 按钮容器
        buttons_container = ctk.CTkFrame(button_frame, fg_color="transparent")
        buttons_container.pack(fill="x", padx=10, pady=10)

        # 重置按钮
        reset_btn = ctk.CTkButton(
            buttons_container,
            text="🔄 重置默认",
            command=self._reset_to_default,
            fg_color="#FF6B6B",
            hover_color="#FF5252"
        )
        reset_btn.pack(side="left", padx=(0, 10))

        # 导入按钮
        import_btn = ctk.CTkButton(
            buttons_container,
            text="📂 导入设置",
            command=self._import_settings
        )
        import_btn.pack(side="left", padx=(0, 10))

        # 导出按钮
        export_btn = ctk.CTkButton(
            buttons_container,
            text="💾 导出设置",
            command=self._export_settings
        )
        export_btn.pack(side="left", padx=(0, 10))

        # 应用按钮
        apply_btn = ctk.CTkButton(
            buttons_container,
            text="✅ 应用设置",
            command=self._apply_settings,
            fg_color="#4CAF50",
            hover_color="#45A049"
        )
        apply_btn.pack(side="right")

    def _get_system_fonts(self) -> List[str]:
        """获取系统字体列表"""
        try:
            # 获取系统字体
            system_fonts = list(tk_font.families())

            # 过滤并排序字体
            common_fonts = [
                "Microsoft YaHei UI",
                "Microsoft YaHei",
                "SimSun",
                "SimHei",
                "KaiTi",
                "FangSong",
                "Arial",
                "Times New Roman",
                "Consolas",
                "Courier New",
                "Helvetica",
                "Georgia",
                "Verdana"
            ]

            # 确保常用字体在前面
            filtered_fonts = []
            for font in common_fonts:
                if font in system_fonts:
                    filtered_fonts.append(font)

            # 添加其他字体
            for font in sorted(system_fonts):
                if font not in filtered_fonts:
                    filtered_fonts.append(font)

            return filtered_fonts[:50]  # 限制数量避免列表过长

        except Exception as e:
            logger.error(f"获取系统字体失败: {e}")
            return ["Microsoft YaHei UI", "Arial", "Times New Roman"]

    def _on_font_changed(self, *args):
        """字体设置变化回调"""
        self._update_font_preview()
        self._notify_setting_changed("font")

    def _on_font_size_changed(self, value):
        """字体大小变化回调"""
        size = int(value)
        self.font_size_label.configure(text=f"{size}px")
        self._update_font_preview()
        self._notify_setting_changed("font")

    def _on_line_spacing_changed(self, value):
        """行间距变化回调"""
        spacing = round(float(value), 1)
        self.line_spacing_label.configure(text=str(spacing))
        self._update_font_preview()
        self._notify_setting_changed("font")

    def _on_theme_changed(self):
        """主题变化回调"""
        self._notify_setting_changed("theme")

    def _on_interface_changed(self):
        """界面设置变化回调"""
        self._notify_setting_changed("interface")

    def _on_editor_changed(self):
        """编辑器设置变化回调"""
        self._notify_setting_changed("editor")

    def _update_font_preview(self):
        """更新字体预览"""
        try:
            family = self.font_family_var.get()
            size = self.font_size_var.get()
            weight = self.font_weight_var.get()

            # 创建字体
            font_kwargs = {"family": family, "size": size}
            if weight == "bold":
                font_kwargs["weight"] = "bold"
            elif weight == "light":
                font_kwargs["weight"] = "light"

            preview_font = ctk.CTkFont(**font_kwargs)

            # 应用到预览文本
            self.preview_text.configure(font=preview_font)

        except Exception as e:
            logger.error(f"更新字体预览失败: {e}")

    def _notify_setting_changed(self, category: str):
        """通知设置变化"""
        if self.preview_callback:
            self.preview_callback(category, self._get_current_settings())

    def _get_current_settings(self) -> Dict[str, Any]:
        """获取当前设置"""
        return {
            "font": {
                "family": self.font_family_var.get(),
                "size": self.font_size_var.get(),
                "weight": self.font_weight_var.get(),
                "line_spacing": self.line_spacing_var.get()
            },
            "ui": {
                "theme": self.theme_var.get(),
                "animations": self.animations_var.get(),
                "auto_save": self.autosave_var.get(),
                "show_status_bar": True
            },
            "editor": {
                "tab_size": self.tabsize_var.get(),
                "word_wrap": self.wordwrap_var.get(),
                "show_line_numbers": False
            }
        }

    def _load_settings(self):
        """加载设置"""
        try:
            # 从状态管理器或配置文件加载设置
            if self.state_manager:
                saved_settings = self.state_manager.get_state('settings', {})
                if saved_settings:
                    self.settings_data = {**self.default_settings, **saved_settings}
                else:
                    self.settings_data = self.default_settings.copy()
            else:
                self.settings_data = self.default_settings.copy()

            logger.info("设置加载完成")

        except Exception as e:
            logger.error(f"加载设置失败: {e}")
            self.settings_data = self.default_settings.copy()

    def _apply_settings_to_ui(self):
        """将设置应用到UI"""
        try:
            # 字体设置
            font_settings = self.settings_data.get("font", {})
            self.font_family_var.set(font_settings.get("family", "Microsoft YaHei UI"))
            self.font_size_var.set(font_settings.get("size", 12))
            self.font_weight_var.set(font_settings.get("weight", "normal"))
            self.line_spacing_var.set(font_settings.get("line_spacing", 1.5))

            # 更新显示标签
            self.font_size_label.configure(text=f"{font_settings.get('size', 12)}px")
            self.line_spacing_label.configure(text=str(font_settings.get('line_spacing', 1.5)))

            # UI设置
            ui_settings = self.settings_data.get("ui", {})
            self.theme_var.set(ui_settings.get("theme", "dark"))
            self.animations_var.set(ui_settings.get("animations", True))
            self.autosave_var.set(ui_settings.get("auto_save", True))

            # 编辑器设置
            editor_settings = self.settings_data.get("editor", {})
            self.tabsize_var.set(editor_settings.get("tab_size", 4))
            self.wordwrap_var.set(editor_settings.get("word_wrap", True))

            # 更新预览
            self._update_font_preview()

            logger.info("设置已应用到UI")

        except Exception as e:
            logger.error(f"应用设置到UI失败: {e}")

    def _reset_to_default(self):
        """重置为默认设置"""
        if messagebox.askyesno("确认重置", "确定要重置所有设置为默认值吗？"):
            self.settings_data = self.default_settings.copy()
            self._apply_settings_to_ui()
            messagebox.showinfo("成功", "设置已重置为默认值")

    def _import_settings(self):
        """导入设置"""
        from tkinter import filedialog

        file_path = filedialog.askopenfilename(
            title="导入设置文件",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )

        if file_path:
            try:
                import json
                with open(file_path, 'r', encoding='utf-8') as f:
                    imported_settings = json.load(f)

                self.settings_data = {**self.default_settings, **imported_settings}
                self._apply_settings_to_ui()
                messagebox.showinfo("成功", "设置导入成功")

            except Exception as e:
                messagebox.showerror("错误", f"导入设置失败: {e}")

    def _export_settings(self):
        """导出设置"""
        from tkinter import filedialog

        file_path = filedialog.asksaveasfilename(
            title="导出设置文件",
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )

        if file_path:
            try:
                current_settings = self._get_current_settings()
                import json
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(current_settings, f, ensure_ascii=False, indent=2)

                messagebox.showinfo("成功", "设置导出成功")

            except Exception as e:
                messagebox.showerror("错误", f"导出设置失败: {e}")

    def _apply_settings(self):
        """应用设置"""
        try:
            # 获取当前设置
            current_settings = self._get_current_settings()

            # 保存到状态管理器
            if self.state_manager:
                self.state_manager.set_state('settings', current_settings)

            # 应用到界面
            self._apply_settings_to_interface(current_settings)

            # 显示成功消息
            self._show_success_message("设置应用成功！")

            logger.info("设置已应用")

        except Exception as e:
            logger.error(f"应用设置失败: {e}")
            messagebox.showerror("错误", f"应用设置失败: {e}")

    def _apply_settings_to_interface(self, settings: Dict[str, Any]):
        """将设置应用到界面"""
        try:
            # 应用字体设置
            font_settings = settings.get("font", {})
            if self.main_window:
                self._apply_font_to_main_window(font_settings)

            # 应用主题设置
            ui_settings = settings.get("ui", {})
            if ui_settings.get("theme") == "light":
                ctk.set_appearance_mode("light")
            else:
                ctk.set_appearance_mode("dark")

            logger.info("设置已应用到主界面")

        except Exception as e:
            logger.error(f"应用设置到界面失败: {e}")

    def _apply_font_to_main_window(self, font_settings: Dict[str, Any]):
        """应用字体设置到主窗口"""
        try:
            if not self.main_window:
                return

            family = font_settings.get("family", "Microsoft YaHei UI")
            size = font_settings.get("size", 12)
            weight = font_settings.get("weight", "normal")

            # 创建字体
            font_kwargs = {"family": family, "size": size}
            if weight == "bold":
                font_kwargs["weight"] = "bold"

            app_font = ctk.CTkFont(**font_kwargs)

            # 这里可以扩展到更多组件
            logger.info(f"应用字体设置: {family} {size}px {weight}")

        except Exception as e:
            logger.error(f"应用字体设置失败: {e}")

    def _show_success_message(self, message: str):
        """显示成功消息（现代化通知）"""
        if self.main_window and hasattr(self.main_window, '_show_modern_notification'):
            self.main_window._show_modern_notification(message, "success")
        else:
            messagebox.showinfo("成功", message)

    def set_preview_callback(self, callback: Callable):
        """设置预览回调"""
        self.preview_callback = callback

    def get_settings(self) -> Dict[str, Any]:
        """获取当前设置"""
        return self._get_current_settings()