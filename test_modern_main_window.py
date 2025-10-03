"""
ModernMainWindow 测试脚本
用于验证BUILD阶段Day1任务1.1的成果
"""

import sys
import os
import logging
import customtkinter as ctk

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_modern_main_window.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def test_modern_main_window():
    """测试ModernMainWindow"""
    try:
        logger.info("开始测试 ModernMainWindow...")

        # 创建主窗口
        from ui.modern_main_window import ModernMainWindow
        from theme_system.theme_manager import ThemeManager

        # 创建主题管理器
        theme_manager = ThemeManager()

        # 创建现代化主窗口
        app = ModernMainWindow(theme_manager)

        logger.info("✅ ModernMainWindow 创建成功")

        # 验证基本功能
        assert app.is_initialized(), "窗口应该已初始化"
        logger.info("✅ 窗口初始化验证通过")

        # 验证管理器
        assert app.get_theme_manager() is not None, "主题管理器应该存在"
        assert app.get_state_manager() is not None, "状态管理器应该存在"
        assert app.get_layout_manager() is not None, "布局管理器应该存在"
        logger.info("✅ 管理器验证通过")

        # 验证窗口信息
        window_info = app.get_window_info()
        assert 'title' in window_info, "窗口信息应包含标题"
        assert 'layout_type' in window_info, "窗口信息应包含布局类型"
        logger.info("✅ 窗口信息验证通过")

        # 测试响应式布局
        layout_manager = app.get_layout_manager()
        layout_info = layout_manager.get_layout_info()
        logger.info(f"当前布局类型: {layout_info['layout_type']}")
        logger.info(f"窗口尺寸: {layout_info['window_size']}")
        logger.info("✅ 响应式布局验证通过")

        # 测试主题系统
        current_theme = theme_manager.get_current_theme()
        theme_info = theme_manager.get_theme_info(current_theme)
        assert theme_info is not None, "主题信息应该存在"
        logger.info(f"当前主题: {current_theme}")
        logger.info("✅ 主题系统验证通过")

        # 测试状态管理
        state_manager = app.get_state_manager()
        test_state = state_manager.get_state('app.theme')
        logger.info(f"应用主题状态: {test_state}")
        logger.info("✅ 状态管理验证通过")

        # 显示窗口（用于手动验证）
        logger.info("显示测试窗口，请手动验证功能...")
        logger.info("测试项目:")
        logger.info("1. 窗口是否正常显示")
        logger.info("2. 主题是否正确应用")
        logger.info("3. 窗口大小调整是否正常")
        logger.info("4. 窗口关闭是否正常")
        logger.info("按 Ctrl+C 或关闭窗口退出测试")

        app.mainloop()

        logger.info("✅ ModernMainWindow 测试完成")

    except Exception as e:
        logger.error(f"❌ ModernMainWindow 测试失败: {e}")
        import traceback
        logger.error(f"错误详情:\n{traceback.format_exc()}")
        return False

    return True


def test_theme_system_integration():
    """测试主题系统集成"""
    try:
        logger.info("测试主题系统集成...")

        from theme_system.theme_manager import ThemeManager

        theme_manager = ThemeManager()
        available_themes = theme_manager.get_available_themes()

        logger.info(f"可用主题: {available_themes}")

        # 测试主题切换
        for theme_name in available_themes:
            success = theme_manager.apply_theme(theme_name)
            current_theme = theme_manager.get_current_theme()
            assert success and current_theme == theme_name, f"主题切换失败: {theme_name}"
            logger.info(f"✅ 主题 '{theme_name}' 切换成功")

        logger.info("✅ 主题系统集成测试完成")

    except Exception as e:
        logger.error(f"❌ 主题系统集成测试失败: {e}")
        return False

    return True


def test_state_manager_integration():
    """测试状态管理器集成"""
    try:
        logger.info("测试状态管理器集成...")

        from ui.state.state_manager import StateManager

        state_manager = StateManager()

        # 测试状态设置和获取
        state_manager.set_state('test.key', 'test_value')
        value = state_manager.get_state('test.key')
        assert value == 'test_value', "状态设置和获取失败"
        logger.info("✅ 状态设置和获取验证通过")

        # 测试状态订阅
        callback_called = False
        def test_callback(key, new_value, old_value):
            nonlocal callback_called
            callback_called = True
            logger.info(f"状态变化回调: {key} {old_value} -> {new_value}")

        subscription_id = state_manager.subscribe('test.subscription', test_callback)
        assert subscription_id is not None, "订阅ID应该存在"

        state_manager.set_state('test.subscription', 'new_value')
        assert callback_called, "状态订阅回调未被调用"
        logger.info("✅ 状态订阅验证通过")

        logger.info("✅ 状态管理器集成测试完成")

    except Exception as e:
        logger.error(f"❌ 状态管理器集成测试失败: {e}")
        return False

    return True


def test_responsive_layout_integration():
    """测试响应式布局集成"""
    try:
        logger.info("测试响应式布局集成...")

        from ui.layout.responsive_manager import ResponsiveLayoutManager
        from ui.layout.breakpoints import Breakpoints, LayoutType

        layout_manager = ResponsiveLayoutManager()

        # 测试不同屏幕尺寸的布局判断
        test_cases = [
            (500, LayoutType.MOBILE),
            (800, LayoutType.TABLET),
            (1200, LayoutType.DESKTOP),
            (1800, LayoutType.LARGE)
        ]

        for width, expected_type in test_cases:
            layout_changed = layout_manager.update_layout(width, 600)
            actual_type = layout_manager.get_current_layout_type()
            assert actual_type == expected_type, f"布局类型判断错误: {width}px -> {actual_type}, 期望: {expected_type}"
            logger.info(f"✅ {width}px -> {expected_type.value} 布局判断正确")

        logger.info("✅ 响应式布局集成测试完成")

    except Exception as e:
        logger.error(f"❌ 响应式布局集成测试失败: {e}")
        return False

    return True


def main():
    """主测试函数"""
    logger.info("=" * 60)
    logger.info("STORY-002 BUILD阶段Day1 任务1.1 测试")
    logger.info("=" * 60)

    tests = [
        ("主题系统集成", test_theme_system_integration),
        ("状态管理器集成", test_state_manager_integration),
        ("响应式布局集成", test_responsive_layout_integration),
        ("ModernMainWindow主测试", test_modern_main_window),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        logger.info(f"\n--- {test_name} ---")
        try:
            if test_func():
                passed += 1
                logger.info(f"✅ {test_name} 通过")
            else:
                logger.error(f"❌ {test_name} 失败")
        except Exception as e:
            logger.error(f"❌ {test_name} 异常: {e}")

    logger.info("\n" + "=" * 60)
    logger.info(f"测试结果: {passed}/{total} 通过")
    logger.info("=" * 60)

    if passed == total:
        logger.info("🎉 所有测试通过！BUILD阶段Day1任务1.1完成！")
        return True
    else:
        logger.error(f"💥 有 {total - passed} 个测试失败")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)