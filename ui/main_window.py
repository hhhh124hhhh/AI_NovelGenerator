# ui/main_window.py
# -*- coding: utf-8 -*-
import os
import threading
import logging
import traceback
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from .role_library import RoleLibrary
from llm_adapters import create_llm_adapter

# 导入高级日志系统
from advanced_logger import main_logger, ui_logger, llm_logger, log_ui_action, log_error

from config_manager import load_config, save_config, test_llm_config, test_embedding_config
from utils import read_file, save_string_to_txt, clear_file_content
from tooltips import tooltips
from .chinese_labels import chinese_labels

from ui.context_menu import TextWidgetContextMenu
from ui.main_tab import build_main_tab, build_left_layout, build_right_layout
from ui.config_tab import build_config_tabview, load_config_btn, save_config_btn
from ui.novel_params_tab import build_novel_params_area, build_optional_buttons_area
from ui.generation_handlers import (
    generate_novel_architecture_ui,
    generate_chapter_blueprint_ui,
    generate_chapter_draft_ui,
    finalize_chapter_ui,
    do_consistency_check,
    import_knowledge_handler,
    clear_vectorstore_handler,
    show_plot_arcs_ui,
    generate_batch_ui
)
from ui.setting_tab import build_setting_tab, load_novel_architecture, save_novel_architecture
from ui.directory_tab import build_directory_tab, load_chapter_blueprint, save_chapter_blueprint
from ui.character_tab import build_character_tab, load_character_state, save_character_state
from ui.summary_tab import build_summary_tab, load_global_summary, save_global_summary
from ui.chapters_tab import build_chapters_tab, refresh_chapters_list, on_chapter_selected, load_chapter_content, save_current_chapter, prev_chapter, next_chapter
from ui.other_settings import build_other_settings_tab

# 类型注解
from typing import TYPE_CHECKING, Dict, Any
if TYPE_CHECKING:
    from customtkinter import CTkTextbox

# 获取日志记录器
logger = logging.getLogger(__name__)


class NovelGeneratorGUI:
    """
    小说生成器的主GUI类，包含所有的界面布局、事件处理、与后端逻辑的交互等。
    """
    def __init__(self, master, theme_manager=None):
        self.master = master
        self.master.title("AI小说生成器")
        try:
            if os.path.exists("icon.ico"):
                self.master.iconbitmap("icon.ico")
        except Exception:
            pass
        self.master.geometry("1350x840")

        # 初始化主题系统
        self.theme_manager = theme_manager
        if self.theme_manager:
            # 订阅主题变化事件
            self.theme_manager.subscribe(self._on_theme_changed)

        # 初始化当前主题变量
        self.current_theme_var = ctk.StringVar(value="默认")
        
        # 初始化字体设置变量
        self.reading_font_var = ctk.StringVar(value="Microsoft YaHei UI")
        self.reading_size_var = ctk.StringVar(value="14")
        self.editing_font_var = ctk.StringVar(value="Microsoft YaHei UI")
        self.editing_size_var = ctk.StringVar(value="13")
        self.line_spacing_var = ctk.StringVar(value="1.5")

        # 添加utils模块引用
        import utils
        self.utils = utils

        # 绑定生成处理函数
        from ui.generation_handlers import (
            generate_novel_architecture_ui,
            generate_chapter_blueprint_ui,
            generate_chapter_draft_ui,
            finalize_chapter_ui,
            do_consistency_check,
            import_knowledge_handler,
            clear_vectorstore_handler,
            show_plot_arcs_ui,
            generate_batch_ui
        )
        
        self.generate_novel_architecture_ui = generate_novel_architecture_ui.__get__(self, self.__class__)
        self.generate_chapter_blueprint_ui = generate_chapter_blueprint_ui.__get__(self, self.__class__)
        self.generate_chapter_draft_ui = generate_chapter_draft_ui.__get__(self, self.__class__)
        self.finalize_chapter_ui = finalize_chapter_ui.__get__(self, self.__class__)
        self.do_consistency_check = do_consistency_check.__get__(self, self.__class__)
        self.import_knowledge_handler = import_knowledge_handler.__get__(self, self.__class__)
        self.clear_vectorstore_handler = clear_vectorstore_handler.__get__(self, self.__class__)
        self.show_plot_arcs_ui = show_plot_arcs_ui.__get__(self, self.__class__)
        self.generate_batch_ui = generate_batch_ui.__get__(self, self.__class__)

        # 绑定设置标签页函数
        from ui.setting_tab import load_novel_architecture, save_novel_architecture
        self.load_novel_architecture = load_novel_architecture.__get__(self, self.__class__)
        self.save_novel_architecture = save_novel_architecture.__get__(self, self.__class__)

        # 绑定目录标签页函数
        from ui.directory_tab import load_chapter_blueprint, save_chapter_blueprint
        self.load_chapter_blueprint = load_chapter_blueprint.__get__(self, self.__class__)
        self.save_chapter_blueprint = save_chapter_blueprint.__get__(self, self.__class__)

        # 绑定角色标签页函数
        from ui.character_tab import load_character_state, save_character_state
        self.load_character_state = load_character_state.__get__(self, self.__class__)
        self.save_character_state = save_character_state.__get__(self, self.__class__)

        # 绑定摘要标签页函数
        from ui.summary_tab import load_global_summary, save_global_summary
        self.load_global_summary = load_global_summary.__get__(self, self.__class__)
        self.save_global_summary = save_global_summary.__get__(self, self.__class__)

        # 绑定章节标签页函数
        from ui.chapters_tab import refresh_chapters_list, on_chapter_selected, load_chapter_content, save_current_chapter, prev_chapter, next_chapter
        self.refresh_chapters_list = refresh_chapters_list.__get__(self, self.__class__)
        self.on_chapter_selected = on_chapter_selected.__get__(self, self.__class__)
        self.load_chapter_content = load_chapter_content.__get__(self, self.__class__)
        self.save_current_chapter = save_current_chapter.__get__(self, self.__class__)
        self.prev_chapter = prev_chapter.__get__(self, self.__class__)
        self.next_chapter = next_chapter.__get__(self, self.__class__)

        # 绑定其他设置标签页函数
        from ui.other_settings import save_theme_settings
        self.save_theme_settings = save_theme_settings.__get__(self, self.__class__)

        # 记录UI初始化
        log_ui_action("初始化主窗口")

        # --------------- 配置文件路径 ---------------
        self.config_file = "config.json"
        self.loaded_config = load_config(self.config_file)

        if self.loaded_config:
            last_llm = next(iter(self.loaded_config["llm_configs"].values())).get("interface_format", "OpenAI")

            last_embedding = self.loaded_config.get("last_embedding_interface_format", "OpenAI")
        else:
            last_llm = "OpenAI"
            last_embedding = "OpenAI"

        # if self.loaded_config and "llm_configs" in self.loaded_config and last_llm in self.loaded_config["llm_configs"]:
        #     llm_conf = next(iter(self.loaded_config["llm_configs"]))
        # else:
        #     llm_conf = {
        #         "api_key": "",
        #         "base_url": "https://api.openai.com/v1",
        #         "model_name": "gpt-4o-mini",
        #         "temperature": 0.7,
        #         "max_tokens": 8192,
        #         "timeout": 600
        #     }
        llm_conf = next(iter(self.loaded_config["llm_configs"].values()))
        choose_configs = self.loaded_config.get("choose_configs", {})


        if self.loaded_config and "embedding_configs" in self.loaded_config and last_embedding in self.loaded_config["embedding_configs"]:
            emb_conf = self.loaded_config["embedding_configs"][last_embedding]
        else:
            emb_conf = {
                "api_key": "",
                "base_url": "https://api.openai.com/v1",
                "model_name": "text-embedding-ada-002",
                "retrieval_k": 4
            }

        # PenBo 增加代理功能支持
        proxy_url = self.loaded_config["proxy_setting"]["proxy_url"]
        proxy_port = self.loaded_config["proxy_setting"]["proxy_port"]
        if self.loaded_config["proxy_setting"]["enabled"]:
            os.environ['HTTP_PROXY'] = f"http://{proxy_url}:{proxy_port}"
            os.environ['HTTPS_PROXY'] = f"http://{proxy_url}:{proxy_port}"
        else:
            os.environ.pop('HTTP_PROXY', None)  
            os.environ.pop('HTTPS_PROXY', None)



        # -- LLM通用参数 --
        # self.llm_conf_name = next(iter(self.loaded_config["llm_configs"]))
        self.api_key_var = ctk.StringVar(value=llm_conf.get("api_key", ""))
        self.base_url_var = ctk.StringVar(value=llm_conf.get("base_url", "https://api.openai.com/v1"))
        self.interface_format_var = ctk.StringVar(value=llm_conf.get("interface_format", "OpenAI"))
        self.model_name_var = ctk.StringVar(value=llm_conf.get("model_name", "gpt-4o-mini"))
        self.temperature_var = ctk.DoubleVar(value=llm_conf.get("temperature", 0.7))
        self.max_tokens_var = ctk.IntVar(value=llm_conf.get("max_tokens", 8192))
        self.timeout_var = ctk.IntVar(value=llm_conf.get("timeout", 600))
        self.interface_config_var = ctk.StringVar(value=next(iter(self.loaded_config["llm_configs"])))



        # -- Embedding相关 --
        self.embedding_interface_format_var = ctk.StringVar(value=last_embedding)
        self.embedding_api_key_var = ctk.StringVar(value=emb_conf.get("api_key", ""))
        self.embedding_url_var = ctk.StringVar(value=emb_conf.get("base_url", "https://api.openai.com/v1"))
        self.embedding_model_name_var = ctk.StringVar(value=emb_conf.get("model_name", "text-embedding-ada-002"))
        self.embedding_retrieval_k_var = ctk.StringVar(value=str(emb_conf.get("retrieval_k", 4)))


        # -- 生成配置相关 --
        # 确保默认配置包含在可用配置中
        available_configs = list(self.loaded_config.get("llm_configs", {}).keys())
        default_architecture = choose_configs.get("architecture_llm", "DeepSeek V3")
        default_chapter_outline = choose_configs.get("chapter_outline_llm", "DeepSeek V3")
        default_final_chapter = choose_configs.get("final_chapter_llm", "DeepSeek V3")
        default_consistency_review = choose_configs.get("consistency_review_llm", "DeepSeek V3")
        default_prompt_draft = choose_configs.get("prompt_draft_llm", "DeepSeek V3")
        
        # 如果默认配置不在可用配置中，使用第一个可用配置
        if default_architecture not in available_configs and available_configs:
            default_architecture = available_configs[0]
        if default_chapter_outline not in available_configs and available_configs:
            default_chapter_outline = available_configs[0]
        if default_final_chapter not in available_configs and available_configs:
            default_final_chapter = available_configs[0]
        if default_consistency_review not in available_configs and available_configs:
            default_consistency_review = available_configs[0]
        if default_prompt_draft not in available_configs and available_configs:
            default_prompt_draft = available_configs[0]

        self.architecture_llm_var = ctk.StringVar(value=default_architecture)
        self.chapter_outline_llm_var = ctk.StringVar(value=default_chapter_outline)
        self.final_chapter_llm_var = ctk.StringVar(value=default_final_chapter)
        self.consistency_review_llm_var = ctk.StringVar(value=default_consistency_review)
        self.prompt_draft_llm_var = ctk.StringVar(value=default_prompt_draft)

        # -- 小说参数相关 --
        if self.loaded_config and "other_params" in self.loaded_config:
            op = self.loaded_config["other_params"]
            self.topic_default = op.get("topic", "")
            self.genre_var = ctk.StringVar(value=op.get("genre", "玄幻"))
            self.num_chapters_var = ctk.StringVar(value=str(op.get("num_chapters", 10)))
            self.word_number_var = ctk.StringVar(value=str(op.get("word_number", 3000)))
            self.filepath_var = ctk.StringVar(value=op.get("filepath", ""))
            self.chapter_num_var = ctk.StringVar(value=str(op.get("chapter_num", "1")))
            self.characters_involved_var = ctk.StringVar(value=op.get("characters_involved", ""))
            self.key_items_var = ctk.StringVar(value=op.get("key_items", ""))
            self.scene_location_var = ctk.StringVar(value=op.get("scene_location", ""))
            self.time_constraint_var = ctk.StringVar(value=op.get("time_constraint", ""))
            self.user_guidance_default = op.get("user_guidance", "")
            self.webdav_url_var = ctk.StringVar(value=op.get("webdav_url", ""))
            self.webdav_username_var = ctk.StringVar(value=op.get("webdav_username", ""))
            self.webdav_password_var = ctk.StringVar(value=op.get("webdav_password", ""))

        else:
            self.topic_default = ""
            self.genre_var = ctk.StringVar(value="玄幻")
            self.num_chapters_var = ctk.StringVar(value="10")
            self.word_number_var = ctk.StringVar(value="3000")
            self.filepath_var = ctk.StringVar(value="")
            self.chapter_num_var = ctk.StringVar(value="1")
            self.characters_involved_var = ctk.StringVar(value="")
            self.key_items_var = ctk.StringVar(value="")
            self.scene_location_var = ctk.StringVar(value="")
            self.time_constraint_var = ctk.StringVar(value="")
            self.user_guidance_default = ""

        # --------------- 整体Tab布局 ---------------
        self.tabview = ctk.CTkTabview(self.master)
        self.tabview.pack(fill="both", expand=True)

        # 创建各个标签页
        build_main_tab(self)
        build_config_tabview(self)
        build_novel_params_area(self, start_row=1)
        build_optional_buttons_area(self, start_row=2)
        build_setting_tab(self)
        build_directory_tab(self)
        build_character_tab(self)
        build_summary_tab(self)
        build_chapters_tab(self)
        build_other_settings_tab(self)

        # 加载字体设置
        self.load_font_settings()

        # 类型注解属性
        self.log_text: 'CTkTextbox'
        self.chapter_result: 'CTkTextbox'
        self.char_inv_text: 'CTkTextbox'
        # 其他标签页的文本框组件
        self.novel_architecture_text: 'CTkTextbox'
        self.chapter_blueprint_text: 'CTkTextbox'
        self.character_state_text: 'CTkTextbox'
        self.global_summary_text: 'CTkTextbox'
        self.chapter_content_text: 'CTkTextbox'

    def get_theme_spacing(self, size_name: str = 'md') -> int:
        """
        获取主题间距值
        
        Args:
            size_name: 间距名称 (xs, sm, md, lg, xl, xxl)
            
        Returns:
            int: 间距值
        """
        if self.theme_manager:
            return self.theme_manager.get_spacing(size_name)
        # 默认间距值
        spacing_map = {
            'xs': 2,
            'sm': 4,
            'md': 8,
            'lg': 16,
            'xl': 24,
            'xxl': 32
        }
        return spacing_map.get(size_name, 8)

    # ----------------- 通用辅助函数 -----------------
    def show_tooltip(self, key: str):
        info_text = tooltips.get(key, "暂无说明")
        messagebox.showinfo("参数说明", info_text)

    def safe_get_int(self, var, default=1):
        try:
            val_str = str(var.get()).strip()
            return int(val_str)
        except:
            var.set(str(default))
            return default

    def log(self, message: str):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")
        # 同时记录到日志文件
        main_logger.info(message)

    def safe_log(self, message: str):
        self.master.after(0, lambda: self.log(message))

    def disable_button_safe(self, btn):
        self.master.after(0, lambda: btn.configure(state="disabled"))

    def enable_button_safe(self, btn):
        self.master.after(0, lambda: btn.configure(state="normal"))

    def handle_exception(self, context: str):
        full_message = f"{context}\n{traceback.format_exc()}"
        logging.error(full_message)
        self.safe_log(full_message)
        log_error(context, traceback.format_exc())

    def show_chapter_in_textbox(self, text: str):
        self.chapter_result.delete("0.0", "end")
        self.chapter_result.insert("0.0", text)
        self.chapter_result.see("end")
    
    def test_llm_config(self):
        """
        测试当前的LLM配置是否可用
        """
        interface_format = self.interface_format_var.get().strip()
        api_key = self.api_key_var.get().strip()
        base_url = self.base_url_var.get().strip()
        model_name = self.model_name_var.get().strip()
        temperature = self.temperature_var.get()
        max_tokens = self.max_tokens_var.get()
        timeout = self.timeout_var.get()
        
        # 记录测试操作
        log_ui_action("测试LLM配置", f"接口格式: {interface_format}, 模型: {model_name}")

        test_llm_config(
            interface_format=interface_format,
            api_key=api_key,
            base_url=base_url,
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            log_func=self.safe_log,
            handle_exception_func=self.handle_exception
        )

    def test_embedding_config(self):
        """
        测试当前的Embedding配置是否可用
        """
        api_key = self.embedding_api_key_var.get().strip()
        base_url = self.embedding_url_var.get().strip()
        interface_format = self.embedding_interface_format_var.get().strip()
        model_name = self.embedding_model_name_var.get().strip()
        
        # 记录测试操作
        log_ui_action("测试Embedding配置", f"接口格式: {interface_format}, 模型: {model_name}")

        test_embedding_config(
            api_key=api_key,
            base_url=base_url,
            interface_format=interface_format,
            model_name=model_name,
            log_func=self.safe_log,
            handle_exception_func=self.handle_exception
        )
    
    def browse_folder(self):
        selected_dir = filedialog.askdirectory()
        if selected_dir:
            self.filepath_var.set(selected_dir)

    def show_character_import_window(self):
        """显示角色导入窗口"""
        import_window = ctk.CTkToplevel(self.master)
        import_window.title("导入角色信息")
        import_window.geometry("600x500")
        import_window.transient(self.master)  # 设置为父窗口的临时窗口
        import_window.grab_set()  # 保持窗口在顶层
        
        # 记录操作
        log_ui_action("显示角色导入窗口")
        
        # 主容器
        main_frame = ctk.CTkFrame(import_window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 滚动容器
        scroll_frame = ctk.CTkScrollableFrame(main_frame)
        scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 获取角色库路径
        role_lib_path = os.path.join(self.filepath_var.get().strip(), "角色库")
        self.selected_roles = []  # 存储选中的角色名称
        
        # 动态加载角色分类
        if os.path.exists(role_lib_path):
            # 配置网格布局参数
            scroll_frame.columnconfigure(0, weight=1)
            max_roles_per_row = 4
            current_row = 0
            
            for category in os.listdir(role_lib_path):
                category_path = os.path.join(role_lib_path, category)
                if os.path.isdir(category_path):
                    # 创建分类容器
                    category_frame = ctk.CTkFrame(scroll_frame)
                    category_frame.grid(row=current_row, column=0, sticky="w", pady=(10,5), padx=5)
                    
                    # 添加分类标签
                    category_label = ctk.CTkLabel(category_frame, text=f"【{category}】", 
                                                font=("Microsoft YaHei", 12, "bold"))
                    category_label.grid(row=0, column=0, padx=(0,10), sticky="w")
                    
                    # 初始化角色排列参数
                    role_count = 0
                    row_num = 0
                    col_num = 1  # 从第1列开始（第0列是分类标签）
                    
                    # 添加角色复选框
                    for role_file in os.listdir(category_path):
                        if role_file.endswith(".txt"):
                            role_name = os.path.splitext(role_file)[0]
                            if not any(name == role_name for _, name in self.selected_roles):
                                chk = ctk.CTkCheckBox(category_frame, text=role_name)
                                chk.grid(row=row_num, column=col_num, padx=5, pady=2, sticky="w")
                                self.selected_roles.append((chk, role_name))
                                
                                # 更新行列位置
                                role_count += 1
                                col_num += 1
                                if col_num > max_roles_per_row:
                                    col_num = 1
                                    row_num += 1
                    
                    # 如果没有角色，调整分类标签占满整行
                    if role_count == 0:
                        category_label.grid(columnspan=max_roles_per_row+1, sticky="w")
                    
                    # 更新主布局的行号
                    current_row += 1
                    
                    # 添加分隔线
                    separator = ctk.CTkFrame(scroll_frame, height=1, fg_color="gray")
                    separator.grid(row=current_row, column=0, sticky="ew", pady=5)
                    current_row += 1
        
        # 底部按钮框架
        btn_frame = ctk.CTkFrame(main_frame)
        btn_frame.pack(fill="x", pady=10)
        
        # 选择按钮
        def confirm_selection():
            selected = [name for chk, name in self.selected_roles if chk.get() == 1]
            self.char_inv_text.delete("0.0", "end")
            self.char_inv_text.insert("0.0", ", ".join(selected))
            import_window.destroy()
            
        btn_confirm = ctk.CTkButton(btn_frame, text="选择", command=confirm_selection)
        btn_confirm.pack(side="left", padx=20)
        
        # 取消按钮
        btn_cancel = ctk.CTkButton(btn_frame, text="取消", command=import_window.destroy)
        btn_cancel.pack(side="right", padx=20)

    def show_role_library(self):
        save_path = self.filepath_var.get().strip()
        if not save_path:
            messagebox.showwarning("警告", "请先设置保存路径")
            return
        
        # 记录操作
        log_ui_action("显示角色库", f"保存路径: {save_path}")
        
        # 初始化LLM适配器
        llm_adapter = create_llm_adapter(
            interface_format=self.interface_format_var.get(),
            base_url=self.base_url_var.get(),
            model_name=self.model_name_var.get(),
            api_key=self.api_key_var.get(),
            temperature=self.temperature_var.get(),
            max_tokens=self.max_tokens_var.get(),
            timeout=self.timeout_var.get()
        )
        
        # 传递LLM适配器实例到角色库
        if hasattr(self, '_role_lib'):
            if self._role_lib.window and self._role_lib.window.winfo_exists():
                self._role_lib.window.destroy()
        
        self._role_lib = RoleLibrary(self.master, save_path, llm_adapter)  # 新增参数

    def load_other_settings(self):
        """加载其他设置"""
        try:
            config = load_config(self.config_file)
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
            config = load_config(self.config_file)
            if not config:
                config = {}

            if "webdav_config" not in config:
                config["webdav_config"] = {}

            config["webdav_config"]["webdav_url"] = self.webdav_url_var.get()
            config["webdav_config"]["webdav_username"] = self.webdav_username_var.get()
            config["webdav_config"]["webdav_password"] = self.webdav_password_var.get()

            if save_config(config, self.config_file):
                self.log("WebDAV配置已保存。")
            else:
                self.log("保存WebDAV配置失败。")
        except Exception as e:
            self.log(f"保存WebDAV配置时出错: {str(e)}")

    def on_theme_changed(self, theme_name: str):
        """主题变化回调函数"""
        try:
            if hasattr(self, 'theme_manager') and self.theme_manager:
                # 更新当前主题显示
                if hasattr(self, 'current_theme_var'):
                    self.current_theme_var.set(theme_name)
                
                self.log(f"主题已切换到: {theme_name}")

                # 保存主题偏好设置
                self.theme_manager.save_theme_preferences()

                # 记录主题切换操作
                log_ui_action("主题切换", f"新主题: {theme_name}")
        except Exception as e:
            self.log(f"主题切换失败: {str(e)}")
            log_error("主题切换失败", str(e))

    def _on_theme_changed(self, theme_name: str, theme_data: Dict[str, Any]) -> None:
        """
        主题变化回调函数 - 应用新主题到整个界面
        
        Args:
            theme_name: 新主题名称
            theme_data: 新主题数据
        """
        try:
            # 更新当前主题显示
            try:
                self.current_theme_var.set(theme_name)
            except:
                pass  # current_theme_var 可能在其他地方定义
            
            self.log(f"主题已切换到: {theme_name}")
            
            # 应用新主题到整个界面
            self._apply_theme_to_ui(theme_data)
            
            # 保存主题偏好设置
            if self.theme_manager:
                self.theme_manager.save_theme_preferences()
            
            # 记录主题切换操作
            log_ui_action("主题切换", f"新主题: {theme_name}")
        except Exception as e:
            self.log(f"主题切换失败: {str(e)}")
            log_error("主题切换失败", str(e))

    def _apply_theme_to_ui(self, theme_data: Dict[str, Any]) -> None:
        """
        应用主题到整个用户界面
        
        Args:
            theme_data: 主题数据
        """
        try:
            # 获取主题颜色
            colors = theme_data.get('colors', {})
            background_color = colors.get('background', '#1E1E1E')
            text_color = colors.get('text', '#CCCCCC')
            primary_color = colors.get('primary', '#0078D4')
            surface_color = colors.get('surface', '#252526')
            border_color = colors.get('border', '#3E3E42')
            
            # 更新主窗口背景色
            self.master.configure(fg_color=background_color)
            
            # 更新标签页背景色
            if hasattr(self, 'tabview'):
                self.tabview.configure(fg_color=background_color)
                
                # 更新所有标签页的内容
                for tab_name in self.tabview._tab_dict.keys():
                    tab = self.tabview.tab(tab_name)
                    tab.configure(fg_color=background_color)
                    
                    # 更新标签页内所有组件的颜色
                    self._update_widget_colors(tab, theme_data)
            
            # 更新当前主题显示
            try:
                current_theme = self.theme_manager.get_current_theme() if self.theme_manager else "默认"
                self.current_theme_var.set(current_theme)
            except:
                pass  # current_theme_var 可能在其他地方定义
                
        except Exception as e:
            logger.error(f"应用主题到UI失败: {e}")

    def _update_widget_colors(self, parent_widget, theme_data: Dict[str, Any]) -> None:
        """
        递归更新组件颜色
        
        Args:
            parent_widget: 父组件
            theme_data: 主题数据
        """
        try:
            # 获取主题颜色
            colors = theme_data.get('colors', {})
            background_color = colors.get('background', '#1E1E1E')
            surface_color = colors.get('surface', '#252526')
            text_color = colors.get('text', '#CCCCCC')
            border_color = colors.get('border', '#3E3E42')
            primary_color = colors.get('primary', '#0078D4')
            
            # 更新父组件颜色
            if hasattr(parent_widget, 'configure'):
                try:
                    parent_widget.configure(fg_color=surface_color)
                except:
                    pass
            
            # 递归更新子组件
            if hasattr(parent_widget, 'winfo_children'):
                for child in parent_widget.winfo_children():
                    # 更新组件颜色
                    if hasattr(child, 'configure'):
                        try:
                            # 根据组件类型应用不同的颜色
                            if isinstance(child, (ctk.CTkFrame, ctk.CTkScrollableFrame)):
                                child.configure(fg_color=surface_color, border_color=border_color)
                            elif isinstance(child, ctk.CTkLabel):
                                child.configure(text_color=text_color)
                            elif isinstance(child, ctk.CTkButton):
                                # 保持按钮的原有样式，只更新文本颜色
                                child.configure(text_color=text_color)
                            elif isinstance(child, (ctk.CTkEntry, ctk.CTkTextbox)):
                                child.configure(fg_color=surface_color, text_color=text_color, border_color=border_color)
                            elif isinstance(child, ctk.CTkTabview):
                                child.configure(fg_color=background_color)
                            elif isinstance(child, ctk.CTkOptionMenu):
                                child.configure(fg_color=surface_color, text_color=text_color, button_color=primary_color)
                        except:
                            pass
                    
                    # 递归处理子组件
                    self._update_widget_colors(child, theme_data)
        except Exception as e:
            logger.error(f"更新组件颜色失败: {e}")

    def reset_fonts(self):
        """
        重置字体设置到默认值
        """
        self.reading_font_var.set("Microsoft YaHei UI")
        self.reading_size_var.set("14")
        self.editing_font_var.set("Microsoft YaHei UI")
        self.editing_size_var.set("13")
        self.line_spacing_var.set("1.5")
        self.log("字体设置已重置为默认值")
        # 更新所有文本框的字体
        self.update_all_textbox_fonts()
        # 保存字体设置
        self.save_font_settings()

    def update_all_textbox_fonts(self):
        """
        更新所有文本框的字体设置
        """
        try:
            # 获取当前字体设置
            reading_font = self.reading_font_var.get()
            reading_size = int(self.reading_size_var.get())
            editing_font = self.editing_font_var.get()
            editing_size = int(self.editing_size_var.get())
            
            self.log(f"更新字体设置 - 阅读: {reading_font} {reading_size}, 编辑: {editing_font} {editing_size}")
            
            # 更新主标签页中的文本框
            updated_count = 0
            if hasattr(self, 'chapter_result') and self.chapter_result:
                self.chapter_result.configure(font=(editing_font, editing_size))
                updated_count += 1
                self.log("已更新 chapter_result 字体")
                
            if hasattr(self, 'log_text') and self.log_text:
                self.log_text.configure(font=(reading_font, reading_size))
                updated_count += 1
                self.log("已更新 log_text 字体")
                
            # 更新设置标签页中的文本框
            if hasattr(self, 'novel_architecture_text') and self.novel_architecture_text:
                self.novel_architecture_text.configure(font=(editing_font, editing_size))
                updated_count += 1
                self.log("已更新 novel_architecture_text 字体")
                
            # 更新目录标签页中的文本框
            if hasattr(self, 'chapter_blueprint_text') and self.chapter_blueprint_text:
                self.chapter_blueprint_text.configure(font=(editing_font, editing_size))
                updated_count += 1
                self.log("已更新 chapter_blueprint_text 字体")
                
            # 更新角色标签页中的文本框
            if hasattr(self, 'character_state_text') and self.character_state_text:
                self.character_state_text.configure(font=(editing_font, editing_size))
                updated_count += 1
                self.log("已更新 character_state_text 字体")
                
            # 更新摘要标签页中的文本框
            if hasattr(self, 'global_summary_text') and self.global_summary_text:
                self.global_summary_text.configure(font=(reading_font, reading_size))
                updated_count += 1
                self.log("已更新 global_summary_text 字体")
                
            # 更新章节标签页中的文本框
            if hasattr(self, 'chapter_content_text') and self.chapter_content_text:
                self.chapter_content_text.configure(font=(reading_font, reading_size))
                updated_count += 1
                self.log("已更新 chapter_content_text 字体")
                
            self.log(f"字体更新完成，共更新了 {updated_count} 个文本框")
        except Exception as e:
            self.log(f"更新字体时出错: {str(e)}")
            import traceback
            self.log(f"错误详情: {traceback.format_exc()}")

    def on_font_changed(self, event=None):
        """
        字体设置改变时的回调函数
        """
        self.log("检测到字体设置更改")
        # 更新所有文本框的字体
        self.update_all_textbox_fonts()
        # 保存字体设置
        self.save_font_settings()
        
    def save_font_settings(self):
        """
        保存字体设置到配置文件
        """
        try:
            from config_manager import load_config, save_config
            
            # 加载现有配置
            config = load_config(self.config_file)
            if not config:
                config = {}
                
            # 确保有字体设置部分
            if "font_settings" not in config:
                config["font_settings"] = {}
                
            # 保存字体设置
            config["font_settings"]["reading_font"] = self.reading_font_var.get()
            config["font_settings"]["reading_size"] = self.reading_size_var.get()
            config["font_settings"]["editing_font"] = self.editing_font_var.get()
            config["font_settings"]["editing_size"] = self.editing_size_var.get()
            config["font_settings"]["line_spacing"] = self.line_spacing_var.get()
            
            # 保存配置
            if save_config(config, self.config_file):
                self.log("字体设置已保存")
            else:
                self.log("保存字体设置失败")
        except Exception as e:
            self.log(f"保存字体设置时出错: {str(e)}")
            
    def save_font_settings_main(self):
        """
        保存字体设置到配置文件 (主窗口方法)
        """
        self.save_font_settings()
            
    def load_font_settings(self):
        """
        从配置文件加载字体设置
        """
        try:
            from config_manager import load_config
            
            # 加载配置
            config = load_config(self.config_file)
            if not config or "font_settings" not in config:
                self.log("未找到字体设置配置")
                return
                
            font_settings = config["font_settings"]
            
            # 应用字体设置
            if "reading_font" in font_settings:
                self.reading_font_var.set(font_settings["reading_font"])
            if "reading_size" in font_settings:
                self.reading_size_var.set(font_settings["reading_size"])
            if "editing_font" in font_settings:
                self.editing_font_var.set(font_settings["editing_font"])
            if "editing_size" in font_settings:
                self.editing_size_var.set(font_settings["editing_size"])
            if "line_spacing" in font_settings:
                self.line_spacing_var.set(font_settings["line_spacing"])
                
            self.log("已加载字体设置")
            # 更新所有文本框的字体
            self.update_all_textbox_fonts()
        except Exception as e:
            self.log(f"加载字体设置时出错: {str(e)}")