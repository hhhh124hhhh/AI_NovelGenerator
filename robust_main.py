#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
健壮启动脚本 - AI小说生成器
基于BMAD方法，提供多版本支持和优雅降级
"""

import sys
import os
import argparse
import logging
import traceback
from typing import Optional

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class RobustLauncher:
    """健壮启动器"""

    def __init__(self):
        self.args = None
        self.startup_result = None

    def parse_arguments(self):
        """解析命令行参数"""
        parser = argparse.ArgumentParser(description='AI小说生成器启动器')
        parser.add_argument('--version', choices=['1.0', '2.0', 'auto'], default='auto',
                          help='选择启动版本 (默认: auto)')
        parser.add_argument('--safe-mode', action='store_true',
                          help='安全模式启动 (禁用增强功能)')
        parser.add_argument('--diagnostic', action='store_true',
                          help='运行环境诊断')
        parser.add_argument('--no-animation', action='store_true',
                          help='禁用动画效果')
        parser.add_argument('--no-performance-monitor', action='store_true',
                          help='禁用性能监控')
        parser.add_argument('--debug', action='store_true',
                          help='调试模式')
        self.args = parser.parse_args()

    def run_diagnostic(self) -> bool:
        """运行环境诊断"""
        try:
            from startup_checker import StartupDiagnostic
            diagnostic = StartupDiagnostic()
            self.startup_result = diagnostic.run_diagnostic()
            return self.startup_result.get('can_start_2_0', False) or \
                   self.startup_result.get('can_start_1_0', False)
        except Exception as e:
            logger.error(f"诊断器运行失败: {e}")
            return False

    def start_version_2_0(self) -> bool:
        """启动2.0版本"""
        try:
            logger.info("🚀 启动2.0版本...")

            # 设置环境变量控制功能
            if self.args.safe_mode:
                os.environ['SAFE_MODE'] = '1'
            if self.args.no_animation:
                os.environ['NO_ANIMATION'] = '1'
            if self.args.no_performance_monitor:
                os.environ['NO_PERFORMANCE_MONITOR'] = '1'

            # 导入2.0版本
            import customtkinter as ctk
            from ui.modern_main_window import ModernMainWindow

            # 设置CustomTkinter外观
            ctk.set_appearance_mode("dark")
            ctk.set_default_color_theme("blue")

            # 创建并运行应用
            app = ModernMainWindow()
            app.mainloop()

            return True

        except ImportError as e:
            logger.error(f"2.0版本导入失败: {e}")
            return False
        except Exception as e:
            logger.error(f"2.0版本启动失败: {e}")
            if self.args.debug:
                logger.error(traceback.format_exc())
            return False

    def start_version_1_0(self) -> bool:
        """启动1.0版本"""
        try:
            logger.info("🔄 回退到1.0版本...")

            # 导入1.0版本
            import customtkinter as ctk
            from ui.main_window import NovelGeneratorGUI

            # 设置CustomTkinter外观
            ctk.set_appearance_mode("dark")
            ctk.set_default_color_theme("blue")

            # 创建应用
            app = ctk.CTk()
            gui = NovelGeneratorGUI(app)
            app.mainloop()

            return True

        except ImportError as e:
            logger.error(f"1.0版本导入失败: {e}")
            return False
        except Exception as e:
            logger.error(f"1.0版本启动失败: {e}")
            if self.args.debug:
                logger.error(traceback.format_exc())
            return False

    def auto_select_version(self) -> bool:
        """自动选择最佳版本"""
        if self.startup_result:
            if self.startup_result.get('can_start_2_0', False):
                logger.info("✅ 自动选择2.0版本")
                return self.start_version_2_0()
            elif self.startup_result.get('can_start_1_0', False):
                logger.info("⚠️ 自动选择1.0版本 (2.0版本不可用)")
                return self.start_version_1_0()
            else:
                logger.error("❌ 没有可用的版本")
                return False
        else:
            # 如果没有诊断结果，尝试2.0版本
            if self.start_version_2_0():
                return True
            else:
                logger.warning("2.0版本启动失败，尝试1.0版本...")
                return self.start_version_1_0()

    def run(self) -> int:
        """运行启动器"""
        try:
            # 解析参数
            self.parse_arguments()

            # 显示启动信息
            logger.info("🎯 AI小说生成器启动器")
            logger.info(f"Python版本: {sys.version}")
            logger.info(f"工作目录: {os.getcwd()}")
            logger.info("=" * 50)

            # 运行诊断
            if self.args.diagnostic or self.args.version == 'auto':
                logger.info("🔍 运行环境诊断...")
                if not self.run_diagnostic():
                    logger.error("❌ 环境诊断失败，无法启动")
                    return 1

            # 根据参数选择版本
            if self.args.version == '1.0':
                success = self.start_version_1_0()
            elif self.args.version == '2.0':
                success = self.start_version_2_0()
            else:  # auto
                success = self.auto_select_version()

            if success:
                logger.info("✅ 应用已正常退出")
                return 0
            else:
                logger.error("❌ 启动失败")
                self.show_help()
                return 1

        except KeyboardInterrupt:
            logger.info("👋 用户中断启动")
            return 0
        except Exception as e:
            logger.error(f"启动器异常: {e}")
            if self.args and self.args.debug:
                logger.error(traceback.format_exc())
            return 1

    def show_help(self):
        """显示帮助信息"""
        logger.info("\n" + "=" * 50)
        logger.info("💡 故障排除建议:")
        logger.info("1. 运行诊断: python robust_main.py --diagnostic")
        logger.info("2. 安全模式: python robust_main.py --safe-mode")
        logger.info("3. 强制1.0版本: python robust_main.py --version 1.0")
        logger.info("4. 安装依赖: pip install -r requirements.txt")
        logger.info("5. 检查Python版本: python --version")
        logger.info("=" * 50)


def main():
    """主函数"""
    launcher = RobustLauncher()
    exit_code = launcher.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()