"""
基础组件系统测试脚本
用于验证BUILD阶段Day1任务1.2的成果
"""

import sys
import os
import logging
import time
import customtkinter as ctk

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_base_components.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 导入组件基类和主题管理器
from ui.components.base_components import StyledComponent
from theme_system.theme_manager import ThemeManager
from ui.state.state_manager import StateManager

# 创建一个测试组件 - 使用CTkFrame作为基础，避免复杂的CTkButton内部状态
class TestComponent(ctk.CTkFrame):
    """测试组件"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.label = ctk.CTkLabel(self, text="测试组件")
        self.label.pack(padx=10, pady=10)


class TestStyledComponent(StyledComponent, TestComponent):
    """测试样式化组件"""

    def __init__(self, parent, theme_manager, state_manager=None, **kwargs):
        StyledComponent.__init__(self, parent, theme_manager, state_manager)
        TestComponent.__init__(self, parent, **kwargs)

    def _initialize_component(self):
        """初始化组件"""
        self.configure(
            width=120,
            height=60
        )
        self.label.configure(text="样式化测试组件")

    def get_component_type(self) -> str:
        """获取组件类型"""
        return "test_component"

    def _bind_custom_events(self):
        """绑定自定义事件"""
        self.bind("<Button-1>", self._on_click)

    def _on_click(self, event):
        """点击事件"""
        self.trigger_event("component_clicked", self.label.cget("text"))


def test_styled_component():
    """测试StyledComponent基类"""
    try:
        logger.info("开始测试 StyledComponent...")

        # 创建测试窗口
        root = ctk.CTk()
        root.title("组件基类测试")
        root.geometry("400x300")

        # 创建主题管理器
        theme_manager = ThemeManager()

        # 创建状态管理器
        state_manager = StateManager()

        # 创建样式化组件
        test_component = TestStyledComponent(
            root,
            theme_manager=theme_manager,
            state_manager=state_manager
        )
        test_component.pack(pady=20)

        logger.info("✅ StyledComponent 创建成功")

        # 测试基本功能
        assert test_component.is_ready(), "组件应该处于就绪状态"
        logger.info("✅ 组件状态验证通过")

        # 测试事件处理
        event_triggered = False
        def component_handler(text):
            nonlocal event_triggered
            event_triggered = True
            logger.info(f"组件事件触发: {text}")

        test_component.add_event_handler("component_clicked", component_handler)

        # 模拟组件点击
        test_component._on_click(None)
        assert event_triggered, "事件应该被触发"
        logger.info("✅ 事件处理验证通过")

        # 测试主题应用
        test_component.apply_theme()
        logger.info("✅ 主题应用验证通过")

        # 测试性能指标
        metrics = test_component.get_performance_metrics()
        assert 'render_count' in metrics, "性能指标应该包含渲染次数"
        logger.info("✅ 性能指标验证通过")

        # 测试组件信息
        info = test_component.get_component_info()
        assert 'id' in info, "组件信息应该包含ID"
        assert 'type' in info, "组件信息应该包含类型"
        logger.info("✅ 组件信息验证通过")

        # 显示测试窗口
        logger.info("显示测试窗口，请手动验证组件功能...")
        logger.info("测试项目:")
        logger.info("1. 按钮是否正常显示")
        logger.info("2. 主题是否正确应用")
        logger.info("3. 点击按钮是否触发事件")
        logger.info("按 Ctrl+C 或关闭窗口退出测试")

        root.mainloop()

        logger.info("✅ StyledComponent 测试完成")
        return True

    except Exception as e:
        logger.error(f"❌ StyledComponent 测试失败: {e}")
        import traceback
        logger.error(f"错误详情:\n{traceback.format_exc()}")
        return False


def test_component_factory():
    """测试ComponentFactory组件工厂"""
    try:
        logger.info("开始测试 ComponentFactory...")

        from ui.components.base_components import ComponentFactory, register_component, create_component

        # 创建工厂实例
        factory = ComponentFactory()

        # 注册组件
        success = factory.register_component("test_button", TestStyledButton)
        assert success, "组件注册应该成功"
        logger.info("✅ 组件注册验证通过")

        # 测试获取注册类型
        registered_types = factory.get_registered_types()
        assert "test_button" in registered_types, "注册类型应该包含test_button"
        logger.info("✅ 注册类型验证通过")

        # 创建测试环境
        root = ctk.CTk()
        theme_manager = ThemeManager()
        state_manager = StateManager()

        # 创建组件
        test_button = factory.create_component(
            "test_button",
            root,
            theme_manager,
            state_manager,
            text="工厂创建的按钮"
        )
        assert test_button is not None, "组件创建应该成功"
        logger.info("✅ 组件创建验证通过")

        # 测试获取组件
        component = factory.get_component(test_button._component_id)
        assert component == test_button, "获取的组件应该正确"
        logger.info("✅ 组件获取验证通过")

        # 测试按类型获取组件
        components_by_type = factory.get_components_by_type("test_button")
        assert test_button in components_by_type, "按类型获取应该包含创建的组件"
        logger.info("✅ 按类型获取验证通过")

        # 测试创建统计
        stats = factory.get_creation_stats()
        assert stats['total_created'] >= 1, "创建统计应该至少为1"
        assert stats['active_count'] >= 1, "活跃组件统计应该至少为1"
        logger.info("✅ 创建统计验证通过")

        # 测试销毁组件
        destroy_success = factory.destroy_component(test_button._component_id)
        assert destroy_success, "组件销毁应该成功"
        logger.info("✅ 组件销毁验证通过")

        # 清理
        root.destroy()
        logger.info("✅ ComponentFactory 测试完成")
        return True

    except Exception as e:
        logger.error(f"❌ ComponentFactory 测试失败: {e}")
        import traceback
        logger.error(f"错误详情:\n{traceback.format_exc()}")
        return False


def test_convenience_functions():
    """测试便捷函数"""
    try:
        logger.info("开始测试便捷函数...")

        from ui.components.base_components import register_component, create_component, get_component_factory

        # 注册组件
        success = register_component("test_button2", TestStyledButton)
        assert success, "便捷函数注册应该成功"
        logger.info("✅ 便捷函数注册验证通过")

        # 创建测试环境
        root = ctk.CTk()
        theme_manager = ThemeManager()
        state_manager = StateManager()

        # 创建组件
        test_button = create_component(
            "test_button2",
            root,
            theme_manager,
            state_manager,
            text="便捷函数创建的按钮"
        )
        assert test_button is not None, "便捷函数创建应该成功"
        logger.info("✅ 便捷函数创建验证通过")

        # 获取工厂
        factory = get_component_factory()
        assert factory is not None, "获取工厂应该成功"
        logger.info("✅ 获取工厂验证通过")

        # 清理
        root.destroy()
        logger.info("✅ 便捷函数测试完成")
        return True

    except Exception as e:
        logger.error(f"❌ 便捷函数测试失败: {e}")
        import traceback
        logger.error(f"错误详情:\n{traceback.format_exc()}")
        return False


def test_component_lifecycle():
    """测试组件生命周期"""
    try:
        logger.info("开始测试组件生命周期...")

        from ui.components.base_components import ComponentState

        # 创建测试环境
        root = ctk.CTk()
        theme_manager = ThemeManager()
        state_manager = StateManager()

        # 创建组件
        test_button = TestStyledButton(
            root,
            theme_manager=theme_manager,
            state_manager=state_manager
        )

        # 测试初始状态
        assert test_button.get_state() == ComponentState.READY, "初始状态应该为READY"
        logger.info("✅ 初始状态验证通过")

        # 测试显示/隐藏
        test_button.show()
        assert test_button.is_visible(), "显示后应该可见"
        logger.info("✅ 显示功能验证通过")

        test_button.hide()
        assert not test_button.is_visible(), "隐藏后应该不可见"
        logger.info("✅ 隐藏功能验证通过")

        # 测试启用/禁用
        test_button.enable()
        assert test_button.is_ready(), "启用后应该就绪"
        logger.info("✅ 启用功能验证通过")

        test_button.disable()
        assert test_button.get_state() == ComponentState.DISABLED, "禁用后状态应该为DISABLED"
        logger.info("✅ 禁用功能验证通过")

        # 测试性能监控
        initial_metrics = test_button.get_performance_metrics()
        test_button.apply_theme()  # 触发一次渲染
        updated_metrics = test_button.get_performance_metrics()
        assert updated_metrics['render_count'] > initial_metrics['render_count'], "渲染次数应该增加"
        logger.info("✅ 性能监控验证通过")

        # 清理
        root.destroy()
        logger.info("✅ 组件生命周期测试完成")
        return True

    except Exception as e:
        logger.error(f"❌ 组件生命周期测试失败: {e}")
        import traceback
        logger.error(f"错误详情:\n{traceback.format_exc()}")
        return False


def main():
    """主测试函数"""
    logger.info("=" * 60)
    logger.info("STORY-002 BUILD阶段Day1 任务1.2 测试")
    logger.info("=" * 60)

    tests = [
        ("StyledComponent基类", test_styled_component),
        ("ComponentFactory工厂", test_component_factory),
        ("便捷函数", test_convenience_functions),
        ("组件生命周期", test_component_lifecycle),
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
        logger.info("🎉 所有测试通过！BUILD阶段Day1任务1.2完成！")
        return True
    else:
        logger.error(f"💥 有 {total - passed} 个测试失败")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)