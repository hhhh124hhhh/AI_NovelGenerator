#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主题系统基础功能测试
不依赖GUI界面的核心功能验证
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_theme_manager():
    """测试主题管理器基础功能"""
    print("=== 测试主题管理器 ===")

    try:
        from theme_system.theme_manager import ThemeManager

        # 创建主题管理器
        tm = ThemeManager(config_path="theme_system/config/themes")
        print(f"✓ 主题管理器创建成功")

        # 测试获取可用主题
        themes = tm.get_available_themes()
        print(f"✓ 可用主题: {themes}")

        # 测试获取当前主题
        current = tm.get_current_theme()
        print(f"✓ 当前主题: {current}")

        # 测试获取颜色
        primary_color = tm.get_color('primary')
        print(f"✓ 主色调: {primary_color}")

        # 测试获取字体
        font = tm.get_font('md')
        print(f"✓ 字体配置: {font}")

        # 测试获取间距
        spacing = tm.get_spacing('md')
        print(f"✓ 间距配置: {spacing}")

        # 测试主题切换
        old_theme = tm.get_current_theme()
        new_theme = tm.toggle_theme()
        print(f"✓ 主题切换: {old_theme} -> {new_theme}")

        # 测试获取样式
        style = tm.get_theme_style('button', 'normal')
        print(f"✓ 按钮样式: {type(style)} (包含 {len(style)} 个属性)")

        return True

    except Exception as e:
        print(f"✗ 主题管理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_style_utils():
    """测试样式工具类"""
    print("\n=== 测试样式工具类 ===")

    try:
        from theme_system.style_utils import StyleUtils

        # 测试颜色解析
        color1 = StyleUtils.parse_color('#FF0000')
        print(f"✓ 颜色解析: {color1}")

        # 测试对比色计算
        contrast = StyleUtils.get_contrast_color('#FFFFFF')
        print(f"✓ 对比色计算: {contrast}")

        # 测试颜色混合
        blended = StyleUtils.blend_colors('#FF0000', '#00FF00', 0.5)
        print(f"✓ 颜色混合: {blended}")

        # 测试颜色变亮
        lightened = StyleUtils.lighten_color('#FF0000', 0.2)
        print(f"✓ 颜色变亮: {lightened}")

        # 测试颜色变暗
        darkened = StyleUtils.darken_color('#FF0000', 0.2)
        print(f"✓ 颜色变暗: {darkened}")

        return True

    except Exception as e:
        print(f"✗ 样式工具类测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_theme_config():
    """测试主题配置"""
    print("\n=== 测试主题配置 ===")

    try:
        from theme_system.theme_config import ThemeConfig, ThemeConfigManager, ColorScheme

        # 创建配置管理器
        config_manager = ThemeConfigManager("theme_system/config/themes")
        print(f"✓ 主题配置管理器创建成功")

        # 创建深色主题
        dark_theme = config_manager.create_dark_theme()
        print(f"✓ 深色主题创建成功: {dark_theme.name}")

        # 创建浅色主题
        light_theme = config_manager.create_light_theme()
        print(f"✓ 浅色主题创建成功: {light_theme.name}")

        # 测试配置验证
        errors = config_manager.validate_theme(dark_theme)
        print(f"✓ 主题验证: {'通过' if not errors else f'失败({len(errors)}个错误)'}")

        # 测试配置序列化
        dark_dict = dark_theme.to_dict()
        print(f"✓ 配置序列化: {len(dark_dict)} 个顶级键")

        # 测试配置反序列化
        restored_theme = ThemeConfig.from_dict(dark_dict)
        print(f"✓ 配置反序列化: {restored_theme.name}")

        return True

    except Exception as e:
        print(f"✗ 主题配置测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_styled_component():
    """测试样式化组件（不依赖GUI）"""
    print("\n=== 测试样式化组件 ===")

    try:
        from theme_system.styled_component import StyledComponent
        from theme_system.theme_manager import ThemeManager

        # 创建一个模拟的样式化组件
        class MockStyledComponent(StyledComponent):
            def __init__(self, theme_manager):
                super().__init__(theme_manager, 'mock_component')
                self._widget = MockWidget()

            def apply_styles(self, state='normal'):
                # 模拟样式应用
                print(f"  应用样式到模拟组件: {state}")

        class MockWidget:
            def configure(self, **kwargs):
                pass

        # 测试组件创建
        tm = ThemeManager(config_path="theme_system/config/themes")
        component = MockStyledComponent(tm)
        print(f"✓ 样式化组件创建成功")

        # 测试样式应用
        component.apply_styles()
        print(f"✓ 样式应用成功")

        # 测试自定义样式
        component.set_custom_style('test_property', 'test_value')
        print(f"✓ 自定义样式设置成功")

        # 测试主题方法
        is_dark = component.is_dark_theme()
        print(f"✓ 主题类型检测: {'深色' if is_dark else '浅色'}")

        return True

    except Exception as e:
        print(f"✗ 样式化组件测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_theme_files():
    """测试主题文件"""
    print("\n=== 测试主题文件 ===")

    try:
        import json
        import os

        # 测试深色主题文件
        dark_file = "theme_system/config/themes/dark_theme.json"
        if os.path.exists(dark_file):
            with open(dark_file, 'r', encoding='utf-8') as f:
                dark_data = json.load(f)
            print(f"✓ 深色主题文件加载成功: {dark_data.get('name', 'Unknown')}")
            print(f"  - 颜色配置: {len(dark_data.get('colors', {}))} 项")
            print(f"  - 组件样式: {len(dark_data.get('components', {}))} 项")
        else:
            print(f"✗ 深色主题文件不存在: {dark_file}")
            return False

        # 测试浅色主题文件
        light_file = "theme_system/config/themes/light_theme.json"
        if os.path.exists(light_file):
            with open(light_file, 'r', encoding='utf-8') as f:
                light_data = json.load(f)
            print(f"✓ 浅色主题文件加载成功: {light_data.get('name', 'Unknown')}")
            print(f"  - 颜色配置: {len(light_data.get('colors', {}))} 项")
            print(f"  - 组件样式: {len(light_data.get('components', {}))} 项")
        else:
            print(f"✗ 浅色主题文件不存在: {light_file}")
            return False

        return True

    except Exception as e:
        print(f"✗ 主题文件测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("开始主题系统功能测试...")
    print("=" * 50)

    tests = [
        test_theme_files,
        test_theme_config,
        test_theme_manager,
        test_style_utils,
        test_styled_component,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1

    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")

    if passed == total:
        print("🎉 所有测试通过！主题系统基础功能正常")
        return 0
    else:
        print("❌ 部分测试失败，请检查上述错误信息")
        return 1

if __name__ == "__main__":
    sys.exit(main())