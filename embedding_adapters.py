# embedding_adapters.py
# -*- coding: utf-8 -*-
import logging
import traceback
from typing import List
import requests
from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings

# 导入高级日志系统
from advanced_logger import embedding_logger, log_embedding_request, log_embedding_response

def ensure_openai_base_url_has_v1(url: str) -> str:
    """
    若用户输入的 url 不包含 '/v1'，则在末尾追加 '/v1'。
    """
    import re
    url = url.strip()
    if not url:
        return url
    if not re.search(r'/v\d+$', url):
        if '/v1' not in url:
            url = url.rstrip('/') + '/v1'
    return url

class BaseEmbeddingAdapter:
    """
    Embedding 接口统一基类
    """
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError

    def embed_query(self, query: str) -> List[float]:
        raise NotImplementedError

class OpenAIEmbeddingAdapter(BaseEmbeddingAdapter):
    """
    基于 OpenAIEmbeddings（或兼容接口）的适配器
    """
    def __init__(self, api_key: str, base_url: str, model_name: str):
        # 忽略类型检查错误，因为实际运行时可以正常工作
        self._embedding = OpenAIEmbeddings(
            api_key=api_key,  # type: ignore
            base_url=ensure_openai_base_url_has_v1(base_url),
            model=model_name
        )

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embedding_logger.info(f"调用OpenAI Embedding模型: {self._embedding.model}")
        log_embedding_request(f"批量文档嵌入 ({len(texts)}个)", self._embedding.model, "OpenAI")
        try:
            result = self._embedding.embed_documents(texts)
            log_embedding_response(result[0] if result else [], self._embedding.model, "OpenAI")
            return result
        except Exception as e:
            embedding_logger.error(f"OpenAI Embedding调用失败: {str(e)}")
            return [[]] * len(texts)

    def embed_query(self, query: str) -> List[float]:
        embedding_logger.info(f"调用OpenAI Embedding模型: {self._embedding.model}")
        log_embedding_request(query, self._embedding.model, "OpenAI")
        try:
            result = self._embedding.embed_query(query)
            log_embedding_response(result, self._embedding.model, "OpenAI")
            return result
        except Exception as e:
            embedding_logger.error(f"OpenAI Embedding调用失败: {str(e)}")
            return []

class AzureOpenAIEmbeddingAdapter(BaseEmbeddingAdapter):
    """
    基于 AzureOpenAIEmbeddings（或兼容接口）的适配器
    """
    def __init__(self, api_key: str, base_url: str, model_name: str):
        import re
        match = re.match(r'https://(.+?)/openai/deployments/(.+?)/embeddings\?api-version=(.+)', base_url)
        if match:
            self.azure_endpoint = f"https://{match.group(1)}"
            self.azure_deployment = match.group(2)
            self.api_version = match.group(3)
        else:
            raise ValueError("Invalid Azure OpenAI base_url format")
        
        self._embedding = AzureOpenAIEmbeddings(
            azure_endpoint=self.azure_endpoint,
            azure_deployment=self.azure_deployment,
            api_key=api_key,  # type: ignore
            api_version=self.api_version,
        )

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embedding_logger.info(f"调用Azure OpenAI Embedding模型: {self.azure_deployment}")
        log_embedding_request(f"批量文档嵌入 ({len(texts)}个)", self.azure_deployment, "Azure OpenAI")
        try:
            result = self._embedding.embed_documents(texts)
            log_embedding_response(result[0] if result else [], self.azure_deployment, "Azure OpenAI")
            return result
        except Exception as e:
            embedding_logger.error(f"Azure OpenAI Embedding调用失败: {str(e)}")
            return [[]] * len(texts)

    def embed_query(self, query: str) -> List[float]:
        embedding_logger.info(f"调用Azure OpenAI Embedding模型: {self.azure_deployment}")
        log_embedding_request(query, self.azure_deployment, "Azure OpenAI")
        try:
            result = self._embedding.embed_query(query)
            log_embedding_response(result, self.azure_deployment, "Azure OpenAI")
            return result
        except Exception as e:
            embedding_logger.error(f"Azure OpenAI Embedding调用失败: {str(e)}")
            return []

class OllamaEmbeddingAdapter(BaseEmbeddingAdapter):
    """
    其接口路径为 /api/embeddings
    """
    def __init__(self, model_name: str, base_url: str):
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embedding_logger.info(f"调用Ollama Embedding模型: {self.model_name}")
        embeddings = []
        for text in texts:
            vec = self._embed_single(text)
            embeddings.append(vec)
        return embeddings

    def embed_query(self, query: str) -> List[float]:
        embedding_logger.info(f"调用Ollama Embedding模型: {self.model_name}")
        log_embedding_request(query, self.model_name, "Ollama")
        result = self._embed_single(query)
        log_embedding_response(result, self.model_name, "Ollama")
        return result

    def _embed_single(self, text: str) -> List[float]:
        """
        调用 Ollama 本地服务 /api/embeddings 接口，获取文本 embedding
        """
        url = self.base_url.rstrip("/")
        if "/api/embeddings" not in url:
            if "/api" in url:
                url = f"{url}/embeddings"
            else:
                if "/v1" in url:
                    url = url[:url.index("/v1")]
                url = f"{url}/api/embeddings"

        data = {
            "model": self.model_name,
            "prompt": text
        }
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            result = response.json()
            if "embedding" not in result:
                raise ValueError("No 'embedding' field in Ollama response.")
            return result["embedding"]
        except requests.exceptions.RequestException as e:
            logging.error(f"Ollama embeddings request error: {e}\n{traceback.format_exc()}")
            return []

class MLStudioEmbeddingAdapter(BaseEmbeddingAdapter):
    """
    基于 LM Studio 的 embedding 适配器
    """
    def __init__(self, api_key: str, base_url: str, model_name: str):
        self.url = ensure_openai_base_url_has_v1(base_url)
        if not self.url.endswith('/embeddings'):
            self.url = f"{self.url}/embeddings"
        
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.model_name = model_name

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embedding_logger.info(f"调用ML Studio Embedding模型: {self.model_name}")
        try:
            payload = {
                "input": texts,
                "model": self.model_name
            }
            response = requests.post(self.url, json=payload, headers=self.headers)
            response.raise_for_status()
            result = response.json()
            if "data" not in result:
                logging.error(f"Invalid response format from LM Studio API: {result}")
                return [[]] * len(texts)
            embeddings = [item.get("embedding", []) for item in result["data"]]
            log_embedding_request(f"批量文档嵌入 ({len(texts)}个)", self.model_name, "ML Studio")
            log_embedding_response(embeddings[0] if embeddings else [], self.model_name, "ML Studio")
            return embeddings
        except requests.exceptions.RequestException as e:
            logging.error(f"LM Studio API request failed: {str(e)}")
            return [[]] * len(texts)
        except (KeyError, IndexError, ValueError, TypeError) as e:
            logging.error(f"Error parsing LM Studio API response: {str(e)}")
            return [[]] * len(texts)

    def embed_query(self, query: str) -> List[float]:
        embedding_logger.info(f"调用ML Studio Embedding模型: {self.model_name}")
        log_embedding_request(query, self.model_name, "ML Studio")
        try:
            payload = {
                "input": query,
                "model": self.model_name
            }
            response = requests.post(self.url, json=payload, headers=self.headers)
            response.raise_for_status()
            result = response.json()
            if "data" not in result or not result["data"]:
                logging.error(f"Invalid response format from LM Studio API: {result}")
                return []
            embedding = result["data"][0].get("embedding", [])
            log_embedding_response(embedding, self.model_name, "ML Studio")
            return embedding
        except requests.exceptions.RequestException as e:
            logging.error(f"LM Studio API request failed: {str(e)}")
            return []
        except (KeyError, IndexError, ValueError, TypeError) as e:
            logging.error(f"Error parsing LM Studio API response: {str(e)}")
            return []

class GeminiEmbeddingAdapter(BaseEmbeddingAdapter):
    """
    基于 Google Generative AI (Gemini) 接口的 Embedding 适配器
    使用直接 POST 请求方式，URL 示例：
    https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key=YOUR_API_KEY
    """
    def __init__(self, api_key: str, model_name: str, base_url: str):
        """
        :param api_key: 传入的 Google API Key
        :param model_name: 这里一般是 "text-embedding-004"
        :param base_url: e.g. https://generativelanguage.googleapis.com/v1beta/models
        """
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embedding_logger.info(f"调用Gemini Embedding模型: {self.model_name}")
        embeddings = []
        for text in texts:
            vec = self._embed_single(text)
            embeddings.append(vec)
        return embeddings

    def embed_query(self, query: str) -> List[float]:
        embedding_logger.info(f"调用Gemini Embedding模型: {self.model_name}")
        log_embedding_request(query, self.model_name, "Gemini")
        result = self._embed_single(query)
        log_embedding_response(result, self.model_name, "Gemini")
        return result

    def _embed_single(self, text: str) -> List[float]:
        """
        直接调用 Google Generative Language API (Gemini) 接口，获取文本 embedding
        """
        url = f"{self.base_url}/{self.model_name}:embedContent?key={self.api_key}"
        payload = {
            "model": self.model_name,
            "content": {
                "parts": [
                    {"text": text}
                ]
            }
        }

        try:
            response = requests.post(url, json=payload)
            print(response.text)
            response.raise_for_status()
            result = response.json()
            embedding_data = result.get("embedding", {})
            return embedding_data.get("values", [])
        except requests.exceptions.RequestException as e:
            logging.error(f"Gemini embed_content request error: {e}\n{traceback.format_exc()}")
            return []
        except Exception as e:
            logging.error(f"Gemini embed_content parse error: {e}\n{traceback.format_exc()}")
            return []

class SiliconFlowEmbeddingAdapter(BaseEmbeddingAdapter):
    """
    基于 SiliconFlow 的 embedding 适配器
    """
    def __init__(self, api_key: str, base_url: str, model_name: str):
        # 自动为 base_url 添加 scheme（如果缺失）
        if not base_url.startswith("http://") and not base_url.startswith("https://"):
            base_url = "https://" + base_url

        # 确保base_url以/v1结尾，然后添加/embeddings路径
        if base_url:
            base_url = base_url.rstrip('/')
            if not base_url.endswith('/v1'):
                if '/v1' not in base_url:
                    base_url = base_url + '/v1'
            self.url = base_url + '/embeddings'
        else:
            self.url = "https://api.siliconflow.cn/v1/embeddings"

        self.payload = {
            "model": model_name,
            "input": "Silicon flow embedding online: fast, affordable, and high-quality embedding services. come try it out!",
            "encoding_format": "float"
        }
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # 记录URL用于调试
        embedding_logger.info(f"SiliconFlow适配器初始化 - URL: {self.url}, 模型: {model_name}")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embedding_logger.info(f"调用SiliconFlow Embedding模型: {self.payload['model']}")
        embeddings = []
        for text in texts:
            try:
                self.payload["input"] = text
                # 创建一个不使用系统代理的会话
                session = requests.Session()
                session.trust_env = False
                response = session.post(self.url, json=self.payload, headers=self.headers)
                response.raise_for_status()
                result = response.json()
                if not result or "data" not in result or not result["data"]:
                    logging.error(f"Invalid response format from SiliconFlow API: {result}")
                    embeddings.append([])
                    continue
                emb = result["data"][0].get("embedding", [])
                embeddings.append(emb)
            except requests.exceptions.RequestException as e:
                logging.error(f"SiliconFlow API request failed: {str(e)}")
                embeddings.append([])
            except (KeyError, IndexError, ValueError, TypeError) as e:
                logging.error(f"Error parsing SiliconFlow API response: {str(e)}")
                embeddings.append([])
        return embeddings

    def embed_query(self, query: str) -> List[float]:
        embedding_logger.info(f"调用SiliconFlow Embedding模型: {self.payload['model']}")
        log_embedding_request(query, self.payload['model'], "SiliconFlow")
        try:
            self.payload["input"] = query
            # 创建一个不使用系统代理的会话
            session = requests.Session()
            session.trust_env = False
            response = session.post(self.url, json=self.payload, headers=self.headers)
            response.raise_for_status()
            result = response.json()

            # 添加详细调试信息
            embedding_logger.info(f"SiliconFlow API响应结构: {list(result.keys()) if isinstance(result, dict) else type(result)}")
            if "data" in result:
                embedding_logger.info(f"SiliconFlow data数组长度: {len(result['data'])}")
                if result["data"] and len(result["data"]) > 0:
                    embedding_logger.info(f"SiliconFlow 第一个data项键: {list(result['data'][0].keys()) if isinstance(result['data'][0], dict) else type(result['data'][0])}")

            if not result or "data" not in result or not result["data"]:
                logging.error(f"Invalid response format from SiliconFlow API: {result}")
                return []
            embedding = result["data"][0].get("embedding", [])
            embedding_logger.info(f"SiliconFlow 提取到的embedding长度: {len(embedding) if embedding else 0}")
            log_embedding_response(embedding, self.payload['model'], "SiliconFlow")
            return embedding
        except requests.exceptions.RequestException as e:
            logging.error(f"SiliconFlow API request failed: {str(e)}")
            return []
        except (KeyError, IndexError, ValueError, TypeError) as e:
            logging.error(f"Error parsing SiliconFlow API response: {str(e)}")
            return []

class GiteeAIEmbeddingAdapter(BaseEmbeddingAdapter):
    """
    基于 Gitee AI 的 embedding 适配器
    """
    def __init__(self, api_key: str, base_url: str, model_name: str):
        # 确保base_url以/v1结尾，然后添加/embeddings路径
        if base_url:
            base_url = base_url.rstrip('/')
            if not base_url.endswith('/v1'):
                if '/v1' not in base_url:
                    base_url = base_url + '/v1'
            self.url = base_url + '/embeddings'
        else:
            self.url = "https://ai.gitee.com/v1/embeddings"
            
        self.model_name = model_name
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "X-Failover-Enabled": "true"
        }

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embedding_logger.info(f"调用Gitee AI Embedding模型: {self.model_name}")
        embeddings = []
        for text in texts:
            try:
                payload = {
                    "input": text,
                    "model": self.model_name
                }
                # 创建一个不使用系统代理的会话
                session = requests.Session()
                session.trust_env = False
                response = session.post(self.url, json=payload, headers=self.headers)
                response.raise_for_status()
                result = response.json()
                if not result or "data" not in result or not result["data"]:
                    logging.error(f"Invalid response format from Gitee AI API: {result}")
                    embeddings.append([])
                    continue
                emb = result["data"][0].get("embedding", [])
                embeddings.append(emb)
            except requests.exceptions.RequestException as e:
                logging.error(f"Gitee AI API request failed: {str(e)}")
                embeddings.append([])
            except (KeyError, IndexError, ValueError, TypeError) as e:
                logging.error(f"Error parsing Gitee AI API response: {str(e)}")
                embeddings.append([])
        return embeddings

    def embed_query(self, query: str) -> List[float]:
        embedding_logger.info(f"调用Gitee AI Embedding模型: {self.model_name}")
        log_embedding_request(query, self.model_name, "Gitee AI")
        try:
            payload = {
                "input": query,
                "model": self.model_name
            }
            # 创建一个不使用系统代理的会话
            session = requests.Session()
            session.trust_env = False
            response = session.post(self.url, json=payload, headers=self.headers)
            response.raise_for_status()
            result = response.json()
            if not result or "data" not in result or not result["data"]:
                logging.error(f"Invalid response format from Gitee AI API: {result}")
                return []
            embedding = result["data"][0].get("embedding", [])
            log_embedding_response(embedding, self.model_name, "Gitee AI")
            return embedding
        except requests.exceptions.RequestException as e:
            logging.error(f"Gitee AI API request failed: {str(e)}")
            return []
        except (KeyError, IndexError, ValueError, TypeError) as e:
            logging.error(f"Error parsing Gitee AI API response: {str(e)}")
            return []


def create_embedding_adapter(
    interface_format: str,
    api_key: str,
    base_url: str,
    model_name: str
) -> BaseEmbeddingAdapter:
    """
    工厂函数：根据 interface_format 返回不同的 embedding 适配器实例
    """
    fmt = interface_format.strip().lower()
    if fmt == "openai":
        return OpenAIEmbeddingAdapter(api_key, base_url, model_name)
    elif fmt == "azure openai":
        return AzureOpenAIEmbeddingAdapter(api_key, base_url, model_name)
    elif fmt == "ollama":
        return OllamaEmbeddingAdapter(model_name, base_url)
    elif fmt == "ml studio":
        return MLStudioEmbeddingAdapter(api_key, base_url, model_name)
    elif fmt == "gemini":
        return GeminiEmbeddingAdapter(api_key, model_name, base_url)
    elif fmt == "siliconflow":
        return SiliconFlowEmbeddingAdapter(api_key, base_url, model_name)
    elif fmt == "gitee ai":
        return GiteeAIEmbeddingAdapter(api_key, base_url, model_name)
    else:
        raise ValueError(f"Unknown embedding interface_format: {interface_format}")