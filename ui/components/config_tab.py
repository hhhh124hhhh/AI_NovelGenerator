"""
现代化配置标签页组件 - AI小说生成器的配置管理界面
包含LLM配置、嵌入配置、系统设置等功能
"""

import logging
import time
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

    def __init__(self, parent: ctk.CTkFrame, theme_manager, state_manager=None, main_window=None, **kwargs):
        """
        初始化配置标签页

        Args:
            parent: 父组件
            theme_manager: 主题管理器
            state_manager: 状态管理器
            main_window: 主窗口引用（用于状态栏更新）
            **kwargs: 其他参数
        """
        # 初始化CustomTkinter Frame
        super().__init__(parent, **kwargs)

        # 存储管理器引用
        self.theme_manager = theme_manager
        self.state_manager = state_manager
        self.main_window = main_window

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

        # 添加日志和异常处理函数
        self._log_func = self._simple_log
        self._handle_exception_func = self._simple_exception_handler

        # 初始化组件
        self._create_config_layout()
        self._load_current_config()

        logger.debug("ConfigTab 组件初始化完成")

    def _simple_log(self, message):
        """简单的日志函数"""
        logger.info(message)
        
    def _simple_exception_handler(self, message):
        """简单的异常处理函数"""
        logger.error(message)

    def _update_status(self, message: str):
        """更新状态栏（如果有主窗口引用）"""
        try:
            if self.main_window and hasattr(self.main_window, '_update_status'):
                self.main_window._update_status(message)
        except Exception as e:
            logger.error(f"更新状态栏失败: {e}")

    def _import_knowledge_base(self):
        """导入知识库"""
        try:
            from tkinter import filedialog
            import os

            # 选择知识库文件
            file_path = filedialog.askopenfilename(
                title="选择知识库文件",
                filetypes=[
                    ("文本文件", "*.txt"),
                    ("Markdown文件", "*.md"),
                    ("Word文档", "*.docx"),
                    ("PDF文件", "*.pdf"),
                    ("所有文件", "*.*")
                ]
            )

            if not file_path:
                return

            logger.info(f"开始导入知识库文件: {file_path}")
            self._update_status("🔄 正在导入知识库...")

            # 获取嵌入配置
            embed_config = {
                'provider': self.embed_provider_var.get(),
                'api_key': self.embed_api_key_entry.get() if hasattr(self, 'embed_api_key_entry') else '',
                'base_url': self.embed_base_url_entry.get() if hasattr(self, 'embed_base_url_entry') else '',
                'model': self.embed_model_var.get()
            }

            # 验证嵌入配置
            if not embed_config['api_key'].strip():
                self._update_status("❌ 请先配置嵌入API密钥！")
                return

            if not embed_config['base_url'].strip():
                self._update_status("❌ 请先配置嵌入基础URL！")
                return

            # 获取项目路径
            project_path = self.config_data.get("other_params", {}).get("filepath", "")

            # 调用知识库导入函数
            from novel_generator.knowledge import import_knowledge_file
            import_knowledge_file(
                embedding_api_key=embed_config['api_key'],
                embedding_url=embed_config['base_url'],
                embedding_interface_format=embed_config['provider'],
                embedding_model_name=embed_config['model'],
                file_path=file_path,
                filepath=project_path
            )

            self._update_status(f"✅ 知识库导入成功！")
            logger.info(f"知识库导入成功: {file_path}")

        except Exception as e:
            error_msg = f"导入知识库失败: {str(e)}"
            logger.error(error_msg)
            self._update_status(f"❌ {error_msg}")

    def _check_test_result(self, test_type: str, log_messages: list):
        """检查异步测试结果"""
        try:
            # 如果没有消息，说明测试可能刚开始，继续保持进行状态
            if not log_messages:
                if hasattr(self, '_test_in_progress'):
                    self.after(5000, lambda: self._check_test_result(test_type, log_messages))
                return

            # 检查是否有测试完成的消息
            if log_messages:
                for message in log_messages[-10:]:  # 检查最后10条消息
                    # 检查LLM测试成功
                    if "✅ LLM配置测试成功！" in message:
                        self._update_status(f"✅ {test_type}配置测试成功！")
                        logger.info(f"✅ {test_type}配置测试成功")
                        return

                    # 检查嵌入测试成功
                    elif "✅ 嵌入配置测试成功！" in message:
                        self._update_status(f"✅ {test_type}配置测试成功！")
                        logger.info(f"✅ {test_type}配置测试成功")
                        return

                    # 检查各种失败情况
                    elif any(keyword in message for keyword in ["❌", "Connection error", "未获取到响应", "未获取到向量", "测试出错", "配置错误"]):
                        if "Connection error" in message:
                            error_msg = "网络连接失败，请检查网络和API配置"
                        elif "未获取到向量" in message:
                            error_msg = "嵌入模型响应异常，请检查模型配置"
                        elif "未获取到响应" in message:
                            error_msg = "LLM未响应，请检查API配置"
                        else:
                            error_msg = message

                        self._update_status(f"❌ {test_type}配置测试失败！{error_msg}")
                        logger.error(f"❌ {test_type}配置测试失败：{message}")
                        return

            # 检查测试超时（最多等待2分钟）
            if hasattr(self, '_test_start_time'):
                elapsed_time = time.time() - self._test_start_time
                if elapsed_time > 120:  # 2分钟超时
                    self._test_in_progress = False
                    self._update_status(f"⏱️ {test_type}配置测试超时（超过2分钟），请检查网络连接")
                    logger.warning(f"{test_type}配置测试超时，用时{elapsed_time:.1f}秒")
                    return

            # 如果还没有结果，继续检查
            if hasattr(self, '_test_in_progress') and self._test_in_progress:
                self.after(5000, lambda: self._check_test_result(test_type, log_messages))
            else:
                # 超时处理
                self._update_status(f"⏱️ {test_type}配置测试超时，请检查网络连接")
                logger.warning(f"{test_type}配置测试超时")

        except Exception as e:
            logger.error(f"检查测试结果失败: {e}")
            self._update_status(f"❌ {test_type}配置测试检查失败")

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
            values=["OpenAI", "Azure OpenAI", "Ollama", "DeepSeek", "Gemini", "ML Studio", "智谱", "SiliconFlow", "Claude", "Custom"],
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

        # 高级参数配置
        params_frame = ctk.CTkFrame(llm_main, fg_color="transparent")
        params_frame.pack(fill="x", padx=20, pady=10)

        params_label = ctk.CTkLabel(
            params_frame,
            text="🔧 高级参数:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        params_label.pack(anchor="w", pady=(0, 10))

        # 参数配置网格
        params_grid = ctk.CTkFrame(params_frame, fg_color="transparent")
        params_grid.pack(fill="x")

        # 第一行：温度、Top P
        params_grid.grid_columnconfigure((1, 3), weight=1)

        # 温度参数
        temp_label = ctk.CTkLabel(
            params_grid,
            text="温度 (Temperature):",
            width=150,
            anchor="w"
        )
        temp_label.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="w")

        self.temperature_var = ctk.DoubleVar(value=0.7)
        temp_slider = ctk.CTkSlider(
            params_grid,
            from_=0.0,
            to=2.0,
            variable=self.temperature_var,
            number_of_steps=20
        )
        temp_slider.grid(row=0, column=1, padx=(0, 10), pady=5, sticky="ew")

        self.temp_value_label = ctk.CTkLabel(
            params_grid,
            text="0.7",
            width=40
        )
        self.temp_value_label.grid(row=0, column=2, padx=(0, 10), pady=5)

        # Top P参数
        top_p_label = ctk.CTkLabel(
            params_grid,
            text="Top P:",
            width=80,
            anchor="w"
        )
        top_p_label.grid(row=0, column=3, padx=(0, 10), pady=5, sticky="w")

        self.top_p_var = ctk.DoubleVar(value=1.0)
        top_p_slider = ctk.CTkSlider(
            params_grid,
            from_=0.0,
            to=1.0,
            variable=self.top_p_var,
            number_of_steps=10
        )
        top_p_slider.grid(row=0, column=4, padx=(0, 10), pady=5, sticky="ew")

        self.top_p_value_label = ctk.CTkLabel(
            params_grid,
            text="1.0",
            width=40
        )
        self.top_p_value_label.grid(row=0, column=5, pady=5)

        # 第二行：最大Token、频率惩罚
        max_tokens_label = ctk.CTkLabel(
            params_grid,
            text="最大Token:",
            width=150,
            anchor="w"
        )
        max_tokens_label.grid(row=1, column=0, padx=(0, 10), pady=5, sticky="w")

        self.max_tokens_var = ctk.IntVar(value=2000)
        max_tokens_entry = ctk.CTkEntry(
            params_grid,
            textvariable=self.max_tokens_var,
            width=100
        )
        max_tokens_entry.grid(row=1, column=1, padx=(0, 10), pady=5, sticky="w")

        freq_pen_label = ctk.CTkLabel(
            params_grid,
            text="频率惩罚:",
            width=80,
            anchor="w"
        )
        freq_pen_label.grid(row=1, column=3, padx=(0, 10), pady=5, sticky="w")

        self.frequency_penalty_var = ctk.DoubleVar(value=0.0)
        freq_pen_slider = ctk.CTkSlider(
            params_grid,
            from_=-2.0,
            to=2.0,
            variable=self.frequency_penalty_var,
            number_of_steps=8
        )
        freq_pen_slider.grid(row=1, column=4, padx=(0, 10), pady=5, sticky="ew")

        self.freq_pen_value_label = ctk.CTkLabel(
            params_grid,
            text="0.0",
            width=40
        )
        self.freq_pen_value_label.grid(row=1, column=5, pady=5)

        # 绑定滑块变化事件
        temp_slider.configure(command=lambda v: self.temp_value_label.configure(text=f"{float(v):.1f}"))
        top_p_slider.configure(command=lambda v: self.top_p_value_label.configure(text=f"{float(v):.1f}"))
        freq_pen_slider.configure(command=lambda v: self.freq_pen_value_label.configure(text=f"{float(v):.1f}"))

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
            values=["OpenAI", "Azure OpenAI", "DeepSeek", "Gemini", "Ollama", "ML Studio", "SiliconFlow", "智谱", "Gitee AI", "HuggingFace", "Custom"],
            command=self._on_embed_provider_changed
        )
        self.embed_provider_combo.pack(side="left", fill="x", expand=True)

        # 嵌入API密钥
        embed_api_key_frame = ctk.CTkFrame(embed_main, fg_color="transparent")
        embed_api_key_frame.pack(fill="x", padx=20, pady=10)

        embed_api_key_label = ctk.CTkLabel(
            embed_api_key_frame,
            text="嵌入API密钥:",
            width=120,
            anchor="w"
        )
        embed_api_key_label.pack(side="left", padx=(0, 10))

        self.embed_api_key_entry = ctk.CTkEntry(
            embed_api_key_frame,
            placeholder_text="输入嵌入API密钥",
            show="*"
        )
        self.embed_api_key_entry.pack(side="left", fill="x", expand=True)

        # 嵌入基础URL
        embed_base_url_frame = ctk.CTkFrame(embed_main, fg_color="transparent")
        embed_base_url_frame.pack(fill="x", padx=20, pady=5)

        embed_base_url_label = ctk.CTkLabel(
            embed_base_url_frame,
            text="嵌入基础URL:",
            width=120,
            anchor="w"
        )
        embed_base_url_label.pack(side="left", padx=(0, 10))

        self.embed_base_url_entry = ctk.CTkEntry(
            embed_base_url_frame,
            placeholder_text="https://api.openai.com/v1"
        )
        self.embed_base_url_entry.pack(side="left", fill="x", expand=True)

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
        test_button.pack(pady=(0, 10))

        # 知识库导入按钮
        import_button = ctk.CTkButton(
            test_frame,
            text="📚 导入知识库",
            command=self._import_knowledge_base,
            fg_color="#1976D2",
            hover_color="#2196F3"
        )
        import_button.pack()

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

        # 模型配置分隔线
        separator_frame = ctk.CTkFrame(system_main, fg_color="transparent")
        separator_frame.pack(fill="x", padx=20, pady=20)

        separator_label = ctk.CTkLabel(
            separator_frame,
            text="生成功能模型配置",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        separator_label.pack()

        # 不同功能的模型选择
        model_configs = [
            ("prompt_draft_llm", "提示词草稿模型"),
            ("chapter_outline_llm", "章节大纲模型"),
            ("architecture_llm", "架构生成模型"),
            ("final_chapter_llm", "最终章节模型"),
            ("consistency_review_llm", "一致性检查模型")
        ]

        self.task_model_vars = {}

        for config_key, label_text in model_configs:
            task_frame = ctk.CTkFrame(system_main, fg_color="transparent")
            task_frame.pack(fill="x", padx=20, pady=5)

            task_label = ctk.CTkLabel(
                task_frame,
                text=f"{label_text}:",
                width=150,
                anchor="w"
            )
            task_label.pack(side="left", padx=(0, 10))

            model_var = ctk.StringVar()
            self.task_model_vars[config_key] = model_var

            model_combo = ctk.CTkComboBox(
                task_frame,
                variable=model_var,
                values=["DeepSeek V3", "GPT 5", "Gemini 2.5 Pro", "智谱GLM-4.5", "SiliconFlow", "Custom"],
                width=200
            )
            model_combo.pack(side="left", fill="x", expand=True)

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
            # 修复配置加载API错误 - 必须传递config_file参数
            self.config_data = load_config(config_file="config.json")

            # 加载LLM配置
            llm_config = self.config_data.get('llm', {})
            self.llm_provider_var.set(llm_config.get('provider', 'OpenAI'))
            self.api_key_entry.delete(0, 'end')
            self.api_key_entry.insert(0, llm_config.get('api_key', ''))
            self.base_url_entry.delete(0, 'end')
            self.base_url_entry.insert(0, llm_config.get('base_url', 'https://api.openai.com/v1'))
            self.model_var.set(llm_config.get('model', 'gpt-3.5-turbo'))

            # 加载LLM高级参数
            if hasattr(self, 'temperature_var'):
                self.temperature_var.set(llm_config.get('temperature', 0.7))
                self.temp_value_label.configure(text=f"{llm_config.get('temperature', 0.7):.1f}")

            if hasattr(self, 'top_p_var'):
                self.top_p_var.set(llm_config.get('top_p', 1.0))
                self.top_p_value_label.configure(text=f"{llm_config.get('top_p', 1.0):.1f}")

            if hasattr(self, 'max_tokens_var'):
                self.max_tokens_var.set(llm_config.get('max_tokens', 2000))

            if hasattr(self, 'frequency_penalty_var'):
                self.frequency_penalty_var.set(llm_config.get('frequency_penalty', 0.0))
                self.freq_pen_value_label.configure(text=f"{llm_config.get('frequency_penalty', 0.0):.1f}")

            # 加载嵌入配置 - 修复配置加载不匹配问题
            embedding_configs = self.config_data.get('embedding_configs', {})
            last_embedding_interface = self.config_data.get('last_embedding_interface_format', 'OpenAI')

            # 尝试从上次使用的接口加载配置
            embed_config_name = f"{last_embedding_interface} Custom"
            if embed_config_name in embedding_configs:
                embed_config = embedding_configs[embed_config_name]
                self.embed_provider_var.set(embed_config.get('interface_format', 'OpenAI'))
                if hasattr(self, 'embed_api_key_entry'):
                    self.embed_api_key_entry.delete(0, 'end')
                    self.embed_api_key_entry.insert(0, embed_config.get('api_key', ''))
                if hasattr(self, 'embed_base_url_entry'):
                    self.embed_base_url_entry.delete(0, 'end')
                    self.embed_base_url_entry.insert(0, embed_config.get('base_url', 'https://api.openai.com/v1'))
                self.embed_model_var.set(embed_config.get('model_name', 'text-embedding-ada-002'))
            else:
                # 兜底：从旧的embedding字段加载
                embed_config = self.config_data.get('embedding', {})
                self.embed_provider_var.set(embed_config.get('provider', 'OpenAI'))
                self.embed_model_var.set(embed_config.get('model', 'text-embedding-ada-002'))
                if hasattr(self, 'embed_api_key_entry'):
                    self.embed_api_key_entry.delete(0, 'end')
                    self.embed_api_key_entry.insert(0, embed_config.get('api_key', ''))
                if hasattr(self, 'embed_base_url_entry'):
                    self.embed_base_url_entry.delete(0, 'end')
                    self.embed_base_url_entry.insert(0, embed_config.get('base_url', 'https://api.openai.com/v1'))

            # 加载向量存储路径
            vectorstore_path = self.config_data.get('other_params', {}).get('vectorstore_path', './vectorstore')
            self.vectorstore_entry.delete(0, 'end')
            self.vectorstore_entry.insert(0, vectorstore_path)

            # 加载系统配置
            system_config = self.config_data.get('system', {})
            self.log_level_var.set(system_config.get('log_level', 'INFO'))
            self.max_retry_var.set(system_config.get('max_retry', 3))
            self.max_retry_label.configure(text=str(system_config.get('max_retry', 3)))
            self.timeout_var.set(system_config.get('timeout', 60))
            self.timeout_entry.delete(0, 'end')
            self.timeout_entry.insert(0, str(system_config.get('timeout', 60)))

            # 加载生成功能模型配置
            choose_configs = self.config_data.get('choose_configs', {})
            for config_key, model_var in self.task_model_vars.items():
                model_var.set(choose_configs.get(config_key, 'DeepSeek V3'))

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

            # 获取当前配置或创建新配置
            try:
                current_config = load_config("config.json")
            except:
                current_config = {}

            # 更新LLM配置
            provider = self.llm_provider_var.get()
            config_name = f"{provider} Custom"

            if 'llm_configs' not in current_config:
                current_config['llm_configs'] = {}

            current_config['llm_configs'][config_name] = {
                'api_key': self.api_key_entry.get(),
                'base_url': self.base_url_entry.get(),
                'model_name': self.model_var.get(),
                'temperature': self.temperature_var.get() if hasattr(self, 'temperature_var') else 0.7,
                'max_tokens': self.max_tokens_var.get() if hasattr(self, 'max_tokens_var') else 2000,
                'timeout': timeout_value,
                'interface_format': provider
            }

            # 更新嵌入配置
            embed_provider = self.embed_provider_var.get()
            embed_config_name = f"{embed_provider} Custom"

            if 'embedding_configs' not in current_config:
                current_config['embedding_configs'] = {}

            # 获取嵌入API密钥和基础URL
            embed_api_key = getattr(self, 'embed_api_key_entry', None)
            embed_base_url = getattr(self, 'embed_base_url_entry', None)

            current_config['embedding_configs'][embed_config_name] = {
                'api_key': embed_api_key.get() if embed_api_key else '',
                'base_url': embed_base_url.get() if embed_base_url else self.base_url_entry.get(),
                'model_name': self.embed_model_var.get(),
                'retrieval_k': 4,
                'interface_format': embed_provider
            }

            # 更新默认配置选择
            current_config['last_interface_format'] = provider
            current_config['last_embedding_interface_format'] = embed_provider

            # 更新系统设置
            if 'other_params' not in current_config:
                current_config['other_params'] = {}

            current_config['other_params'].update({
                'log_level': self.log_level_var.get(),
                'max_retry': self.max_retry_var.get(),
                'timeout': timeout_value,
                'vectorstore_path': self.vectorstore_entry.get()
            })

            # 更新生成功能模型配置
            if 'choose_configs' not in current_config:
                current_config['choose_configs'] = {}

            for config_key, model_var in self.task_model_vars.items():
                current_config['choose_configs'][config_key] = model_var.get()

            config = current_config

            # 保存配置
            success = save_config(config, "config.json")
            if success:
                self.config_data = config
                logger.info("配置保存成功")
                self._update_status("✅ 配置保存成功！")

                # 通知配置变化
                if self.config_changed_callback:
                    self.config_changed_callback(config)
            else:
                logger.error("配置保存失败")
                self._update_status("❌ 配置保存失败！")

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
                self._update_status("✅ 配置已重置到默认值！")

            except Exception as e:
                logger.error(f"重置配置失败: {e}")
                self._update_status("❌ 重置配置失败！")

    def _test_llm_config(self):
        """测试LLM配置"""
        try:
            config = {
                'provider': self.llm_provider_var.get(),
                'api_key': self.api_key_entry.get(),
                'base_url': self.base_url_entry.get(),
                'model': self.model_var.get()
            }

            # 验证必要参数
            if not config['api_key'].strip():
                self._update_status("❌ 请输入API密钥！")
                return

            if not config['base_url'].strip():
                self._update_status("❌ 请输入基础URL！")
                return

            logger.info("开始测试LLM配置...")
            logger.info(f"提供商: {config['provider']}, 模型: {config['model']}")

            # 创建测试状态跟踪
            self._test_in_progress = True
            self._test_start_time = time.time()
            self._update_status("🔄 正在测试LLM配置...")

            # 创建增强的日志和异常处理函数
            test_log_messages = []

            def enhanced_log_func(message):
                self._log_func(message)
                test_log_messages.append(message)

            def enhanced_exception_func(message):
                self._handle_exception_func(message)
                self._test_in_progress = False
                self._update_status(f"❌ LLM配置测试失败：{message}")
                logger.error(f"❌ LLM配置测试失败：{message}")

            # 导入新的测试函数
            from config_manager import test_llm_config_with_dict
            success, message = test_llm_config_with_dict(config, enhanced_log_func, enhanced_exception_func)

            if success:
                # 异步检查测试结果 - 传递消息列表而不是函数
                self.after(2000, lambda: self._check_test_result("LLM", test_log_messages))
            else:
                self._update_status(f"❌ LLM配置测试失败！{message}")
                logger.error(f"❌ LLM配置测试失败：{message}")

        except Exception as e:
            error_msg = f"测试LLM配置时出错: {str(e)}"
            logger.error(error_msg)
            self._update_status(f"❌ {error_msg}")

    def _test_embedding_config(self):
        """测试嵌入配置"""
        try:
            config = {
                'provider': self.embed_provider_var.get(),
                'api_key': self.embed_api_key_entry.get() if hasattr(self, 'embed_api_key_entry') else '',
                'base_url': self.embed_base_url_entry.get() if hasattr(self, 'embed_base_url_entry') else '',
                'model': self.embed_model_var.get(),
                'vectorstore_path': self.vectorstore_entry.get()
            }

            # 验证必要参数
            if not config['api_key'].strip():
                self._update_status("❌ 请输入嵌入API密钥！")
                return

            if not config['base_url'].strip():
                self._update_status("❌ 请输入嵌入基础URL！")
                return

            logger.info("开始测试嵌入配置...")
            logger.info(f"提供商: {config['provider']}, 模型: {config['model']}")

            # 创建测试状态跟踪
            self._test_in_progress = True
            self._test_start_time = time.time()
            self._update_status("🔄 正在测试嵌入配置...")

            # 创建增强的日志和异常处理函数
            embed_test_log_messages = []

            def enhanced_embed_log_func(message):
                self._log_func(message)
                embed_test_log_messages.append(message)

            def enhanced_embed_exception_func(message):
                self._handle_exception_func(message)
                self._test_in_progress = False
                self._update_status(f"❌ 嵌入配置测试失败：{message}")
                logger.error(f"❌ 嵌入配置测试失败：{message}")

            # 导入新的测试函数
            from config_manager import test_embedding_config_with_dict
            success, message = test_embedding_config_with_dict(config, enhanced_embed_log_func, enhanced_embed_exception_func)

            if success:
                # 异步检查测试结果 - 传递消息列表而不是函数
                self.after(2000, lambda: self._check_test_result("嵌入", embed_test_log_messages))
            else:
                self._update_status(f"❌ 嵌入配置测试失败！{message}")
                logger.error(f"❌ 嵌入配置测试失败：{message}")

        except Exception as e:
            error_msg = f"测试嵌入配置时出错: {str(e)}"
            logger.error(error_msg)
            self._update_status(f"❌ {error_msg}")

    def _on_llm_provider_changed(self, choice):
        """LLM提供商变化处理"""
        # 根据提供商更新模型选项和基础URL
        if choice == "OpenAI":
            models = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "gpt-4o", "gpt-4o-mini"]
            self.base_url_entry.delete(0, 'end')
            self.base_url_entry.insert(0, 'https://api.openai.com/v1')
        elif choice == "Azure OpenAI":
            models = ["gpt-35-turbo", "gpt-4", "gpt-4-32k"]
            self.base_url_entry.delete(0, 'end')
            self.base_url_entry.insert(0, 'https://your-resource.openai.azure.com')
        elif choice == "DeepSeek":
            models = ["deepseek-chat", "deepseek-coder"]
            self.base_url_entry.delete(0, 'end')
            self.base_url_entry.insert(0, 'https://api.deepseek.com/v1')
        elif choice == "Ollama":
            models = ["llama2", "codellama", "mistral", "vicuna", "llama3", "qwen2"]
            self.base_url_entry.delete(0, 'end')
            self.base_url_entry.insert(0, 'http://localhost:11434')
        elif choice == "Gemini":
            models = ["gemini-pro", "gemini-pro-vision"]
            self.base_url_entry.delete(0, 'end')
            self.base_url_entry.insert(0, 'https://generativelanguage.googleapis.com')
        elif choice == "ML Studio":
            models = ["meta-llama-Llama-2-7b-chat-hf", "meta-llama-Llama-2-13b-chat-hf", "meta-llama-Llama-2-70b-chat-hf"]
            self.base_url_entry.delete(0, 'end')
            self.base_url_entry.insert(0, 'https://mlstudio.example.com')
        elif choice == "智谱":
            models = ["glm-4", "glm-3-turbo", "glm-4v", "glm-4-0520", "glm-4-air", "glm-4-airx", "glm-4-long"]
            self.base_url_entry.delete(0, 'end')
            self.base_url_entry.insert(0, 'https://open.bigmodel.cn/api/paas/v4')
        elif choice == "SiliconFlow":
            models = ["qwen/Qwen2-7B-Instruct", "deepseek-ai/DeepSeek-V2.5", "meta-llama/Llama-3.1-8B-Instruct"]
            self.base_url_entry.delete(0, 'end')
            self.base_url_entry.insert(0, 'https://api.siliconflow.cn/v1')
        elif choice == "Claude":
            models = ["claude-3-haiku", "claude-3-sonnet", "claude-3-opus"]
            self.base_url_entry.delete(0, 'end')
            self.base_url_entry.insert(0, 'https://api.anthropic.com')
        else:  # Custom
            models = ["custom"]
            self.base_url_entry.delete(0, 'end')
            self.base_url_entry.insert(0, 'https://api.example.com/v1')

        self.model_combo.configure(values=models)
        if models:
            self.model_var.set(models[0])

    def _on_embed_provider_changed(self, choice):
        """嵌入提供商变化处理"""
        # 根据提供商更新模型选项和基础URL
        if choice == "OpenAI":
            models = ["text-embedding-ada-002", "text-embedding-3-small", "text-embedding-3-large"]
            self.embed_base_url_entry.delete(0, 'end')
            self.embed_base_url_entry.insert(0, 'https://api.openai.com/v1')
        elif choice == "Azure OpenAI":
            models = ["text-embedding-ada-002", "text-embedding-3-small", "text-embedding-3-large"]
            self.embed_base_url_entry.delete(0, 'end')
            self.embed_base_url_entry.insert(0, 'https://your-resource.openai.azure.com')
        elif choice == "DeepSeek":
            models = ["deepseek-chat", "deepseek-coder"]
            self.embed_base_url_entry.delete(0, 'end')
            self.embed_base_url_entry.insert(0, 'https://api.deepseek.com')
        elif choice == "Gemini":
            models = ["text-embedding-001", "text-multilingual-embedding-002"]
            self.embed_base_url_entry.delete(0, 'end')
            self.embed_base_url_entry.insert(0, 'https://generativelanguage.googleapis.com')
        elif choice == "Ollama":
            models = ["llama2", "nomic-embed-text", "mxbai-embed-large"]
            self.embed_base_url_entry.delete(0, 'end')
            self.embed_base_url_entry.insert(0, 'http://localhost:11434')
        elif choice == "ML Studio":
            models = ["text-embedding-ada-002", "text-embedding-3-small"]
            self.embed_base_url_entry.delete(0, 'end')
            self.embed_base_url_entry.insert(0, 'https://mlstudio.example.com')
        elif choice == "SiliconFlow":
            models = ["BAAI/bge-m3", "BAAI/bge-large-zh-v1.5", "BAAI/bge-large-en-v1.5", "netease-youdao/bce-embedding-base_v1"]
            self.embed_base_url_entry.delete(0, 'end')
            self.embed_base_url_entry.insert(0, 'https://api.siliconflow.cn/v1')
        elif choice == "智谱":
            models = ["embedding-2", "embedding-3"]
            self.embed_base_url_entry.delete(0, 'end')
            self.embed_base_url_entry.insert(0, 'https://open.bigmodel.cn/api/paas/v4')
        elif choice == "Gitee AI":
            models = ["BAAI/bge-large-zh-v1.5", "maidalun1020/bce-embedding-base_v1"]
            self.embed_base_url_entry.delete(0, 'end')
            self.embed_base_url_entry.insert(0, 'https://ai.gitee.com/v1')
        elif choice == "HuggingFace":
            models = ["sentence-transformers/all-MiniLM-L6-v2", "sentence-transformers/all-mpnet-base-v2", "BAAI/bge-large-zh-v1.5"]
            self.embed_base_url_entry.delete(0, 'end')
            self.embed_base_url_entry.insert(0, 'https://api-inference.huggingface.co')
        else:  # Custom
            models = ["custom"]
            self.embed_base_url_entry.delete(0, 'end')
            self.embed_base_url_entry.insert(0, 'https://api.example.com/v1')

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