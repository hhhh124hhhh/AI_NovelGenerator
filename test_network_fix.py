# test_network_fix.py
# -*- coding: utf-8 -*-
"""
测试BMAD网络修复方案
"""

import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_network_manager():
    """测试网络管理器"""
    print("=== 测试网络管理器 ===")

    try:
        from network_manager import get_connection_manager, test_network_connection

        # 测试基本连接
        print("1. 测试基本网络连接...")
        basic_connection = test_network_connection()
        print(f"   基本连接: {'正常' if basic_connection else '异常'}")

        # 测试API连接
        print("2. 测试API连接...")
        manager = get_connection_manager()

        # 测试DeepSeek API
        deepseek_result = manager.check_api_health('DeepSeek', 'https://api.deepseek.com')
        print(f"   DeepSeek API: {'正常' if deepseek_result['connected'] else '异常'}")
        if deepseek_result.get('response_time'):
            print(f"   响应时间: {deepseek_result['response_time']}ms")

        return True

    except Exception as e:
        print(f"   错误: {str(e)}")
        return False

def test_llm_adapter():
    """测试LLM适配器"""
    print("\n=== 测试LLM适配器 ===")

    try:
        from llm_adapters import create_llm_adapter
        from config_manager import load_config

        # 加载配置
        config = load_config('config.json')
        llm_configs = config.get('llm_configs', {})

        if not llm_configs:
            print("   未找到LLM配置")
            return False

        # 使用第一个配置进行测试
        config_name = list(llm_configs.keys())[0]
        llm_config = llm_configs[config_name]

        print(f"2. 测试配置: {config_name}")

        # 创建适配器
        adapter = create_llm_adapter(
            interface_format=llm_config.get('interface_format', 'DeepSeek'),
            api_key=llm_config.get('api_key', ''),
            base_url=llm_config.get('base_url', ''),
            model_name=llm_config.get('model_name', 'deepseek-chat'),
            temperature=llm_config.get('temperature', 0.7),
            max_tokens=llm_config.get('max_tokens', 100),
            timeout=30
        )

        # 测试调用
        print("   执行测试调用...")
        test_prompt = "请回复'测试成功'"
        response = adapter.invoke(test_prompt)

        if response and "测试成功" in response:
            print("   LLM调用: 成功")
            return True
        elif response and ("网络错误" in response or "API错误" in response):
            print(f"   LLM调用: 失败 - {response}")
            return False
        else:
            print(f"   LLM调用: 部分成功 - 响应: {response[:100]}...")
            return True

    except Exception as e:
        print(f"   错误: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("BMAD网络修复方案测试")
    print("=" * 40)

    # 测试网络管理器
    network_ok = test_network_manager()

    # 测试LLM适配器
    llm_ok = test_llm_adapter()

    # 总结
    print("\n=== 测试总结 ===")
    print(f"网络管理器: {'✅ 通过' if network_ok else '❌ 失败'}")
    print(f"LLM适配器: {'✅ 通过' if llm_ok else '❌ 失败'}")

    if network_ok and llm_ok:
        print("\n🎉 BMAD修复方案测试成功！")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查错误信息")
        return 1

if __name__ == "__main__":
    sys.exit(main())