# quick_test.py
# -*- coding: utf-8 -*-
"""
快速验证修复效果
"""

import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_all_components():
    """测试所有组件"""
    print("AI小说生成器 - 快速验证测试")
    print("=" * 40)

    results = {}

    # 1. 测试配置
    print("1. 测试配置加载...")
    try:
        from config_manager import load_config
        config = load_config('config.json')
        results['config'] = len(config.get('llm_configs', {})) > 0
        print(f"   配置加载: {'成功' if results['config'] else '失败'}")
    except Exception as e:
        results['config'] = False
        print(f"   配置加载: 失败 - {e}")

    # 2. 测试网络管理器
    print("2. 测试网络管理器...")
    try:
        from network_manager import get_connection_manager, test_network_connection
        manager = get_connection_manager()
        basic_connection = test_network_connection()
        results['network'] = basic_connection
        print(f"   网络连接: {'正常' if results['network'] else '异常'}")
    except Exception as e:
        results['network'] = False
        print(f"   网络管理器: 失败 - {e}")

    # 3. 测试LLM适配器
    print("3. 测试LLM适配器...")
    try:
        from llm_adapters import create_llm_adapter
        from config_manager import load_config

        config = load_config('config.json')
        llm_configs = config.get('llm_configs', {})
        config_name = list(llm_configs.keys())[0]
        llm_config = llm_configs[config_name]

        adapter = create_llm_adapter(
            interface_format=llm_config.get('interface_format', 'DeepSeek'),
            api_key=llm_config.get('api_key', ''),
            base_url=llm_config.get('base_url', ''),
            model_name=llm_config.get('model_name', 'deepseek-chat'),
            temperature=0.7,
            max_tokens=10,
            timeout=15
        )

        # 快速测试
        response = adapter.invoke("Hi")
        results['llm'] = len(response) > 0
        print(f"   LLM适配器: {'成功' if results['llm'] else '失败'}")
    except Exception as e:
        results['llm'] = False
        print(f"   LLM适配器: 失败 - {e}")

    # 4. 测试UI组件
    print("4. 测试UI组件...")
    try:
        from ui.main_window import NovelGeneratorGUI
        from ui.modern_main_window import ModernMainWindow
        results['ui'] = True
        print("   UI组件: 可用")
    except Exception as e:
        results['ui'] = False
        print(f"   UI组件: 失败 - {e}")

    # 总结
    print("\n" + "=" * 40)
    print("测试总结:")

    success_count = sum(results.values())
    total_count = len(results)

    for component, success in results.items():
        name = {
            'config': '配置系统',
            'network': '网络管理',
            'llm': 'LLM适配器',
            'ui': 'UI组件'
        }.get(component, component)
        status = "✓" if success else "✗"
        print(f"  {status} {name}")

    print(f"\n通过率: {success_count}/{total_count} ({success_count/total_count*100:.0f}%)")

    if success_count >= 3:
        print("\n🎉 核心功能修复成功！AI小说生成器可以正常使用！")
        print("\n建议启动方式:")
        print("  .venv/Scripts/python.exe launch.py")
        return True
    else:
        print("\n⚠️  仍有问题需要解决")
        return False

if __name__ == "__main__":
    test_all_components()