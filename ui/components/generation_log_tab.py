# generation_log_tab.py
# -*- coding: utf-8 -*-
"""
生成日志标签页组件
专门用于显示生成过程日志，提供详细的执行信息
"""

import logging
import threading
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
import customtkinter as ctk
from tkinter import scrolledtext

logger = logging.getLogger(__name__)

class GenerationLogTab(ctk.CTkFrame):
    """
    生成日志标签页

    功能：
    - 实时显示生成过程日志
    - 提供日志过滤和搜索功能
    - 支持日志导出
    - 显示生成进度和状态
    """

    def __init__(self, parent, theme_manager=None, state_manager=None, **kwargs):
        """
        初始化生成日志标签页

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

        # 日志数据
        self.log_entries: List[Dict[str, Any]] = []
        self.log_lock = threading.Lock()
        self.max_log_entries = 1000  # 最大日志条数

        # 过滤设置
        self.current_filter = "all"  # all, info, warning, error, debug
        self.search_term = ""

        # 初始化组件
        self._create_layout()
        self._setup_logging()

        logger.info("生成日志标签页初始化完成")

    def _create_layout(self):
        """创建布局"""
        # 配置主框架
        self.configure(
            corner_radius=8,
            fg_color="transparent"
        )

        # 配置网格布局
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 创建控制栏
        self._create_control_bar()

        # 创建日志显示区域
        self._create_log_display()

        # 创建状态栏
        self._create_status_bar()

    def _create_control_bar(self):
        """创建控制栏"""
        control_frame = ctk.CTkFrame(self, corner_radius=8)
        control_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        control_frame.grid_columnconfigure((1, 2, 3), weight=1)

        # 左侧：过滤器
        filter_frame = ctk.CTkFrame(control_frame)
        filter_frame.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="w")

        filter_label = ctk.CTkLabel(filter_frame, text="过滤器:")
        filter_label.pack(side="left", padx=(0, 5))

        self.filter_var = ctk.StringVar(value="all")
        filter_menu = ctk.CTkOptionMenu(
            filter_frame,
            variable=self.filter_var,
            values=["all", "info", "warning", "error", "debug"],
            command=self._on_filter_changed,
            width=80
        )
        filter_menu.pack(side="left")

        # 中间：搜索框
        search_frame = ctk.CTkFrame(control_frame)
        search_frame.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            placeholder_text="搜索日志...",
            width=200
        )
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", self._on_search_changed)

        # 右侧：操作按钮
        action_frame = ctk.CTkFrame(control_frame)
        action_frame.grid(row=0, column=2, padx=(5, 10), pady=10, sticky="e")

        # 清除日志按钮
        self.clear_btn = ctk.CTkButton(
            action_frame,
            text="清除",
            command=self._clear_logs,
            width=60
        )
        self.clear_btn.pack(side="left", padx=(0, 5))

        # 导出日志按钮
        self.export_btn = ctk.CTkButton(
            action_frame,
            text="导出",
            command=self._export_logs,
            width=60
        )
        self.export_btn.pack(side="left")

        # 实时跟踪开关
        self.follow_var = ctk.BooleanVar(value=True)
        self.follow_checkbox = ctk.CTkCheckBox(
            action_frame,
            text="实时跟踪",
            variable=self.follow_var
        )
        self.follow_checkbox.pack(side="left", padx=(5, 0))

    def _create_log_display(self):
        """创建日志显示区域"""
        # 日志容器
        log_container = ctk.CTkFrame(self, corner_radius=8)
        log_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        log_container.grid_columnconfigure(0, weight=1)
        log_container.grid_rowconfigure(0, weight=1)

        # 使用scrolledtext创建高性能日志显示
        self.log_text = scrolledtext.ScrolledText(
            log_container,
            wrap="word",
            font=("Consolas", 10),
            bg="#1a1a1a",
            fg="#ffffff",
            insertbackground="#ffffff",
            selectbackground="#3498db",
            height=20
        )
        self.log_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # 配置文本标签
        self.log_text.tag_configure("info", foreground="#3498db")
        self.log_text.tag_configure("warning", foreground="#f39c12")
        self.log_text.tag_configure("error", foreground="#e74c3c")
        self.log_text.tag_configure("debug", foreground="#95a5a6")
        self.log_text.tag_configure("success", foreground="#27ae60")
        self.log_text.tag_configure("timestamp", foreground="#7f8c8d")

        # 设置为只读
        self.log_text.configure(state="disabled")

    def _create_status_bar(self):
        """创建状态栏"""
        status_frame = ctk.CTkFrame(self, corner_radius=8)
        status_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(5, 10))
        status_frame.grid_columnconfigure(1, weight=1)

        # 日志统计
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="日志条数: 0",
            font=ctk.CTkFont(size=11)
        )
        self.status_label.pack(side="left", padx=10)

        # 最后更新时间
        self.last_update_label = ctk.CTkLabel(
            status_frame,
            text="最后更新: --",
            font=ctk.CTkFont(size=11)
        )
        self.last_update_label.pack(side="right", padx=10)

    def _setup_logging(self):
        """设置日志处理"""
        # 创建自定义日志处理器
        self.log_handler = GenerationLogHandler(self)
        self.log_handler.setLevel(logging.INFO)

        # 获取根日志记录器
        root_logger = logging.getLogger()
        root_logger.addHandler(self.log_handler)

    def add_log_entry(self, level: str, message: str, module: str = ""):
        """
        添加日志条目

        Args:
            level: 日志级别 (info, warning, error, debug, success)
            message: 日志消息
            module: 模块名称
        """
        with self.log_lock:
            # 创建日志条目
            entry = {
                "timestamp": datetime.now(),
                "level": level,
                "message": message,
                "module": module
            }

            # 添加到列表
            self.log_entries.append(entry)

            # 限制日志数量
            if len(self.log_entries) > self.max_log_entries:
                self.log_entries = self.log_entries[-self.max_log_entries:]

        # 更新显示
        self._update_log_display()

    def _update_log_display(self):
        """更新日志显示"""
        try:
            # 过滤日志条目
            filtered_entries = self._filter_logs()

            # 检查是否需要实时跟踪
            if not self.follow_var.get():
                return

            # 更新文本显示
            self.log_text.configure(state="normal")
            self.log_text.delete(1.0, "end")

            for entry in filtered_entries:
                # 格式化时间戳
                timestamp = entry["timestamp"].strftime("%H:%M:%S")

                # 格式化日志行
                log_line = f"[{timestamp}] "
                if entry["module"]:
                    log_line += f"[{entry['module']}] "
                log_line += f"{entry['message']}\n"

                # 插入文本并应用标签
                start_pos = self.log_text.index("end-1c")
                self.log_text.insert("end", log_line)
                end_pos = self.log_text.index("end-1c")

                # 应用颜色标签
                self.log_text.tag_add(entry["level"], start_pos, end_pos)
                self.log_text.tag_add("timestamp", start_pos, f"{start_pos}+9c")

            # 滚动到底部
            self.log_text.see("end")
            self.log_text.configure(state="disabled")

            # 更新状态栏
            self._update_status_bar()

        except Exception as e:
            logger.error(f"更新日志显示失败: {e}")

    def _filter_logs(self) -> List[Dict[str, Any]]:
        """过滤日志条目"""
        filtered = []

        for entry in self.log_entries:
            # 级别过滤
            if self.current_filter != "all" and entry["level"] != self.current_filter:
                continue

            # 搜索过滤
            if self.search_term:
                search_lower = self.search_term.lower()
                if (search_lower not in entry["message"].lower() and
                    search_lower not in entry["module"].lower()):
                    continue

            filtered.append(entry)

        return filtered

    def _update_status_bar(self):
        """更新状态栏"""
        try:
            # 更新日志条数
            total_entries = len(self.log_entries)
            filtered_entries = len(self._filter_logs())
            self.status_label.configure(
                text=f"日志条数: {filtered_entries}/{total_entries}"
            )

            # 更新最后更新时间
            if self.log_entries:
                last_time = self.log_entries[-1]["timestamp"].strftime("%H:%M:%S")
                self.last_update_label.configure(text=f"最后更新: {last_time}")

        except Exception as e:
            logger.error(f"更新状态栏失败: {e}")

    def _on_filter_changed(self, value):
        """过滤器改变回调"""
        self.current_filter = value
        self._update_log_display()

    def _on_search_changed(self, event):
        """搜索改变回调"""
        self.search_term = self.search_var.get()
        self._update_log_display()

    def _clear_logs(self):
        """清除所有日志"""
        with self.log_lock:
            self.log_entries.clear()

        self._update_log_display()
        self.add_log_entry("info", "日志已清除", "GenerationLogTab")

    def _export_logs(self):
        """导出日志到文件"""
        try:
            from tkinter import filedialog
            from datetime import datetime

            # 选择保存文件
            filename = filedialog.asksaveasfilename(
                title="导出日志",
                defaultextension=".txt",
                filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
                initialfile=f"generation_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            )

            if filename:
                # 过滤并导出日志
                filtered_entries = self._filter_logs()

                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("AI小说生成器 - 生成日志\n")
                    f.write("=" * 50 + "\n")
                    f.write(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"日志条数: {len(filtered_entries)}\n")
                    f.write("=" * 50 + "\n\n")

                    for entry in filtered_entries:
                        timestamp = entry["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
                        f.write(f"[{timestamp}] [{entry['level'].upper()}] ")
                        if entry["module"]:
                            f.write(f"[{entry['module']}] ")
                        f.write(f"{entry['message']}\n")

                self.add_log_entry("success", f"日志已导出到: {filename}", "GenerationLogTab")

        except Exception as e:
            self.add_log_entry("error", f"导出日志失败: {e}", "GenerationLogTab")


class GenerationLogHandler(logging.Handler):
    """自定义日志处理器"""

    def __init__(self, log_tab: GenerationLogTab):
        super().__init__()
        self.log_tab = log_tab

    def emit(self, record):
        """发射日志记录"""
        try:
            # 确定日志级别
            if record.levelno >= logging.ERROR:
                level = "error"
            elif record.levelno >= logging.WARNING:
                level = "warning"
            elif record.levelno >= logging.INFO:
                level = "info"
            else:
                level = "debug"

            # 提取模块名称
            module = record.name.split('.')[-1] if '.' in record.name else record.name

            # 添加到日志标签页
            self.log_tab.add_log_entry(level, record.getMessage(), module)

        except Exception:
            # 避免日志处理本身出错
            pass