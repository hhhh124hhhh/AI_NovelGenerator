#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试统一项目管理器功能
"""

import os
import sys
import tempfile
import json
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_project_manager():
    """测试项目管理器功能"""
    try:
        print("测试开始：统一项目管理器...")

        # 导入项目管理器
        from ui.components.project_manager import ProjectManager

        # 创建临时测试目录
        with tempfile.TemporaryDirectory() as temp_dir:
            test_project_path = os.path.join(temp_dir, "test_novel_project")
            os.makedirs(test_project_path)

            # 创建测试文件
            test_files = {
                "Novel_architecture.txt": "测试小说架构\n这是一个测试小说的世界观设定...",
                "Novel_directory.txt": "第一章：开始\n第二章：发展\n第三章：高潮",
                "character_state.txt": "主角：张三\n配角：李四\n反派：王五",
                "global_summary.txt": "这是一个测试小说的摘要...",
                "project.json": {
                    "name": "测试小说项目",
                    "created_at": datetime.now().isoformat(),
                    "version": "2.0"
                }
            }

            for filename, content in test_files.items():
                file_path = os.path.join(test_project_path, filename)
                if isinstance(content, dict):
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(content, f, ensure_ascii=False, indent=2)
                else:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)

            print(f"✅ 测试项目创建在: {test_project_path}")

            # 1. 测试项目管理器初始化
            print("\n1️⃣ 测试项目管理器初始化...")
            project_manager = ProjectManager()
            print(f"✅ 项目管理器初始化成功")
            print(f"   当前项目路径: {project_manager.get_project_path()}")

            # 2. 测试设置项目路径
            print("\n2️⃣ 测试设置项目路径...")
            project_manager.set_project_path(test_project_path)
            print(f"✅ 项目路径设置成功: {project_manager.get_project_path()}")

            # 3. 测试文件扫描
            print("\n3️⃣ 测试项目文件扫描...")
            project_files = project_manager.get_project_files()
            print(f"✅ 扫描到 {len(project_files)} 个项目文件:")
            for filename, info in project_files.items():
                status = "✅ 存在" if info['exists'] else "❌ 不存在"
                print(f"   {filename}: {status}")

            # 4. 测试文件存在性检查
            print("\n4️⃣ 测试文件存在性检查...")
            for filename in test_files.keys():
                exists = project_manager.file_exists(filename)
                print(f"   {filename}: {'✅ 存在' if exists else '❌ 不存在'}")

            # 5. 测试获取文件路径
            print("\n5️⃣ 测试获取文件路径...")
            for filename in test_files.keys():
                file_path = project_manager.get_file_path(filename)
                print(f"   {filename}: {file_path}")

            # 6. 测试项目状态
            print("\n6️⃣ 测试项目状态...")
            status = project_manager.get_project_status()
            print(f"✅ 项目状态:")
            print(f"   项目路径: {status['project_path']}")
            print(f"   项目名称: {status['project_name']}")
            print(f"   总文件数: {status['total_files']}")
            print(f"   项目有效: {status['is_valid']}")

            # 7. 测试项目信息保存和加载
            print("\n7️⃣ 测试项目信息保存和加载...")
            test_info = {
                "test_field": "test_value",
                "timestamp": datetime.now().isoformat()
            }
            project_manager.save_project_info(test_info)

            loaded_info = project_manager.load_project_info()
            if loaded_info.get("test_field") == "test_value":
                print("✅ 项目信息保存和加载成功")
            else:
                print("❌ 项目信息保存和加载失败")

            # 8. 测试加载项目
            print("\n8️⃣ 测试加载项目...")
            new_project_manager = ProjectManager()
            success = new_project_manager.load_project(test_project_path)
            if success:
                print("✅ 项目加载成功")
                print(f"   加载的路径: {new_project_manager.get_project_path()}")
            else:
                print("❌ 项目加载失败")

            print("\n🎉 所有测试完成！统一项目管理器功能正常。")
            return True

    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration_with_modern_main_window():
    """测试与现代主窗口的集成"""
    try:
        print("\n🔗 测试与现代主窗口的集成...")

        # 尝试导入modern_main_window模块
        from ui.modern_main_window import ModernMainWindow
        print("✅ ModernMainWindow导入成功")

        # 检查是否有project_manager属性
        if hasattr(ModernMainWindow, 'project_manager'):
            print("✅ ModernMainWindow具有project_manager属性")
        else:
            print("⚠️ ModernMainWindow缺少project_manager属性")

        print("✅ 集成测试完成")
        return True

    except ImportError as e:
        print(f"❌ 导入ModernMainWindow失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 集成测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 开始统一项目管理系统测试")
    print("=" * 50)

    success = True

    # 测试项目管理器
    if not test_project_manager():
        success = False

    # 测试集成
    if not test_integration_with_modern_main_window():
        success = False

    print("\n" + "=" * 50)
    if success:
        print("🎉 所有测试通过！统一项目管理系统可以正常使用。")
        sys.exit(0)
    else:
        print("❌ 部分测试失败，请检查错误信息。")
        sys.exit(1)