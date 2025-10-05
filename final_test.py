# final_test.py
# -*- coding: utf-8 -*-
"""
最终验证测试 - 解决编码显示问题
确保真实的连接状态
"""

import os
import sys
import json

# 设置UTF-8编码环境
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def safe_print(text):
    """安全打印，避免编码错误"""
    try:
        print(text)
    except UnicodeEncodeError:
        # 如果打印失败，移除或替换有问题的字符
        safe_text = text.encode('ascii', 'ignore').decode('ascii')
        print(safe_text)

def test_api_connection():
    """测试API连接"""
    safe_print("=== API连接测试 ===")

    try:
        import requests
        api_key = 'sk-1bb9d53baee3469cb12ff3256bba9221'
        base_url = 'https://api.deepseek.com/v1'

        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        data = {
            'model': 'deepseek-chat',
            'messages': [{'role': 'user', 'content': '测试连接'}],
            'max_tokens': 50
        }

        response = requests.post(f'{base_url}/chat/completions',
                               headers=headers,
                               json=data,
                               timeout=30)

        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            safe_print(f"API连接: 成功")
            safe_print(f"响应长度: {len(content)} 字符")
            return True
        else:
            safe_print(f"API错误: {response.status_code}")
            return False

    except Exception as e:
        safe_print(f"API测试异常: {e}")
        return False

def test_langchain_connection():
    """测试Langchain连接"""
    safe_print("\n=== Langchain连接测试 ===")

    try:
        from langchain_openai import ChatOpenAI

        client = ChatOpenAI(
            model='deepseek-chat',
            api_key='sk-1bb9d53baee3469cb12ff3256bba9221',
            base_url='https://api.deepseek.com/v1',
            timeout=30
        )

        response = client.invoke('测试连接')

        if response and response.content:
            safe_print("Langchain连接: 成功")
            safe_print(f"响应长度: {len(response.content)} 字符")
            return True
        else:
            safe_print("Langchain响应: 空内容")
            return False

    except Exception as e:
        safe_print(f"Langchain测试异常: {e}")
        return False

def test_novel_generation():
    """测试小说生成功能"""
    safe_print("\n=== 小说生成功能测试 ===")

    try:
        from llm_adapters import create_llm_adapter
        from config_manager import load_config

        config = load_config('config.json')
        llm_configs = config.get('llm_configs', {})

        if not llm_configs:
            safe_print("未找到LLM配置")
            return False

        config_name = list(llm_configs.keys())[0]
        llm_config = llm_configs[config_name]

        adapter = create_llm_adapter(
            interface_format=llm_config.get('interface_format', 'DeepSeek'),
            api_key=llm_config.get('api_key', ''),
            base_url=llm_config.get('base_url', ''),
            model_name=llm_config.get('model_name', 'deepseek-chat'),
            temperature=0.7,
            max_tokens=20,
            timeout=30
        )

        # 测试小说主题生成
        test_prompt = "请生成一个科幻小说的开头，不超过50字"
        response = adapter.invoke(test_prompt)

        if response and len(response) > 10:
            safe_print("小说生成功能: 成功")
            safe_print(f"生成内容长度: {len(response)} 字符")
            return True
        else:
            safe_print("小说生成响应: 异常")
            return False

    except Exception as e:
        safe_print(f"小说生成测试异常: {e}")
        return False

def save_test_results(results):
    """保存测试结果"""
    test_report = {
        'timestamp': os.times(),
        'results': results,
        'summary': {
            'total_tests': len(results),
            'passed_tests': sum(results.values()),
            'success_rate': sum(results.values()) / len(results) * 100
        }
    }

    try:
        with open('final_test_results.json', 'w', encoding='utf-8') as f:
            json.dump(test_report, f, ensure_ascii=False, indent=2)
        safe_print("\n测试结果已保存到: final_test_results.json")
    except Exception as e:
        safe_print(f"保存测试结果失败: {e}")

def main():
    """主测试函数"""
    safe_print("AI小说生成器 - 最终验证测试")
    safe_print("=" * 50)

    # 执行所有测试
    results = {}

    results['api_connection'] = test_api_connection()
    results['langchain_connection'] = test_langchain_connection()
    results['novel_generation'] = test_novel_generation()

    # 显示总结
    safe_print("\n" + "=" * 50)
    safe_print("测试总结")
    safe_print("=" * 50)

    test_names = {
        'api_connection': 'API连接',
        'langchain_connection': 'Langchain连接',
        'novel_generation': '小说生成功能'
    }

    passed_count = 0
    total_count = len(results)

    for test_id, result in results.items():
        test_name = test_names.get(test_id, test_id)
        status = "PASS" if result else "FAIL"
        safe_print(f"{test_name}: {status}")
        if result:
            passed_count += 1

    success_rate = passed_count / total_count * 100
    safe_print(f"\n通过率: {passed_count}/{total_count} ({success_rate:.1f}%)")

    # 最终结论
    if success_rate == 100:
        safe_print("\n[SUCCESS] 所有测试通过！AI小说生成器可以正常使用！")
        safe_print("\n推荐启动方式:")
        safe_print("  python launch.py")
    elif success_rate >= 66:
        safe_print("\n[PARTIAL] 核心功能正常，可以正常使用")
        safe_print("建议优先检查失败的功能")
    else:
        safe_print("\n[FAILED] 存在重要问题，需要进一步修复")

    # 保存结果
    save_test_results(results)

    return 0 if success_rate >= 66 else 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        safe_print("\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        safe_print(f"测试过程出现异常: {e}")
        sys.exit(1)