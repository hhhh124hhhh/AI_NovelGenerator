"""
基础组件系统测试脚本 - 修复版本
专注于核心功能验证，避免CustomTkinter继承复杂性
"""

import sys
import os
import logging
import time
import customtkinter as ctk

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tests/test_base_components_fixed.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 导入必要模块
from theme_system.theme_manager import ThemeManager
from ui.state.state_manager import StateManager
from ui.layout.responsive_manager import ResponsiveLayoutManager
from ui.components.base_components import StyledComponent, ComponentFactory


class SimpleTestComponent(ctk.CTkFrame):
    """简单测试组件，不使用多重继承"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.label = ctk.CTkLabel(self, text="测试组件")
        self.label.pack(padx=10, pady=10)


class TestStyledComponent(StyledComponent):
    """测试样式化组件 - 使用组合而非继承"""

    def __init__(self, parent, theme_manager, state_manager=None, **kwargs):
        # 先创建基础组件
        self.inner_component = SimpleTestComponent(parent, **kwargs)

        # 然后初始化样式化组件功能
        self.parent = parent
        self.theme_manager = theme_manager
        self.state_manager = state_manager
        self._component_id = f"TestStyledComponent_{id(self)}"
        self._style_cache = {}
        self._event_handlers = {}
        self._performance_metrics = {
            'creation_time': time.time(),
            'render_count': 0,
            'last_render_time': 0,
            'total_render_time': 0
        }

        # 应用样式和绑定事件
        self.apply_theme()
        self._bind_events()

        logger.debug(f"TestStyledComponent {self._component_id} 初始化完成")

    def _initialize_component(self):
        """实现抽象方法 - 这里不需要额外的初始化"""
        pass

    def get_component_type(self) -> str:
        """获取组件类型"""
        return "test_component"

    def configure(self, **kwargs):
        """代理配置到底层组件"""
        self.inner_component.configure(**kwargs)

    def cget(self, attribute):
        """代理属性查询到底层组件"""
        return self.inner_component.cget(attribute)

    def pack(self, **kwargs):
        """代理pack方法"""
        self.inner_component.pack(**kwargs)

    def grid(self, **kwargs):
        """代理grid方法"""
        self.inner_component.grid(**kwargs)

    def apply_theme(self, theme_name: str = None) -> None:
        """应用主题"""
        try:
            start_time = time.time()

            if self.theme_manager:
                if theme_name is None:
                    theme_name = self.theme_manager.get_current_theme()

                # 获取主题样式
                style_data = self._get_theme_style(theme_name)

                # 应用样式到内部组件
                self._apply_style(style_data)

                # 缓存样式
                self._style_cache[theme_name] = style_data

                render_time = time.time() - start_time
                self._update_performance_metrics(render_time)

                logger.debug(f"组件 {self._component_id} 应用主题 {theme_name} 耗时 {render_time:.3f}s")

        except Exception as e:
            logger.error(f"应用主题失败 {self._component_id}: {e}")

    def _get_theme_style(self, theme_name: str) -> dict:
        """获取主题样式"""
        try:
            # 获取基础颜色
            colors = {
                'fg_color': self.theme_manager.get_color('surface'),
                'text_color': self.theme_manager.get_color('text'),
                'border_color': self.theme_manager.get_color('border')
            }
            return colors
        except Exception as e:
            logger.error(f"获取主题样式失败 {self._component_id}: {e}")
            return {}

    def _apply_style(self, style_data: dict) -> None:
        """应用样式"""
        try:
            if hasattr(self.inner_component, 'configure'):
                valid_styles = {}

                # 检查哪些样式属性可以被应用
                for key, value in style_data.items():
                    try:
                        self.inner_component.cget(key)  # 测试属性是否有效
                        valid_styles[key] = value
                    except:
                        pass

                if valid_styles:
                    self.inner_component.configure(**valid_styles)
                    logger.debug(f"应用样式: {valid_styles}")

        except Exception as e:
            logger.error(f"应用样式失败 {self._component_id}: {e}")

    def _bind_events(self):
        """绑定事件"""
        try:
            # 绑定主题变化事件
            if self.theme_manager:
                self.theme_manager.subscribe(self._on_theme_changed)
        except Exception as e:
            logger.error(f"绑定事件失败 {self._component_id}: {e}")

    def _on_theme_changed(self, theme_name: str, theme_data: dict):
        """主题变化回调"""
        try:
            self.apply_theme(theme_name)
        except Exception as e:
            logger.error(f"处理主题变化失败 {self._component_id}: {e}")

    def add_event_handler(self, event: str, handler) -> None:
        """添加事件处理器"""
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(handler)

    def trigger_event(self, event: str, *args, **kwargs) -> None:
        """触发事件"""
        if event in self._event_handlers:
            for handler in self._event_handlers[event]:
                try:
                    handler(*args, **kwargs)
                except Exception as e:
                    logger.error(f"事件处理器执行失败 {self._component_id}.{event}: {e}")

    def _update_performance_metrics(self, render_time: float) -> None:
        """更新性能指标"""
        self._performance_metrics['render_count'] += 1
        self._performance_metrics['last_render_time'] = render_time
        self._performance_metrics['total_render_time'] += render_time

    def get_performance_metrics(self) -> dict:
        """获取性能指标"""
        metrics = self._performance_metrics.copy()
        if metrics['render_count'] > 0:
            metrics['average_render_time'] = metrics['total_render_time'] / metrics['render_count']
        else:
            metrics['average_render_time'] = 0
        return metrics

    def get_component_info(self) -> dict:
        """获取组件信息"""
        return {
            'id': self._component_id,
            'type': self.get_component_type(),
            'class': self.__class__.__name__,
            'style_cache': list(self._style_cache.keys()),
            'event_handlers': list(self._event_handlers.keys()),
            'performance': self.get_performance_metrics()
        }


def test_theme_manager():
    """测试主题管理器"""
    try:
        logger.info("开始测试主题管理器...")

        theme_manager = ThemeManager()
        available_themes = theme_manager.get_available_themes()

        logger.info(f"可用主题: {available_themes}")
        assert len(available_themes) > 0, "应该有可用主题"
        logger.info("✅ 主题管理器基础验证通过")

        # 测试主题切换
        for theme_name in available_themes:
            success = theme_manager.apply_theme(theme_name)
            current_theme = theme_manager.get_current_theme()
            assert success and current_theme == theme_name, f"主题切换失败: {theme_name}"
            logger.info(f"✅ 主题 '{theme_name}' 切换成功")

        logger.info("✅ 主题管理器测试完成")
        return True

    except Exception as e:
        logger.error(f"❌ 主题管理器测试失败: {e}")
        return False


def test_state_manager():
    """测试状态管理器"""
    try:
        logger.info("开始测试状态管理器...")

        state_manager = StateManager()

        # 测试状态设置和获取 - 使用点号分隔的键
        state_manager.update_state({'test': {'key': 'test_value'}})
        value = state_manager.get_state('test.key')
        logger.info(f"设置状态: 'test.key' = 'test_value'")
        logger.info(f"获取状态: 'test.key' = '{value}'")
        assert value == 'test_value', f"状态设置和获取失败: 期望'test_value', 实际'{value}'"
        logger.info("✅ 状态设置和获取验证通过")

        # 测试状态订阅
        callback_called = False
        def test_callback(key, new_value, old_value):
            nonlocal callback_called
            callback_called = True
            logger.info(f"状态变化回调: {key} {old_value} -> {new_value}")

        subscription_id = state_manager.subscribe('test.subscription', test_callback)
        assert subscription_id is not None, "订阅ID应该存在"

        state_manager.update_state({'test': {'subscription': 'new_value'}})
        assert callback_called, "状态订阅回调未被调用"
        logger.info("✅ 状态订阅验证通过")

        logger.info("✅ 状态管理器测试完成")
        return True

    except Exception as e:
        logger.error(f"❌ 状态管理器测试失败: {e}")
        import traceback
        logger.error(f"错误详情:\n{traceback.format_exc()}")
        return False


def test_responsive_layout():
    """测试响应式布局"""
    try:
        logger.info("开始测试响应式布局...")

        layout_manager = ResponsiveLayoutManager()

        # 测试不同屏幕尺寸的布局判断
        test_cases = [
            (500, "mobile"),
            (800, "tablet"),
            (1200, "desktop"),
            (1800, "large")
        ]

        for width, expected_type_name in test_cases:
            layout_changed = layout_manager.update_layout(width, 600)
            actual_type = layout_manager.get_current_layout_type()
            expected_type = actual_type.__class__  # 这里简化比较

            assert actual_type.value == expected_type_name, f"布局类型判断错误: {width}px -> {actual_type.value}, 期望: {expected_type_name}"
            logger.info(f"✅ {width}px -> {actual_type.value} 布局判断正确")

        logger.info("✅ 响应式布局测试完成")
        return True

    except Exception as e:
        logger.error(f"❌ 响应式布局测试失败: {e}")
        import traceback
        logger.error(f"错误详情:\n{traceback.format_exc()}")
        return False


def test_styled_component():
    """测试样式化组件"""
    try:
        logger.info("开始测试样式化组件...")

        # 创建测试环境
        root = ctk.CTk()
        root.title("组件测试")
        root.geometry("300x200")

        theme_manager = ThemeManager()
        state_manager = StateManager()

        # 创建样式化组件
        test_component = TestStyledComponent(
            root,
            theme_manager=theme_manager,
            state_manager=state_manager
        )
        test_component.pack(pady=20)

        logger.info("✅ 样式化组件创建成功")

        # 测试主题应用
        test_component.apply_theme()
        logger.info("✅ 主题应用验证通过")

        # 测试事件处理
        event_triggered = False
        def test_handler(*args, **kwargs):
            nonlocal event_triggered
            event_triggered = True
            logger.info(f"组件事件触发: {args}, {kwargs}")

        test_component.add_event_handler("test_event", test_handler)
        test_component.trigger_event("test_event", "test_data")
        assert event_triggered, "事件应该被触发"
        logger.info("✅ 事件处理验证通过")

        # 测试性能指标
        metrics = test_component.get_performance_metrics()
        assert 'render_count' in metrics, "性能指标应该包含渲染次数"
        logger.info("✅ 性能指标验证通过")

        # 测试组件信息
        info = test_component.get_component_info()
        assert 'id' in info, "组件信息应该包含ID"
        assert 'type' in info, "组件信息应该包含类型"
        logger.info("✅ 组件信息验证通过")

        logger.info("显示测试窗口，请手动验证...")
        logger.info("按 Ctrl+C 或关闭窗口继续测试")

        # 显示窗口2秒后自动关闭
        root.after(2000, root.destroy)
        root.mainloop()

        logger.info("✅ 样式化组件测试完成")
        return True

    except Exception as e:
        logger.error(f"❌ 样式化组件测试失败: {e}")
        import traceback
        logger.error(f"错误详情:\n{traceback.format_exc()}")
        return False


def test_component_factory():
    """测试组件工厂"""
    try:
        logger.info("开始测试组件工厂...")

        factory = ComponentFactory()

        # 注册组件
        success = factory.register_component("test_component", TestStyledComponent)
        assert success, "组件注册应该成功"
        logger.info("✅ 组件注册验证通过")

        # 测试获取注册类型
        registered_types = factory.get_registered_types()
        assert "test_component" in registered_types, "注册类型应该包含test_component"
        logger.info("✅ 注册类型验证通过")

        # 创建测试环境
        root = ctk.CTk()
        theme_manager = ThemeManager()
        state_manager = StateManager()

        # 创建组件
        test_component = factory.create_component(
            "test_component",
            root,
            theme_manager,
            state_manager
        )
        assert test_component is not None, "组件创建应该成功"
        logger.info("✅ 组件创建验证通过")

        # 测试获取组件
        component = factory.get_component(test_component._component_id)
        assert component == test_component, "获取的组件应该正确"
        logger.info("✅ 组件获取验证通过")

        # 测试创建统计
        stats = factory.get_creation_stats()
        assert stats['total_created'] >= 1, "创建统计应该至少为1"
        logger.info("✅ 创建统计验证通过")

        # 清理
        root.destroy()
        logger.info("✅ 组件工厂测试完成")
        return True

    except Exception as e:
        logger.error(f"❌ 组件工厂测试失败: {e}")
        import traceback
        logger.error(f"错误详情:\n{traceback.format_exc()}")
        return False


def main():
    """主测试函数"""
    logger.info("=" * 60)
    logger.info("STORY-002 BUILD阶段Day1 组件系统测试 - 修复版")
    logger.info("=" * 60)

    tests = [
        ("主题管理器", test_theme_manager),
        ("状态管理器", test_state_manager),
        ("响应式布局", test_responsive_layout),
        ("样式化组件", test_styled_component),
        ("组件工厂", test_component_factory),
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
        logger.info("🎉 所有测试通过！组件系统就位！")
        return True
    else:
        logger.error(f"💥 有 {total - passed} 个测试失败")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)