# llm_adapters.py
# -*- coding: utf-8 -*-
import logging
import time
from typing import Optional, Dict, Any
from langchain_openai import ChatOpenAI, AzureChatOpenAI
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.inference.models import SystemMessage, UserMessage
from openai import OpenAI
import requests

# 导入高级日志系统
try:
    from advanced_logger import llm_logger, log_llm_request, log_llm_response
    ADVANCED_LOGGING = True
except ImportError:
    ADVANCED_LOGGING = False
    llm_logger = logging.getLogger("llm_adapters")

# 导入BMAD网络管理器
try:
    from network_manager import get_connection_manager, NetworkError
    NETWORK_MANAGER_AVAILABLE = True
except ImportError:
    NETWORK_MANAGER_AVAILABLE = False
    NetworkError = Exception

def check_base_url(url: str) -> str:
    """
    处理base_url的规则：
    1. 如果url以#结尾，则移除#并直接使用用户提供的url
    2. 否则检查是否需要添加/v1后缀
    """
    import re
    url = url.strip()
    if not url:
        return url
        
    if url.endswith('#'):
        return url.rstrip('#')
        
    if not re.search(r'/v\d+$', url):
        if '/v1' not in url:
            url = url.rstrip('/') + '/v1'
    return url

class BaseLLMAdapter:
    """
    统一的 LLM 接口基类，为不同后端（OpenAI、Ollama、ML Studio、Gemini等）提供一致的方法签名。
    """
    def invoke(self, prompt: str) -> str:
        raise NotImplementedError("Subclasses must implement .invoke(prompt) method.")

class DeepSeekAdapter(BaseLLMAdapter):
    """
    增强的DeepSeek适配器 - 使用增强的LLM适配器确保连接稳定
    """
    def __init__(self, api_key: str, base_url: str, model_name: str, max_tokens: int, temperature: float = 0.7, timeout: Optional[int] = 600):
        try:
            # 尝试导入增强适配器
            from enhanced_llm_adapter import create_enhanced_llm_adapter

            self.enhanced_adapter = create_enhanced_llm_adapter(
                interface_format="DeepSeek",
                api_key=api_key,
                base_url=base_url,
                model_name=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=timeout or 60
            )
            self.use_enhanced = True

            if ADVANCED_LOGGING:
                llm_logger.info("使用增强的DeepSeek适配器")

        except ImportError:
            # 回退到原始适配器
            self.use_enhanced = False
            self.base_url = check_base_url(base_url)
            self.api_key = api_key
            self.model_name = model_name
            self.max_tokens = max_tokens
            self.temperature = temperature
            self.timeout = timeout

            # 初始化BMAD网络管理器
            if NETWORK_MANAGER_AVAILABLE:
                self.network_manager = get_connection_manager({
                    'timeout': timeout,
                    'max_retries': 3,
                    'retry_delay': 2
                })
                # 动态调整超时时间
                self.timeout = self.network_manager.get_best_timeout(self.base_url)
            else:
                self.network_manager = None

            self._client = ChatOpenAI(
                model=self.model_name,
                api_key=self.api_key,  # type: ignore
                base_url=self.base_url,
                temperature=self.temperature,
                timeout=self.timeout
            )

            if ADVANCED_LOGGING:
                llm_logger.info("使用原始DeepSeek适配器")

    def invoke(self, prompt: str) -> str:
        if self.use_enhanced:
            # 使用增强适配器
            return self.enhanced_adapter.invoke(prompt)
        else:
            # 使用原始适配器逻辑
            llm_logger.info(f"调用DeepSeek模型: {self.model_name}")
            log_llm_request(prompt, self.model_name, "DeepSeek")

            def _make_request():
                """内部请求函数，用于重试机制"""
                response = self._client.invoke(prompt)
                if not response:
                    raise ValueError("No response from DeepSeekAdapter")
                content = response.content
                result = content if isinstance(content, str) else str(content)
                return result

            try:
                # 使用BMAD网络管理器执行请求
                if self.network_manager:
                    result = self.network_manager.make_request_with_retry(_make_request)
                else:
                    # 回退到原始方法
                    result = _make_request()

                log_llm_response(result, self.model_name, "DeepSeek")
                return result

            except NetworkError as e:
                error_msg = f"网络连接失败: {str(e)}"
                llm_logger.error(error_msg)
                logging.error(error_msg)
                return f"[网络错误] {error_msg}"

            except Exception as e:
                error_msg = f"DeepSeek API调用失败: {str(e)}"
                llm_logger.error(error_msg)
                logging.error(error_msg)
                return f"[API错误] {error_msg}"

class OpenAIAdapter(BaseLLMAdapter):
    """
    适配官方/OpenAI兼容接口（使用 langchain.ChatOpenAI）
    集成BMAD网络管理器提供稳定的连接
    """
    def __init__(self, api_key: str, base_url: str, model_name: str, max_tokens: int, temperature: float = 0.7, timeout: Optional[int] = 600):
        self.base_url = check_base_url(base_url)
        self.api_key = api_key
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout

        # 初始化BMAD网络管理器
        if NETWORK_MANAGER_AVAILABLE:
            self.network_manager = get_connection_manager({
                'timeout': timeout,
                'max_retries': 3,
                'retry_delay': 2
            })
            # 动态调整超时时间
            self.timeout = self.network_manager.get_best_timeout(self.base_url)
        else:
            self.network_manager = None

        self._client = ChatOpenAI(
            model=self.model_name,
            api_key=self.api_key,  # type: ignore
            base_url=self.base_url,
            temperature=self.temperature,
            timeout=self.timeout
        )

    def invoke(self, prompt: str) -> str:
        llm_logger.info(f"调用OpenAI模型: {self.model_name}")
        log_llm_request(prompt, self.model_name, "OpenAI")

        def _make_request():
            """内部请求函数，用于重试机制"""
            response = self._client.invoke(prompt)
            if not response:
                raise ValueError("No response from OpenAIAdapter")
            content = response.content
            result = content if isinstance(content, str) else str(content)
            return result

        try:
            # 使用BMAD网络管理器执行请求
            if self.network_manager:
                result = self.network_manager.make_request_with_retry(_make_request)
            else:
                # 回退到原始方法
                result = _make_request()

            log_llm_response(result, self.model_name, "OpenAI")
            return result

        except NetworkError as e:
            error_msg = f"网络连接失败: {str(e)}"
            llm_logger.error(error_msg)
            logging.error(error_msg)
            return f"[网络错误] {error_msg}"

        except Exception as e:
            error_msg = f"OpenAI API调用失败: {str(e)}"
            llm_logger.error(error_msg)
            logging.error(error_msg)
            return f"[API错误] {error_msg}"

class GeminiAdapter(BaseLLMAdapter):
    """
    适配 Google Gemini (Google Generative AI) 接口
    """

    # PenBo 修复新版本google-generativeai 不支持 Client 类问题；而是使用 GenerativeModel 类来访问API
    def __init__(self, api_key: str, base_url: str, model_name: str, max_tokens: int, temperature: float = 0.7, timeout: Optional[int] = 600):
        self.api_key = api_key
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout

        # 配置API密钥
        genai.configure(api_key=self.api_key)  # type: ignore
        
        # 创建生成模型实例
        self._model = genai.GenerativeModel(model_name=self.model_name)  # type: ignore

    def invoke(self, prompt: str) -> str:
        llm_logger.info(f"调用Gemini模型: {self.model_name}")
        log_llm_request(prompt, self.model_name, "Gemini")
        try:
            # 设置生成配置
            generation_config = GenerationConfig(
                max_output_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            
            # 生成内容
            response = self._model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            if response and response.text:
                result = response.text
                log_llm_response(result, self.model_name, "Gemini")
                return result
            else:
                logging.warning("No text response from Gemini API.")
                return ""
        except Exception as e:
            logging.error(f"Gemini API 调用失败: {e}")
            return ""

class AzureOpenAIAdapter(BaseLLMAdapter):
    """
    适配 Azure OpenAI 接口（使用 langchain.ChatOpenAI）
    """
    def __init__(self, api_key: str, base_url: str, model_name: str, max_tokens: int, temperature: float = 0.7, timeout: Optional[int] = 600):
        import re
        match = re.match(r'https://(.+?)/openai/deployments/(.+?)/chat/completions\?api-version=(.+)', base_url)
        if match:
            self.azure_endpoint = f"https://{match.group(1)}"
            self.azure_deployment = match.group(2)
            self.api_version = match.group(3)
        else:
            raise ValueError("Invalid Azure OpenAI base_url format")
        
        self.api_key = api_key
        self.model_name = self.azure_deployment
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout

        self._client = AzureChatOpenAI(
            azure_endpoint=self.azure_endpoint,
            azure_deployment=self.azure_deployment,
            api_version=self.api_version,
            api_key=self.api_key,  # type: ignore
            temperature=self.temperature,
            timeout=self.timeout
        )

    def invoke(self, prompt: str) -> str:
        llm_logger.info(f"调用Azure OpenAI模型: {self.model_name}")
        log_llm_request(prompt, self.model_name, "Azure OpenAI")
        response = self._client.invoke(prompt)
        if not response:
            logging.warning("No response from AzureOpenAIAdapter.")
            return ""
        content = response.content
        result = content if isinstance(content, str) else str(content)
        log_llm_response(result, self.model_name, "Azure OpenAI")
        return result

class OllamaAdapter(BaseLLMAdapter):
    """
    Ollama 同样有一个 OpenAI-like /v1/chat 接口，可直接使用 ChatOpenAI。
    """
    def __init__(self, api_key: str, base_url: str, model_name: str, max_tokens: int, temperature: float = 0.7, timeout: Optional[int] = 600):
        self.base_url = check_base_url(base_url)
        self.api_key = api_key
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout

        if self.api_key == '':
            self.api_key= 'ollama'

        self._client = ChatOpenAI(
            model=self.model_name,
            api_key=self.api_key,  # type: ignore
            base_url=self.base_url,
            temperature=self.temperature,
            timeout=self.timeout
        )

    def invoke(self, prompt: str) -> str:
        llm_logger.info(f"调用Ollama模型: {self.model_name}")
        log_llm_request(prompt, self.model_name, "Ollama")
        response = self._client.invoke(prompt)
        if not response:
            logging.warning("No response from OllamaAdapter.")
            return ""
        content = response.content
        result = content if isinstance(content, str) else str(content)
        log_llm_response(result, self.model_name, "Ollama")
        return result

class MLStudioAdapter(BaseLLMAdapter):
    """
    适配 LM Studio 的 /v1/chat/completions 接口
    """
    def __init__(self, api_key: str, base_url: str, model_name: str, max_tokens: int, temperature: float = 0.7, timeout: Optional[int] = 600):
        self.base_url = check_base_url(base_url)
        self.api_key = api_key
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout

        self._client = ChatOpenAI(
            model=self.model_name,
            api_key=self.api_key,  # type: ignore
            base_url=self.base_url,
            temperature=self.temperature,
            timeout=self.timeout
        )

    def invoke(self, prompt: str) -> str:
        llm_logger.info(f"调用ML Studio模型: {self.model_name}")
        log_llm_request(prompt, self.model_name, "ML Studio")
        response = self._client.invoke(prompt)
        if not response:
            logging.warning("No response from MLStudioAdapter.")
            return ""
        content = response.content
        result = content if isinstance(content, str) else str(content)
        log_llm_response(result, self.model_name, "ML Studio")
        return result

class AzureAIAdapter(BaseLLMAdapter):
    """
    适配 Azure AI Inference API (非 Azure OpenAI)
    """
    def __init__(self, api_key: str, base_url: str, model_name: str, max_tokens: int, temperature: float = 0.7, timeout: Optional[int] = 600):
        self.api_key = api_key
        self.base_url = base_url
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout

        self._client = ChatCompletionsClient(
            endpoint=self.base_url,
            credential=AzureKeyCredential(self.api_key),
        )

    def invoke(self, prompt: str) -> str:
        llm_logger.info(f"调用Azure AI模型: {self.model_name}")
        log_llm_request(prompt, self.model_name, "Azure AI")
        try:
            response = self._client.complete(
                messages=[
                    SystemMessage(content="You are a helpful AI assistant."),
                    UserMessage(content=prompt),
                ],
                model=self.model_name,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=self.timeout
            )
            
            if response and response.choices:
                content = response.choices[0].message.content
                result = content if content is not None else ""
                log_llm_response(result, self.model_name, "Azure AI")
                return result
            else:
                logging.warning("No response from AzureAIAdapter.")
                return ""
        except Exception as e:
            logging.error(f"Azure AI API 调用失败: {e}")
            return ""

# 火山引擎实现
class VolcanoEngineAIAdapter(BaseLLMAdapter):
    def __init__(self, api_key: str, base_url: str, model_name: str, max_tokens: int, temperature: float = 0.7, timeout: Optional[int] = 600):
        self.base_url = check_base_url(base_url)
        self.api_key = api_key
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout

        self._client = OpenAI(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout  # 添加超时配置
        )
    def invoke(self, prompt: str) -> str:
        llm_logger.info(f"调用火山引擎模型: {self.model_name}")
        log_llm_request(prompt, self.model_name, "火山引擎")
        try:
            response = self._client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "你是DeepSeek，是一个 AI 人工智能助手"},
                    {"role": "user", "content": prompt},
                ],
                timeout=self.timeout  # 添加超时参数
            )
            if not response:
                logging.warning("No response from DeepSeekAdapter.")
                return ""
            content = response.choices[0].message.content
            result = content if content is not None else ""
            log_llm_response(result, self.model_name, "火山引擎")
            return result
        except Exception as e:
            logging.error(f"火山引擎API调用超时或失败: {e}")
            return ""

class SiliconFlowAdapter(BaseLLMAdapter):
    def __init__(self, api_key: str, base_url: str, model_name: str, max_tokens: int, temperature: float = 0.7, timeout: Optional[int] = 600):
        self.base_url = check_base_url(base_url)
        self.api_key = api_key
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout

        self._client = OpenAI(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout  # 添加超时配置
        )
    def invoke(self, prompt: str) -> str:
        llm_logger.info(f"调用硅基流动模型: {self.model_name}")
        log_llm_request(prompt, self.model_name, "硅基流动")
        try:
            response = self._client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "你是DeepSeek，是一个 AI 人工智能助手"},
                    {"role": "user", "content": prompt},
                ],
                timeout=self.timeout  # 添加超时参数
            )
            if not response:
                logging.warning("No response from DeepSeekAdapter.")
                return ""
            content = response.choices[0].message.content
            result = content if content is not None else ""
            log_llm_response(result, self.model_name, "硅基流动")
            return result
        except Exception as e:
            logging.error(f"硅基流动API调用超时或失败: {e}")
            return ""
# grok實現
class GrokAdapter(BaseLLMAdapter):
    """
    适配 xAI Grok API
    """
    def __init__(self, api_key: str, base_url: str, model_name: str, max_tokens: int, temperature: float = 0.7, timeout: Optional[int] = 600):
        self.base_url = check_base_url(base_url)
        self.api_key = api_key
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout

        self._client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            timeout=self.timeout
        )

    def invoke(self, prompt: str) -> str:
        llm_logger.info(f"调用Grok模型: {self.model_name}")
        log_llm_request(prompt, self.model_name, "Grok")
        try:
            response = self._client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are Grok, created by xAI."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                timeout=self.timeout
            )
            if response and response.choices:
                content = response.choices[0].message.content
                result = content if content is not None else ""
                log_llm_response(result, self.model_name, "Grok")
                return result
            else:
                logging.warning("No response from GrokAdapter.")
                return ""
        except Exception as e:
            logging.error(f"Grok API 调用失败: {e}")
            return ""

# 智谱AI实现
class ZhipuAIAdapter(BaseLLMAdapter):
    """
    适配智谱AI GLM系列模型
    """
    def __init__(self, api_key: str, base_url: str, model_name: str, max_tokens: int, temperature: float = 0.7, timeout: Optional[int] = 600):
        self.base_url = check_base_url(base_url) if base_url else "https://open.bigmodel.cn/api/paas/v4"
        self.api_key = api_key
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout

        self._client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            timeout=self.timeout
        )

    def invoke(self, prompt: str) -> str:
        llm_logger.info(f"调用智谱AI模型: {self.model_name}")
        log_llm_request(prompt, self.model_name, "智谱")
        try:
            response = self._client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "你是一个AI助手"},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                timeout=self.timeout
            )
            if response and response.choices:
                content = response.choices[0].message.content
                # 修复：确保content不为None
                result = content if content is not None else ""
                # 添加调试信息
                llm_logger.debug(f"原始响应内容: {content}")
                llm_logger.debug(f"响应对象: {response}")
                log_llm_response(result, self.model_name, "智谱")
                return result
            else:
                logging.warning("No response from ZhipuAIAdapter.")
                return ""
        except Exception as e:
            logging.error(f"智谱AI API 调用失败: {e}")
            # 添加异常详细信息
            logging.error(f"异常详情: {type(e).__name__}: {str(e)}")
            import traceback
            logging.error(f"异常追踪: {traceback.format_exc()}")
            return ""

    def get_model_list(self):
        """
        获取智谱AI支持的模型列表
        """
        try:
            import requests
            import json
            
            # 智谱AI的模型列表API端点
            url = f"{self.base_url}/models"
            
            # 设置请求头
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # 发送请求
            response = requests.get(url, headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                # 提取模型名称列表
                models = [model["id"] for model in data.get("data", [])]
                return models
            else:
                logging.error(f"获取智谱AI模型列表失败: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            logging.error(f"获取智谱AI模型列表时出错: {e}")
            return []

def create_llm_adapter(
    interface_format: str,
    base_url: str,
    model_name: str,
    api_key: str,
    temperature: float,
    max_tokens: int,
    timeout: int
) -> BaseLLMAdapter:
    """
    工厂函数：根据 interface_format 返回不同的适配器实例。
    """
    fmt = interface_format.strip().lower()
    if fmt == "deepseek":
        return DeepSeekAdapter(api_key, base_url, model_name, max_tokens, temperature, timeout)
    elif fmt == "openai":
        return OpenAIAdapter(api_key, base_url, model_name, max_tokens, temperature, timeout)
    elif fmt == "azure openai":
        return AzureOpenAIAdapter(api_key, base_url, model_name, max_tokens, temperature, timeout)
    elif fmt == "azure ai":
        return AzureAIAdapter(api_key, base_url, model_name, max_tokens, temperature, timeout)
    elif fmt == "ollama":
        return OllamaAdapter(api_key, base_url, model_name, max_tokens, temperature, timeout)
    elif fmt == "ml studio":
        return MLStudioAdapter(api_key, base_url, model_name, max_tokens, temperature, timeout)
    elif fmt == "gemini":
        return GeminiAdapter(api_key, base_url, model_name, max_tokens, temperature, timeout)
    elif fmt == "阿里云百炼":
        return OpenAIAdapter(api_key, base_url, model_name, max_tokens, temperature, timeout)
    elif fmt == "火山引擎":
        return VolcanoEngineAIAdapter(api_key, base_url, model_name, max_tokens, temperature, timeout)
    elif fmt == "硅基流动":
        return SiliconFlowAdapter(api_key, base_url, model_name, max_tokens, temperature, timeout)
    elif fmt == "grok":
        return GrokAdapter(api_key, base_url, model_name, max_tokens, temperature, timeout)
    elif fmt == "智谱":
        return ZhipuAIAdapter(api_key, base_url, model_name, max_tokens, temperature, timeout)
    else:
        raise ValueError(f"Unknown interface_format: {interface_format}")