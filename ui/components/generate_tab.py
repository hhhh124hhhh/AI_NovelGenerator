"""
现代化生成标签页组件 - AI小说生成器的核心生成界面
包含小说架构生成、章节规划、内容生成等功能
"""

import logging
import threading
from typing import Dict, Any, Optional, Callable
import customtkinter as ctk
from tkinter import messagebox, scrolledtext
from novel_generator import (
    Novel_architecture_generate,
    Chapter_blueprint_generate,
    generate_chapter_draft
)
from config_manager import load_config

logger = logging.getLogger(__name__)


class GenerateTab(ctk.CTkFrame):
    """
    现代化生成标签页组件

    功能：
    - 小说架构生成
    - 章节蓝图生成
    - 章节内容生成
    - 生成进度监控
    - 生成结果预览
    """

    def __init__(self, parent: ctk.CTkFrame, theme_manager, state_manager=None, **kwargs):
        """
        初始化生成标签页

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

        # 配置实例
        self.config = None
        self.generation_thread = None

        # 生成状态
        self.is_generating = False
        self.current_step = ""
        self.generation_progress = 0

        # 组件引用
        self.generate_tabview = None
        self.architecture_frame = None
        self.blueprint_frame = None
        self.content_frame = None

        # 回调函数
        self.generation_started_callback = None
        self.generation_completed_callback = None

        # 初始化组件
        self._create_generate_layout()
        self._initialize_generator()

        logger.debug("GenerateTab 组件初始化完成")

    def _create_generate_layout(self):
        """创建生成布局"""
        # 配置主框架
        self.configure(
            corner_radius=8,
            fg_color="transparent"
        )

        # 创建生成选项卡
        self.generate_tabview = ctk.CTkTabview(
            self,
            segmented_button_fg_color="#2A2A2A",
            segmented_button_selected_color="#404040",
            segmented_button_unselected_color="#1E1E1E"
        )
        self.generate_tabview.pack(fill="both", expand=True, padx=10, pady=10)

        # 添加选项卡
        self.architecture_frame = self.generate_tabview.add("小说架构")
        self.blueprint_frame = self.generate_tabview.add("章节规划")
        self.content_frame = self.generate_tabview.add("内容生成")

        # 构建各个生成页面
        self._build_architecture_tab()
        self._build_blueprint_tab()
        self._build_content_tab()

    def _build_architecture_tab(self):
        """构建小说架构生成界面"""
        # 架构生成主框架
        arch_main = ctk.CTkFrame(self.architecture_frame, fg_color="#2A2A2A")
        arch_main.pack(fill="both", expand=True, padx=10, pady=10)

        # 标题
        title_label = ctk.CTkLabel(
            arch_main,
            text="小说架构生成",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(10, 20))

        # 参数配置区域
        params_frame = ctk.CTkFrame(arch_main, fg_color="transparent")
        params_frame.pack(fill="x", padx=20, pady=10)

        # 小说主题
        theme_frame = ctk.CTkFrame(params_frame, fg_color="transparent")
        theme_frame.pack(fill="x", pady=5)

        theme_label = ctk.CTkLabel(
            theme_frame,
            text="小说主题:",
            width=100,
            anchor="w"
        )
        theme_label.pack(side="left", padx=(0, 10))

        self.theme_entry = ctk.CTkEntry(
            theme_frame,
            placeholder_text="输入小说主题，如：科幻冒险、历史传奇等"
        )
        self.theme_entry.pack(side="left", fill="x", expand=True)

        # 小说类型
        genre_frame = ctk.CTkFrame(params_frame, fg_color="transparent")
        genre_frame.pack(fill="x", pady=5)

        genre_label = ctk.CTkLabel(
            genre_frame,
            text="小说类型:",
            width=100,
            anchor="w"
        )
        genre_label.pack(side="left", padx=(0, 10))

        self.genre_var = ctk.StringVar(value="奇幻")
        self.genre_combo = ctk.CTkComboBox(
            genre_frame,
            variable=self.genre_var,
            values=["奇幻", "科幻", "历史", "现代", "悬疑", "爱情", "冒险", "战争"]
        )
        self.genre_combo.pack(side="left", fill="x", expand=True)

        # 世界观背景
        world_frame = ctk.CTkFrame(params_frame, fg_color="transparent")
        world_frame.pack(fill="x", pady=5)

        world_label = ctk.CTkLabel(
            world_frame,
            text="世界观背景:",
            width=100,
            anchor="w"
        )
        world_label.pack(side="left", padx=(0, 10))

        self.world_textbox = ctk.CTkTextbox(
            world_frame,
            height=80
        )
        self.world_textbox.pack(side="left", fill="both", expand=True)

        # 主要角色
        characters_frame = ctk.CTkFrame(params_frame, fg_color="transparent")
        characters_frame.pack(fill="x", pady=5)

        characters_label = ctk.CTkLabel(
            characters_frame,
            text="主要角色:",
            width=100,
            anchor="w"
        )
        characters_label.pack(side="left", padx=(0, 10))

        self.characters_textbox = ctk.CTkTextbox(
            characters_frame,
            height=60
        )
        self.characters_textbox.pack(side="left", fill="both", expand=True)

        # 生成按钮
        button_frame = ctk.CTkFrame(arch_main, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=20)

        self.arch_generate_button = ctk.CTkButton(
            button_frame,
            text="生成小说架构",
            command=self._generate_architecture,
            fg_color="#2E7D32",
            hover_color="#388E3C",
            height=40
        )
        self.arch_generate_button.pack(fill="x")

        # 进度条
        self.arch_progress_bar = ctk.CTkProgressBar(arch_main)
        self.arch_progress_bar.pack(fill="x", padx=20, pady=(10, 5))
        self.arch_progress_bar.set(0)

        # 状态标签
        self.arch_status_label = ctk.CTkLabel(
            arch_main,
            text="就绪",
            text_color="gray"
        )
        self.arch_status_label.pack(pady=(0, 10))

        # 结果预览区域
        result_frame = ctk.CTkFrame(arch_main, fg_color="transparent")
        result_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))

        result_label = ctk.CTkLabel(
            result_frame,
            text="生成结果:",
            anchor="w"
        )
        result_label.pack(anchor="w", pady=(0, 5))

        self.arch_result_textbox = ctk.CTkTextbox(
            result_frame,
            height=200
        )
        self.arch_result_textbox.pack(fill="both", expand=True)

    def _build_blueprint_tab(self):
        """构建章节规划生成界面"""
        # 蓝图生成主框架
        blue_main = ctk.CTkFrame(self.blueprint_frame, fg_color="#2A2A2A")
        blue_main.pack(fill="both", expand=True, padx=10, pady=10)

        # 标题
        title_label = ctk.CTkLabel(
            blue_main,
            text="章节规划生成",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(10, 20))

        # 参数配置区域
        params_frame = ctk.CTkFrame(blue_main, fg_color="transparent")
        params_frame.pack(fill="x", padx=20, pady=10)

        # 章节数量
        chapters_frame = ctk.CTkFrame(params_frame, fg_color="transparent")
        chapters_frame.pack(fill="x", pady=5)

        chapters_label = ctk.CTkLabel(
            chapters_frame,
            text="章节数量:",
            width=100,
            anchor="w"
        )
        chapters_label.pack(side="left", padx=(0, 10))

        self.chapters_var = ctk.IntVar(value=20)
        self.chapters_slider = ctk.CTkSlider(
            chapters_frame,
            from_=5,
            to=100,
            number_of_steps=19,  # 5, 10, 15, ..., 100
            variable=self.chapters_var
        )
        self.chapters_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.chapters_label = ctk.CTkLabel(
            chapters_frame,
            text="20",
            width=30
        )
        self.chapters_label.pack(side="left")

        def update_chapters_label(value):
            # 映射到5-100的步进值
            stepped_value = round((value - 5) / 5) * 5 + 5
            stepped_value = min(100, max(5, stepped_value))
            self.chapters_label.configure(text=str(int(stepped_value)))
            self.chapters_var.set(stepped_value)

        self.chapters_slider.configure(command=update_chapters_label)

        # 章节长度
        length_frame = ctk.CTkFrame(params_frame, fg_color="transparent")
        length_frame.pack(fill="x", pady=5)

        length_label = ctk.CTkLabel(
            length_frame,
            text="平均字数:",
            width=100,
            anchor="w"
        )
        length_label.pack(side="left", padx=(0, 10))

        self.length_var = ctk.IntVar(value=3000)
        self.length_entry = ctk.CTkEntry(
            length_frame,
            width=120
        )
        self.length_entry.pack(side="left", padx=(0, 10))
        self.length_entry.insert(0, "3000")

        length_info = ctk.CTkLabel(
            length_frame,
            text="1000-10000字",
            text_color="gray"
        )
        length_info.pack(side="left")

        # 故事大纲
        outline_frame = ctk.CTkFrame(params_frame, fg_color="transparent")
        outline_frame.pack(fill="x", pady=5)

        outline_label = ctk.CTkLabel(
            outline_frame,
            text="故事大纲:",
            width=100,
            anchor="w"
        )
        outline_label.pack(side="left", padx=(0, 10))

        self.outline_textbox = ctk.CTkTextbox(
            outline_frame,
            height=100
        )
        self.outline_textbox.pack(side="left", fill="both", expand=True)

        # 生成按钮
        button_frame = ctk.CTkFrame(blue_main, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=20)

        self.blue_generate_button = ctk.CTkButton(
            button_frame,
            text="生成章节规划",
            command=self._generate_blueprint,
            fg_color="#1976D2",
            hover_color="#2196F3",
            height=40
        )
        self.blue_generate_button.pack(fill="x")

        # 进度条
        self.blue_progress_bar = ctk.CTkProgressBar(blue_main)
        self.blue_progress_bar.pack(fill="x", padx=20, pady=(10, 5))
        self.blue_progress_bar.set(0)

        # 状态标签
        self.blue_status_label = ctk.CTkLabel(
            blue_main,
            text="就绪",
            text_color="gray"
        )
        self.blue_status_label.pack(pady=(0, 10))

        # 结果预览区域
        result_frame = ctk.CTkFrame(blue_main, fg_color="transparent")
        result_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))

        result_label = ctk.CTkLabel(
            result_frame,
            text="章节规划:",
            anchor="w"
        )
        result_label.pack(anchor="w", pady=(0, 5))

        self.blue_result_textbox = ctk.CTkTextbox(
            result_frame,
            height=200
        )
        self.blue_result_textbox.pack(fill="both", expand=True)

    def _build_content_tab(self):
        """构建内容生成界面"""
        # 内容生成主框架
        content_main = ctk.CTkFrame(self.content_frame, fg_color="#2A2A2A")
        content_main.pack(fill="both", expand=True, padx=10, pady=10)

        # 标题
        title_label = ctk.CTkLabel(
            content_main,
            text="章节内容生成",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(10, 20))

        # 参数配置区域
        params_frame = ctk.CTkFrame(content_main, fg_color="transparent")
        params_frame.pack(fill="x", padx=20, pady=10)

        # 章节选择
        chapter_frame = ctk.CTkFrame(params_frame, fg_color="transparent")
        chapter_frame.pack(fill="x", pady=5)

        chapter_label = ctk.CTkLabel(
            chapter_frame,
            text="选择章节:",
            width=100,
            anchor="w"
        )
        chapter_label.pack(side="left", padx=(0, 10))

        self.chapter_var = ctk.StringVar(value="第1章")
        self.chapter_combo = ctk.CTkComboBox(
            chapter_frame,
            variable=self.chapter_var,
            values=["第1章", "第2章", "第3章"]
        )
        self.chapter_combo.pack(side="left", fill="x", expand=True)

        # 内容风格
        style_frame = ctk.CTkFrame(params_frame, fg_color="transparent")
        style_frame.pack(fill="x", pady=5)

        style_label = ctk.CTkLabel(
            style_frame,
            text="内容风格:",
            width=100,
            anchor="w"
        )
        style_label.pack(side="left", padx=(0, 10))

        self.style_var = ctk.StringVar(value="描述性")
        self.style_combo = ctk.CTkComboBox(
            style_frame,
            variable=self.style_var,
            values=["描述性", "对话为主", "动作场景", "心理描写", "抒情"]
        )
        self.style_combo.pack(side="left", fill="x", expand=True)

        # 特殊要求
        special_frame = ctk.CTkFrame(params_frame, fg_color="transparent")
        special_frame.pack(fill="x", pady=5)

        special_label = ctk.CTkLabel(
            special_frame,
            text="特殊要求:",
            width=100,
            anchor="w"
        )
        special_label.pack(side="left", padx=(0, 10))

        self.special_textbox = ctk.CTkTextbox(
            special_frame,
            height=60
        )
        self.special_textbox.pack(side="left", fill="both", expand=True)

        # 生成按钮
        button_frame = ctk.CTkFrame(content_main, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=20)

        self.content_generate_button = ctk.CTkButton(
            button_frame,
            text="生成章节内容",
            command=self._generate_content,
            fg_color="#FF9800",
            hover_color="#F57C00",
            height=40
        )
        self.content_generate_button.pack(fill="x")

        # 进度条
        self.content_progress_bar = ctk.CTkProgressBar(content_main)
        self.content_progress_bar.pack(fill="x", padx=20, pady=(10, 5))
        self.content_progress_bar.set(0)

        # 状态标签
        self.content_status_label = ctk.CTkLabel(
            content_main,
            text="就绪",
            text_color="gray"
        )
        self.content_status_label.pack(pady=(0, 10))

        # 结果预览区域
        result_frame = ctk.CTkFrame(content_main, fg_color="transparent")
        result_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))

        result_label = ctk.CTkLabel(
            result_frame,
            text="生成内容:",
            anchor="w"
        )
        result_label.pack(anchor="w", pady=(0, 5))

        self.content_result_textbox = ctk.CTkTextbox(
            result_frame,
            height=200
        )
        self.content_result_textbox.pack(fill="both", expand=True)

    def _initialize_generator(self):
        """初始化配置"""
        try:
            self.config = load_config("config.json")
            logger.info("配置加载成功")
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
            messagebox.showerror("错误", f"加载配置失败: {e}")

    def _generate_architecture(self):
        """生成小说架构"""
        if self.is_generating:
            messagebox.showwarning("警告", "正在生成中，请等待完成")
            return

        # 获取参数
        theme = self.theme_entry.get().strip()
        if not theme:
            messagebox.showwarning("警告", "请输入小说主题")
            return

        genre = self.genre_var.get()
        world = self.world_textbox.get("1.0", "end-1c").strip()
        characters = self.characters_textbox.get("1.0", "end-1c").strip()

        # 启动生成线程
        self.generation_thread = threading.Thread(
            target=self._do_generate_architecture,
            args=(theme, genre, world, characters),
            daemon=True
        )
        self.generation_thread.start()

    def _do_generate_architecture(self, theme, genre, world, characters):
        """执行小说架构生成"""
        try:
            self.is_generating = True
            self.current_step = "生成小说架构"

            # 更新UI状态
            self._update_arch_status("正在生成小说架构...", 0.2)
            self._toggle_arch_button(False)

            if self.generation_started_callback:
                self.generation_started_callback("architecture")

            # 生成架构
            if self.config:
                try:
                    # 从配置中获取LLM设置
                    llm_config = self.config.get('llm', {})
                    system_config = self.config.get('system', {})

                    # 设置基本参数
                    interface_format = "OpenAI"  # 固定格式
                    api_key = llm_config.get('api_key', '')
                    base_url = llm_config.get('base_url', 'https://api.openai.com/v1')
                    llm_model = llm_config.get('model', 'gpt-3.5-turbo')
                    number_of_chapters = 20  # 默认值
                    word_number = 3000  # 默认值
                    filepath = "Novel_setting.txt"  # 默认文件路径
                    user_guidance = f"世界观背景: {world}\n主要角色: {characters}" if world or characters else ""
                    temperature = 0.7
                    max_tokens = 2048
                    timeout = system_config.get('timeout', 600)

                    # 调用小说架构生成函数
                    Novel_architecture_generate(
                        interface_format=interface_format,
                        api_key=api_key,
                        base_url=base_url,
                        llm_model=llm_model,
                        topic=theme,
                        genre=genre,
                        number_of_chapters=number_of_chapters,
                        word_number=word_number,
                        filepath=filepath,
                        user_guidance=user_guidance,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        timeout=timeout
                    )

                    # 读取生成的结果
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            architecture = f.read()
                    except FileNotFoundError:
                        architecture = f"架构生成完成，请查看 {filepath} 文件"

                    # 更新结果
                    self._update_arch_result(architecture)
                    self._update_arch_status("架构生成完成", 1.0)

                    if self.generation_completed_callback:
                        self.generation_completed_callback("architecture", architecture)

                except Exception as gen_e:
                    error_msg = f"架构生成失败: {str(gen_e)}"
                    self._update_arch_status(error_msg, 0)
                    logger.error(error_msg)
                    messagebox.showerror("错误", error_msg)
            else:
                self._update_arch_status("配置未初始化", 0)
                messagebox.showerror("错误", "配置未初始化")

        except Exception as e:
            logger.error(f"生成小说架构失败: {e}")
            self._update_arch_status(f"生成失败: {e}", 0)
            messagebox.showerror("错误", f"生成小说架构失败: {e}")
        finally:
            self.is_generating = False
            self._toggle_arch_button(True)

    def _generate_blueprint(self):
        """生成章节规划"""
        if self.is_generating:
            messagebox.showwarning("警告", "正在生成中，请等待完成")
            return

        # 获取参数
        chapters = int(self.chapters_var.get())
        try:
            avg_length = int(self.length_entry.get())
            avg_length = max(1000, min(10000, avg_length))  # 限制在1000-10000之间
        except (ValueError, TypeError):
            avg_length = 3000
        outline = self.outline_textbox.get("1.0", "end-1c").strip()

        # 启动生成线程
        self.generation_thread = threading.Thread(
            target=self._do_generate_blueprint,
            args=(chapters, avg_length, outline),
            daemon=True
        )
        self.generation_thread.start()

    def _do_generate_blueprint(self, chapters, avg_length, outline):
        """执行章节规划生成"""
        try:
            self.is_generating = True
            self.current_step = "生成章节规划"

            # 更新UI状态
            self._update_blue_status("正在生成章节规划...", 0.2)
            self._toggle_blue_button(False)

            if self.generation_started_callback:
                self.generation_started_callback("blueprint")

            # 生成蓝图
            if self.novel_generator:
                blueprint = self.novel_generator.generate_blueprint(
                    chapter_count=chapters,
                    avg_length=avg_length,
                    outline=outline
                )

                # 更新结果
                self._update_blue_result(blueprint)
                self._update_blue_status("章节规划生成完成", 1.0)

                if self.generation_completed_callback:
                    self.generation_completed_callback("blueprint", blueprint)
            else:
                self._update_blue_status("生成器未初始化", 0)
                messagebox.showerror("错误", "小说生成器未初始化")

        except Exception as e:
            logger.error(f"生成章节规划失败: {e}")
            self._update_blue_status(f"生成失败: {e}", 0)
            messagebox.showerror("错误", f"生成章节规划失败: {e}")
        finally:
            self.is_generating = False
            self._toggle_blue_button(True)

    def _generate_content(self):
        """生成章节内容"""
        if self.is_generating:
            messagebox.showwarning("警告", "正在生成中，请等待完成")
            return

        # 获取参数
        chapter = self.chapter_var.get()
        style = self.style_var.get()
        special = self.special_textbox.get("1.0", "end-1c").strip()

        # 启动生成线程
        self.generation_thread = threading.Thread(
            target=self._do_generate_content,
            args=(chapter, style, special),
            daemon=True
        )
        self.generation_thread.start()

    def _do_generate_content(self, chapter, style, special):
        """执行章节内容生成"""
        try:
            self.is_generating = True
            self.current_step = "生成章节内容"

            # 更新UI状态
            self._update_content_status("正在生成章节内容...", 0.2)
            self._toggle_content_button(False)

            if self.generation_started_callback:
                self.generation_started_callback("content")

            # 生成内容
            if self.novel_generator:
                content = self.novel_generator.generate_chapter(
                    chapter_name=chapter,
                    style=style,
                    special_requirements=special
                )

                # 更新结果
                self._update_content_result(content)
                self._update_content_status("章节内容生成完成", 1.0)

                if self.generation_completed_callback:
                    self.generation_completed_callback("content", content)
            else:
                self._update_content_status("生成器未初始化", 0)
                messagebox.showerror("错误", "小说生成器未初始化")

        except Exception as e:
            logger.error(f"生成章节内容失败: {e}")
            self._update_content_status(f"生成失败: {e}", 0)
            messagebox.showerror("错误", f"生成章节内容失败: {e}")
        finally:
            self.is_generating = False
            self._toggle_content_button(True)

    def _update_arch_status(self, text, progress):
        """更新架构生成状态"""
        self.arch_status_label.configure(text=text)
        self.arch_progress_bar.set(progress)

    def _update_arch_result(self, result):
        """更新架构生成结果"""
        self.arch_result_textbox.delete("1.0", "end")
        self.arch_result_textbox.insert("1.0", result)

    def _toggle_arch_button(self, enabled):
        """切换架构生成按钮状态"""
        if enabled:
            self.arch_generate_button.configure(state="normal")
        else:
            self.arch_generate_button.configure(state="disabled")

    def _update_blue_status(self, text, progress):
        """更新蓝图生成状态"""
        self.blue_status_label.configure(text=text)
        self.blue_progress_bar.set(progress)

    def _update_blue_result(self, result):
        """更新蓝图生成结果"""
        self.blue_result_textbox.delete("1.0", "end")
        self.blue_result_textbox.insert("1.0", result)

    def _toggle_blue_button(self, enabled):
        """切换蓝图生成按钮状态"""
        if enabled:
            self.blue_generate_button.configure(state="normal")
        else:
            self.blue_generate_button.configure(state="disabled")

    def _update_content_status(self, text, progress):
        """更新内容生成状态"""
        self.content_status_label.configure(text=text)
        self.content_progress_bar.set(progress)

    def _update_content_result(self, result):
        """更新内容生成结果"""
        self.content_result_textbox.delete("1.0", "end")
        self.content_result_textbox.insert("1.0", result)

    def _toggle_content_button(self, enabled):
        """切换内容生成按钮状态"""
        if enabled:
            self.content_generate_button.configure(state="normal")
        else:
            self.content_generate_button.configure(state="disabled")

    def set_generation_started_callback(self, callback: Callable[[str], None]):
        """设置生成开始回调函数"""
        self.generation_started_callback = callback

    def set_generation_completed_callback(self, callback: Callable[[str, str], None]):
        """设置生成完成回调函数"""
        self.generation_completed_callback = callback

    def is_generation_in_progress(self) -> bool:
        """检查是否正在生成"""
        return self.is_generating

    def stop_generation(self):
        """停止生成"""
        # 这里可以实现停止生成的逻辑
        logger.info("停止生成功能待实现")

    def apply_theme_style(self, theme_data: Dict[str, Any]):
        """应用主题样式"""
        try:
            colors = theme_data.get('colors', {})

            # 更新标签页样式
            if self.generate_tabview:
                self.generate_tabview.configure(
                    segmented_button_fg_color=colors.get('surface', '#2A2A2A'),
                    segmented_button_selected_color=colors.get('primary', '#404040'),
                    segmented_button_unselected_color=colors.get('background', '#1E1E1E')
                )

        except Exception as e:
            logger.error(f"应用主题到生成标签页失败: {e}")

    def get_generation_info(self) -> Dict[str, Any]:
        """获取生成标签页信息"""
        return {
            'is_generating': self.is_generating,
            'current_step': self.current_step,
            'generation_progress': self.generation_progress,
            'has_config': self.config is not None,
            'has_started_callback': self.generation_started_callback is not None,
            'has_completed_callback': self.generation_completed_callback is not None
        }