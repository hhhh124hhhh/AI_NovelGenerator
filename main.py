# main.py
# -*- coding: utf-8 -*-
"""
AI小说生成器 - 主启动入口
支持自动版本选择和优雅降级
集成增强日志系统
"""

import sys
import os

# 导入增强日志系统
try:
    from enhanced_logging_config import init_logging, log_startup, log_error, get_logger
    init_logging()
    logger = get_logger('main')
    log_startup("主程序", "start", "初始化增强日志系统")
    ENHANCED_LOGGING = True
except ImportError as e:
    # 回退到基础日志
    import logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    logger = logging.getLogger(__name__)
    logger.warning(f"增强日志系统不可用: {e}")
    ENHANCED_LOGGING = False


def try_start_version_2_0():
    """尝试启动2.0版本"""
    try:
        if ENHANCED_LOGGING:
            log_startup("2.0版本", "start", "初始化现代化界面")
        else:
            logger.info("🚀 尝试启动2.0版本...")

        import customtkinter as ctk
        from ui.modern_main_window import ModernMainWindow

        # 设置CustomTkinter外观
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # 创建并运行应用
        app = ModernMainWindow()

        if ENHANCED_LOGGING:
            log_startup("2.0版本", "success", "现代化界面启动成功")
        else:
            logger.info("✅ 2.0版本启动成功")

        app.mainloop()

        return True

    except ImportError as e:
        if ENHANCED_LOGGING:
            log_startup("2.0版本", "error", f"导入失败: {e}")
        else:
            logger.warning(f"2.0版本导入失败: {e}")
        return False
    except Exception as e:
        if ENHANCED_LOGGING:
            log_error(e, "2.0版本启动失败")
            log_startup("2.0版本", "error", "启动失败")
        else:
            logger.warning(f"2.0版本启动失败: {e}")
        return False


def try_start_version_1_0():
    """尝试启动1.0版本"""
    try:
        logger.info("🔄 回退到1.0版本...")

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
        return False


def main():
    """主函数"""
    logger.info("🎯 AI小说生成器启动")
    logger.info(f"Python版本: {sys.version}")
    logger.info(f"工作目录: {os.getcwd()}")
    logger.info("-" * 50)

    # 首先尝试2.0版本
    if try_start_version_2_0():
        logger.info("✅ 2.0版本已正常退出")
        return 0

    # 如果2.0版本失败，尝试1.0版本
    elif try_start_version_1_0():
        logger.info("✅ 1.0版本已正常退出")
        return 0

    # 如果都失败，提供帮助信息
    else:
        logger.error("❌ 所有版本启动失败")
        logger.info("\n" + "=" * 50)
        logger.info("💡 故障排除建议:")
        logger.info("1. 运行诊断: python startup_checker.py")
        logger.info("2. 使用健壮启动器: python robust_main.py")
        logger.info("3. 安装依赖: pip install -r requirements.txt")
        logger.info("4. 检查环境: python --version")
        logger.info("=" * 50)
        return 1


if __name__ == "__main__":
    sys.exit(main())