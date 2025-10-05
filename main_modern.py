# main_modern.py
# -*- coding: utf-8 -*-
"""
AI小说生成器 - 现代版主启动入口
基于现代化架构和设计理念
集成增强日志系统和主题管理
"""

import sys
import os
import traceback
from typing import Optional

# 导入增强日志系统
try:
    from enhanced_logging_config import init_logging, log_startup, log_error, get_logger
    init_logging()
    logger = get_logger('main_modern')
    log_startup("现代版主程序", "start", "初始化增强日志系统")
    ENHANCED_LOGGING = True
except ImportError as e:
    # 回退到基础日志
    import logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    logger = logging.getLogger(__name__)
    logger.warning(f"增强日志系统不可用: {e}")
    ENHANCED_LOGGING = False


def check_dependencies():
    """检查必要的依赖"""
    missing_deps = []

    try:
        import customtkinter
    except ImportError:
        missing_deps.append("customtkinter")

    try:
        import tkinter
    except ImportError:
        missing_deps.append("tkinter")

    if missing_deps:
        logger.error(f"缺少依赖: {', '.join(missing_deps)}")
        return False

    return True


def initialize_theme_system():
    """初始化主题系统"""
    try:
        from theme_system.theme_manager import ThemeManager
        theme_manager = ThemeManager()
        theme_manager.load_theme("modern_dark")

        if ENHANCED_LOGGING:
            log_startup("主题系统", "success", "现代化主题加载成功")
        else:
            logger.info("✅ 主题系统初始化成功")

        return theme_manager
    except Exception as e:
        if ENHANCED_LOGGING:
            log_error(e, "主题系统初始化失败")
        else:
            logger.warning(f"主题系统初始化失败: {e}")
        return None


def start_modern_ui():
    """启动现代化UI界面"""
    try:
        if ENHANCED_LOGGING:
            log_startup("现代化UI", "start", "初始化2.0版本界面")
        else:
            logger.info("🚀 启动现代化UI界面...")

        import customtkinter as ctk

        # 设置CustomTkinter外观
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # 尝试导入并启动现代化主窗口
        try:
            from ui.modern_main_window import ModernMainWindow

            # 初始化主题系统
            theme_manager = initialize_theme_system()

            # 创建并运行应用
            app = ModernMainWindow()

            if ENHANCED_LOGGING:
                log_startup("现代化UI", "success", "2.0版本启动成功")
            else:
                logger.info("✅ 现代化UI启动成功")

            app.mainloop()
            return True

        except ImportError as e:
            if ENHANCED_LOGGING:
                log_startup("现代化UI", "error", f"导入现代化主窗口失败: {e}")
            else:
                logger.error(f"导入现代化主窗口失败: {e}")

            # 回退到基础现代化界面
            from ui.modern_ui import ModernUI
            app = ModernUI()
            app.mainloop()
            return True

    except Exception as e:
        if ENHANCED_LOGGING:
            log_error(e, "现代化UI启动失败")
        else:
            logger.error(f"现代化UI启动失败: {e}")
        return False


def start_legacy_ui():
    """启动经典UI界面作为备选"""
    try:
        if ENHANCED_LOGGING:
            log_startup("经典UI", "start", "回退到1.0版本界面")
        else:
            logger.info("🔄 回退到经典UI界面...")

        import customtkinter as ctk
        from ui.main_window import NovelGeneratorGUI

        # 设置CustomTkinter外观
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # 创建应用
        app = ctk.CTk()
        gui = NovelGeneratorGUI(app)
        app.mainloop()

        if ENHANCED_LOGGING:
            log_startup("经典UI", "success", "1.0版本启动成功")
        else:
            logger.info("✅ 经典UI启动成功")

        return True

    except Exception as e:
        if ENHANCED_LOGGING:
            log_error(e, "经典UI启动失败")
        else:
            logger.error(f"经典UI启动失败: {e}")
        return False


def show_system_info():
    """显示系统信息"""
    logger.info("🎯 AI小说生成器 - 现代版")
    logger.info(f"Python版本: {sys.version}")
    logger.info(f"工作目录: {os.getcwd()}")

    # 检测环境
    try:
        import config_manager
        env_info = config_manager.get_environment_info()
        logger.info(f"运行环境: {'uv' if env_info['is_uv'] else 'pip'}")
    except:
        logger.info("运行环境: 未知")

    logger.info("-" * 60)


def main():
    """现代版主函数"""
    show_system_info()

    # 检查依赖
    if not check_dependencies():
        logger.error("❌ 缺少必要依赖，请安装 requirements.txt")
        logger.info("安装命令: pip install -r requirements.txt")
        return 1

    # 尝试启动现代化UI
    if start_modern_ui():
        if ENHANCED_LOGGING:
            log_startup("现代版主程序", "success", "正常退出")
        else:
            logger.info("✅ 现代版正常退出")
        return 0

    # 如果现代化UI失败，尝试经典UI
    elif start_legacy_ui():
        if ENHANCED_LOGGING:
            log_startup("现代版主程序", "warning", "回退到经典版退出")
        else:
            logger.info("✅ 回退到经典版退出")
        return 0

    # 如果都失败，提供详细帮助
    else:
        logger.error("❌ 所有UI版本启动失败")
        logger.info("\n" + "=" * 60)
        logger.info("💡 故障排除建议:")
        logger.info("1. 运行诊断: python startup_checker.py")
        logger.info("2. 使用经典版: python main_classic.py")
        logger.info("3. 使用启动器: python launch.py")
        logger.info("4. 安装依赖: pip install -r requirements.txt")
        logger.info("5. 检查环境: python --version")
        logger.info("6. 查看详细错误: python main_modern.py 2>&1 | tee error.log")
        logger.info("=" * 60)
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("👋 用户中断，程序退出")
        sys.exit(0)
    except Exception as e:
        if ENHANCED_LOGGING:
            log_error(e, "现代版主程序异常退出")
        else:
            logger.error(f"现代版主程序异常退出: {e}")
        sys.exit(1)