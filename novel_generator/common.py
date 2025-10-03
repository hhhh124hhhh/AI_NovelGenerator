#novel_generator/common.py
# -*- coding: utf-8 -*-
"""
通用重试、清洗、日志工具
"""
import logging
import re
import time
import traceback
import os

# 检查是否启用详细日志模式
SHOW_DETAILED_LOGS = os.environ.get('SHOW_DETAILED_LOGS', 'false').lower() == 'true'

logging.basicConfig(
    filename='app.log',      # 日志文件名
    filemode='a',            # 追加模式（'w' 会覆盖）
    level=logging.INFO,      # 记录 INFO 及以上级别的日志
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8'         # 确保UTF-8编码
)


def call_with_retry(func, max_retries=3, sleep_time=2, fallback_return=None, **kwargs):
    """
    通用的重试机制封装。
    :param func: 要执行的函数
    :param max_retries: 最大重试次数
    :param sleep_time: 重试前的等待秒数
    :param fallback_return: 如果多次重试仍失败时的返回值
    :param kwargs: 传给func的命名参数
    :return: func的结果，若失败则返回 fallback_return
    """
    for attempt in range(1, max_retries + 1):
        try:
            return func(**kwargs)
        except Exception as e:
            logging.warning(f"[call_with_retry] Attempt {attempt} failed with error: {e}")
            traceback.print_exc()
            if attempt < max_retries:
                time.sleep(sleep_time)
            else:
                logging.error("Max retries reached, returning fallback_return.")
                return fallback_return

def remove_think_tags(text: str) -> str:
    """移除 <think>...</think> 包裹的内容"""
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)

def debug_log(prompt: str, response_content: str):
    logging.info(
        f"\n[#########################################  Prompt  #########################################]\n{prompt}\n"
    )
    logging.info(
        f"\n[######################################### Response #########################################]\n{response_content}\n"
    )

def invoke_with_cleaning(llm_adapter, prompt: str, max_retries: int = 3) -> str:
    """调用 LLM 并清理返回结果"""
    # 根据环境变量决定是否显示详细日志
    if SHOW_DETAILED_LOGS:
        print("\n" + "="*50)
        print("发送到 LLM 的提示词:")
        print("-"*50)
        print(prompt)
        print("="*50 + "\n")
    else:
        print("发送到 LLM 的提示词...")
    
    result = ""
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            result = llm_adapter.invoke(prompt)
            # 根据环境变量决定是否显示详细日志
            if SHOW_DETAILED_LOGS:
                print("\n" + "="*50)
                print("LLM 返回的内容:")
                print("-"*50)
                print(result)
                print("="*50 + "\n")
            else:
                print("LLM 返回的内容...")
            
            # 清理结果中的特殊格式标记
            result = result.replace("```", "").strip()
            # 如果结果不为空，直接返回
            if result:
                return result
            # 如果结果为空，记录并继续重试
            print(f"收到空响应 ({retry_count + 1}/{max_retries})")
            retry_count += 1
        except Exception as e:
            print(f"调用失败 ({retry_count + 1}/{max_retries}): {str(e)}")
            retry_count += 1
            if retry_count >= max_retries:
                raise e
    
    # 如果所有重试都失败，返回空字符串而不是继续循环
    return result

