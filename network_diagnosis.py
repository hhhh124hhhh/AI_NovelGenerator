# network_diagnosis.py
# -*- coding: utf-8 -*-
"""
网络连接诊断工具 - BMAD方法的专业诊断模块
提供详细的网络连接分析和修复建议
"""

import os
import sys
import time
import json
from typing import Dict, Any, List
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from network_manager import diagnose_network, get_connection_manager, NetworkConfig
    from config_manager import load_config
    NETWORK_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  网络模块导入失败: {e}")
    NETWORK_AVAILABLE = False


class NetworkDiagnosisTool:
    """网络诊断工具"""

    def __init__(self):
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.results = {
            'timestamp': self.timestamp,
            'basic_connectivity': {},
            'api_endpoints': {},
            'config_analysis': {},
            'proxy_analysis': {},
            'recommendations': [],
            'overall_status': 'unknown'
        }

    def print_header(self):
        """打印诊断头部信息"""
        print("🔍 AI小说生成器 - 网络连接诊断工具")
        print("=" * 60)
        print(f"诊断时间: {self.timestamp}")
        print(f"Python版本: {sys.version.split()[0]}")
        print(f"操作系统: {os.name}")
        print(f"工作目录: {os.getcwd()}")
        print("=" * 60)

    def test_basic_connectivity(self):
        """测试基础网络连接"""
        print("\n📡 1. 基础网络连接测试")
        print("-" * 40)

        if not NETWORK_AVAILABLE:
            print("❌ 网络管理模块不可用，跳过连接测试")
            self.results['basic_connectivity']['status'] = 'module_unavailable'
            return

        # 测试基础网站连接
        test_sites = [
            ('百度搜索', 'https://www.baidu.com'),
            ('谷歌搜索', 'https://www.google.com'),
            ('微软官网', 'https://www.microsoft.com')
        ]

        connectivity_results = {}

        for name, url in test_sites:
            try:
                manager = get_connection_manager()
                success = manager.test_connection(url, timeout=10)
                status = "✅ 正常" if success else "❌ 失败"
                print(f"   {name}: {status}")
                connectivity_results[name] = {'url': url, 'status': success}
            except Exception as e:
                print(f"   {name}: ❌ 异常 ({str(e)[:50]}...)")
                connectivity_results[name] = {'url': url, 'status': False, 'error': str(e)}

        self.results['basic_connectivity'] = {
            'status': 'completed',
            'results': connectivity_results,
            'success_rate': sum(1 for r in connectivity_results.values() if r['status']) / len(connectivity_results)
        }

    def test_api_endpoints(self):
        """测试API端点连接"""
        print("\n🔌 2. API端点连接测试")
        print("-" * 40)

        if not NETWORK_AVAILABLE:
            print("❌ 网络管理模块不可用，跳过API测试")
            self.results['api_endpoints']['status'] = 'module_unavailable'
            return

        # 从配置文件获取API端点
        api_endpoints = {}
        try:
            config = load_config('config.json')
            llm_configs = config.get('llm_configs', {})
            embedding_configs = config.get('embedding_configs', {})

            # 收集所有API端点
            for name, cfg in llm_configs.items():
                base_url = cfg.get('base_url', '').rstrip('/v1')
                if base_url and base_url not in [ep['url'] for ep in api_endpoints.values()]:
                    api_endpoints[name] = {
                        'url': base_url,
                        'type': 'LLM',
                        'provider': cfg.get('interface_format', 'Unknown')
                    }

            for name, cfg in embedding_configs.items():
                base_url = cfg.get('base_url', '').rstrip('/v1')
                if base_url and base_url not in [ep['url'] for ep in api_endpoints.values()]:
                    api_endpoints[f"{name}(Embedding)"] = {
                        'url': base_url,
                        'type': 'Embedding',
                        'provider': cfg.get('interface_format', 'Unknown')
                    }

        except Exception as e:
            print(f"⚠️  无法读取配置文件: {str(e)}")
            # 使用默认API端点
            api_endpoints = NetworkConfig.HEALTH_CHECK_URLS

        if not api_endpoints:
            print("❌ 没有找到API端点配置")
            self.results['api_endpoints']['status'] = 'no_endpoints'
            return

        # 测试每个API端点
        api_results = {}
        manager = get_connection_manager()

        for name, endpoint_info in api_endpoints.items():
            url = endpoint_info['url'] if isinstance(endpoint_info, dict) else endpoint_info
            provider = endpoint_info.get('provider', 'Unknown') if isinstance(endpoint_info, dict) else name

            try:
                health_result = manager.check_api_health(provider, url)
                status = "✅ 正常" if health_result['connected'] else f"❌ 失败"
                response_time = f" ({health_result['response_time']}ms)" if health_result['response_time'] else ""

                print(f"   {name}: {status}{response_time}")
                if health_result.get('error'):
                    print(f"      错误: {health_result['error'][:50]}...")

                api_results[name] = health_result

            except Exception as e:
                print(f"   {name}: ❌ 异常 ({str(e)[:50]}...)")
                api_results[name] = {
                    'provider': provider,
                    'url': url,
                    'connected': False,
                    'error': str(e)
                }

        self.results['api_endpoints'] = {
            'status': 'completed',
            'results': api_results,
            'success_rate': sum(1 for r in api_results.values() if r['connected']) / len(api_results)
        }

    def analyze_configuration(self):
        """分析配置文件"""
        print("\n⚙️  3. 配置文件分析")
        print("-" * 40)

        try:
            config = load_config('config.json')
            print("✅ 配置文件加载成功")

            # 分析LLM配置
            llm_configs = config.get('llm_configs', {})
            print(f"   LLM配置数量: {len(llm_configs)}")

            for name, cfg in llm_configs.items():
                api_key = cfg.get('api_key', '')
                base_url = cfg.get('base_url', '')
                model = cfg.get('model_name', '')

                # 检查API密钥
                key_status = "✅ 已配置" if api_key and not api_key.startswith('${') else "⚠️  未配置/环境变量"
                print(f"   {name}: {key_status}, 模型: {model}")

            # 分析嵌入配置
            embedding_configs = config.get('embedding_configs', {})
            print(f"   嵌入配置数量: {len(embedding_configs)}")

            self.results['config_analysis'] = {
                'status': 'success',
                'llm_configs': len(llm_configs),
                'embedding_configs': len(embedding_configs),
                'config_file': 'config.json'
            }

        except Exception as e:
            print(f"❌ 配置文件分析失败: {str(e)}")
            self.results['config_analysis'] = {
                'status': 'failed',
                'error': str(e)
            }

    def analyze_proxy_settings(self):
        """分析代理设置"""
        print("\n🌐 4. 代理设置分析")
        print("-" * 40)

        proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
        proxy_settings = {}
        has_proxy = False

        for var in proxy_vars:
            value = os.environ.get(var)
            if value:
                has_proxy = True
                print(f"   {var}: ✅ 已设置")
                proxy_settings[var] = value
            else:
                print(f"   {var}: 未设置")
                proxy_settings[var] = None

        if has_proxy:
            print("\n⚠️  检测到代理设置，这可能影响API连接")
            print("   建议: 如果遇到连接问题，尝试清除代理设置")
        else:
            print("\n✅ 未检测到代理设置")

        self.results['proxy_analysis'] = {
            'has_proxy': has_proxy,
            'settings': proxy_settings
        }

    def generate_recommendations(self):
        """生成修复建议"""
        print("\n💡 5. 修复建议")
        print("-" * 40)

        recommendations = []

        # 基于基础连接结果的建议
        basic_conn = self.results.get('basic_connectivity', {})
        if basic_conn.get('status') == 'completed':
            success_rate = basic_conn.get('success_rate', 0)
            if success_rate < 0.5:
                recommendations.append("🔧 基础网络连接较差，请检查网络设置")
                recommendations.append("📶 尝试连接其他网络或重启路由器")

        # 基于API端点结果的建议
        api_endpoints = self.results.get('api_endpoints', {})
        if api_endpoints.get('status') == 'completed':
            success_rate = api_endpoints.get('success_rate', 0)
            if success_rate == 0:
                recommendations.append("❌ 所有API都无法连接，请检查网络防火墙设置")
                recommendations.append("🔐 确认API密钥配置正确")
            elif success_rate < 1:
                recommendations.append("⚠️  部分API无法连接，建议优先使用可用的API")

        # 基于代理设置的建议
        proxy_analysis = self.results.get('proxy_analysis', {})
        if proxy_analysis.get('has_proxy'):
            recommendations.append("🌐 如果遇到连接问题，尝试暂时禁用代理")
            recommendations.append("   Windows: set HTTP_PROXY= && set HTTPS_PROXY=")
            recommendations.append("   Linux/Mac: unset HTTP_PROXY HTTPS_PROXY")

        # 基于配置分析的建议
        config_analysis = self.results.get('config_analysis', {})
        if config_analysis.get('status') == 'failed':
            recommendations.append("📄 修复配置文件错误或创建新的配置文件")

        # 通用建议
        if not recommendations:
            recommendations.append("✅ 网络连接正常，如仍有问题请联系技术支持")
        else:
            recommendations.append("📞 如问题持续，请查看详细日志或联系技术支持")

        # 输出建议
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")

        self.results['recommendations'] = recommendations

        # 确定整体状态
        basic_ok = basic_conn.get('success_rate', 0) > 0.5
        api_ok = api_endpoints.get('success_rate', 0) > 0

        if basic_ok and api_ok:
            self.results['overall_status'] = 'good'
        elif basic_ok or api_ok:
            self.results['overall_status'] = 'fair'
        else:
            self.results['overall_status'] = 'poor'

    def save_results(self, filename: str = None):
        """保存诊断结果"""
        if filename is None:
            filename = f"network_diagnosis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)
            print(f"\n💾 诊断结果已保存到: {filename}")
        except Exception as e:
            print(f"\n❌ 保存诊断结果失败: {str(e)}")

    def run_diagnosis(self):
        """运行完整诊断"""
        self.print_header()
        self.test_basic_connectivity()
        self.test_api_endpoints()
        self.analyze_configuration()
        self.analyze_proxy_settings()
        self.generate_recommendations()

        # 显示总体状态
        print(f"\n📊 诊断总结")
        print("-" * 40)

        status_map = {
            'good': '✅ 网络连接正常',
            'fair': '⚠️  网络连接一般',
            'poor': '❌ 网络连接较差',
            'unknown': '❓ 无法确定'
        }

        overall_status = self.results.get('overall_status', 'unknown')
        print(f"整体状态: {status_map.get(overall_status, '未知')}")

        # 保存结果
        self.save_results()


def main():
    """主函数"""
    print("启动网络诊断工具...\n")

    try:
        tool = NetworkDiagnosisTool()
        tool.run_diagnosis()

    except KeyboardInterrupt:
        print("\n\n诊断被用户中断")
    except Exception as e:
        print(f"\n诊断过程出现异常: {str(e)}")
        print("请检查网络管理模块是否正确安装")


if __name__ == "__main__":
    main()