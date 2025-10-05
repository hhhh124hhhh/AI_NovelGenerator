# ui_fixes_integration.py
# -*- coding: utf-8 -*-
"""
UI修复集成脚本 - BMAD方法的完整实现
解决UI 2.0的所有问题：角色面板、窗口大小、字体设置
"""

import os
import sys
import logging
from typing import Dict, Any, Optional

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logger = logging.getLogger(__name__)


class UIFixesIntegration:
    """
    UI修复集成器

    功能：
    - 集成所有UI修复组件
    - 提供统一的修复接口
    - 自动应用修复到现有UI
    """

    def __init__(self):
        """初始化UI修复集成器"""
        self.data_bridge = None
        self.responsive_settings = None
        self.character_manager = None

        # 初始化组件
        self._initialize_components()

        logger.info("UI修复集成器初始化完成")

    def _initialize_components(self):
        """初始化修复组件"""
        try:
            # 初始化数据桥接器
            from .ui.data_bridge import get_data_bridge
            self.data_bridge = get_data_bridge()
            logger.info("数据桥接器初始化成功")
        except ImportError as e:
            logger.warning(f"数据桥接器初始化失败: {e}")

        try:
            # 初始化响应式设置管理器
            from .ui.components.responsive_settings import get_responsive_settings
            self.responsive_settings = get_responsive_settings()
            logger.info("响应式设置管理器初始化成功")
        except ImportError as e:
            logger.warning(f"响应式设置管理器初始化失败: {e}")

        try:
            # 初始化增强角色管理器
            from .ui.components.characters_tab_enhanced import CharactersTabEnhanced
            self.character_manager = CharactersTabEnhanced
            logger.info("增强角色管理器初始化成功")
        except ImportError as e:
            logger.warning(f"增强角色管理器初始化失败: {e}")

    def apply_character_data_fix(self, main_window):
        """
        应用角色数据修复

        Args:
            main_window: 主窗口实例
        """
        if not self.data_bridge:
            logger.warning("数据桥接器不可用，无法应用角色数据修复")
            return False

        try:
            # 检查是否有生成的角色数据
            character_files = [
                './Novel_setting.txt',
                './novel_output/Novel_setting.txt',
                './test_output/Novel_setting.txt'
            ]

            character_data = None
            character_file = None

            for file_path in character_files:
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if len(content) > 100:  # 确保有实际内容
                            character_data = content
                            character_file = file_path
                            break

            if character_data:
                # 解析并更新角色数据
                characters = self.data_bridge.convert_character_data(character_data)
                if characters:
                    self.data_bridge.update_data('characters', characters, notify=True)
                    logger.info(f"从 {character_file} 加载了 {len(characters)} 个角色")
                    return True
                else:
                    logger.warning(f"从 {character_file} 未能解析出角色数据")
            else:
                logger.info("未找到角色数据文件")

        except Exception as e:
            logger.error(f"应用角色数据修复失败: {e}")

        return False

    def apply_responsive_settings_fix(self, main_window):
        """
        应用响应式设置修复

        Args:
            main_window: 主窗口实例
        """
        if not self.responsive_settings:
            logger.warning("响应式设置管理器不可用，无法应用设置修复")
            return False

        try:
            # 设置窗口最小大小
            min_width, min_height = self.responsive_settings.get_min_window_size()
            main_window.minsize(min_width, min_height)

            # 设置默认窗口大小
            default_width, default_height = self.responsive_settings.get_window_size()
            main_window.geometry(f"{default_width}x{default_height}")

            logger.info(f"窗口大小设置为: {default_width}x{default_height} (最小: {min_width}x{min_height})")

            # 应用字体设置到主窗口
            self._apply_fonts_to_window(main_window)

            return True

        except Exception as e:
            logger.error(f"应用响应式设置修复失败: {e}")
            return False

    def _apply_fonts_to_window(self, window):
        """应用字体设置到窗口"""
        try:
            # 应用基础字体
            base_font = self.responsive_settings.get_font('base')
            title_font = self.responsive_settings.get_font('title')
            small_font = self.responsive_settings.get_font('small')

            # 遍历所有子组件应用字体
            def apply_fonts_recursive(widget):
                try:
                    # 应用字体到支持字体的组件
                    if hasattr(widget, 'configure'):
                        if isinstance(widget, ctk.CTkLabel):
                            if '标题' in str(widget.cget('text')) or 'Label' in str(widget.__class__):
                                widget.configure(font=title_font)
                            else:
                                widget.configure(font=base_font)
                        elif isinstance(widget, (ctk.CTkButton, ctk.CTkEntry)):
                            widget.configure(font=base_font)
                        elif isinstance(widget, ctk.CTkTextbox):
                            widget.configure(font=base_font)
                        elif isinstance(widget, ctk.CTkOptionMenu):
                            widget.configure(font=base_font)

                    # 递归应用到子组件
                    for child in widget.winfo_children():
                        apply_fonts_recursive(child)

                except Exception as e:
                    # 忽略单个组件的字体应用失败
                    pass

            apply_fonts_recursive(window)
            logger.info("字体设置应用到窗口")

        except Exception as e:
            logger.error(f"应用字体设置失败: {e}")

    def replace_character_tab(self, main_window):
        """
        替换角色标签页为增强版本

        Args:
            main_window: 主窗口实例
        """
        if not self.character_manager:
            logger.warning("增强角色管理器不可用，无法替换角色标签页")
            return False

        try:
            # 这里需要根据实际的UI结构来实现
            # 由于不同版本的UI结构可能不同，这里提供通用逻辑

            # 查找现有的角色标签页
            character_tab = None
            parent_frame = None

            # 尝试找到角色相关的组件
            def find_character_tab(widget):
                nonlocal character_tab, parent_frame

                if hasattr(widget, '__class__'):
                    class_name = widget.__class__.__name__
                    if 'Character' in class_name or 'character' in str(widget.__dict__):
                        character_tab = widget
                        parent_frame = widget.master
                        return True

                for child in widget.winfo_children():
                    if find_character_tab(child):
                        return True
                return False

            # 从主窗口开始搜索
            find_character_tab(main_window)

            if character_tab and parent_frame:
                # 创建增强的角色标签页
                enhanced_character_tab = self.character_manager(
                    parent_frame,
                    theme_manager=getattr(main_window, 'theme_manager', None),
                    state_manager=getattr(main_window, 'state_manager', None),
                    main_window=main_window
                )

                # 替换旧的标签页
                character_tab.destroy()

                # 如果有布局管理器，需要重新布局
                try:
                    if hasattr(parent_frame, 'pack_slaves'):
                        # 使用pack布局
                        enhanced_character_tab.pack(fill="both", expand=True)
                    elif hasattr(parent_frame, 'grid_slaves'):
                        # 使用grid布局
                        enhanced_character_tab.grid(row=0, column=0, sticky="nsew")
                    else:
                        # 默认使用pack
                        enhanced_character_tab.pack(fill="both", expand=True)
                except Exception as e:
                    logger.warning(f"布局调整失败: {e}")

                logger.info("角色标签页已替换为增强版本")
                return True
            else:
                logger.info("未找到角色标签页，跳过替换")

        except Exception as e:
            logger.error(f"替换角色标签页失败: {e}")

        return False

    def apply_all_fixes(self, main_window):
        """
        应用所有UI修复

        Args:
            main_window: 主窗口实例

        Returns:
            修复结果字典
        """
        results = {
            'character_data_fix': False,
            'responsive_settings_fix': False,
            'character_tab_replacement': False,
            'font_applied': False
        }

        # 应用角色数据修复
        results['character_data_fix'] = self.apply_character_data_fix(main_window)

        # 应用响应式设置修复
        results['responsive_settings_fix'] = self.apply_responsive_settings_fix(main_window)

        # 替换角色标签页
        results['character_tab_replacement'] = self.replace_character_tab(main_window)

        # 字体应用在响应式设置修复中已经包含
        results['font_applied'] = results['responsive_settings_fix']

        success_count = sum(results.values())
        total_count = len(results)

        logger.info(f"UI修复完成: {success_count}/{total_count} 项修复成功")

        return results

    def create_settings_dialog(self, parent):
        """
        创建增强的设置对话框

        Args:
            parent: 父窗口

        Returns:
            设置对话框
        """
        if self.responsive_settings:
            return self.responsive_settings.create_responsive_settings_dialog(parent)
        else:
            # 回退到基础设置对话框
            import customtkinter as ctk
            from tkinter import messagebox

            dialog = ctk.CTkToplevel(parent)
            dialog.title("设置")
            dialog.geometry("600x400")

            label = ctk.CTkLabel(
                dialog,
                text="设置功能暂不可用\n请确保响应式设置管理器正常工作",
                font=ctk.CTkFont(size=14)
            )
            label.pack(expand=True)

            button = ctk.CTkButton(
                dialog,
                text="关闭",
                command=dialog.destroy
            )
            button.pack(pady=20)

            return dialog


def apply_ui_fixes_to_main_window(main_window):
    """
    应用UI修复到主窗口的便捷函数

    Args:
        main_window: 主窗口实例

    Returns:
        修复结果
    """
    integrator = UIFixesIntegration()
    return integrator.apply_all_fixes(main_window)


if __name__ == "__main__":
    # 测试UI修复
    print("UI修复集成测试")
    print("=" * 40)

    integrator = UIFixesIntegration()

    print("1. 数据桥接器:", "✅ 可用" if integrator.data_bridge else "❌ 不可用")
    print("2. 响应式设置:", "✅ 可用" if integrator.responsive_settings else "❌ 不可用")
    print("3. 增强角色管理:", "✅ 可用" if integrator.character_manager else "❌ 不可用")

    if integrator.data_bridge:
        print("4. 测试数据桥接器...")
        test_data = [
            {"name": "测试角色1", "description": "测试描述1"},
            {"name": "测试角色2", "description": "测试描述2"}
        ]
        integrator.data_bridge.update_data('characters', test_data)
        loaded_data = integrator.data_bridge.get_data('characters')
        print(f"   数据桥接器测试: {'✅ 成功' if len(loaded_data) == 2 else '❌ 失败'}")

    if integrator.responsive_settings:
        print("5. 测试响应式设置...")
        font = integrator.responsive_settings.get_font('title')
        window_size = integrator.responsive_settings.get_window_size()
        print(f"   字体获取: {'✅ 成功' if font else '❌ 失败'}")
        print(f"   窗口大小: {'✅ 成功' if window_size else '❌ 失败'}")

    print("\nUI修复集成测试完成")