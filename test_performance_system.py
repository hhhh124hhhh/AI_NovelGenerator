"""
性能系统测试 - 验证性能监控和优化功能
测试各种性能指标监控和自动优化
"""

import logging
import time
import customtkinter as ctk
from ui.modern_main_window import ModernMainWindow

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerformanceTestApp:
    """性能测试应用"""

    def __init__(self):
        """初始化测试应用"""
        self.root = ctk.CTk()
        self.root.title("AI小说生成器 - 性能系统测试")
        self.root.geometry("1400x900")

        # 创建现代化主窗口
        self.main_window = ModernMainWindow()
        # 注意：ModernMainWindow继承自CTk，本身就是一个窗口，不需要pack

        # 创建性能测试控制面板
        self.create_performance_test_panel()

        logger.info("性能测试应用初始化完成")

    def create_performance_test_panel(self):
        """创建性能测试控制面板"""
        test_frame = ctk.CTkFrame(self.root, width=300)
        test_frame.pack(side="right", fill="y", padx=5, pady=5)

        title_label = ctk.CTkLabel(
            test_frame,
            text="🧪 性能测试控制台",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=10)

        # 性能信息显示
        self.info_text = ctk.CTkTextbox(test_frame, height=200, width=280)
        self.info_text.pack(padx=10, pady=5)

        # 测试按钮
        test_buttons = [
            ("📊 显示性能报告", self.show_performance_report),
            ("⚡ 运行性能测试", self.run_performance_test),
            ("🔧 手动优化性能", self.manual_optimize),
            ("🧹 清理内存", self.cleanup_memory),
            ("📈 测试动画性能", self.test_animation_performance),
            ("🎯 测试UI响应", self.test_ui_response)
        ]

        for text, command in test_buttons:
            btn = ctk.CTkButton(test_frame, text=text, command=command)
            btn.pack(padx=10, pady=3, fill="x")

        # 自动刷新
        self.auto_refresh_var = ctk.BooleanVar(value=True)
        auto_refresh_cb = ctk.CTkCheckBox(
            test_frame,
            text="自动刷新性能信息",
            variable=self.auto_refresh_var
        )
        auto_refresh_cb.pack(pady=10)

        # 开始自动刷新
        self.schedule_refresh()

    def show_performance_report(self):
        """显示性能报告"""
        try:
            performance_info = self.main_window.get_performance_info()
            if performance_info:
                report = performance_info.get('report', '无性能数据')
                self.info_text.delete("1.0", "end")
                self.info_text.insert("1.0", report)
            else:
                self.info_text.delete("1.0", "end")
                self.info_text.insert("1.0", "性能监控系统未运行")
        except Exception as e:
            logger.error(f"显示性能报告失败: {e}")

    def run_performance_test(self):
        """运行性能测试"""
        try:
            self.info_text.delete("1.0", "end")
            self.info_text.insert("1.0", "🧪 开始性能测试...\n\n")

            # 测试1: 窗口创建性能
            start_time = time.time()
            test_window = ctk.CTkToplevel(self.root)
            test_window.title("测试窗口")
            test_window.geometry("400x300")
            creation_time = time.time() - start_time

            # 测试2: 组件创建性能
            start_time = time.time()
            for i in range(10):
                label = ctk.CTkLabel(test_window, text=f"测试标签 {i}")
                label.pack()
            component_time = time.time() - start_time

            # 测试3: 渲染性能
            start_time = time.time()
            test_window.update()
            render_time = time.time() - start_time

            # 关闭测试窗口
            test_window.destroy()

            # 显示结果
            results = f"""🧪 性能测试结果

⏱️ 窗口创建时间: {creation_time*1000:.2f} ms
🏗️ 组件创建时间: {component_time*1000:.2f} ms
🎨 渲染时间: {render_time*1000:.2f} ms

✅ 测试完成"""

            self.info_text.delete("1.0", "end")
            self.info_text.insert("1.0", results)

        except Exception as e:
            logger.error(f"性能测试失败: {e}")

    def manual_optimize(self):
        """手动优化性能"""
        try:
            self.main_window.optimize_performance()
            self.show_performance_report()
        except Exception as e:
            logger.error(f"手动优化失败: {e}")

    def cleanup_memory(self):
        """清理内存"""
        try:
            freed = self.main_window.performance_monitor.optimize_memory()
            self.info_text.delete("1.0", "end")
            self.info_text.insert("1.0", f"🧹 内存清理完成\n\n清理对象: {freed} 个")
        except Exception as e:
            logger.error(f"内存清理失败: {e}")

    def test_animation_performance(self):
        """测试动画性能"""
        try:
            self.info_text.delete("1.0", "end")
            self.info_text.insert("1.0", "🎬 开始动画性能测试...\n")

            # 测试多种动画效果
            animations = []
            
            # 只有当组件存在时才添加动画测试
            if self.main_window.title_bar is not None:
                # 使用类型转换来解决类型检查问题
                title_bar_widget = self.main_window.title_bar  # type: ignore
                animations.append(("淡入", lambda: self.main_window.animation_manager.fade_in(title_bar_widget, duration=500)))
            
            if self.main_window.main_content is not None:
                main_content_widget = self.main_window.main_content  # type: ignore
                animations.append(("缩放", lambda: self.main_window.animation_manager.scale_up(main_content_widget, duration=300)))
            
            if self.main_window.title_bar is not None:
                title_bar_widget2 = self.main_window.title_bar  # type: ignore
                animations.append(("高亮", lambda: self.main_window.animation_manager.highlight(title_bar_widget2, duration=400)))
            
            if self.main_window.sidebar is not None:
                sidebar_widget = self.main_window.sidebar  # type: ignore
                animations.append(("脉冲", lambda: self.main_window.animation_manager.pulse(sidebar_widget, duration=600)))

            results = []
            for name, animation_func in animations:
                start_time = time.time()
                animation_func()
                # 等待动画完成
                time.sleep(0.8)
                animation_time = time.time() - start_time
                results.append(f"{name}: {animation_time*1000:.2f} ms")

            results_text = "\n🎬 动画性能测试结果:\n" + "\n".join(results)
            self.info_text.insert("end", results_text)

        except Exception as e:
            logger.error(f"动画性能测试失败: {e}")

    def test_ui_response(self):
        """测试UI响应性能"""
        try:
            self.info_text.delete("1.0", "end")
            self.info_text.insert("1.0", "⚡ 开始UI响应测试...\n")

            # 只有当main_content存在时才进行测试
            if self.main_window.main_content is not None:
                main_content_widget = self.main_window.main_content  # type: ignore
                # 测试标签页切换响应时间
                response_times = []
                for i in range(5):
                    start_time = time.time()
                    main_content_widget.switch_to_tab("config")
                    self.main_window.update()
                    response_time = time.time() - start_time
                    response_times.append(response_time)

                avg_response = sum(response_times) / len(response_times)
                min_response = min(response_times)
                max_response = max(response_times)

                results = f"""
⚡ UI响应测试结果

平均响应时间: {avg_response*1000:.2f} ms
最快响应时间: {min_response*1000:.2f} ms
最慢响应时间: {max_response*1000:.2f} ms

📊 性能评级: {self._get_performance_rating(avg_response)}
"""
                self.info_text.delete("1.0", "end")
                self.info_text.insert("1.0", results)
            else:
                self.info_text.delete("1.0", "end")
                self.info_text.insert("1.0", "❌ UI响应测试失败: main_content组件未初始化")

        except Exception as e:
            logger.error(f"UI响应测试失败: {e}")

    def _get_performance_rating(self, response_time: float) -> str:
        """获取性能评级"""
        if response_time < 0.05:
            return "🟢 优秀"
        elif response_time < 0.1:
            return "🟡 良好"
        elif response_time < 0.2:
            return "🟠 一般"
        else:
            return "🔴 需要优化"

    def schedule_refresh(self):
        """调度自动刷新"""
        if self.auto_refresh_var.get():
            try:
                self.update_performance_info()
            except:
                pass
            # 每5秒刷新一次
            self.root.after(5000, self.schedule_refresh)

    def update_performance_info(self):
        """更新性能信息"""
        try:
            if hasattr(self.main_window, 'performance_monitor'):
                summary = self.main_window.performance_monitor.get_performance_summary()

                info_lines = ["📊 实时性能监控", "=" * 30, ""]

                for metric_name, data in summary.items():
                    current_value = data['current']
                    unit = data['unit']

                    # 格式化显示
                    if unit == "bytes":
                        display_value = f"{current_value / 1024 / 1024:.1f} MB"
                    elif unit == "%":
                        display_value = f"{current_value:.1f} %"
                    else:
                        display_value = f"{current_value:.1f} {unit}"

                    info_lines.append(f"{metric_name}: {display_value}")

                info_text = "\n".join(info_lines)

                # 检查是否需要更新（避免频繁更新GUI）
                if not hasattr(self, '_last_info_text') or self._last_info_text != info_text:
                    self.info_text.delete("1.0", "end")
                    self.info_text.insert("1.0", info_text)
                    self._last_info_text = info_text

        except Exception as e:
            logger.error(f"更新性能信息失败: {e}")

    def run(self):
        """运行测试应用"""
        try:
            logger.info("开始运行性能系统测试...")
            self.root.mainloop()

        except Exception as e:
            logger.error(f"运行测试应用失败: {e}")

def main():
    """主函数"""
    try:
        # 设置CustomTkinter主题
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # 创建并运行测试应用
        app = PerformanceTestApp()
        app.run()

    except Exception as e:
        logger.error(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()