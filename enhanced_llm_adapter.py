# enhanced_llm_adapter.py
# -*- coding: utf-8 -*-
"""
增强的LLM适配器 - 专门解决连接问题
使用BMAD方法确保稳定的API调用
"""

import os
import time
import logging
import requests
from typing import Optional, Dict, Any, Union
from openai import OpenAI
import httpx

# 导入高级日志系统
try:
    from advanced_logger import llm_logger, log_llm_request, log_llm_response
    ADVANCED_LOGGING = True
except ImportError:
    ADVANCED_LOGGING = False
    llm_logger = logging.getLogger("enhanced_llm_adapter")

# 导入网络管理器
try:
    from network_manager import get_connection_manager, NetworkError
    NETWORK_MANAGER_AVAILABLE = True
except ImportError:
    NETWORK_MANAGER_AVAILABLE = False
    NetworkError = Exception


class EnhancedLLMAdapter:
    """增强的LLM适配器，确保连接稳定性"""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        model_name: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        timeout: int = 60,
        interface_format: str = "DeepSeek"
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/').rstrip('/v1') + '/v1'  # 确保正确的URL格式
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.interface_format = interface_format

        # 初始化网络管理器
        if NETWORK_MANAGER_AVAILABLE:
            self.network_manager = get_connection_manager({
                'timeout': timeout,
                'max_retries': 5,  # 增加重试次数
                'retry_delay': 1
            })
        else:
            self.network_manager = None

        # 创建OpenAI客户端 - 使用更稳定的配置
        self.client = self._create_enhanced_client()

        if ADVANCED_LOGGING:
            llm_logger.info(f"初始化增强LLM适配器: {model_name}")

    def _create_enhanced_client(self) -> OpenAI:
        """创建增强的OpenAI客户端"""
        try:
            # 创建HTTP客户端，配置更稳定的参数
            http_client = httpx.Client(
                timeout=httpx.Timeout(
                    connect=10.0,  # 连接超时
                    read=30.0,     # 读取超时
                    write=10.0,    # 写入超时
                    pool=60.0      # 连接池超时
                ),
                limits=httpx.Limits(
                    max_keepalive_connections=5,
                    max_connections=10,
                    keepalive_expiry=30.0
                ),
                follow_redirects=True,
                verify=True  # SSL验证
            )

            # 创建OpenAI客户端
            client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.timeout,
                http_client=http_client,
                max_retries=0  # 我们自己处理重试
            )

            if ADVANCED_LOGGING:
                llm_logger.info(f"创建增强OpenAI客户端成功: {self.base_url}")

            return client

        except Exception as e:
            if ADVANCED_LOGGING:
                llm_logger.error(f"创建增强OpenAI客户端失败: {e}")
            # 回退到基础客户端
            return OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.timeout
            )

    def _make_direct_request(self, messages: list) -> str:
        """直接使用requests进行API调用"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            data = {
                'model': self.model_name,
                'messages': messages,
                'temperature': self.temperature,
                'max_tokens': self.max_tokens
            }

            if ADVANCED_LOGGING:
                llm_logger.info(f"直接API调用: {self.base_url}")

            # 使用网络管理器进行请求
            if self.network_manager:
                response = self.network_manager.make_request_with_retry(
                    requests.post,
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data,
                    use_proxy=False
                )
            else:
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=self.timeout
                )

            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                return content
            else:
                raise Exception(f"API错误: {response.status_code} - {response.text}")

        except Exception as e:
            if ADVANCED_LOGGING:
                llm_logger.error(f"直接API调用失败: {e}")
            raise

    def invoke(self, prompt: str) -> str:
        """调用LLM，支持多种方法回退"""
        messages = [{"role": "user", "content": prompt}]

        if ADVANCED_LOGGING:
            llm_logger.info(f"调用增强LLM: {self.model_name}")
            log_llm_request(prompt, self.model_name, self.interface_format)

        try:
            # 方法1: 使用OpenAI客户端
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )

                if response and response.choices:
                    content = response.choices[0].message.content
                    if ADVANCED_LOGGING:
                        log_llm_response(content, self.model_name, self.interface_format)
                    return content

            except Exception as e:
                if ADVANCED_LOGGING:
                    llm_logger.warning(f"OpenAI客户端调用失败，尝试直接API调用: {e}")

            # 方法2: 直接API调用
            try:
                content = self._make_direct_request(messages)
                if ADVANCED_LOGGING:
                    log_llm_response(content, self.model_name, self.interface_format)
                return content

            except Exception as e:
                if ADVANCED_LOGGING:
                    llm_logger.error(f"直接API调用也失败: {e}")

                # 方法3: 最小化请求
                try:
                    content = self._make_minimal_request(prompt)
                    if ADVANCED_LOGGING:
                        log_llm_response(content, self.model_name, self.interface_format)
                    return content

                except Exception as final_e:
                    raise Exception(f"所有调用方法都失败了: {final_e}")

        except Exception as e:
            error_msg = f"增强LLM调用失败: {str(e)}"
            if ADVANCED_LOGGING:
                llm_logger.error(error_msg)
            return f"[错误] {error_msg}"

    def _make_minimal_request(self, prompt: str) -> str:
        """最小化的请求，仅用于最后回退"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        data = {
            'model': self.model_name,
            'messages': [{"role": "user", "content": prompt}],
            'max_tokens': min(100, self.max_tokens)  # 减少token数量
        }

        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=data,
            timeout=30  # 更短的超时
        )

        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            raise Exception(f"最小化请求失败: {response.status_code}")

    def test_connection(self) -> bool:
        """测试连接是否正常"""
        try:
            test_response = self.invoke("测试")
            return len(test_response) > 0
        except:
            return False


def create_enhanced_llm_adapter(
    interface_format: str,
    api_key: str,
    base_url: str,
    model_name: str,
    temperature: float = 0.7,
    max_tokens: int = 2000,
    timeout: int = 60
) -> EnhancedLLMAdapter:
    """创建增强的LLM适配器"""
    return EnhancedLLMAdapter(
        api_key=api_key,
        base_url=base_url,
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=timeout,
        interface_format=interface_format
    )


if __name__ == "__main__":
    # 测试增强的LLM适配器
    print("测试增强的LLM适配器")

    try:
        adapter = create_enhanced_llm_adapter(
            interface_format="DeepSeek",
            api_key="sk-1bb9d53baee3469cb12ff3256bba9221",
            base_url="https://api.deepseek.com/v1",
            model_name="deepseek-chat",
            temperature=0.7,
            max_tokens=100,
            timeout=30
        )

        print("适配器创建成功")
        print("测试连接...")
        result = adapter.invoke("请回复'测试成功'")
        print(f"测试结果: {result}")

    except Exception as e:
        print(f"测试失败: {e}")