"""
现代化主工作区组件 - AI小说生成器的核心操作界面
迁移自1.0版本的主标签页功能，采用2.0架构重构
"""

import logging
import threading
from typing import Dict, Any, Optional, Callable
import customtkinter as ctk
from tkinter import messagebox, filedialog
import os
from config_manager import load_config

logger = logging.getLogger(__name__)


class MainWorkspace(ctk.CTkFrame):
    """
    现代化主工作区组件

    功能：
    - 章节内容编辑
    - 生成步骤控制
    - 日志输出显示
    - 小说参数设置
    - 生成流程管理
    """

    def __init__(self, parent: ctk.CTkFrame, theme_manager, state_manager=None, **kwargs):
        """
        初始化主工作区

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
        try:
            self.app_config: Dict[str, Any] = load_config("config.json")
        except:
            self.app_config = {}
            
        # 确保config是字典类型
        if not isinstance(self.app_config, dict):
            self.app_config = {}
            
        self.novel_params = {}
        self.generation_state = {
            'current_step': 0,
            'is_generating': False,
            'generation_thread': None
        }

        # 组件引用
        self.main_frame = None
        self.chapter_editor = None
        self.log_output = None
        self.step_buttons = {}

        # 回调函数
        self.step_changed_callback = None
        self.generation_started_callback = None
        self.generation_completed_callback = None

        # 初始化组件
        self._create_workspace_layout()
        self._initialize_parameters()
        self._setup_event_handlers()

        logger.debug("MainWorkspace 组件初始化完成")

    def _create_workspace_layout(self):
        """创建工作区布局"""
        # 配置主框架
        self.configure(
            corner_radius=8,
            fg_color="transparent"
        )

        # 配置网格布局 - 移除右侧面板
        self.grid_columnconfigure(0, weight=1)  # 主内容区域占据全部空间
        self.grid_rowconfigure(0, weight=1)

        # 只创建主内容面板
        self._create_main_panel()

    def _create_main_panel(self):
        """创建主内容面板"""
        self.main_frame = ctk.CTkFrame(self, corner_radius=8)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=0)
        self.main_frame.grid_rowconfigure(1, weight=2)  # 章节编辑区
        self.main_frame.grid_rowconfigure(2, weight=0)  # 步骤按钮区
        self.main_frame.grid_rowconfigure(4, weight=1)  # 日志输出区
        self.main_frame.grid_rowconfigure(5, weight=0)  # 参数配置区
        self.main_frame.grid_columnconfigure(0, weight=1)

        # 章节内容编辑区
        self._create_chapter_editor()

        # 步骤控制按钮区
        self._create_step_buttons()

        # 日志输出区
        self._create_log_output()

        # 小说参数配置区 - 移到主内容区域底部
        self._create_compact_params()

    def _create_chapter_editor(self):
        """创建章节内容编辑器"""
        # 章节标签
        self.chapter_label = ctk.CTkLabel(
            self.main_frame,
            text="📝 章节内容 (字数: 0)",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.chapter_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        # 章节内容编辑框
        self.chapter_editor = ctk.CTkTextbox(
            self.main_frame,
            wrap="word",
            font=ctk.CTkFont(size=14),
            height=300
        )
        self.chapter_editor.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        # 绑定字数统计
        self.chapter_editor.bind("<KeyRelease>", self._update_word_count)
        self.chapter_editor.bind("<ButtonRelease>", self._update_word_count)

    def _create_step_buttons(self):
        """创建步骤控制按钮"""
        # 按钮容器
        step_frame = ctk.CTkFrame(self.main_frame, corner_radius=8)
        step_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        step_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        # 步骤按钮定义
        steps = [
            ("step1", "🏗️ 生成架构", self._on_generate_architecture),
            ("step2", "📋 生成目录", self._on_generate_blueprint),
            ("step3", "✍️ 生成草稿", self._on_generate_chapter),
            ("step4", "✨ 完善章节", self._on_finalize_chapter),
            ("consistency", "🔍 一致性检测", self._on_consistency_check),
            ("batch", "🚀 批量生成", self._on_batch_generate)
        ]

        for i, (step_id, text, command) in enumerate(steps):
            btn = ctk.CTkButton(
                step_frame,
                text=text,
                command=command,
                font=ctk.CTkFont(size=12),
                height=40
            )
            btn.grid(row=0, column=i, padx=2, pady=5, sticky="ew")
            self.step_buttons[step_id] = btn

    def _create_log_output(self):
        """创建日志输出区域"""
        # 日志标签
        log_label = ctk.CTkLabel(
            self.main_frame,
            text="📋 输出日志",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        log_label.grid(row=3, column=0, padx=10, pady=(10, 5), sticky="w")

        # 日志文本框
        self.log_output = ctk.CTkTextbox(
            self.main_frame,
            wrap="word",
            font=ctk.CTkFont(size=12),
            height=200
        )
        self.log_output.grid(row=4, column=0, sticky="nsew", padx=10, pady=(0, 10))

    def _create_compact_params(self):
        """创建紧凑的小说参数配置区域"""
        # 参数配置容器
        params_frame = ctk.CTkFrame(self.main_frame, corner_radius=8)
        params_frame.grid(row=5, column=0, sticky="ew", padx=10, pady=(10, 5))
        params_frame.grid_columnconfigure((1, 3, 5, 7), weight=1)

        # 配置标题
        config_title = ctk.CTkLabel(
            params_frame,
            text="⚙️ 小说参数配置",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        config_title.grid(row=0, column=0, columnspan=8, padx=10, pady=(10, 5), sticky="w")

        # 第一行：主题、类型
        self._create_compact_topic_input(params_frame, row=1)
        self._create_compact_genre_input(params_frame, row=1, col=2)

        # 第二行：章节数、字数
        self._create_compact_chapter_word_inputs(params_frame, row=2)

        # 第三行：保存路径、章节号
        self._create_compact_filepath_input(params_frame, row=3)
        self._create_compact_chapter_number_input(params_frame, row=3, col=2)

        # 第四行：内容指导
        self._create_compact_guidance_input(params_frame, row=4)

        # 第五行：角色设定
        self._create_compact_characters_input(params_frame, row=5)

    def _create_compact_topic_input(self, parent, row: int, col: int = 0):
        """创建紧凑的主题输入"""
        ctk.CTkLabel(
            parent,
            text="🎯 主题:",
            font=ctk.CTkFont(size=11, weight="bold")
        ).grid(row=row, column=col, padx=5, pady=5, sticky="w")

        self.topic_text = ctk.CTkTextbox(
            parent,
            height=60,
            wrap="word",
            font=ctk.CTkFont(size=11)
        )
        self.topic_text.grid(row=row, column=col+1, padx=5, pady=5, sticky="ew", columnspan=3)

    def _create_compact_genre_input(self, parent, row: int, col: int = 4):
        """创建紧凑的类型输入"""
        ctk.CTkLabel(
            parent,
            text="📚 类型:",
            font=ctk.CTkFont(size=11, weight="bold")
        ).grid(row=row, column=col, padx=5, pady=5, sticky="w")

        self.genre_var = ctk.StringVar(value="玄幻")
        genre_entry = ctk.CTkEntry(
            parent,
            textvariable=self.genre_var,
            font=ctk.CTkFont(size=11)
        )
        genre_entry.grid(row=row, column=col+1, padx=5, pady=5, sticky="ew")

    def _create_compact_chapter_word_inputs(self, parent, row: int):
        """创建紧凑的章节数和字数输入"""
        # 章节数
        ctk.CTkLabel(
            parent,
            text="📊 章节数:",
            font=ctk.CTkFont(size=11, weight="bold")
        ).grid(row=row, column=0, padx=5, pady=5, sticky="w")

        self.num_chapters_var = ctk.StringVar(value="10")
        ctk.CTkEntry(
            parent,
            textvariable=self.num_chapters_var,
            width=80,
            font=ctk.CTkFont(size=11)
        ).grid(row=row, column=1, padx=5, pady=5, sticky="w")

        # 每章字数
        ctk.CTkLabel(
            parent,
            text="📝 每章字数:",
            font=ctk.CTkFont(size=11, weight="bold")
        ).grid(row=row, column=2, padx=5, pady=5, sticky="w")

        self.word_number_var = ctk.StringVar(value="3000")
        ctk.CTkEntry(
            parent,
            textvariable=self.word_number_var,
            width=80,
            font=ctk.CTkFont(size=11)
        ).grid(row=row, column=3, padx=5, pady=5, sticky="w")

    def _create_compact_filepath_input(self, parent, row: int):
        """创建紧凑的保存路径输入"""
        ctk.CTkLabel(
            parent,
            text="📁 保存路径:",
            font=ctk.CTkFont(size=11, weight="bold")
        ).grid(row=row, column=0, padx=5, pady=5, sticky="w")

        self.filepath_var = ctk.StringVar(value="")
        filepath_entry = ctk.CTkEntry(
            parent,
            textvariable=self.filepath_var,
            font=ctk.CTkFont(size=11)
        )
        filepath_entry.grid(row=row, column=1, padx=5, pady=5, sticky="ew", columnspan=3)

        browse_btn = ctk.CTkButton(
            parent,
            text="浏览",
            command=self._browse_folder,
            width=50,
            font=ctk.CTkFont(size=10)
        )
        browse_btn.grid(row=row, column=4, padx=5, pady=5)

    def _create_compact_chapter_number_input(self, parent, row: int, col: int = 5):
        """创建紧凑的章节号输入"""
        ctk.CTkLabel(
            parent,
            text="📖 当前章节:",
            font=ctk.CTkFont(size=11, weight="bold")
        ).grid(row=row, column=col, padx=5, pady=5, sticky="w")

        self.chapter_num_var = ctk.StringVar(value="1")
        chapter_entry = ctk.CTkEntry(
            parent,
            textvariable=self.chapter_num_var,
            width=60,
            font=ctk.CTkFont(size=11)
        )
        chapter_entry.grid(row=row, column=col+1, padx=5, pady=5, sticky="w")

    def _create_compact_guidance_input(self, parent, row: int):
        """创建紧凑的内容指导输入"""
        ctk.CTkLabel(
            parent,
            text="💡 内容指导:",
            font=ctk.CTkFont(size=11, weight="bold")
        ).grid(row=row, column=0, padx=5, pady=5, sticky="nw")

        self.guidance_text = ctk.CTkTextbox(
            parent,
            height=50,
            wrap="word",
            font=ctk.CTkFont(size=11)
        )
        self.guidance_text.grid(row=row, column=1, padx=5, pady=5, sticky="ew", columnspan=7)

    def _create_compact_characters_input(self, parent, row: int):
        """创建紧凑的角色设定输入"""
        ctk.CTkLabel(
            parent,
            text="👥 角色设定:",
            font=ctk.CTkFont(size=11, weight="bold")
        ).grid(row=row, column=0, padx=5, pady=5, sticky="nw")

        self.characters_text = ctk.CTkTextbox(
            parent,
            height=40,
            wrap="word",
            font=ctk.CTkFont(size=11)
        )
        self.characters_text.grid(row=row, column=1, padx=5, pady=5, sticky="ew", columnspan=7)

    
    def _initialize_parameters(self):
        """初始化参数"""
        try:
            # 从配置中加载默认值
            if isinstance(self.app_config, dict) and "other_params" in self.app_config:
                params = self.app_config["other_params"]

                if hasattr(self, 'topic_text') and params.get("topic"):
                    self.topic_text.insert("0.0", params["topic"])

                if hasattr(self, 'genre_var') and params.get("genre"):
                    self.genre_var.set(params["genre"])

                if hasattr(self, 'num_chapters_var') and params.get("num_chapters"):
                    self.num_chapters_var.set(str(params["num_chapters"]))

                if hasattr(self, 'word_number_var') and params.get("word_number"):
                    self.word_number_var.set(str(params["word_number"]))

                if hasattr(self, 'filepath_var') and params.get("filepath"):
                    self.filepath_var.set(params["filepath"])

        except Exception as e:
            logger.error(f"初始化参数失败: {e}")

    def _setup_event_handlers(self):
        """设置事件处理器"""
        # 这里可以添加事件处理器
        pass

    def _update_word_count(self, event=None):
        """更新字数统计"""
        try:
            if self.chapter_editor is not None:
                text = self.chapter_editor.get("0.0", "end")
                count = len(text) - 1  # 减去最后一个换行符
                self.chapter_label.configure(text=f"📝 章节内容 (字数: {count})")
        except Exception as e:
            logger.error(f"更新字数统计失败: {e}")

    def _browse_folder(self):
        """浏览文件夹"""
        try:
            folder_path = filedialog.askdirectory()
            if folder_path:
                self.filepath_var.set(folder_path)
        except Exception as e:
            logger.error(f"浏览文件夹失败: {e}")

    # 步骤按钮回调方法
    def _on_generate_architecture(self):
        """生成小说架构"""
        if self.generation_state['is_generating']:
            self._log("⚠️ 正在生成中，请等待...")
            return

        # 验证参数
        params = self.get_novel_parameters()
        if not params.get('topic'):
            self._log("❌ 请先输入小说主题")
            return

        self._log("🏗️ 开始生成小说架构...")
        self._set_step_active("step1")
        self._start_generation("architecture")

    def _on_generate_blueprint(self):
        """生成章节目录"""
        if self.generation_state['is_generating']:
            self._log("⚠️ 正在生成中，请等待...")
            return

        # 验证参数
        params = self.get_novel_parameters()
        if not params.get('topic'):
            self._log("❌ 请先输入小说主题")
            return

        self._log("📋 开始生成章节目录...")
        self._set_step_active("step2")
        self._start_generation("blueprint")

    def _on_generate_chapter(self):
        """生成章节草稿"""
        if self.generation_state['is_generating']:
            self._log("⚠️ 正在生成中，请等待...")
            return

        # 验证参数
        params = self.get_novel_parameters()
        if not params.get('topic'):
            self._log("❌ 请先输入小说主题")
            return

        chapter_num = int(params.get('chapter_num', 1))
        self._log(f"✍️ 开始生成第{chapter_num}章草稿...")
        self._set_step_active("step3")
        self._start_generation("chapter")

    def _on_finalize_chapter(self):
        """完善章节内容"""
        if self.generation_state['is_generating']:
            self._log("⚠️ 正在生成中，请等待...")
            return

        # 检查是否有章节内容
        content = self.get_chapter_content()
        if not content.strip():
            self._log("❌ 请先生成章节草稿")
            return

        self._log("✨ 开始完善章节内容...")
        self._set_step_active("step4")
        self._start_generation("finalize")

    def _on_consistency_check(self):
        """一致性检测"""
        if self.generation_state['is_generating']:
            self._log("⚠️ 正在生成中，请等待...")
            return

        # 检查是否有章节内容
        content = self.get_chapter_content()
        if not content.strip():
            self._log("❌ 请先生成章节内容")
            return

        self._log("🔍 开始进行一致性检测...")
        self._set_step_active("consistency")
        self._start_generation("consistency")

    def _on_batch_generate(self):
        """批量生成"""
        if self.generation_state['is_generating']:
            self._log("⚠️ 正在生成中，请等待...")
            return

        # 验证参数
        params = self.get_novel_parameters()
        if not params.get('topic'):
            self._log("❌ 请先输入小说主题")
            return

        self._log("🚀 开始批量生成...")
        self._set_step_active("batch")
        self._start_generation("batch")

    def _set_step_active(self, step_id: str):
        """设置当前活动步骤"""
        try:
            # 重置所有按钮状态
            for btn_id, btn in self.step_buttons.items():
                btn.configure(fg_color=("gray75", "gray25"))

            # 设置当前步骤为活动状态
            if step_id in self.step_buttons:
                self.step_buttons[step_id].configure(fg_color=("darkblue", "darkblue"))

            # 通知状态变化
            if self.step_changed_callback:
                self.step_changed_callback(step_id)

        except Exception as e:
            logger.error(f"设置活动步骤失败: {e}")

    def _log(self, message: str):
        """添加日志消息"""
        try:
            if self.log_output:
                self.log_output.configure(state="normal")
                self.log_output.insert("end", f"{message}\n")
                self.log_output.see("end")
                self.log_output.configure(state="disabled")
        except Exception as e:
            logger.error(f"添加日志失败: {e}")

    # 公共接口方法
    def get_novel_parameters(self) -> Dict[str, Any]:
        """获取小说参数"""
        try:
            return {
                'topic': self.topic_text.get("0.0", "end").strip() if hasattr(self, 'topic_text') else "",
                'genre': self.genre_var.get() if hasattr(self, 'genre_var') else "",
                'num_chapters': int(self.num_chapters_var.get()) if hasattr(self, 'num_chapters_var') else 10,
                'word_number': int(self.word_number_var.get()) if hasattr(self, 'word_number_var') else 3000,
                'filepath': self.filepath_var.get() if hasattr(self, 'filepath_var') else "",
                'chapter_num': int(self.chapter_num_var.get()) if hasattr(self, 'chapter_num_var') else 1,
                'guidance': self.guidance_text.get("0.0", "end").strip() if hasattr(self, 'guidance_text') else "",
                'characters': self.characters_text.get("0.0", "end").strip() if hasattr(self, 'characters_text') else ""
            }
        except Exception as e:
            logger.error(f"获取小说参数失败: {e}")
            return {}

    def set_chapter_content(self, content: str):
        """设置章节内容"""
        try:
            if self.chapter_editor:
                self.chapter_editor.delete("0.0", "end")
                self.chapter_editor.insert("0.0", content)
                self._update_word_count()
        except Exception as e:
            logger.error(f"设置章节内容失败: {e}")

    def get_chapter_content(self) -> str:
        """获取章节内容"""
        try:
            if self.chapter_editor:
                return self.chapter_editor.get("0.0", "end").strip()
            return ""
        except Exception as e:
            logger.error(f"获取章节内容失败: {e}")
            return ""

    def clear_log(self):
        """清空日志"""
        try:
            if self.log_output:
                self.log_output.configure(state="normal")
                self.log_output.delete("0.0", "end")
                self.log_output.configure(state="disabled")
        except Exception as e:
            logger.error(f"清空日志失败: {e}")

    def set_step_changed_callback(self, callback: Callable):
        """设置步骤变化回调"""
        self.step_changed_callback = callback

    def set_generation_started_callback(self, callback: Callable):
        """设置生成开始回调"""
        self.generation_started_callback = callback

    def set_generation_completed_callback(self, callback: Callable):
        """设置生成完成回调"""
        self.generation_completed_callback = callback

    def _start_generation(self, generation_type: str):
        """开始生成流程"""
        try:
            # 设置生成状态
            self.generation_state['is_generating'] = True
            self.generation_state['current_step'] = generation_type

            # 禁用所有生成按钮
            self._set_buttons_enabled(False)

            # 调用生成开始回调
            if self.generation_started_callback:
                self.generation_started_callback(generation_type)

            # 在新线程中执行生成
            self.generation_state['generation_thread'] = threading.Thread(
                target=self._execute_generation,
                args=(generation_type,),
                daemon=True
            )
            self.generation_state['generation_thread'].start()

        except Exception as e:
            logger.error(f"启动生成流程失败: {e}")
            self._finish_generation(error=str(e))

    def _execute_generation(self, generation_type: str):
        """执行具体的生成逻辑"""
        try:
            params = self.get_novel_parameters()

            if generation_type == "architecture":
                # 生成小说架构
                self._log("🔄 正在连接AI服务...")
                
                # 导入小说生成器模块
                try:
                    from novel_generator.architecture import Novel_architecture_generate
                    from config_manager import load_config
                    
                    # 获取配置
                    config = load_config("config.json")
                    llm_config = config.get('llm', {})
                    other_params = config.get('other_params', {})
                    
                    # 调用真正的生成函数
                    Novel_architecture_generate(
                        interface_format=llm_config.get('provider', 'DeepSeek'),
                        api_key=llm_config.get('api_key', ''),
                        base_url=llm_config.get('base_url', 'https://api.deepseek.com'),
                        llm_model=llm_config.get('model', 'deepseek-chat'),
                        topic=params.get('topic', ''),
                        genre=params.get('genre', ''),
                        number_of_chapters=int(params.get('num_chapters', 10)),
                        word_number=int(params.get('word_number', 3000)),
                        filepath=params.get('filepath', '.'),
                        user_guidance=params.get('guidance', ''),
                        temperature=llm_config.get('temperature', 0.7),
                        max_tokens=llm_config.get('max_tokens', 2048),
                        timeout=llm_config.get('timeout', 600)
                    )
                    
                    # 读取生成的架构文件
                    import os
                    architecture_file = os.path.join(params.get('filepath', '.'), "Novel_architecture.txt")
                    if os.path.exists(architecture_file):
                        with open(architecture_file, 'r', encoding='utf-8') as f:
                            architecture_content = f.read()
                        self._save_novel_architecture(architecture_content)
                        self._log("✅ 小说架构生成完成！")
                        self._log(f"📄 已保存到 Novel_architecture.txt")
                    else:
                        self._log("❌ 未找到生成的小说架构文件")
                        
                except Exception as e:
                    logger.error(f"生成小说架构失败: {e}")
                    self._log(f"❌ 生成小说架构失败: {str(e)}")
                    import traceback
                    logger.error(traceback.format_exc())

            elif generation_type == "blueprint":
                # 生成章节目录
                self._log("🔄 正在生成章节目录...")
                
                # 导入章节目录生成器
                try:
                    from novel_generator.blueprint import Chapter_blueprint_generate
                    from config_manager import load_config
                    
                    # 获取配置
                    config = load_config("config.json")
                    llm_config = config.get('llm', {})
                    other_params = config.get('other_params', {})
                    
                    # 调用真正的生成函数
                    Chapter_blueprint_generate(
                        interface_format=llm_config.get('provider', 'DeepSeek'),
                        api_key=llm_config.get('api_key', ''),
                        base_url=llm_config.get('base_url', 'https://api.deepseek.com'),
                        llm_model=llm_config.get('model', 'deepseek-chat'),
                        number_of_chapters=int(params.get('num_chapters', 10)),
                        filepath=params.get('filepath', '.'),
                        user_guidance=params.get('guidance', ''),
                        temperature=llm_config.get('temperature', 0.7),
                        max_tokens=llm_config.get('max_tokens', 4096),
                        timeout=llm_config.get('timeout', 600)
                    )
                    
                    # 读取生成的目录文件
                    blueprint_file = os.path.join(params.get('filepath', '.'), "Novel_directory.txt")
                    if os.path.exists(blueprint_file):
                        with open(blueprint_file, 'r', encoding='utf-8') as f:
                            blueprint_content = f.read()
                        self._save_chapter_blueprint(blueprint_content)
                        self._log("✅ 章节目录生成完成！")
                        self._log(f"📄 已保存到 Novel_directory.txt")
                    else:
                        self._log("❌ 未找到生成的章节目录文件")
                        
                except Exception as e:
                    logger.error(f"生成章节目录失败: {e}")
                    self._log(f"❌ 生成章节目录失败: {str(e)}")
                    import traceback
                    logger.error(traceback.format_exc())

            elif generation_type == "chapter":
                # 生成章节内容
                chapter_num = int(params.get('chapter_num', 1))
                self._log(f"🔄 正在生成第{chapter_num}章内容...")
                
                # 导入章节生成器
                try:
                    from novel_generator.chapter import generate_chapter_draft, build_chapter_prompt
                    from config_manager import load_config
                    
                    # 获取配置
                    config = load_config("config.json")
                    llm_config = config.get('llm', {})
                    embedding_config = config.get('embedding_configs', {}).get('OpenAI', {})
                    other_params = config.get('other_params', {})
                    
                    # 确保必要的文件存在
                    import os
                    architecture_file = os.path.join(params.get('filepath', '.'), "Novel_architecture.txt")
                    blueprint_file = os.path.join(params.get('filepath', '.'), "Novel_directory.txt")
                    
                    if not os.path.exists(architecture_file):
                        self._log("❌ 请先生成小说架构")
                        return
                        
                    if not os.path.exists(blueprint_file):
                        self._log("❌ 请先生成章节目录")
                        return
                    
                    # 调用真正的生成函数
                    result = generate_chapter_draft(
                        api_key=llm_config.get('api_key', ''),
                        base_url=llm_config.get('base_url', 'https://api.deepseek.com'),
                        model_name=llm_config.get('model', 'deepseek-chat'),
                        filepath=params.get('filepath', '.'),
                        novel_number=chapter_num,
                        word_number=int(params.get('word_number', 3000)),
                        temperature=llm_config.get('temperature', 0.7),
                        user_guidance=params.get('guidance', ''),
                        characters_involved=params.get('characters', ''),
                        key_items="",
                        scene_location="",
                        time_constraint="",
                        embedding_api_key=embedding_config.get('api_key', ''),
                        embedding_url=embedding_config.get('base_url', 'https://api.siliconflow.cn/v1'),
                        embedding_interface_format=embedding_config.get('interface_format', 'SiliconFlow'),
                        embedding_model_name=embedding_config.get('model_name', 'BAAI/bge-m3'),
                        embedding_retrieval_k=embedding_config.get('retrieval_k', 4),
                        interface_format=llm_config.get('provider', 'DeepSeek'),
                        max_tokens=llm_config.get('max_tokens', 2048),
                        timeout=llm_config.get('timeout', 600)
                    )
                    
                    if result:
                        # 设置章节内容到编辑器
                        self.set_chapter_content(result)
                        self._log(f"✅ 第{chapter_num}章内容生成完成！")
                        self._log(f"📝 字数：{len(result)}字")
                    else:
                        self._log("❌ 章节内容生成失败")
                        
                except Exception as e:
                    logger.error(f"生成章节内容失败: {e}")
                    self._log(f"❌ 生成章节内容失败: {str(e)}")
                    import traceback
                    logger.error(traceback.format_exc())

            elif generation_type == "finalize":
                # 完善章节内容
                self._log("🔄 正在完善章节内容...")
                
                # 导入完善器
                try:
                    from novel_generator.finalization import finalize_chapter
                    from config_manager import load_config
                    
                    # 获取配置
                    config = load_config("config.json")
                    llm_config = config.get('llm', {})
                    embedding_config = config.get('embedding_configs', {}).get('OpenAI', {})
                    
                    # 获取当前章节内容
                    current_content = self.get_chapter_content()
                    if not current_content.strip():
                        self._log("❌ 请先生成章节草稿")
                        return
                    
                    # 获取当前章节号
                    chapter_num = int(params.get('chapter_num', 1))
                    
                    # 调用完善函数
                    finalize_chapter(
                        novel_number=chapter_num,
                        word_number=int(params.get('word_number', 3000)),
                        api_key=llm_config.get('api_key', ''),
                        base_url=llm_config.get('base_url', 'https://api.deepseek.com'),
                        model_name=llm_config.get('model', 'deepseek-chat'),
                        temperature=llm_config.get('temperature', 0.7),
                        filepath=params.get('filepath', '.'),
                        embedding_api_key=embedding_config.get('api_key', ''),
                        embedding_url=embedding_config.get('base_url', 'https://api.siliconflow.cn/v1'),
                        embedding_interface_format=embedding_config.get('interface_format', 'SiliconFlow'),
                        embedding_model_name=embedding_config.get('model_name', 'BAAI/bge-m3'),
                        interface_format=llm_config.get('provider', 'DeepSeek'),
                        max_tokens=llm_config.get('max_tokens', 2048),
                        timeout=llm_config.get('timeout', 600)
                    )
                    
                    # 读取完善后的章节内容
                    import os
                    chapters_dir = os.path.join(params.get('filepath', '.'), "chapters")
                    chapter_file = os.path.join(chapters_dir, f"chapter_{chapter_num}.txt")
                    
                    if os.path.exists(chapter_file):
                        with open(chapter_file, 'r', encoding='utf-8') as f:
                            refined_content = f.read()
                        self.set_chapter_content(refined_content)
                        self._log("✅ 章节内容完善完成！")
                    else:
                        self._log("❌ 章节内容完善失败")
                        
                except Exception as e:
                    logger.error(f"完善章节内容失败: {e}")
                    self._log(f"❌ 完善章节内容失败: {str(e)}")
                    import traceback
                    logger.error(traceback.format_exc())

            elif generation_type == "consistency":
                # 一致性检测
                self._log("🔄 正在进行一致性检测...")
                
                try:
                    # 调用一致性检查器
                    consistency_result = self._perform_consistency_check()
                    self._log("📋 一致性检测结果：")
                    self._log(consistency_result)
                except Exception as e:
                    self._log(f"❌ 一致性检测失败: {e}")
                    logger.error(f"一致性检测失败: {e}")

            elif generation_type == "batch":
                # 批量生成
                self._log("🔄 开始批量生成流程...")

                # 依次执行各个步骤
                self._log("1️⃣ 生成小说架构...")
                self._execute_generation("architecture")
                
                self._log("2️⃣ 生成章节目录...")
                self._execute_generation("blueprint")
                
                self._log("3️⃣ 生成第一章内容...")
                # 保存当前章节号
                original_chapter_num = params.get('chapter_num', '1')
                # 设置为第一章
                if hasattr(self, 'chapter_num_var'):
                    self.chapter_num_var.set('1')
                self._execute_generation("chapter")
                # 恢复原章节号
                if hasattr(self, 'chapter_num_var'):
                    self.chapter_num_var.set(original_chapter_num)

                self._log("✅ 批量生成完成！")
                self._log("💡 您可以继续生成后续章节或开始完善内容")

            # 调用生成完成回调
            if self.generation_completed_callback:
                self.generation_completed_callback({
                    'type': generation_type,
                    'success': True,
                    'params': params
                })

        except Exception as e:
            logger.error(f"生成执行失败: {e}")
            self._log(f"❌ 生成失败: {str(e)}")
            if self.generation_completed_callback:
                self.generation_completed_callback({
                    'type': generation_type,
                    'success': False,
                    'error': str(e)
                })
        finally:
            # 完成生成流程
            self._finish_generation()

    def _finish_generation(self, error: str = ""):
        """完成生成流程"""
        try:
            # 重置生成状态
            self.generation_state['is_generating'] = False
            self.generation_state['current_step'] = None
            self.generation_state['generation_thread'] = None

            # 重新启用所有按钮
            self._set_buttons_enabled(True)

            if error:
                self._log(f"❌ 生成流程因错误结束: {error}")
            else:
                self._log("🎉 生成流程完成！")

        except Exception as e:
            logger.error(f"完成生成流程失败: {e}")

    def _set_buttons_enabled(self, enabled: bool):
        """设置生成按钮的启用状态"""
        try:
            for step_id, button in self.step_buttons.items():
                if button and hasattr(button, 'configure'):
                    button.configure(state="normal" if enabled else "disabled")
        except Exception as e:
            logger.error(f"设置按钮状态失败: {e}")

    def _save_novel_architecture(self, content: str):
        """保存小说架构"""
        try:
            import os
            filepath = self.filepath_var.get() if hasattr(self, 'filepath_var') else ""
            if filepath:
                filename = os.path.join(filepath, "Novel_architecture.txt")
            else:
                filename = "Novel_architecture.txt"

            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            logger.error(f"保存小说架构失败: {e}")

    def _save_chapter_blueprint(self, content: str):
        """保存章节目录"""
        try:
            import os
            filepath = self.filepath_var.get() if hasattr(self, 'filepath_var') else ""
            if filepath:
                filename = os.path.join(filepath, "Novel_directory.txt")
            else:
                filename = "Novel_directory.txt"

            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            logger.error(f"保存章节目录失败: {e}")

    def _perform_consistency_check(self) -> str:
        """执行一致性检测"""
        try:
            # 导入一致性检查器
            from consistency_checker import check_consistency

            # 获取LLM配置
            llm_config = {}
            if isinstance(self.config, dict):
                llm_config = self.config.get('llm', {})
                
            # 获取其他参数
            other_params = {}
            if isinstance(self.config, dict):
                other_params = self.config.get('other_params', {})

            # 获取各种内容
            current_chapter = self.get_chapter_content()
            novel_setting = self._load_file_content("Novel_architecture.txt")
            character_state = self._load_file_content("character_state.txt")
            global_summary = self._load_file_content("global_summary.txt")

            # 调用一致性检查器
            result = check_consistency(
                novel_setting=novel_setting,
                character_state=character_state,
                global_summary=global_summary,
                chapter_text=current_chapter,
                api_key=llm_config.get('api_key', ''),
                base_url=llm_config.get('base_url', 'https://api.openai.com/v1'),
                model_name=llm_config.get('model', 'gpt-3.5-turbo'),
                temperature=llm_config.get('temperature', 0.3),
                interface_format=llm_config.get('provider', 'OpenAI'),
                max_tokens=llm_config.get('max_tokens', 2048),
                timeout=llm_config.get('timeout', 600)
            )

            return result

        except Exception as e:
            logger.error(f"执行一致性检测失败: {e}")
            return f"一致性检测出错: {str(e)}"

    def _load_file_content(self, filename: str) -> str:
        """加载文件内容"""
        try:
            import os
            filepath = ""
            if isinstance(self.app_config, dict):
                other_params = self.app_config.get('other_params', {})
                if isinstance(other_params, dict):
                    filepath = other_params.get('filepath', '')
            if filepath:
                full_path = os.path.join(filepath, filename)
            else:
                full_path = filename

            if os.path.exists(full_path):
                with open(full_path, 'r', encoding='utf-8') as f:
                    return f.read()
            return ""
        except Exception as e:
            logger.error(f"加载文件 {filename} 失败: {e}")
            return ""