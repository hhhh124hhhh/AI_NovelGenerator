# network_manager.py
# -*- coding: utf-8 -*-
"""
网络连接管理器 - BMAD方法的网络处理模块
提供稳定的网络连接、智能重试和连接检测功能
"""

import os
import time
import requests
import logging
from typing import Optional, Dict, Any, Callable
from urllib.parse import urlparse
import socket
from contextlib import contextmanager

# 导入高级日志系统
try:
    from advanced_logger import main_logger, log_network_request, log_network_response
    ADVANCED_LOGGING = True
except ImportError:
    ADVANCED_LOGGING = False
    main_logger = logging.getLogger("network_manager")


class NetworkConfig:
    """网络配置类"""

    DEFAULT_TIMEOUT = 30
    DEFAULT_RETRIES = 3
    DEFAULT_RETRY_DELAY = 1

    # 常用API端点的健康检查URL
    HEALTH_CHECK_URLS = {
        'DeepSeek': 'https://api.deepseek.com',
        'OpenAI': 'https://api.openai.com',
        'SiliconFlow': 'https://api.siliconflow.cn',
        'ZhipuAI': 'https://open.bigmodel.cn'
    }


class NetworkError(Exception):
    """网络连接错误"""
    pass


class ConnectionManager:
    """连接管理器 - BMAD方法的核心组件"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.timeout = self.config.get('timeout', NetworkConfig.DEFAULT_TIMEOUT)
        self.max_retries = self.config.get('max_retries', NetworkConfig.DEFAULT_RETRIES)
        self.retry_delay = self.config.get('retry_delay', NetworkConfig.DEFAULT_RETRY_DELAY)

        # 保存原始代理设置
        self.original_proxies = {
            'http': os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy'),
            'https': os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
        }

        if ADVANCED_LOGGING:
            log_network_request("ConnectionManager", "初始化连接管理器")

    @contextmanager
    def proxy_context(self, use_proxy: bool = False):
        """
        代理上下文管理器 - BMAD的Adapt模式

        Args:
            use_proxy: 是否使用代理，默认False（清除代理）
        """
        # 保存当前代理设置
        current_proxies = {}

        try:
            if not use_proxy:
                # 清除代理设置
                for proxy_var in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']:
                    current_proxies[proxy_var] = os.environ.pop(proxy_var, None)

                if ADVANCED_LOGGING:
                    log_network_request("ProxyContext", "已清除代理设置")

            yield

        finally:
            # 恢复代理设置
            if not use_proxy:
                for var, value in current_proxies.items():
                    if value:
                        os.environ[var] = value

                if ADVANCED_LOGGING:
                    log_network_response("ProxyContext", "已恢复代理设置")

    def test_connection(self, url: str, timeout: Optional[int] = None) -> bool:
        """
        测试网络连接 - BMAD的Bridge模式

        Args:
            url: 测试URL
            timeout: 超时时间

        Returns:
            bool: 连接是否成功
        """
        timeout = timeout or self.timeout

        try:
            with self.proxy_context(use_proxy=False):
                response = requests.get(url, timeout=timeout)
                success = response.status_code in [200, 401, 403]  # 这些状态码表示连接成功

                if ADVANCED_LOGGING:
                    log_network_response(
                        "ConnectionTest",
                        f"连接测试: {url} - {'成功' if success else '失败'} (状态码: {response.status_code})"
                    )

                return success

        except Exception as e:
            if ADVANCED_LOGGING:
                log_network_request("ConnectionTest", f"连接测试失败: {url} - {str(e)}")

            return False

    def check_api_health(self, provider: str, base_url: str) -> Dict[str, Any]:
        """
        检查API健康状态 - BMAD的Modernize模式

        Args:
            provider: 提供商名称
            base_url: API基础URL

        Returns:
            Dict: 健康检查结果
        """
        health_url = base_url.rstrip('/')

        result = {
            'provider': provider,
            'url': health_url,
            'connected': False,
            'status_code': None,
            'response_time': None,
            'error': None
        }

        try:
            start_time = time.time()

            with self.proxy_context(use_proxy=False):
                response = requests.get(health_url, timeout=10)

                result['connected'] = True
                result['status_code'] = response.status_code
                result['response_time'] = round((time.time() - start_time) * 1000, 2)

                if ADVANCED_LOGGING:
                    log_network_response(
                        "APIHealthCheck",
                        f"{provider} - 状态码: {response.status_code}, 响应时间: {result['response_time']}ms"
                    )

        except Exception as e:
            result['error'] = str(e)

            if ADVANCED_LOGGING:
                log_network_request("APIHealthCheck", f"{provider} - 健康检查失败: {str(e)}")

        return result

    def make_request_with_retry(
        self,
        request_func: Callable,
        *args,
        use_proxy: bool = False,
        **kwargs
    ) -> Any:
        """
        带重试机制的请求执行 - BMAD的De-couple模式

        Args:
            request_func: 请求函数
            *args: 函数参数
            use_proxy: 是否使用代理
            **kwargs: 函数关键字参数

        Returns:
            请求结果

        Raises:
            NetworkError: 所有重试失败后抛出
        """
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                with self.proxy_context(use_proxy=use_proxy):
                    result = request_func(*args, **kwargs)

                    if ADVANCED_LOGGING:
                        log_network_response(
                            "RequestWithRetry",
                            f"请求成功 - 尝试次数: {attempt + 1}"
                        )

                    return result

            except Exception as e:
                last_exception = e

                if ADVANCED_LOGGING:
                    log_network_request(
                        "RequestWithRetry",
                        f"请求失败 - 尝试次数: {attempt + 1}/{self.max_retries}, 错误: {str(e)}"
                    )

                # 如果不是最后一次尝试，等待后重试
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)  # 指数退避
                    time.sleep(delay)

        # 所有重试都失败了
        raise NetworkError(f"网络请求失败，已重试{self.max_retries}次: {str(last_exception)}")

    def diagnose_connection_issues(self) -> Dict[str, Any]:
        """
        诊断连接问题 - BMAD的综合诊断功能

        Returns:
            Dict: 诊断结果
        """
        diagnosis = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'system_info': {},
            'proxy_settings': {},
            'api_health': {},
            'recommendations': []
        }

        # 系统信息
        diagnosis['system_info'] = {
            'platform': os.name,
            'python_version': os.sys.version,
            'working_directory': os.getcwd()
        }

        # 代理设置
        diagnosis['proxy_settings'] = {
            name: os.environ.get(name, 'Not set')
            for name in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
        }

        # API健康检查
        health_results = []
        for provider, url in NetworkConfig.HEALTH_CHECK_URLS.items():
            health_result = self.check_api_health(provider, url)
            health_results.append(health_result)

        diagnosis['api_health'] = health_results

        # 生成建议
        connected_apis = [r for r in health_results if r['connected']]

        if not connected_apis:
            diagnosis['recommendations'].append("❌ 所有API都无法连接，请检查网络连接")
            diagnosis['recommendations'].append("🔧 检查防火墙设置，确保允许HTTPS连接")
        elif len(connected_apis) < len(health_results):
            diagnosis['recommendations'].append(f"⚠️  只有{len(connected_apis)}/{len(health_results)}个API可连接")

        # 检查代理设置问题
        has_proxy = any(os.environ.get(name) for name in diagnosis['proxy_settings'])
        if has_proxy:
            diagnosis['recommendations'].append("🔧 检测到代理设置，可能影响API连接")

        return diagnosis

    def get_best_timeout(self, base_url: str) -> int:
        """
        根据网络状况动态调整超时时间 - BMAD的Adapt模式

        Args:
            base_url: API基础URL

        Returns:
            int: 推荐的超时时间
        """
        try:
            start_time = time.time()

            with self.proxy_context(use_proxy=False):
                requests.get(base_url, timeout=5)

            response_time = time.time() - start_time

            # 根据响应时间动态调整超时
            if response_time < 1:
                return 30  # 快速网络，使用标准超时
            elif response_time < 3:
                return 60  # 中等网络，延长超时
            else:
                return 120  # 慢速网络，使用长超时

        except:
            return 120  # 无法检测，使用长超时


# 全局连接管理器实例
_connection_manager = None

def get_connection_manager(config: Optional[Dict[str, Any]] = None) -> ConnectionManager:
    """获取全局连接管理器实例"""
    global _connection_manager
    if _connection_manager is None:
        _connection_manager = ConnectionManager(config)
    return _connection_manager


def test_network_connection() -> bool:
    """快速测试网络连接"""
    manager = get_connection_manager()
    return manager.test_connection('https://www.baidu.com')


def diagnose_network() -> Dict[str, Any]:
    """诊断网络连接问题"""
    manager = get_connection_manager()
    return manager.diagnose_connection_issues()


if __name__ == "__main__":
    # 测试网络连接管理器
    print("🔍 网络连接诊断")
    print("=" * 50)

    manager = ConnectionManager()

    # 测试基本连接
    print("1. 测试基本网络连接...")
    basic_connection = test_network_connection()
    print(f"   基本连接: {'✅ 正常' if basic_connection else '❌ 异常'}")

    # API健康检查
    print("\n2. API健康检查...")
    for provider, url in NetworkConfig.HEALTH_CHECK_URLS.items():
        result = manager.check_api_health(provider, url)
        status = f"✅ {result['status_code']} ({result['response_time']}ms)" if result['connected'] else f"❌ {result['error']}"
        print(f"   {provider}: {status}")

    # 完整诊断
    print("\n3. 完整网络诊断...")
    diagnosis = manager.diagnose_connection_issues()

    print("\n建议:")
    for rec in diagnosis['recommendations']:
        print(f"   {rec}")