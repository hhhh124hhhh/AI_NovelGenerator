# ui/other_settings.py
# -*- coding: utf-8 -*-
import customtkinter as ctk
from tkinter import filedialog, messagebox
from .chinese_labels import chinese_labels

def build_other_settings_tab(self):
    self.other_settings_tab = self.tabview.add(chinese_labels["other_settings_tab"])
    self.other_settings_tab.columnconfigure(0, weight=1)
    self.other_settings_tab.rowconfigure(2, weight=1)

    # 主题设置标签
    theme_label = ctk.CTkLabel(self.other_settings_tab, text="主题设置", font=("Microsoft YaHei", 14, "bold"))
    theme_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

    # 主题设置框架
    theme_frame = ctk.CTkFrame(self.other_settings_tab)
    theme_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
    theme_frame.columnconfigure((0, 1, 2), weight=1)

    # 当前主题显示
    current_theme_label = ctk.CTkLabel(theme_frame, text="当前主题:", font=("Microsoft YaHei", 12))
    current_theme_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")

    self.current_theme_var = ctk.StringVar(value="默认")
    current_theme_display = ctk.CTkLabel(theme_frame, textvariable=self.current_theme_var, font=("Microsoft YaHei", 12))
    current_theme_display.grid(row=0, column=1, padx=5, pady=5, sticky="w")

    # 主题切换按钮
    if hasattr(self, 'theme_manager') and self.theme_manager:
        try:
            from theme_system.components.theme_toggle import ThemeToggleButton
            theme_toggle = ThemeToggleButton(theme_frame, self.theme_manager, self.on_theme_changed)
            theme_toggle.grid(row=0, column=2, padx=5, pady=5, sticky="e")
        except ImportError:
            # 如果主题切换组件不可用，显示一个简单的按钮
            toggle_btn = ctk.CTkButton(
                theme_frame, 
                text="切换主题", 
                command=lambda: self.theme_manager.toggle_theme() if self.theme_manager else None,
                font=("Microsoft YaHei", 12)
            )
            toggle_btn.grid(row=0, column=2, padx=5, pady=5, sticky="e")

    # 字体设置标签
    font_label = ctk.CTkLabel(self.other_settings_tab, text="字体设置", font=("Microsoft YaHei", 14, "bold"))
    font_label.grid(row=2, column=0, padx=10, pady=(10, 5), sticky="w")

    # 字体设置框架
    font_frame = ctk.CTkFrame(self.other_settings_tab)
    font_frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
    font_frame.columnconfigure((0, 1, 2, 3), weight=1)

    # 阅读字体设置
    reading_font_label = ctk.CTkLabel(font_frame, text="阅读字体:", font=("Microsoft YaHei", 12))
    reading_font_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")

    self.reading_font_var = ctk.StringVar(value="Microsoft YaHei UI")
    self.reading_font_combo = ctk.CTkComboBox(
        font_frame,
        variable=self.reading_font_var,
        values=["Microsoft YaHei UI", "Microsoft YaHei", "SimSun", "SimHei", "KaiTi", "FangSong", "Arial", "Times New Roman"],
        font=("Microsoft YaHei", 11),
        command=self.on_font_changed
    )
    self.reading_font_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    # 阅读字体大小
    reading_size_label = ctk.CTkLabel(font_frame, text="大小:", font=("Microsoft YaHei", 12))
    reading_size_label.grid(row=0, column=2, padx=5, pady=5, sticky="e")

    self.reading_size_var = ctk.StringVar(value="14")
    reading_size_combo = ctk.CTkComboBox(
        font_frame,
        variable=self.reading_size_var,
        values=["10", "11", "12", "13", "14", "15", "16", "18", "20", "22", "24"],
        font=("Microsoft YaHei", 11),
        command=self.on_font_changed
    )
    reading_size_combo.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

    # 编辑字体设置
    editing_font_label = ctk.CTkLabel(font_frame, text="编辑字体:", font=("Microsoft YaHei", 12))
    editing_font_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")

    self.editing_font_var = ctk.StringVar(value="Microsoft YaHei UI")
    self.editing_font_combo = ctk.CTkComboBox(
        font_frame,
        variable=self.editing_font_var,
        values=["Microsoft YaHei UI", "Microsoft YaHei", "SimSun", "SimHei", "KaiTi", "FangSong", "Arial", "Times New Roman"],
        font=("Microsoft YaHei", 11),
        command=self.on_font_changed
    )
    self.editing_font_combo.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    # 编辑字体大小
    editing_size_label = ctk.CTkLabel(font_frame, text="大小:", font=("Microsoft YaHei", 12))
    editing_size_label.grid(row=1, column=2, padx=5, pady=5, sticky="e")

    self.editing_size_var = ctk.StringVar(value="13")
    editing_size_combo = ctk.CTkComboBox(
        font_frame,
        variable=self.editing_size_var,
        values=["10", "11", "12", "13", "14", "15", "16", "18", "20", "22", "24"],
        font=("Microsoft YaHei", 11),
        command=self.on_font_changed
    )
    editing_size_combo.grid(row=1, column=3, padx=5, pady=5, sticky="ew")

    # 行间距设置
    line_spacing_label = ctk.CTkLabel(font_frame, text="行间距:", font=("Microsoft YaHei", 12))
    line_spacing_label.grid(row=2, column=0, padx=5, pady=5, sticky="e")

    self.line_spacing_var = ctk.StringVar(value="1.5")
    line_spacing_combo = ctk.CTkComboBox(
        font_frame,
        variable=self.line_spacing_var,
        values=["1.0", "1.2", "1.4", "1.5", "1.6", "1.8", "2.0"],
        font=("Microsoft YaHei", 11),
        command=self.on_font_changed
    )
    line_spacing_combo.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

    # 重置按钮
    reset_fonts_btn = ctk.CTkButton(
        font_frame,
        text="重置字体",
        command=self.reset_fonts,
        font=("Microsoft YaHei", 12)
    )
    reset_fonts_btn.grid(row=2, column=3, padx=5, pady=5, sticky="ew")

    # 保存字体设置按钮
    save_fonts_btn = ctk.CTkButton(
        font_frame,
        text="保存字体设置",
        command=self.save_font_settings,
        font=("Microsoft YaHei", 12)
    )
    save_fonts_btn.grid(row=2, column=2, padx=5, pady=5, sticky="ew")

    # WebDAV配置标签
    label = ctk.CTkLabel(self.other_settings_tab, text=chinese_labels["webdav_config"], font=("Microsoft YaHei", 14, "bold"))
    label.grid(row=4, column=0, padx=10, pady=(10, 5), sticky="w")

    # WebDAV配置框架
    webdav_frame = ctk.CTkFrame(self.other_settings_tab)
    webdav_frame.grid(row=5, column=0, padx=10, pady=5, sticky="nsew")
    webdav_frame.columnconfigure(1, weight=1)

    # WebDAV URL
    url_label = ctk.CTkLabel(webdav_frame, text=chinese_labels["webdav_url"] + ":", font=("Microsoft YaHei", 12))
    url_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
    self.webdav_url_var = ctk.StringVar(value="")
    url_entry = ctk.CTkEntry(webdav_frame, textvariable=self.webdav_url_var, font=("Microsoft YaHei", 12))
    url_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    # WebDAV用户名
    username_label = ctk.CTkLabel(webdav_frame, text=chinese_labels["webdav_username"] + ":", font=("Microsoft YaHei", 12))
    username_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
    self.webdav_username_var = ctk.StringVar(value="")
    username_entry = ctk.CTkEntry(webdav_frame, textvariable=self.webdav_username_var, font=("Microsoft YaHei", 12))
    username_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    # WebDAV密码
    password_label = ctk.CTkLabel(webdav_frame, text=chinese_labels["webdav_password"] + ":", font=("Microsoft YaHei", 12))
    password_label.grid(row=2, column=0, padx=5, pady=5, sticky="e")
    self.webdav_password_var = ctk.StringVar(value="")
    password_entry = ctk.CTkEntry(webdav_frame, textvariable=self.webdav_password_var, font=("Microsoft YaHei", 12), show="*")
    password_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

    # 按钮框架
    btn_frame = ctk.CTkFrame(self.other_settings_tab)
    btn_frame.grid(row=6, column=0, padx=10, pady=5, sticky="ew")
    btn_frame.columnconfigure((0, 1, 2), weight=1)

    # 加载按钮
    load_btn = ctk.CTkButton(btn_frame, text=chinese_labels["refresh"], command=self.load_other_settings, font=("Microsoft YaHei", 12))
    load_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

    # 保存按钮
    save_btn = ctk.CTkButton(btn_frame, text=chinese_labels["save"], command=self.save_other_settings, font=("Microsoft YaHei", 12))
    save_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    # 保存主题设置按钮
    save_theme_btn = ctk.CTkButton(btn_frame, text="保存主题设置", command=self.save_theme_settings, font=("Microsoft YaHei", 12))
    save_theme_btn.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

def load_other_settings(self):
    """加载其他设置"""
    try:
        config = self.config_manager.load_config(self.config_file)
        if config and "webdav_config" in config:
            webdav_config = config["webdav_config"]
            self.webdav_url_var.set(webdav_config.get("webdav_url", ""))
            self.webdav_username_var.set(webdav_config.get("webdav_username", ""))
            self.webdav_password_var.set(webdav_config.get("webdav_password", ""))
            self.log("已加载WebDAV配置。")
        else:
            self.log("未找到WebDAV配置。")
    except Exception as e:
        self.log(f"加载WebDAV配置时出错: {str(e)}")

def save_other_settings(self):
    """保存其他设置"""
    try:
        config = self.config_manager.load_config(self.config_file)
        if not config:
            config = {}
            
        if "webdav_config" not in config:
            config["webdav_config"] = {}
            
        config["webdav_config"]["webdav_url"] = self.webdav_url_var.get()
        config["webdav_config"]["webdav_username"] = self.webdav_username_var.get()
        config["webdav_config"]["webdav_password"] = self.webdav_password_var.get()
        
        if self.config_manager.save_config(config, self.config_file):
            self.log("WebDAV配置已保存。")
        else:
            self.log("保存WebDAV配置失败。")
    except Exception as e:
        self.log(f"保存WebDAV配置时出错: {str(e)}")

def save_font_settings(self):
    """保存字体设置"""
    self.save_font_settings()

def save_theme_settings(self):
    """保存主题设置"""
    try:
        # 保存主题偏好设置
        if hasattr(self, 'theme_manager') and self.theme_manager:
            self.theme_manager.save_theme_preferences()
            self.log("主题设置已保存")
        else:
            self.log("主题管理器不可用")
    except Exception as e:
        self.log(f"保存主题设置时出错: {str(e)}")
