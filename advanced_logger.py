# advanced_logger.py
# -*- coding: utf-8 -*-
"""
高级日志系统，用于调试AI小说生成器的各种问题
"""

import logging
import os
import sys
from datetime import datetime
from functools import wraps

# 创建logs目录
LOGS_DIR = "logs"
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

# 配置日志格式
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# 创建日志记录器
def setup_logger(name, log_file, level=logging.INFO):
    """创建并配置日志记录器"""
    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    
    # 文件处理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # 创建记录器
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# 创建不同类型的日志记录器
main_logger = setup_logger('main', os.path.join(LOGS_DIR, 'main.log'))
llm_logger = setup_logger('llm', os.path.join(LOGS_DIR, 'llm.log'))
embedding_logger = setup_logger('embedding', os.path.join(LOGS_DIR, 'embedding.log'))
ui_logger = setup_logger('ui', os.path.join(LOGS_DIR, 'ui.log'))
role_logger = setup_logger('role', os.path.join(LOGS_DIR, 'role.log'))

def log_function_call(logger):
    """装饰器：记录函数调用"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 记录函数调用
            logger.info(f"调用函数: {func.__name__}")
            logger.debug(f"  参数: args={args}, kwargs={kwargs}")
            
            try:
                result = func(*args, **kwargs)
                logger.info(f"函数 {func.__name__} 执行成功")
                logger.debug(f"  返回值: {result}")
                return result
            except Exception as e:
                logger.error(f"函数 {func.__name__} 执行失败: {str(e)}")
                raise
        return wrapper
    return decorator

def log_llm_request(prompt, model_name, adapter_type):
    """记录LLM请求"""
    llm_logger.info(f"LLM请求 - 模型: {model_name}, 适配器: {adapter_type}")
    llm_logger.debug(f"提示词: {prompt[:200]}..." if len(prompt) > 200 else f"提示词: {prompt}")

def log_llm_response(response, model_name, adapter_type):
    """记录LLM响应"""
    llm_logger.info(f"LLM响应 - 模型: {model_name}, 适配器: {adapter_type}")
    llm_logger.debug(f"响应内容: {response[:200]}..." if len(response) > 200 else f"响应内容: {response}")

def log_embedding_request(text, model_name, adapter_type):
    """记录Embedding请求"""
    embedding_logger.info(f"Embedding请求 - 模型: {model_name}, 适配器: {adapter_type}")
    embedding_logger.debug(f"文本: {text[:100]}..." if len(text) > 100 else f"文本: {text}")

def log_embedding_response(embedding, model_name, adapter_type):
    """记录Embedding响应"""
    embedding_logger.info(f"Embedding响应 - 模型: {model_name}, 适配器: {adapter_type}")
    embedding_logger.debug(f"向量维度: {len(embedding) if embedding else 0}")

def log_ui_action(action, details=""):
    """记录UI操作"""
    ui_logger.info(f"UI操作: {action}")
    if details:
        ui_logger.debug(f"  详情: {details}")

def log_role_operation(operation, role_name, details=""):
    """记录角色库操作"""
    role_logger.info(f"角色操作: {operation} - 角色: {role_name}")
    if details:
        role_logger.debug(f"  详情: {details}")

def log_config_loading(config_file):
    """记录配置加载"""
    main_logger.info(f"加载配置文件: {config_file}")

def log_config_saving(config_file):
    """记录配置保存"""
    main_logger.info(f"保存配置文件: {config_file}")

def log_error(error_msg, context=""):
    """记录错误"""
    main_logger.error(f"错误: {error_msg}")
    if context:
        main_logger.debug(f"  上下文: {context}")

def get_log_files():
    """获取所有日志文件列表"""
    log_files = []
    for file in os.listdir(LOGS_DIR):
        if file.endswith('.log'):
            log_files.append(os.path.join(LOGS_DIR, file))
    return log_files

def clear_logs():
    """清空所有日志文件"""
    for log_file in get_log_files():
        try:
            open(log_file, 'w').close()
        except Exception as e:
            main_logger.error(f"清空日志文件 {log_file} 失败: {str(e)}")

# 使用示例:
# @log_function_call(main_logger)
# def some_function():
#     pass