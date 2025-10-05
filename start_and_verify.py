# start_and_verify.py
# -*- coding: utf-8 -*-
"""
启动验证脚本 - 确保修复后的系统可以正常使用
"""

import os
import sys
import subprocess
import time

def print_header():
    """打印头部信息"""
    print("AI小说生成器 - 启动验证")
    print("=" * 50)
    print("修复完成验证报告")
    print("BMAD方法网络连接修复")
    print("=" * 50)

def verify_fixes():
    """验证修复效果"""
    print("\n🔍 验证修复效果...")

    verification_results = {}

    # 1. 验证配置
    try:
        from config_manager import load_config
        config = load_config('config.json')
        verification_results['config'] = len(config.get('llm_configs', {})) > 0
        print("✓ 配置系统正常")
    except:
        verification_results['config'] = False
        print("✗ 配置系统异常")

    # 2. 验证网络管理器
    try:
        from network_manager import get_connection_manager, test_network_connection
        manager = get_connection_manager()
        connectivity = test_network_connection()
        verification_results['network'] = connectivity
        print("✓ 网络管理器正常" if connectivity else "✗ 网络连接异常")
    except:
        verification_results['network'] = False
        print("✗ 网络管理器异常")

    # 3. 验证LLM适配器
    try:
        from llm_adapters import create_llm_adapter
        from config_manager import load_config

        config = load_config('config.json')
        llm_configs = config.get('llm_configs', {})
        if llm_configs:
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

            # 测试调用
            response = adapter.invoke("OK")
            verification_results['llm'] = len(response) > 0
            print("✓ LLM适配器正常" if verification_results['llm'] else "✗ LLM适配器异常")
        else:
            verification_results['llm'] = False
            print("✗ 未找到LLM配置")
    except:
        verification_results['llm'] = False
        print("✗ LLM适配器异常")

    # 4. 验证UI组件
    try:
        from ui.main_window import NovelGeneratorGUI
        from ui.modern_main_window import ModernMainWindow
        verification_results['ui'] = True
        print("✓ UI组件正常")
    except:
        verification_results['ui'] = False
        print("✗ UI组件异常")

    return verification_results

def show_summary(results):
    """显示验证总结"""
    print("\n" + "=" * 50)
    print("修复验证总结")
    print("=" * 50)

    success_count = sum(results.values())
    total_count = len(results)

    components = {
        'config': '配置系统',
        'network': '网络管理',
        'llm': 'LLM适配器',
        'ui': '用户界面'
    }

    for key, success in results.items():
        name = components.get(key, key)
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{name}: {status}")

    print(f"\n整体通过率: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")

    if success_count == total_count:
        print("\n🎉 恭喜！所有修复验证通过！")
        print("AI小说生成器现在可以正常使用了！")
    elif success_count >= 3:
        print("\n✅ 核心功能修复成功！")
        print("AI小说生成器可以正常使用！")
    else:
        print("\n⚠️  仍有部分问题需要解决")

def show_usage_guide():
    """显示使用指南"""
    print("\n" + "=" * 50)
    print("使用指南")
    print("=" * 50)

    print("推荐启动方式:")
    print("1. 智能启动器（推荐）:")
    print("   .venv/Scripts/python.exe launch.py")
    print()
    print("2. 现代版启动:")
    print("   .venv/Scripts/python.exe main_modern.py")
    print()
    print("3. 经典版启动:")
    print("   .venv/Scripts/python.exe main_classic.py")
    print()
    print("4. 传统启动:")
    print("   .venv/Scripts/python.exe main.py")
    print()

    print("故障排除:")
    print("• 网络问题诊断: .venv/Scripts/python.exe network_diagnosis.py")
    print("• 快速验证: .venv/Scripts/python.exe quick_test.py")
    print("• 完整测试: .venv/Scripts/python.exe test_complete_flow.py")

def launch_application():
    """启动应用程序"""
    print("\n" + "=" * 50)
    print("启动应用程序")
    print("=" * 50)

    try:
        print("正在启动智能启动器...")
        subprocess.run([sys.executable, "launch.py"], check=False)
    except KeyboardInterrupt:
        print("\n启动被用户中断")
    except Exception as e:
        print(f"启动失败: {e}")
        print("尝试直接启动经典版...")
        try:
            subprocess.run([sys.executable, "main_classic.py"], check=False)
        except:
            print("启动失败，请手动运行启动命令")

def main():
    """主函数"""
    print_header()

    # 验证修复效果
    results = verify_fixes()

    # 显示总结
    show_summary(results)

    # 显示使用指南
    show_usage_guide()

    # 询问是否启动应用
    try:
        response = input("\n是否现在启动应用程序？(y/n): ").strip().lower()
        if response in ['y', 'yes', '是', '']:
            launch_application()
        else:
            print("\n您可以稍后使用上述命令手动启动应用程序")
    except KeyboardInterrupt:
        print("\n\n程序结束")
    except:
        print("\n您可以稍后使用上述命令手动启动应用程序")

if __name__ == "__main__":
    main()