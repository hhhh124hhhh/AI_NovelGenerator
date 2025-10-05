# config_manager.py
# -*- coding: utf-8 -*-
import json
import os
import threading
import sys
import yaml
from typing import Dict, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入高级日志系统
from advanced_logger import main_logger, llm_logger, embedding_logger, log_llm_request, log_llm_response, log_embedding_request, log_embedding_response

from llm_adapters import create_llm_adapter
from embedding_adapters import create_embedding_adapter


def is_uv_environment():
    """检测是否在 uv 环境中运行"""
    # 检查是否使用 uv run 命令运行
    return 'UV' in os.environ or 'uv' in sys.argv[0].lower()


def get_environment_info():
    """获取环境信息"""
    info = {
        'is_uv': is_uv_environment(),
        'python_version': sys.version,
        'platform': sys.platform
    }
    return info


def load_config(config_file: str) -> dict:
    """从指定的 config_file 加载配置，支持JSON和YAML格式，若不存在则创建一个默认配置文件。"""
    main_logger.info(f"加载配置文件: {config_file}")

    # 如果配置文件不存在，创建默认配置文件
    if not os.path.exists(config_file):
        main_logger.info("配置文件不存在，创建默认配置")
        create_config(config_file)

    try:
        # 根据文件扩展名确定格式
        if config_file.endswith('.yaml') or config_file.endswith('.yml'):
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        else:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        main_logger.error(f"加载配置文件时出错: {e}")
        return {}


def replace_env_vars(config: Dict[Any, Any]) -> Dict[Any, Any]:
    """替换配置中的环境变量占位符"""
    if isinstance(config, dict):
        return {k: replace_env_vars(v) for k, v in config.items()}
    elif isinstance(config, list):
        return [replace_env_vars(item) for item in config]
    elif isinstance(config, str):
        # 替换 ${VAR_NAME} 格式的环境变量
        import re
        def replace_var(match):
            var_name = match.group(1)
            return os.getenv(var_name, match.group(0))  # 如果环境变量不存在，保持原样
        return re.sub(r'\$\{([^}]+)\}', replace_var, config)
    else:
        return config


# PenBo 增加了创建默认配置文件函数
def create_config(config_file: str) -> dict:
    """创建一个默认配置文件。"""
    main_logger.info("创建默认配置文件")
    config = {
    "last_interface_format": "OpenAI",
    "last_embedding_interface_format": "OpenAI",
    "llm_configs": {
        "DeepSeek V3": {
            "api_key": "${DEEPSEEK_API_KEY}",
            "base_url": "https://api.deepseek.com/v1",
            "model_name": "deepseek-chat",
            "temperature": 0.7,
            "max_tokens": 8192,
            "timeout": 600,
            "interface_format": "OpenAI"
        },
        "GPT 5": {
            "api_key": "${OPENAI_API_KEY}",
            "base_url": "https://api.openai.com/v1",
            "model_name": "gpt-5",
            "temperature": 0.7,
            "max_tokens": 32768,
            "timeout": 600,
            "interface_format": "OpenAI"
        },
        "Gemini 2.5 Pro": {
            "api_key": "${GEMINI_API_KEY}",
            "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
            "model_name": "gemini-2.5-pro",
            "temperature": 0.7,
            "max_tokens": 32768,
            "timeout": 600,
            "interface_format": "OpenAI"
        },
        "智谱GLM-4.5": {
            "api_key": "${ZHIPUAI_API_KEY}",
            "base_url": "https://open.bigmodel.cn/api/paas/v4",
            "model_name": "glm-4.5-air",
            "temperature": 0.7,
            "max_tokens": 8192,
            "timeout": 600,
            "interface_format": "智谱"
        }
    },
    "embedding_configs": {
        "OpenAI": {
            "api_key": "${OPENAI_EMBEDDING_API_KEY}",
            "base_url": "https://api.openai.com/v1",
            "model_name": "text-embedding-ada-002",
            "retrieval_k": 4,
            "interface_format": "OpenAI"
        },
        "智谱": {
            "api_key": "${ZHIPUAI_API_KEY}",
            "base_url": "https://open.bigmodel.cn/api/paas/v4",
            "model_name": "embedding-2",
            "retrieval_k": 4,
            "interface_format": "智谱"
        },
        "SiliconFlow": {
            "api_key": "${SILICONFLOW_API_KEY}",
            "base_url": "https://api.siliconflow.cn/v1",
            "model_name": "BAAI/bge-m3",
            "retrieval_k": 4,
            "interface_format": "SiliconFlow"
        },
        "Gitee AI": {
            "api_key": "${GITEE_AI_API_KEY}",
            "base_url": "https://ai.gitee.com/v1",
            "model_name": "bge-m3",
            "retrieval_k": 4,
            "interface_format": "Gitee AI"
        }
    },
    "other_params": {
        "topic": "",
        "genre": "",
        "num_chapters": 0,
        "word_number": 0,
        "filepath": "./novel_output",
        "chapter_num": "120",
        "user_guidance": "",
        "characters_involved": "",
        "key_items": "",
        "scene_location": "",
        "time_constraint": ""
    },
    "choose_configs": {
        "prompt_draft_llm": "DeepSeek V3",
        "chapter_outline_llm": "DeepSeek V3",
        "architecture_llm": "Gemini 2.5 Pro",
        "final_chapter_llm": "GPT 5",
        "consistency_review_llm": "DeepSeek V3"
    },
    "proxy_setting": {
        "proxy_url": "127.0.0.1",
        "proxy_port": "",
        "enabled": False
    },
    "webdav_config": {
        "webdav_url": "",
        "webdav_username": "",
        "webdav_password": ""
    }
}
    save_config(config, config_file)
    return config


def save_config(config_data: dict, config_file: str) -> bool:
    """将 config_data 保存到 config_file 中，支持JSON和YAML格式，返回 True/False 表示是否成功。"""
    main_logger.info(f"保存配置文件: {config_file}")
    try:
        # 根据文件扩展名确定格式
        if config_file.endswith('.yaml') or config_file.endswith('.yml'):
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config_data, f, allow_unicode=True, indent=2)
        else:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        main_logger.error(f"保存配置文件时出错: {e}")
        return False

def test_llm_config(interface_format, api_key, base_url, model_name, temperature, max_tokens, timeout, log_func, handle_exception_func):
    """测试当前的LLM配置是否可用"""
    def task():
        # 初始化代理变量
        old_http_proxy = None
        old_https_proxy = None
        old_http_proxy_lower = None
        old_https_proxy_lower = None
        
        try:
            # 临时清除代理环境变量以避免连接问题
            import os
            old_http_proxy = os.environ.pop('HTTP_PROXY', None)
            old_https_proxy = os.environ.pop('HTTPS_PROXY', None)
            old_http_proxy_lower = os.environ.pop('http_proxy', None)
            old_https_proxy_lower = os.environ.pop('https_proxy', None)

            try:
                log_func("开始测试LLM配置...")
                main_logger.info(f"测试LLM配置 - 接口格式: {interface_format}, 模型: {model_name}")

                llm_adapter = create_llm_adapter(
                    interface_format=interface_format,
                    base_url=base_url,
                    model_name=model_name,
                    api_key=api_key,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=timeout
                )

                test_prompt = "Please reply 'OK'"
                log_llm_request(test_prompt, model_name, interface_format)

                response = llm_adapter.invoke(test_prompt)
                log_llm_response(response, model_name, interface_format)

                if response:
                    log_func("✅ LLM配置测试成功！")
                    log_func(f"测试回复: {response}")
                else:
                    log_func("❌ LLM配置测试失败：未获取到响应")

            finally:
                # 恢复代理环境变量
                import os
                if old_http_proxy:
                    os.environ['HTTP_PROXY'] = old_http_proxy
                if old_https_proxy:
                    os.environ['HTTPS_PROXY'] = old_https_proxy
                if old_http_proxy_lower:
                    os.environ['http_proxy'] = old_http_proxy_lower
                if old_https_proxy_lower:
                    os.environ['https_proxy'] = old_https_proxy_lower

        except Exception as e:
            # 确保在异常情况下也恢复代理设置
            import os
            if old_http_proxy:
                os.environ['HTTP_PROXY'] = old_http_proxy
            if old_https_proxy:
                os.environ['HTTPS_PROXY'] = old_https_proxy
            if old_http_proxy_lower:
                os.environ['http_proxy'] = old_http_proxy_lower
            if old_https_proxy_lower:
                os.environ['https_proxy'] = old_https_proxy_lower

            log_func(f"❌ LLM配置测试出错: {str(e)}")
            handle_exception_func("测试LLM配置时出错")

    threading.Thread(target=task, daemon=True).start()


def test_llm_config_with_dict(config_dict, log_func, handle_exception_func):
    """使用配置字典测试LLM配置"""
    try:
        # 从配置字典中提取参数，提供默认值
        interface_format = config_dict.get('interface_format', 'OpenAI')
        api_key = config_dict.get('api_key', '')
        base_url = config_dict.get('base_url', 'https://api.openai.com/v1')
        model_name = config_dict.get('model_name', 'gpt-3.5-turbo')
        temperature = config_dict.get('temperature', 0.7)
        max_tokens = config_dict.get('max_tokens', 8192)
        timeout = config_dict.get('timeout', 300)
        
        # 调用原始测试函数
        test_llm_config(
            interface_format=interface_format,
            api_key=api_key,
            base_url=base_url,
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            log_func=log_func,
            handle_exception_func=handle_exception_func
        )
        return True, "测试已启动"
    except Exception as e:
        error_msg = f"配置参数错误: {str(e)}"
        log_func(f"❌ {error_msg}")
        return False, error_msg


def test_embedding_config(api_key, base_url, interface_format, model_name, log_func, handle_exception_func):
    """测试当前的Embedding配置是否可用"""
    def task():
        # 初始化代理变量
        old_http_proxy = None
        old_https_proxy = None
        old_http_proxy_lower = None
        old_https_proxy_lower = None
        
        try:
            # 临时清除代理环境变量以避免连接问题
            import os
            old_http_proxy = os.environ.pop('HTTP_PROXY', None)
            old_https_proxy = os.environ.pop('HTTPS_PROXY', None)
            old_http_proxy_lower = os.environ.pop('http_proxy', None)
            old_https_proxy_lower = os.environ.pop('https_proxy', None)

            try:
                log_func("开始测试Embedding配置...")
                main_logger.info(f"测试Embedding配置 - 接口格式: {interface_format}, 模型: {model_name}")

                # 在测试前打印配置信息用于调试
                log_func(f"测试配置: interface_format={interface_format}, base_url={base_url}, model_name={model_name}")

                embedding_adapter = create_embedding_adapter(
                    interface_format=interface_format,
                    api_key=api_key,
                    base_url=base_url,
                    model_name=model_name
                )

                test_text = "测试文本"
                log_embedding_request(test_text, model_name, interface_format)

                embeddings = embedding_adapter.embed_query(test_text)
                log_embedding_response(embeddings, model_name, interface_format)

                # 更详细的向量检查
                if embeddings is None:
                    log_func("❌ Embedding配置测试失败：返回值为None")
                    main_logger.error("嵌入测试失败 - embed_query返回None")
                elif isinstance(embeddings, list):
                    if len(embeddings) > 0:
                        # 检查向量内容是否有效
                        valid_count = sum(1 for x in embeddings if isinstance(x, (int, float)) and not str(x).lower() == 'nan')
                        if valid_count == len(embeddings):
                            log_func("✅ Embedding配置测试成功！")
                            log_func(f"生成的向量维度: {len(embeddings)}")
                            main_logger.info(f"嵌入测试成功 - 向量维度: {len(embeddings)}")
                        else:
                            log_func(f"❌ Embedding配置测试失败：向量包含无效数据 ({valid_count}/{len(embeddings)} 有效)")
                            main_logger.error(f"嵌入测试失败 - 向量数据无效: {embeddings[:5]}...")
                    else:
                        log_func("❌ Embedding配置测试失败：返回空向量")
                        main_logger.error("嵌入测试失败 - 返回空向量列表")
                else:
                    log_func(f"❌ Embedding配置测试失败：返回值类型错误 ({type(embeddings)})")
                    main_logger.error(f"嵌入测试失败 - 返回值类型错误: {type(embeddings)}, 值: {str(embeddings)[:200]}")

                # 如果embeddings有问题，打印调试信息
                if not embeddings or (isinstance(embeddings, list) and len(embeddings) == 0):
                    log_func("🔍 调试信息：检查API响应格式...")
                    # 尝试直接调用API获取原始响应来调试
                    try:
                        import requests
                        headers = {"Authorization": f"Bearer {api_key}"}
                        debug_url = f"{base_url}/embeddings"
                        debug_payload = {"input": test_text, "model": model_name}
                        debug_response = requests.post(debug_url, json=debug_payload, headers=headers, timeout=10)
                        if debug_response.status_code == 200:
                            log_func(f"🔍 API调用成功，响应长度: {len(debug_response.text)} 字符")
                            # 只显示前200个字符避免日志过长
                            response_preview = debug_response.text[:200] + "..." if len(debug_response.text) > 200 else debug_response.text
                            log_func(f"🔍 响应预览: {response_preview}")
                        else:
                            log_func(f"🔍 API调用失败，状态码: {debug_response.status_code}")
                    except Exception as debug_e:
                        log_func(f"🔍 调试API调用失败: {str(debug_e)}")

            finally:
                # 恢复代理环境变量
                import os
                if old_http_proxy:
                    os.environ['HTTP_PROXY'] = old_http_proxy
                if old_https_proxy:
                    os.environ['HTTPS_PROXY'] = old_https_proxy
                if old_http_proxy_lower:
                    os.environ['http_proxy'] = old_http_proxy_lower
                if old_https_proxy_lower:
                    os.environ['https_proxy'] = old_https_proxy_lower

        except Exception as e:
            # 确保在异常情况下也恢复代理设置
            import os
            if old_http_proxy:
                os.environ['HTTP_PROXY'] = old_http_proxy
            if old_https_proxy:
                os.environ['HTTPS_PROXY'] = old_https_proxy
            if old_http_proxy_lower:
                os.environ['http_proxy'] = old_http_proxy_lower
            if old_https_proxy_lower:
                os.environ['https_proxy'] = old_https_proxy_lower

            log_func(f"❌ Embedding配置测试出错: {str(e)}")
            handle_exception_func("测试Embedding配置时出错")

    threading.Thread(target=task, daemon=True).start()


def test_embedding_config_with_dict(config_dict, log_func, handle_exception_func):
    """使用配置字典测试Embedding配置"""
    try:
        # 从配置字典中提取参数，提供默认值
        interface_format = config_dict.get('interface_format', 'OpenAI')
        api_key = config_dict.get('api_key', '')
        base_url = config_dict.get('base_url', 'https://api.openai.com/v1')
        model_name = config_dict.get('model_name', 'text-embedding-ada-002')
        
        # 调用原始测试函数
        test_embedding_config(
            api_key=api_key,
            base_url=base_url,
            interface_format=interface_format,
            model_name=model_name,
            log_func=log_func,
            handle_exception_func=handle_exception_func
        )
        return True, "测试已启动"
    except Exception as e:
        error_msg = f"配置参数错误: {str(e)}"
        log_func(f"❌ {error_msg}")
        return False, error_msg


def get_zhipu_model_list(api_key, base_url, log_func):
    """获取智谱AI模型列表"""
    try:
        log_func("正在获取智谱AI模型列表...")
        from llm_adapters import ZhipuAIAdapter
        
        # 创建智谱AI适配器实例
        adapter = ZhipuAIAdapter(
            api_key=api_key,
            base_url=base_url,
            model_name="glm-4.5-air",  # 临时使用默认模型
            max_tokens=1000,
            temperature=0.7,
            timeout=30
        )
        
        # 获取模型列表
        models = adapter.get_model_list()
        if models:
            log_func(f"✅ 获取到 {len(models)} 个模型:")
            for model in models:
                log_func(f"  - {model}")
            return models
        else:
            log_func("❌ 未获取到模型列表")
            return []
    except Exception as e:
        log_func(f"❌ 获取模型列表时出错: {str(e)}")
        return []