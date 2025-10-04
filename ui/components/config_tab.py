"""
现代化配置标签页组件 - AI小说生成器的配置管理界面
包含LLM配置、嵌入配置、系统设置等功能
"""

import logging
from typing import Dict, Any, Optional, Callable
import customtkinter as ctk
from tkinter import messagebox
from config_manager import load_config, save_config, test_llm_config, test_embedding_config
from tooltips import tooltips

logger = logging.getLogger(__name__)


class ConfigTab(ctk.CTkFrame):
    """
    现代化配置标签页组件

    功能：
    - LLM模型配置
    - 嵌入模型配置
    - 系统参数设置
    - 配置保存和加载
    - 配置测试功能
    """

    def __init__(self, parent: ctk.CTkFrame, theme_manager, state_manager=None, **kwargs):
        """
        初始化配置标签页

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

        # 配置数据
        self.config_data = {}
        self.llm_configs = {}
        self.embedding_configs = {}

        # 组件引用
        self.config_tabview = None
        self.llm_frame = None
        self.embedding_frame = None
        self.system_frame = None

        # 回调函数
        self.config_changed_callback = None

        # 初始化组件
        self._create_config_layout()
        self._load_current_config()

        logger.debug("ConfigTab 组件初始化完成")

    def _create_config_layout(self):
        """创建配置布局"""
        # 配置主框架
        self.configure(
            corner_radius=8,
            fg_color="transparent"
        )

        # 创建配置选项卡
        self.config_tabview = ctk.CTkTabview(
            self,
            segmented_button_fg_color="#2A2A2A",
            segmented_button_selected_color="#404040",
            segmented_button_unselected_color="#1E1E1E"
        )
        self.config_tabview.pack(fill="both", expand=True, padx=10, pady=10)

        # 添加选项卡
        self.llm_frame = self.config_tabview.add("LLM配置")
        self.embedding_frame = self.config_tabview.add("嵌入配置")
        self.system_frame = self.config_tabview.add("系统设置")

        # 构建各个配置页面
        self._build_llm_config()
        self._build_embedding_config()
        self._build_system_config()

        # 底部按钮区域
        self._create_button_area()

    def _build_llm_config(self):
        """构建LLM配置界面"""
        # LLM配置主框架
        llm_main = ctk.CTkFrame(self.llm_frame, fg_color="#2A2A2A")
        llm_main.pack(fill="both", expand=True, padx=10, pady=10)

        # 配置选项标题
        title_label = ctk.CTkLabel(
            llm_main,
            text="大语言模型配置",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(10, 20))

        # LLM提供商选择
        provider_frame = ctk.CTkFrame(llm_main, fg_color="transparent")
        provider_frame.pack(fill="x", padx=20, pady=5)

        provider_label = ctk.CTkLabel(
            provider_frame,
            text="LLM提供商:",
            width=120,
            anchor="w"
        )
        provider_label.pack(side="left", padx=(0, 10))

        self.llm_provider_var = ctk.StringVar(value="OpenAI")
        self.llm_provider_combo = ctk.CTkComboBox(
            provider_frame,
            variable=self.llm_provider_var,
            values=["OpenAI", "DeepSeek", "Ollama", "Claude", "Custom"],
            command=self._on_llm_provider_changed
        )
        self.llm_provider_combo.pack(side="left", fill="x", expand=True)

        # API密钥
        api_key_frame = ctk.CTkFrame(llm_main, fg_color="transparent")
        api_key_frame.pack(fill="x", padx=20, pady=10)

        api_key_label = ctk.CTkLabel(
            api_key_frame,
            text="API密钥:",
            width=120,
            anchor="w"
        )
        api_key_label.pack(side="left", padx=(0, 10))

        self.api_key_entry = ctk.CTkEntry(
            api_key_frame,
            placeholder_text="输入API密钥",
            show="*"
        )
        self.api_key_entry.pack(side="left", fill="x", expand=True)

        # 基础URL
        base_url_frame = ctk.CTkFrame(llm_main, fg_color="transparent")
        base_url_frame.pack(fill="x", padx=20, pady=5)

        base_url_label = ctk.CTkLabel(
            base_url_frame,
            text="基础URL:",
            width=120,
            anchor="w"
        )
        base_url_label.pack(side="left", padx=(0, 10))

        self.base_url_entry = ctk.CTkEntry(
            base_url_frame,
            placeholder_text="https://api.openai.com/v1"
        )
        self.base_url_entry.pack(side="left", fill="x", expand=True)

        # 模型选择
        model_frame = ctk.CTkFrame(llm_main, fg_color="transparent")
        model_frame.pack(fill="x", padx=20, pady=10)

        model_label = ctk.CTkLabel(
            model_frame,
            text="模型:",
            width=120,
            anchor="w"
        )
        model_label.pack(side="left", padx=(0, 10))

        self.model_var = ctk.StringVar(value="gpt-3.5-turbo")
        self.model_combo = ctk.CTkComboBox(
            model_frame,
            variable=self.model_var,
            values=["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "gpt-4o", "custom"]
        )
        self.model_combo.pack(side="left", fill="x", expand=True)

        # 测试按钮
        test_frame = ctk.CTkFrame(llm_main, fg_color="transparent")
        test_frame.pack(fill="x", padx=20, pady=20)

        test_button = ctk.CTkButton(
            test_frame,
            text="测试LLM配置",
            command=self._test_llm_config,
            fg_color="#404040",
            hover_color="#505050"
        )
        test_button.pack()

    def _build_embedding_config(self):
        """构建嵌入配置界面"""
        # 嵌入配置主框架
        embed_main = ctk.CTkFrame(self.embedding_frame, fg_color="#2A2A2A")
        embed_main.pack(fill="both", expand=True, padx=10, pady=10)

        # 配置选项标题
        title_label = ctk.CTkLabel(
            embed_main,
            text="嵌入模型配置",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(10, 20))

        # 嵌入提供商选择
        provider_frame = ctk.CTkFrame(embed_main, fg_color="transparent")
        provider_frame.pack(fill="x", padx=20, pady=5)

        provider_label = ctk.CTkLabel(
            provider_frame,
            text="嵌入提供商:",
            width=120,
            anchor="w"
        )
        provider_label.pack(side="left", padx=(0, 10))

        self.embed_provider_var = ctk.StringVar(value="OpenAI")
        self.embed_provider_combo = ctk.CTkComboBox(
            provider_frame,
            variable=self.embed_provider_var,
            values=["OpenAI", "HuggingFace", "Custom"],
            command=self._on_embed_provider_changed
        )
        self.embed_provider_combo.pack(side="left", fill="x", expand=True)

        # 嵌入模型
        embed_model_frame = ctk.CTkFrame(embed_main, fg_color="transparent")
        embed_model_frame.pack(fill="x", padx=20, pady=10)

        embed_model_label = ctk.CTkLabel(
            embed_model_frame,
            text="嵌入模型:",
            width=120,
            anchor="w"
        )
        embed_model_label.pack(side="left", padx=(0, 10))

        self.embed_model_var = ctk.StringVar(value="text-embedding-ada-002")
        self.embed_model_combo = ctk.CTkComboBox(
            embed_model_frame,
            variable=self.embed_model_var,
            values=["text-embedding-ada-002", "text-embedding-3-small", "text-embedding-3-large"]
        )
        self.embed_model_combo.pack(side="left", fill="x", expand=True)

        # 向量存储路径
        vectorstore_frame = ctk.CTkFrame(embed_main, fg_color="transparent")
        vectorstore_frame.pack(fill="x", padx=20, pady=10)

        vectorstore_label = ctk.CTkLabel(
            vectorstore_frame,
            text="向量存储路径:",
            width=120,
            anchor="w"
        )
        vectorstore_label.pack(side="left", padx=(0, 10))

        self.vectorstore_entry = ctk.CTkEntry(
            vectorstore_frame,
            placeholder_text="./vectorstore"
        )
        self.vectorstore_entry.pack(side="left", fill="x", expand=True)

        # 测试按钮
        test_frame = ctk.CTkFrame(embed_main, fg_color="transparent")
        test_frame.pack(fill="x", padx=20, pady=20)

        test_button = ctk.CTkButton(
            test_frame,
            text="测试嵌入配置",
            command=self._test_embedding_config,
            fg_color="#404040",
            hover_color="#505050"
        )
        test_button.pack()

    def _build_system_config(self):
        """构建系统配置界面"""
        # 系统配置主框架
        system_main = ctk.CTkFrame(self.system_frame, fg_color="#2A2A2A")
        system_main.pack(fill="both", expand=True, padx=10, pady=10)

        # 配置选项标题
        title_label = ctk.CTkLabel(
            system_main,
            text="系统设置",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(10, 20))

        # 日志级别
        log_frame = ctk.CTkFrame(system_main, fg_color="transparent")
        log_frame.pack(fill="x", padx=20, pady=5)

        log_label = ctk.CTkLabel(
            log_frame,
            text="日志级别:",
            width=120,
            anchor="w"
        )
        log_label.pack(side="left", padx=(0, 10))

        self.log_level_var = ctk.StringVar(value="INFO")
        self.log_level_combo = ctk.CTkComboBox(
            log_frame,
            variable=self.log_level_var,
            values=["DEBUG", "INFO", "WARNING", "ERROR"]
        )
        self.log_level_combo.pack(side="left", fill="x", expand=True)

        # 最大重试次数
        retry_frame = ctk.CTkFrame(system_main, fg_color="transparent")
        retry_frame.pack(fill="x", padx=20, pady=10)

        retry_label = ctk.CTkLabel(
            retry_frame,
            text="最大重试次数:",
            width=120,
            anchor="w"
        )
        retry_label.pack(side="left", padx=(0, 10))

        self.max_retry_var = ctk.IntVar(value=3)
        self.max_retry_slider = ctk.CTkSlider(
            retry_frame,
            from_=0,
            to=10,
            number_of_steps=10,
            variable=self.max_retry_var
        )
        self.max_retry_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.max_retry_label = ctk.CTkLabel(
            retry_frame,
            text="3",
            width=30
        )
        self.max_retry_label.pack(side="left")

        def update_retry_label(value):
            self.max_retry_label.configure(text=str(int(value)))

        self.max_retry_slider.configure(command=update_retry_label)

        # 请求超时
        timeout_frame = ctk.CTkFrame(system_main, fg_color="transparent")
        timeout_frame.pack(fill="x", padx=20, pady=10)

        timeout_label = ctk.CTkLabel(
            timeout_frame,
            text="请求超时(秒):",
            width=120,
            anchor="w"
        )
        timeout_label.pack(side="left", padx=(0, 10))

        self.timeout_var = ctk.IntVar(value=60)
        self.timeout_entry = ctk.CTkEntry(
            timeout_frame,
            width=100
        )
        self.timeout_entry.pack(side="left", padx=(0, 10))
        self.timeout_entry.insert(0, "60")

        timeout_info = ctk.CTkLabel(
            timeout_frame,
            text="10-300秒",
            text_color="gray"
        )
        timeout_info.pack(side="left")

    def _create_button_area(self):
        """创建底部按钮区域"""
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=10, pady=(0, 10))

        # 保存配置按钮
        save_button = ctk.CTkButton(
            button_frame,
            text="保存配置",
            command=self._save_config,
            fg_color="#2E7D32",
            hover_color="#388E3C"
        )
        save_button.pack(side="left", padx=(0, 10))

        # 重置配置按钮
        reset_button = ctk.CTkButton(
            button_frame,
            text="重置配置",
            command=self._reset_config,
            fg_color="#D32F2F",
            hover_color="#F44336"
        )
        reset_button.pack(side="left", padx=(0, 10))

        # 重新加载按钮
        reload_button = ctk.CTkButton(
            button_frame,
            text="重新加载",
            command=self._load_current_config,
            fg_color="#1976D2",
            hover_color="#2196F3"
        )
        reload_button.pack(side="left")

    def _load_current_config(self):
        """加载当前配置"""
        try:
            self.config_data = load_config("config.json")

            # 加载LLM配置
            llm_config = self.config_data.get('llm', {})
            self.llm_provider_var.set(llm_config.get('provider', 'OpenAI'))
            self.api_key_entry.delete(0, 'end')
            self.api_key_entry.insert(0, llm_config.get('api_key', ''))
            self.base_url_entry.delete(0, 'end')
            self.base_url_entry.insert(0, llm_config.get('base_url', 'https://api.openai.com/v1'))
            self.model_var.set(llm_config.get('model', 'gpt-3.5-turbo'))

            # 加载嵌入配置
            embed_config = self.config_data.get('embedding', {})
            self.embed_provider_var.set(embed_config.get('provider', 'OpenAI'))
            self.embed_model_var.set(embed_config.get('model', 'text-embedding-ada-002'))
            self.vectorstore_entry.delete(0, 'end')
            self.vectorstore_entry.insert(0, embed_config.get('vectorstore_path', './vectorstore'))

            # 加载系统配置
            system_config = self.config_data.get('system', {})
            self.log_level_var.set(system_config.get('log_level', 'INFO'))
            self.max_retry_var.set(system_config.get('max_retry', 3))
            self.max_retry_label.configure(text=str(system_config.get('max_retry', 3)))
            self.timeout_var.set(system_config.get('timeout', 60))
            self.timeout_entry.delete(0, 'end')
            self.timeout_entry.insert(0, str(system_config.get('timeout', 60)))

            logger.info("配置加载成功")

        except Exception as e:
            logger.error(f"加载配置失败: {e}")
            messagebox.showerror("错误", f"加载配置失败: {e}")

    def _save_config(self):
        """保存配置"""
        try:
            # 获取超时值
            try:
                timeout_value = int(self.timeout_entry.get())
                timeout_value = max(10, min(300, timeout_value))  # 限制在10-300之间
            except (ValueError, TypeError):
                timeout_value = 60

            # 构建配置数据
            config = {
                'llm': {
                    'provider': self.llm_provider_var.get(),
                    'api_key': self.api_key_entry.get(),
                    'base_url': self.base_url_entry.get(),
                    'model': self.model_var.get()
                },
                'embedding': {
                    'provider': self.embed_provider_var.get(),
                    'model': self.embed_model_var.get(),
                    'vectorstore_path': self.vectorstore_entry.get()
                },
                'system': {
                    'log_level': self.log_level_var.get(),
                    'max_retry': self.max_retry_var.get(),
                    'timeout': timeout_value
                }
            }

            # 保存配置
            success = save_config(config, "config.json")
            if success:
                self.config_data = config
                logger.info("配置保存成功")
                messagebox.showinfo("成功", "配置保存成功！")

                # 通知配置变化
                if self.config_changed_callback:
                    self.config_changed_callback(config)
            else:
                logger.error("配置保存失败")
                messagebox.showerror("错误", "配置保存失败！")

        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            messagebox.showerror("错误", f"保存配置失败: {e}")

    def _reset_config(self):
        """重置配置到默认值"""
        if messagebox.askyesno("确认", "确定要重置所有配置到默认值吗？"):
            try:
                # 重置到默认值
                self.llm_provider_var.set("OpenAI")
                self.api_key_entry.delete(0, 'end')
                self.base_url_entry.delete(0, 'end')
                self.base_url_entry.insert(0, 'https://api.openai.com/v1')
                self.model_var.set("gpt-3.5-turbo")

                self.embed_provider_var.set("OpenAI")
                self.embed_model_var.set("text-embedding-ada-002")
                self.vectorstore_entry.delete(0, 'end')
                self.vectorstore_entry.insert(0, './vectorstore')

                self.log_level_var.set("INFO")
                self.max_retry_var.set(3)
                self.max_retry_label.configure(text="3")
                self.timeout_var.set(60)
                self.timeout_entry.delete(0, 'end')
                self.timeout_entry.insert(0, "60")

                logger.info("配置已重置到默认值")
                messagebox.showinfo("成功", "配置已重置到默认值！")

            except Exception as e:
                logger.error(f"重置配置失败: {e}")
                messagebox.showerror("错误", f"重置配置失败: {e}")

    def _test_llm_config(self):
        """测试LLM配置"""
        try:
            config = {
                'provider': self.llm_provider_var.get(),
                'api_key': self.api_key_entry.get(),
                'base_url': self.base_url_entry.get(),
                'model': self.model_var.get()
            }

            success, message = test_llm_config(config)
            if success:
                messagebox.showinfo("测试成功", f"LLM配置测试成功！\n{message}")
            else:
                messagebox.showerror("测试失败", f"LLM配置测试失败！\n{message}")

        except Exception as e:
            logger.error(f"测试LLM配置失败: {e}")
            messagebox.showerror("错误", f"测试LLM配置失败: {e}")

    def _test_embedding_config(self):
        """测试嵌入配置"""
        try:
            config = {
                'provider': self.embed_provider_var.get(),
                'model': self.embed_model_var.get(),
                'vectorstore_path': self.vectorstore_entry.get()
            }

            success, message = test_embedding_config(config)
            if success:
                messagebox.showinfo("测试成功", f"嵌入配置测试成功！\n{message}")
            else:
                messagebox.showerror("测试失败", f"嵌入配置测试失败！\n{message}")

        except Exception as e:
            logger.error(f"测试嵌入配置失败: {e}")
            messagebox.showerror("错误", f"测试嵌入配置失败: {e}")

    def _on_llm_provider_changed(self, choice):
        """LLM提供商变化处理"""
        # 根据提供商更新模型选项
        if choice == "OpenAI":
            models = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "gpt-4o"]
            self.base_url_entry.delete(0, 'end')
            self.base_url_entry.insert(0, 'https://api.openai.com/v1')
        elif choice == "DeepSeek":
            models = ["deepseek-chat", "deepseek-coder"]
            self.base_url_entry.delete(0, 'end')
            self.base_url_entry.insert(0, 'https://api.deepseek.com')
        elif choice == "Ollama":
            models = ["llama2", "codellama", "mistral", "vicuna"]
            self.base_url_entry.delete(0, 'end')
            self.base_url_entry.insert(0, 'http://localhost:11434')
        else:
            models = ["custom"]

        self.model_combo.configure(values=models)
        if models:
            self.model_var.set(models[0])

    def _on_embed_provider_changed(self, choice):
        """嵌入提供商变化处理"""
        # 根据提供商更新模型选项
        if choice == "OpenAI":
            models = ["text-embedding-ada-002", "text-embedding-3-small", "text-embedding-3-large"]
        elif choice == "HuggingFace":
            models = ["sentence-transformers/all-MiniLM-L6-v2", "sentence-transformers/all-mpnet-base-v2"]
        else:
            models = ["custom"]

        self.embed_model_combo.configure(values=models)
        if models:
            self.embed_model_var.set(models[0])

    def set_config_changed_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """设置配置变化回调函数"""
        self.config_changed_callback = callback

    def get_current_config(self) -> Dict[str, Any]:
        """获取当前配置"""
        return self.config_data

    def apply_theme_style(self, theme_data: Dict[str, Any]):
        """应用主题样式"""
        try:
            colors = theme_data.get('colors', {})

            # 更新标签页样式
            if self.config_tabview:
                self.config_tabview.configure(
                    segmented_button_fg_color=colors.get('surface', '#2A2A2A'),
                    segmented_button_selected_color=colors.get('primary', '#404040'),
                    segmented_button_unselected_color=colors.get('background', '#1E1E1E')
                )

        except Exception as e:
            logger.error(f"应用主题到配置标签页失败: {e}")

    def get_config_info(self) -> Dict[str, Any]:
        """获取配置标签页信息"""
        return {
            'llm_provider': self.llm_provider_var.get(),
            'llm_model': self.model_var.get(),
            'embed_provider': self.embed_provider_var.get(),
            'embed_model': self.embed_model_var.get(),
            'log_level': self.log_level_var.get(),
            'has_config_data': len(self.config_data) > 0,
            'has_callback': self.config_changed_callback is not None
        }