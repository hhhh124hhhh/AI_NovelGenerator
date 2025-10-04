"""
现代化目录管理组件 - AI小说生成器的章节大纲和结构管理
迁移自1.0版本的directory_tab.py功能，采用2.0架构重构
"""

import logging
import os
from typing import Dict, Any, Optional, Callable, List
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from config_manager import load_config
import customtkinter as ctk
from tkinter import messagebox, filedialog
from config_manager import load_config
from ..file_watcher import get_file_watcher
from tkinter import filedialog, messagebox

logger = logging.getLogger(__name__)


class DirectoryManager(ctk.CTkFrame):
    """
    现代化目录管理组件

    功能：
    - 章节大纲显示和编辑
    - 章节顺序调整
    - 章节预览功能
    - 章节导入导出
    - 章节统计信息
    """

    def __init__(self, parent: ctk.CTkFrame, theme_manager, state_manager=None, **kwargs):
        """
        初始化目录管理器

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
        self.config_data: Dict[str, Any] = load_config("config.json")
        self.chapters = []
        self.selected_chapter = None

        # 组件引用
        self.chapters_tree = None
        self.chapter_preview = None
        self.chapter_info_labels = {}

        # 回调函数
        self.chapter_selected_callback = None
        self.chapter_modified_callback = None

        # 初始化组件
        self._create_directory_layout()
        self._initialize_data()
        self._setup_event_handlers()
        
        # 设置文件监控
        self._setup_file_watcher()

        logger.debug("DirectoryManager 组件初始化完成")

    def _create_directory_layout(self):
        """创建目录管理布局"""
        # 配置主框架
        self.configure(
            corner_radius=8,
            fg_color="transparent"
        )

        # 配置网格布局
        self.grid_columnconfigure(0, weight=2)  # 章节列表
        self.grid_columnconfigure(1, weight=1)  # 预览区域
        self.grid_rowconfigure(0, weight=1)

        # 创建左侧章节列表区域
        self._create_chapters_panel()

        # 创建右侧预览区域
        self._create_preview_panel()

    def _create_chapters_panel(self):
        """创建章节列表面板"""
        # 章节列表容器
        chapters_container = ctk.CTkFrame(self, corner_radius=8)
        chapters_container.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=10)
        chapters_container.grid_rowconfigure(1, weight=1)
        chapters_container.grid_columnconfigure(0, weight=1)

        # 标题区域
        header_frame = ctk.CTkFrame(chapters_container, corner_radius=8)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        header_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # 标题标签
        title_label = ctk.CTkLabel(
            header_frame,
            text="📚 章节大纲",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=10, pady=10, sticky="w", columnspan=2)

        # 章节统计
        self.chapter_info_labels['count'] = ctk.CTkLabel(
            header_frame,
            text="章节数: 0",
            font=ctk.CTkFont(size=12)
        )
        self.chapter_info_labels['count'].grid(row=0, column=2, padx=5, pady=10)

        # 操作按钮
        btn_frame = ctk.CTkFrame(header_frame)
        btn_frame.grid(row=0, column=3, padx=10, pady=10)

        buttons = [
            ("📁 导入", self._import_chapters),
            ("📤 导出", self._export_chapters)
        ]

        for i, (text, command) in enumerate(buttons):
            btn = ctk.CTkButton(
                btn_frame,
                text=text,
                command=command,
                width=60,
                height=25,
                font=ctk.CTkFont(size=10)
            )
            btn.pack(side="left", padx=2)

        # 章节树形列表
        tree_frame = ctk.CTkFrame(chapters_container, corner_radius=8)
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        # 创建章节树
        self.chapters_tree = ctk.CTkScrollableFrame(
            tree_frame,
            orientation="vertical",
            height=500,
            corner_radius=8
        )
        self.chapters_tree.pack(fill="both", expand=True)

        # 控制按钮区域
        control_frame = ctk.CTkFrame(chapters_container, corner_radius=8)
        control_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        control_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        control_buttons = [
            ("➕ 新增", self._add_chapter),
            ("✏️ 编辑", self._edit_chapter),
            ("⬆️ 上移", self._move_chapter_up),
            ("⬇️ 下移", self._move_chapter_down),
            ("🗑️ 删除", self._delete_chapter)
        ]

        for i, (text, command) in enumerate(control_buttons):
            btn = ctk.CTkButton(
                control_frame,
                text=text,
                command=command,
                font=ctk.CTkFont(size=12),
                height=35
            )
            btn.grid(row=0, column=i, padx=2, pady=8, sticky="ew")

    def _create_preview_panel(self):
        """创建预览面板"""
        # 预览容器
        preview_container = ctk.CTkFrame(self, corner_radius=8)
        preview_container.grid(row=0, column=1, sticky="nsew", padx=5, pady=10)
        preview_container.grid_rowconfigure(1, weight=1)
        preview_container.grid_columnconfigure(0, weight=1)

        # 预览标题
        preview_header = ctk.CTkFrame(preview_container, corner_radius=8)
        preview_header.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))

        preview_title_label = ctk.CTkLabel(
            preview_header,
            text="🔍 章节预览",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        preview_title_label.pack(padx=10, pady=10, anchor="w")

        # 章节信息标签
        info_frame = ctk.CTkFrame(preview_container, corner_radius=8)
        info_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        info_frame.grid_columnconfigure((0, 1), weight=1)

        # 章节编号
        ctk.CTkLabel(
            info_frame,
            text="章节编号:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.chapter_info_labels['number'] = ctk.CTkLabel(
            info_frame,
            text="-",
            font=ctk.CTkFont(size=12)
        )
        self.chapter_info_labels['number'].grid(row=0, column=1, padx=10, pady=5, sticky="w")

        # 章节标题
        ctk.CTkLabel(
            info_frame,
            text="章节标题:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.chapter_info_labels['title'] = ctk.CTkLabel(
            info_frame,
            text="-",
            font=ctk.CTkFont(size=12)
        )
        self.chapter_info_labels['title'].grid(row=1, column=1, padx=10, pady=5, sticky="w")

        # 预览文本区域
        self.chapter_preview = ctk.CTkTextbox(
            preview_container,
            wrap="word",
            font=ctk.CTkFont(size=12),
            height=400
        )
        self.chapter_preview.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

        # 设置为只读
        self.chapter_preview.configure(state="disabled")

    def _initialize_data(self):
        """初始化数据"""
        try:
            # 从配置中获取保存路径
            self.save_path = self.config_data.get("other_params", {}).get("filepath", "")

            # 尝试加载现有章节目录
            self._load_chapters()

        except Exception as e:
            logger.error(f"初始化数据失败: {e}")

    def _setup_event_handlers(self):
        """设置事件处理器"""
        # 这里可以添加事件处理器
        pass
        
    def _setup_file_watcher(self):
        """设置文件监控"""
        try:
            if self.save_path and os.path.exists(self.save_path):
                file_watcher = get_file_watcher()
                file_watcher.add_watch_path(self.save_path, self._on_file_changed)
                logger.info(f"开始监控目录: {self.save_path}")
        except Exception as e:
            logger.error(f"设置文件监控失败: {e}")
            
    def _on_file_changed(self, filepath: str, change_type: str):
        """文件变化回调"""
        try:
            # 如果是章节目录文件变化，重新加载
            if os.path.basename(filepath) == "Novel_directory.txt":
                logger.info(f"章节目录文件变化: {change_type}")
                self._load_chapters()
                
            # 如果是章节内容文件变化，更新预览
            elif filepath.endswith('.txt') and 'Chapter' in filepath:
                logger.info(f"章节文件变化: {filepath} ({change_type})")
                # 如果当前选中的是变化的章节，更新预览
                if (self.selected_chapter and 
                    f"第{self.selected_chapter['number']}章" in filepath):
                    self._load_chapter_content(filepath)
        except Exception as e:
            logger.error(f"处理文件变化失败: {e}")
            
    def _load_chapter_content(self, filepath: str):
        """加载章节内容"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 更新预览
                if self.chapter_preview:
                    self.chapter_preview.configure(state="normal")
                    self.chapter_preview.delete("0.0", "end")
                    self.chapter_preview.insert("0.0", content[:500] + "..." if len(content) > 500 else content)
                    self.chapter_preview.configure(state="disabled")
        except Exception as e:
            logger.error(f"加载章节内容失败: {e}")

    def _load_chapters(self):
        """加载章节目录"""
        try:
            chapters = []

            # 构建文件路径
            if self.save_path:
                blueprint_path = os.path.join(self.save_path, "Novel_directory.txt")
            else:
                blueprint_path = "Novel_directory.txt"

            # 读取章节目录文件
            if os.path.exists(blueprint_path):
                with open(blueprint_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 解析章节目录
                chapters = self._parse_chapter_content(content)

            # 如果没有章节，创建默认章节
            if not chapters:
                chapters = self._create_default_chapters()

            # 更新章节列表
            self._update_chapters_list(chapters)

            logger.info(f"已加载{len(chapters)}个章节")

        except Exception as e:
            logger.error(f"加载章节目录失败: {e}")
            # 创建默认章节
            default_chapters = self._create_default_chapters()
            self._update_chapters_list(default_chapters)

    def _parse_chapter_content(self, content: str) -> List[Dict[str, Any]]:
        """解析章节目录内容"""
        chapters = []
        lines = content.split('\n')

        current_chapter = None

        for line in lines:
            line = line.strip()
            if line.startswith('## 第'):
                # 解析章节标题
                if '章：' in line:
                    parts = line.split('章：', 1)
                    number_part = parts[0].replace('## 第', '').strip()
                    title_part = parts[1].strip() if len(parts) > 1 else "未命名章节"

                    try:
                        chapter_num = int(number_part)
                    except:
                        chapter_num = len(chapters) + 1

                    current_chapter = {
                        'number': chapter_num,
                        'title': title_part,
                        'preview': line
                    }
                    chapters.append(current_chapter)

            elif current_chapter and line and not line.startswith('#'):
                # 添加章节描述
                if 'preview' not in current_chapter:
                    current_chapter['preview'] = line
                else:
                    current_chapter['preview'] += '\n' + line

        return chapters

    def _create_default_chapters(self) -> List[Dict[str, Any]]:
        """创建默认章节"""
        default_chapters = []
        num_chapters = self.config_data.get("other_params", {}).get("num_chapters", 10)

        for i in range(1, num_chapters + 1):
            default_chapters.append({
                'number': i,
                'title': f"第{i}章：待定标题",
                'preview': "本章主要内容将在生成后显示..."
            })

        return default_chapters

    def _update_chapters_list(self, chapters: List[Dict[str, Any]]):
        """更新章节列表"""
        try:
            # 清空现有组件
            if self.chapters_tree:
                for widget in self.chapters_tree.winfo_children():
                    widget.destroy()

            self.chapters = chapters

            # 创建章节项
            for i, chapter in enumerate(chapters):
                chapter_frame = ctk.CTkFrame(
                    self.chapters_tree,
                    corner_radius=6,
                    fg_color="#2A2A2A" if i % 2 == 0 else "#252526"
                )
                chapter_frame.pack(fill="x", padx=5, pady=2)

                # 章节信息
                info_label = ctk.CTkLabel(
                    chapter_frame,
                    text=f"第{chapter['number']}章 - {chapter['title']}",
                    font=ctk.CTkFont(size=12),
                    anchor="w"
                )
                info_label.pack(side="left", padx=10, pady=8)

                # 选择按钮
                select_btn = ctk.CTkButton(
                    chapter_frame,
                    text="查看",
                    width=60,
                    height=30,
                    font=ctk.CTkFont(size=10),
                    command=lambda c=chapter: self._select_chapter(c)
                )
                select_btn.pack(side="right", padx=10, pady=8)

            # 更新统计信息
            self.chapter_info_labels['count'].configure(text=f"章节数: {len(chapters)}")

        except Exception as e:
            logger.error(f"更新章节列表失败: {e}")

    def _select_chapter(self, chapter: Dict[str, Any]):
        """选择章节"""
        try:
            self.selected_chapter = chapter

            # 更新章节信息
            self.chapter_info_labels['number'].configure(text=str(chapter['number']))
            self.chapter_info_labels['title'].configure(text=chapter['title'])

            # 更新预览内容
            if self.chapter_preview:
                self.chapter_preview.configure(state="normal")
                self.chapter_preview.delete("0.0", "end")

                preview_content = chapter.get('preview', '暂无预览内容')
                self.chapter_preview.insert("0.0", preview_content)
                self.chapter_preview.configure(state="disabled")

            # 调用选择回调
            if self.chapter_selected_callback:
                self.chapter_selected_callback(chapter)

            logger.info(f"选择章节: {chapter['number']} - {chapter['title']}")

        except Exception as e:
            logger.error(f"选择章节失败: {e}")

    def _add_chapter(self):
        """添加章节"""
        try:
            if not self.chapters:
                next_number = 1
            else:
                next_number = max(ch['number'] for ch in self.chapters) + 1

            new_chapter = {
                'number': next_number,
                'title': f"第{next_number}章：新章节",
                'preview': "新章节的预览内容..."
            }

            self.chapters.append(new_chapter)
            self._update_chapters_list(self.chapters)
            self._save_chapters()

            logger.info(f"添加章节: {new_chapter['number']} - {new_chapter['title']}")

        except Exception as e:
            logger.error(f"添加章节失败: {e}")

    def _edit_chapter(self):
        """编辑章节"""
        try:
            if not self.selected_chapter:
                messagebox.showwarning("提示", "请先选择要编辑的章节")
                return

            # 创建编辑对话框
            edit_dialog = ChapterEditDialog(self, self.selected_chapter)
            result = edit_dialog.show()

            if result:
                # 更新章节信息
                for chapter in self.chapters:
                    if chapter['number'] == result['number']:
                        chapter.update(result)
                        break

                self._update_chapters_list(self.chapters)
                self._save_chapters()
                self._select_chapter(result)  # 重新选择以更新预览

                logger.info(f"编辑章节: {result['number']} - {result['title']}")

        except Exception as e:
            logger.error(f"编辑章节失败: {e}")

    def _move_chapter_up(self):
        """章节上移"""
        try:
            if not self.selected_chapter:
                messagebox.showwarning("提示", "请先选择要移动的章节")
                return

            current_index = next(i for i, ch in enumerate(self.chapters)
                                if ch['number'] == self.selected_chapter['number'])

            if current_index > 0:
                # 交换位置
                self.chapters[current_index], self.chapters[current_index - 1] = \
                    self.chapters[current_index - 1], self.chapters[current_index]

                self._update_chapters_list(self.chapters)
                self._save_chapters()

                # 重新选择
                self._select_chapter(self.chapters[current_index - 1])

                logger.info(f"章节上移: {self.selected_chapter['title']}")

        except Exception as e:
            logger.error(f"章节上移失败: {e}")

    def _move_chapter_down(self):
        """章节下移"""
        try:
            if not self.selected_chapter:
                messagebox.showwarning("提示", "请先选择要移动的章节")
                return

            current_index = next(i for i, ch in enumerate(self.chapters)
                                if ch['number'] == self.selected_chapter['number'])

            if current_index < len(self.chapters) - 1:
                # 交换位置
                self.chapters[current_index], self.chapters[current_index + 1] = \
                    self.chapters[current_index + 1], self.chapters[current_index]

                self._update_chapters_list(self.chapters)
                self._save_chapters()

                # 重新选择
                self._select_chapter(self.chapters[current_index + 1])

                logger.info(f"章节下移: {self.selected_chapter['title']}")

        except Exception as e:
            logger.error(f"章节下移失败: {e}")

    def _delete_chapter(self):
        """删除章节"""
        try:
            if not self.selected_chapter:
                messagebox.showwarning("提示", "请先选择要删除的章节")
                return

            if messagebox.askyesno("确认删除", f"确定要删除章节 {self.selected_chapter['title']} 吗？"):
                # 删除章节
                self.chapters = [ch for ch in self.chapters
                                if ch['number'] != self.selected_chapter['number']]

                # 重新编号
                for i, chapter in enumerate(self.chapters, 1):
                    chapter['number'] = i
                    if chapter['title'].startswith(f"第{chapter['number']-1}章"):
                        chapter['title'] = chapter['title'].replace(f"第{chapter['number']-1}章", f"第{chapter['number']}章")

                self._update_chapters_list(self.chapters)
                self._save_chapters()

                # 清空预览
                self._clear_preview()

                logger.info(f"删除章节: {self.selected_chapter['title']}")

        except Exception as e:
            logger.error(f"删除章节失败: {e}")

    def _clear_preview(self):
        """清空预览"""
        try:
            self.selected_chapter = None

            if self.chapter_preview:
                self.chapter_preview.configure(state="normal")
                self.chapter_preview.delete("0.0", "end")
                self.chapter_preview.configure(state="disabled")

            self.chapter_info_labels['number'].configure(text="-")
            self.chapter_info_labels['title'].configure(text="-")

        except Exception as e:
            logger.error(f"清空预览失败: {e}")

    def _save_chapters(self):
        """保存章节目录"""
        try:
            # 生成章节目录内容
            blueprint_content = "# 小说章节目录\n\n"

            for chapter in self.chapters:
                blueprint_content += f"## 第{chapter['number']}章：{chapter['title']}\n"
                blueprint_content += f"{chapter.get('preview', '')}\n\n"

            # 构建文件路径
            if self.save_path:
                blueprint_path = os.path.join(self.save_path, "Novel_directory.txt")
            else:
                blueprint_path = "Novel_directory.txt"

            # 确保目录存在
            os.makedirs(os.path.dirname(blueprint_path), exist_ok=True)

            # 保存文件
            with open(blueprint_path, 'w', encoding='utf-8') as f:
                f.write(blueprint_content)

            logger.info(f"章节目录已保存到 {blueprint_path}")

        except Exception as e:
            logger.error(f"保存章节目录失败: {e}")

    def _import_chapters(self):
        """导入章节"""
        try:
            # 选择文件
            file_path = filedialog.askopenfilename(
                title="导入章节目录",
                filetypes=[
                    ("文本文件", "*.txt"),
                    ("Markdown文件", "*.md"),
                    ("所有文件", "*.*")
                ]
            )

            if file_path:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 解析章节
                imported_chapters = self._parse_chapter_content(content)

                if imported_chapters:
                    self.chapters.extend(imported_chapters)
                    self._update_chapters_list(self.chapters)
                    self._save_chapters()
                    messagebox.showinfo("导入成功", f"已导入{len(imported_chapters)}个章节")
                else:
                    messagebox.showwarning("导入失败", "文件中没有找到有效的章节信息")

        except Exception as e:
            logger.error(f"导入章节失败: {e}")
            messagebox.showerror("导入失败", f"导入章节时出错: {str(e)}")

    def _export_chapters(self):
        """导出章节"""
        try:
            if not self.chapters:
                messagebox.showwarning("导出提示", "没有章节可以导出")
                return

            # 选择保存位置
            export_path = filedialog.asksaveasfilename(
                title="导出章节目录",
                defaultextension=".txt",
                filetypes=[
                    ("文本文件", "*.txt"),
                    ("Markdown文件", "*.md"),
                    ("JSON文件", "*.json"),
                    ("所有文件", "*.*")
                ]
            )

            if export_path:
                file_ext = os.path.splitext(export_path)[1].lower()

                if file_ext == '.json':
                    # 导出为JSON格式
                    export_data = {
                        'title': '小说章节目录',
                        'chapters': self.chapters,
                        'total_chapters': len(self.chapters),
                        'exported_at': str(os.path.getctime(export_path) if os.path.exists(export_path) else '')
                    }
                    import json
                    with open(export_path, 'w', encoding='utf-8') as f:
                        json.dump(export_data, f, ensure_ascii=False, indent=2)
                else:
                    # 导出为文本格式
                    blueprint_content = "# 小说章节目录\n\n"

                    for chapter in self.chapters:
                        blueprint_content += f"## 第{chapter['number']}章：{chapter['title']}\n"
                        blueprint_content += f"{chapter.get('preview', '')}\n\n"

                    with open(export_path, 'w', encoding='utf-8') as f:
                        f.write(blueprint_content)

                logger.info(f"章节目录已导出到 {export_path}")
                messagebox.showinfo("导出成功", f"已导出{len(self.chapters)}个章节")

        except Exception as e:
            logger.error(f"导出章节失败: {e}")
            messagebox.showerror("导出失败", f"导出章节时出错: {str(e)}")

    # 公共接口方法
    def get_chapters(self) -> List[Dict[str, Any]]:
        """获取章节列表"""
        return self.chapters.copy()

    def set_chapters(self, chapters: List[Dict[str, Any]]):
        """设置章节列表"""
        self.chapters = chapters.copy()
        self._update_chapters_list(self.chapters)
        self._save_chapters()

    def set_chapter_selected_callback(self, callback: Callable):
        """设置章节选择回调"""
        self.chapter_selected_callback = callback

    def set_chapter_modified_callback(self, callback: Callable):
        """设置章节修改回调"""
        self.chapter_modified_callback = callback


class ChapterEditDialog:
    """章节编辑对话框"""

    def __init__(self, parent, chapter: Dict[str, Any]):
        self.parent = parent
        self.chapter = chapter.copy()
        self.result = None

    def show(self) -> Optional[Dict[str, Any]]:
        """显示对话框"""
        try:
            # 创建对话框窗口
            dialog = ctk.CTkToplevel(self.parent)
            dialog.title("编辑章节")
            dialog.geometry("400x200")
            dialog.transient(self.parent)
            dialog.grab_set()

            # 章节编号
            ctk.CTkLabel(dialog, text="章节编号:", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(10, 5))
            number_var = ctk.StringVar(value=str(self.chapter['number']))
            number_entry = ctk.CTkEntry(dialog, textvariable=number_var, font=ctk.CTkFont(size=12))
            number_entry.pack(padx=20, pady=(0, 10), fill="x")

            # 章节标题
            ctk.CTkLabel(dialog, text="章节标题:", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(10, 5))
            title_var = ctk.StringVar(value=self.chapter['title'])
            title_entry = ctk.CTkEntry(dialog, textvariable=title_var, font=ctk.CTkFont(size=12))
            title_entry.pack(padx=20, pady=(0, 10), fill="x")

            # 章节预览
            ctk.CTkLabel(dialog, text="章节预览:", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(10, 5))
            preview_text = ctk.CTkTextbox(dialog, height=80, font=ctk.CTkFont(size=11))
            preview_text.pack(padx=20, pady=(0, 10), fill="x")
            preview_text.insert("0.0", self.chapter.get('preview', ''))

            # 按钮区域
            btn_frame = ctk.CTkFrame(dialog)
            btn_frame.pack(pady=10)

            def on_ok():
                try:
                    self.result = {
                        'number': int(number_var.get()),
                        'title': title_var.get(),
                        'preview': preview_text.get("0.0", "end").strip()
                    }
                    dialog.destroy()
                except ValueError:
                    messagebox.showerror("错误", "章节编号必须是数字")

            def on_cancel():
                dialog.destroy()

            ctk.CTkButton(btn_frame, text="确定", command=on_ok, width=80).pack(side="left", padx=5)
            ctk.CTkButton(btn_frame, text="取消", command=on_cancel, width=80).pack(side="right", padx=5)

            # 等待对话框关闭
            dialog.wait_window()

            return self.result

        except Exception as e:
            logger.error(f"显示编辑对话框失败: {e}")
            return None