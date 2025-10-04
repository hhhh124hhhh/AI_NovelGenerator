#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强日志配置系统 - AI小说生成器专用
提供详细的调试信息和错误追踪
"""

import logging
import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any
import json

# 创建logs目录
LOGS_DIR = "logs"
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)
    print(f"创建日志目录: {LOGS_DIR}")

# 日志配置
class EnhancedLoggingConfig:
    """增强日志配置"""

    def __init__(self):
        self.log_level = logging.INFO
        self.log_format = '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        self.date_format = '%Y-%m-%d %H:%M:%S'
        self.loggers = {}

    def setup_logger(self, name: str, log_file: str = None, level: int = None) -> logging.Logger:
        """设置日志记录器"""
        if name in self.loggers:
            return self.loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(level or self.log_level)

        # 清除现有处理器
        logger.handlers.clear()

        # 创建格式器
        formatter = logging.Formatter(self.log_format, self.date_format)

        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # 文件处理器
        if log_file:
            file_path = os.path.join(LOGS_DIR, log_file)
            file_handler = logging.FileHandler(file_path, encoding='utf-8')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        self.loggers[name] = logger
        return logger

    def setup_ui_logger(self) -> logging.Logger:
        """设置UI专用日志记录器"""
        return self.setup_logger('ui', 'ui.log')

    def setup_main_logger(self) -> logging.Logger:
        """设置主程序日志记录器"""
        return self.setup_logger('main', 'main.log')

    def setup_performance_logger(self) -> logging.Logger:
        """设置性能监控日志记录器"""
        return self.setup_logger('performance', 'performance.log')

    def setup_error_logger(self) -> logging.Logger:
        """设置错误日志记录器"""
        return self.setup_logger('error', 'error.log', logging.ERROR)

    def log_system_info(self):
        """记录系统信息"""
        logger = self.setup_logger('system', 'system.log')

        import platform
        logger.info("=" * 50)
        logger.info("AI小说生成器 - 系统信息")
        logger.info("=" * 50)
        logger.info(f"Python版本: {sys.version}")
        logger.info(f"操作系统: {platform.system()} {platform.release()}")
        logger.info(f"架构: {platform.architecture()[0]}")
        logger.info(f"处理器: {platform.processor()}")
        logger.info(f"工作目录: {os.getcwd()}")
        logger.info(f"脚本目录: {os.path.dirname(__file__)}")

        # 检查关键依赖
        dependencies = ['customtkinter', 'langchain', 'chromadb']
        for dep in dependencies:
            try:
                __import__(dep)
                logger.info(f"✅ {dep}: 已安装")
            except ImportError:
                logger.error(f"❌ {dep}: 未安装")

        logger.info("=" * 50)

    def log_startup_sequence(self, component: str, status: str, details: str = ""):
        """记录启动序列"""
        logger = self.setup_logger('startup', 'startup.log')

        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        status_symbol = {
            'start': '🚀',
            'success': '✅',
            'warning': '⚠️',
            'error': '❌',
            'info': 'ℹ️'
        }.get(status, '•')

        message = f"{status_symbol} [{timestamp}] {component}"
        if details:
            message += f" - {details}"

        if status == 'error':
            logger.error(message)
        elif status == 'warning':
            logger.warning(message)
        else:
            logger.info(message)

    def create_error_report(self, error: Exception, context: str = "") -> Dict[str, Any]:
        """创建错误报告"""
        error_logger = self.setup_error_logger()

        import traceback

        error_report = {
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'traceback': traceback.format_exc(),
            'system_info': {
                'python_version': sys.version,
                'working_directory': os.getcwd(),
            }
        }

        # 记录到日志
        error_logger.error("=" * 50)
        error_logger.error(f"错误报告 - {context}")
        error_logger.error("=" * 50)
        error_logger.error(f"错误类型: {error_report['error_type']}")
        error_logger.error(f"错误消息: {error_report['error_message']}")
        error_logger.error(f"上下文: {context}")
        error_logger.error(f"堆栈跟踪:\n{error_report['traceback']}")
        error_logger.error("=" * 50)

        # 保存错误报告到文件
        error_report_file = os.path.join(LOGS_DIR, f"error_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        try:
            with open(error_report_file, 'w', encoding='utf-8') as f:
                json.dump(error_report, f, ensure_ascii=False, indent=2)
            error_logger.info(f"错误报告已保存: {error_report_file}")
        except Exception as e:
            error_logger.error(f"保存错误报告失败: {e}")

        return error_report

    def get_log_summary(self) -> Dict[str, Any]:
        """获取日志摘要"""
        summary = {
            'log_directory': LOGS_DIR,
            'log_files': [],
            'total_size': 0,
            'latest_entries': {}
        }

        if os.path.exists(LOGS_DIR):
            for file_name in os.listdir(LOGS_DIR):
                if file_name.endswith('.log'):
                    file_path = os.path.join(LOGS_DIR, file_name)
                    try:
                        stat = os.stat(file_path)
                        file_info = {
                            'name': file_name,
                            'size': stat.st_size,
                            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                        }
                        summary['log_files'].append(file_info)
                        summary['total_size'] += stat.st_size

                        # 读取最新条目
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                lines = f.readlines()
                                if lines:
                                    summary['latest_entries'][file_name] = lines[-1].strip()
                        except Exception:
                            pass
                    except Exception:
                        continue

        return summary


# 全局日志配置实例
logging_config = EnhancedLoggingConfig()

# 便捷函数
def get_logger(name: str) -> logging.Logger:
    """获取日志记录器"""
    return logging_config.setup_logger(name)

def log_startup(component: str, status: str, details: str = ""):
    """记录启动事件"""
    logging_config.log_startup_sequence(component, status, details)

def log_error(error: Exception, context: str = "") -> Dict[str, Any]:
    """记录错误"""
    return logging_config.create_error_report(error, context)

def init_logging():
    """初始化日志系统"""
    logging_config.log_system_info()
    log_startup("日志系统", "success", "增强日志配置已加载")

# 初始化
if __name__ == "__main__":
    init_logging()

    # 测试日志
    ui_logger = logging_config.setup_ui_logger()
    main_logger = logging_config.setup_main_logger()

    ui_logger.info("UI日志测试")
    main_logger.info("主程序日志测试")

    # 测试错误记录
    try:
        raise ValueError("这是一个测试错误")
    except Exception as e:
        log_error(e, "日志系统测试")

    # 显示日志摘要
    summary = logging_config.get_log_summary()
    print(json.dumps(summary, ensure_ascii=False, indent=2))