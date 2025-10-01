# ui/other_settings.py
# -*- coding: utf-8 -*-
import customtkinter as ctk
from tkinter import filedialog, messagebox
from .chinese_labels import chinese_labels

def build_other_settings_tab(self):
    self.other_settings_tab = self.tabview.add(chinese_labels["other_settings_tab"])
    self.other_settings_tab.columnconfigure(0, weight=1)
    self.other_settings_tab.rowconfigure(1, weight=1)

    # WebDAV配置标签
    label = ctk.CTkLabel(self.other_settings_tab, text=chinese_labels["webdav_config"], font=("Microsoft YaHei", 14, "bold"))
    label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

    # WebDAV配置框架
    webdav_frame = ctk.CTkFrame(self.other_settings_tab)
    webdav_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
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
    btn_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
    btn_frame.columnconfigure((0, 1), weight=1)

    # 加载按钮
    load_btn = ctk.CTkButton(btn_frame, text=chinese_labels["refresh"], command=self.load_other_settings, font=("Microsoft YaHei", 12))
    load_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

    # 保存按钮
    save_btn = ctk.CTkButton(btn_frame, text=chinese_labels["save"], command=self.save_other_settings, font=("Microsoft YaHei", 12))
    save_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

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
