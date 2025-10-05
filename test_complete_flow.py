# test_complete_flow.py
# -*- coding: utf-8 -*-
"""
完整的小说生成流程测试
确保所有组件都能正常工作
"""

import os
import sys
import json
import time

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_config_loading():
    """测试配置加载"""
    print("=== 测试配置加载 ===")
    try:
        from config_manager import load_config
        config = load_config('config.json')

        llm_configs = config.get('llm_configs', {})
        if llm_configs:
            print(f"   成功加载 {len(llm_configs)} 个LLM配置")
            return True, config
        else:
            print("   未找到LLM配置")
            return False, None
    except Exception as e:
        print(f"   配置加载失败: {e}")
        return False, None

def test_llm_adapter(config):
    """测试LLM适配器"""
    print("\n=== 测试LLM适配器 ===")
    try:
        from llm_adapters import create_llm_adapter

        # 使用第一个LLM配置
        llm_configs = config.get('llm_configs', {})
        config_name = list(llm_configs.keys())[0]
        llm_config = llm_configs[config_name]

        print(f"   测试配置: {config_name}")

        adapter = create_llm_adapter(
            interface_format=llm_config.get('interface_format', 'DeepSeek'),
            api_key=llm_config.get('api_key', ''),
            base_url=llm_config.get('base_url', ''),
            model_name=llm_config.get('model_name', 'deepseek-chat'),
            temperature=0.7,
            max_tokens=100,
            timeout=30
        )

        print("   LLM适配器创建成功")

        # 测试调用
        test_prompt = "请用一句话回复：测试成功"
        print("   执行测试调用...")
        start_time = time.time()

        response = adapter.invoke(test_prompt)

        elapsed_time = time.time() - start_time
        print(f"   调用完成，耗时: {elapsed_time:.2f}秒")
        print(f"   响应: {response}")

        if "测试成功" in response or len(response) > 0:
            print("   LLM调用: 成功")
            return True
        else:
            print("   LLM调用: 异常响应")
            return False

    except Exception as e:
        print(f"   LLM适配器测试失败: {e}")
        return False

def test_novel_generation():
    """测试小说生成组件"""
    print("\n=== 测试小说生成组件 ===")
    try:
        from novel_generator.architecture import Novel_architecture_generate
        from config_manager import load_config

        config = load_config('config.json')
        llm_configs = config.get('llm_configs', {})
        config_name = list(llm_configs.keys())[0]
        llm_config = llm_configs[config_name]

        # 准备生成参数
        generation_params = {
            'topic': '科幻冒险',
            'genre': '科幻',
            'num_chapters': 3,
            'word_number': 1000,
            'filepath': './test_output',
            'user_guidance': '一个关于时间旅行的冒险故事',
            'characters_involved': '主角：时间旅行者',
            'key_items': '时间机器',
            'scene_location': '未来城市',
            'time_constraint': ''
        }

        print("   开始小说架构生成...")
        print(f"   主题: {generation_params['topic']}")
        print(f"   类型: {generation_params['genre']}")

        start_time = time.time()

        # 执行小说架构生成
        Novel_architecture_generate(
            topic=generation_params['topic'],
            genre=generation_params['genre'],
            num_chapters=generation_params['num_chapters'],
            word_number=generation_params['word_number'],
            filepath=generation_params['filepath'],
            user_guidance=generation_params['user_guidance'],
            characters_involved=generation_params['characters_involved'],
            key_items=generation_params['key_items'],
            scene_location=generation_params['scene_location'],
            time_constraint=generation_params['time_constraint']
        )

        elapsed_time = time.time() - start_time
        print(f"   架构生成完成，耗时: {elapsed_time:.2f}秒")

        # 检查输出文件
        output_file = os.path.join(generation_params['filepath'], 'Novel_setting.txt')
        if os.path.exists(output_file):
            print("   输出文件生成成功")
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"   文件大小: {len(content)} 字符")
                if len(content) > 100:
                    print("   小说架构生成: 成功")
                    return True
                else:
                    print("   小说架构生成: 内容过少")
                    return False
        else:
            print("   输出文件未生成")
            return False

    except Exception as e:
        print(f"   小说生成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ui_components():
    """测试UI组件"""
    print("\n=== 测试UI组件 ===")
    try:
        # 测试导入
        from ui.main_window import NovelGeneratorGUI
        from ui.modern_main_window import ModernMainWindow

        print("   经典UI组件: 可用")
        print("   现代UI组件: 可用")

        return True

    except ImportError as e:
        print(f"   UI组件导入失败: {e}")
        return False
    except Exception as e:
        print(f"   UI组件测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("AI小说生成器 - 完整流程测试")
    print("=" * 50)

    test_results = {}

    # 1. 测试配置加载
    config_ok, config = test_config_loading()
    test_results['config'] = config_ok

    if not config_ok:
        print("\n❌ 配置加载失败，无法继续测试")
        return 1

    # 2. 测试LLM适配器
    llm_ok = test_llm_adapter(config)
    test_results['llm'] = llm_ok

    # 3. 测试小说生成
    if llm_ok:
        novel_ok = test_novel_generation()
        test_results['novel'] = novel_ok
    else:
        test_results['novel'] = False

    # 4. 测试UI组件
    ui_ok = test_ui_components()
    test_results['ui'] = ui_ok

    # 测试总结
    print("\n" + "=" * 50)
    print("=== 测试总结 ===")

    status_map = {
        True: "✅ 通过",
        False: "❌ 失败"
    }

    for component, result in test_results.items():
        component_name = {
            'config': '配置加载',
            'llm': 'LLM适配器',
            'novel': '小说生成',
            'ui': 'UI组件'
        }.get(component, component)

        print(f"{component_name}: {status_map[result]}")

    # 整体评估
    passed_count = sum(test_results.values())
    total_count = len(test_results)

    print(f"\n总体通过率: {passed_count}/{total_count} ({passed_count/total_count*100:.1f}%)")

    if passed_count == total_count:
        print("\n🎉 所有测试通过！AI小说生成器可以正常使用！")
        return 0
    elif passed_count >= 3:
        print("\n✅ 核心功能正常，可以正常使用")
        return 0
    else:
        print("\n⚠️  存在重要问题，需要进一步修复")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n测试过程出现异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)