"""
性能监控器 - AI小说生成器的性能优化系统
监控UI性能、内存使用、渲染性能等指标，提供优化建议
"""

import logging
import time
import psutil
import threading
import gc
from typing import Dict, Any, Optional, List, Callable
from collections import deque
from dataclasses import dataclass
from enum import Enum
import customtkinter as ctk

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """性能指标类型"""
    MEMORY = "memory"
    CPU = "cpu"
    RENDER_TIME = "render_time"
    ANIMATION_TIME = "animation_time"
    UI_RESPONSE = "ui_response"
    GC_COUNT = "gc_count"


@dataclass
class PerformanceMetric:
    """性能指标数据"""
    name: str
    value: float
    unit: str
    timestamp: float
    category: MetricType


class PerformanceMonitor:
    """
    性能监控器

    功能：
    - 内存使用监控
    - CPU使用率监控
    - UI渲染性能监控
    - 动画性能监控
    - 垃圾回收监控
    - 性能报告生成
    - 自动优化建议
    """

    def __init__(self, root_widget: ctk.CTkBaseClass, max_history: int = 100):
        """
        初始化性能监控器

        Args:
            root_widget: 根组件
            max_history: 最大历史记录数
        """
        self.root_widget = root_widget
        self.max_history = max_history

        # 监控状态 - 修复监控频率问题
        self.is_monitoring = False
        self.monitor_thread = None
        self.monitor_interval = 5.0  # 监控间隔（秒）- 从1秒调整为5秒

        # 性能数据存储
        self.metrics_history = {
            MetricType.MEMORY: deque(maxlen=max_history),
            MetricType.CPU: deque(maxlen=max_history),
            MetricType.RENDER_TIME: deque(maxlen=max_history),
            MetricType.ANIMATION_TIME: deque(maxlen=max_history),
            MetricType.UI_RESPONSE: deque(maxlen=max_history),
            MetricType.GC_COUNT: deque(maxlen=max_history)
        }

        # 性能阈值 - 修复阈值过低问题
        self.performance_thresholds = {
            MetricType.MEMORY: 500 * 1024 * 1024,  # 500MB (从200MB提高)
            MetricType.CPU: 90.0,  # 90% (从80%提高)
            MetricType.RENDER_TIME: 200.0,  # 200ms (从100ms提高)
            MetricType.ANIMATION_TIME: 100.0,  # 100ms (从50ms提高)
            MetricType.UI_RESPONSE: 300.0,  # 300ms (从200ms提高)
            MetricType.GC_COUNT: 20  # 20次/分钟 (从10次提高)
        }

        # 警告控制
        self.warning_cooldown = 30.0  # 警告冷却时间（秒）
        self.last_warning_time = {}

        # 回调函数
        self.performance_warning_callbacks = []
        self.optimization_callbacks = []

        # 性能计时器
        self.timers = {}
        self.render_start_time = None

        logger.debug("PerformanceMonitor 初始化完成")

    def start_monitoring(self):
        """开始性能监控"""
        if self.is_monitoring:
            logger.warning("性能监控已在运行")
            return

        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()

        logger.info("性能监控已启动")

    def stop_monitoring(self):
        """停止性能监控"""
        if not self.is_monitoring:
            return

        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)

        logger.info("性能监控已停止")

    def start_timer(self, name: str):
        """开始计时"""
        self.timers[name] = time.time()

    def end_timer(self, name: str) -> float:
        """结束计时并返回耗时"""
        if name not in self.timers:
            logger.warning(f"计时器 {name} 不存在")
            return 0.0

        elapsed = time.time() - self.timers[name]
        del self.timers[name]

        # 记录性能指标
        if name == "render":
            self._add_metric(MetricType.RENDER_TIME, elapsed * 1000, "ms")
        elif name == "animation":
            self._add_metric(MetricType.ANIMATION_TIME, elapsed * 1000, "ms")
        elif name == "ui_response":
            self._add_metric(MetricType.UI_RESPONSE, elapsed * 1000, "ms")

        return elapsed

    def measure_render_performance(self, render_func: Callable, *args, **kwargs):
        """测量渲染性能"""
        self.start_timer("render")
        try:
            result = render_func(*args, **kwargs)
            return result
        finally:
            self.end_timer("render")

    def measure_animation_performance(self, animation_func: Callable, *args, **kwargs):
        """测量动画性能"""
        self.start_timer("animation")
        try:
            result = animation_func(*args, **kwargs)
            return result
        finally:
            self.end_timer("animation")

    def measure_ui_response(self, ui_func: Callable, *args, **kwargs):
        """测量UI响应性能"""
        self.start_timer("ui_response")
        try:
            result = ui_func(*args, **kwargs)
            return result
        finally:
            self.end_timer("ui_response")

    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        summary = {}

        for metric_type, history in self.metrics_history.items():
            if not history:
                continue

            values = [metric.value for metric in history]
            summary[metric_type.value] = {
                'current': values[-1] if values else 0,
                'average': sum(values) / len(values),
                'min': min(values),
                'max': max(values),
                'count': len(values),
                'unit': history[-1].unit if history else ""
            }

        return summary

    def get_optimization_suggestions(self) -> List[str]:
        """获取优化建议"""
        suggestions = []
        summary = self.get_performance_summary()

        # 内存优化建议
        if 'memory' in summary:
            current_memory = summary['memory']['current']
            if current_memory > self.performance_thresholds[MetricType.MEMORY]:
                suggestions.append(f"内存使用过高 ({current_memory/1024/1024:.1f}MB)，建议清理缓存或重启应用")

        # CPU优化建议
        if 'cpu' in summary:
            avg_cpu = summary['cpu']['average']
            if avg_cpu > self.performance_thresholds[MetricType.CPU]:
                suggestions.append(f"CPU使用率过高 ({avg_cpu:.1f}%)，建议减少后台任务或优化算法")

        # 渲染性能建议
        if 'render_time' in summary:
            avg_render = summary['render_time']['average']
            if avg_render > self.performance_thresholds[MetricType.RENDER_TIME]:
                suggestions.append(f"渲染时间过长 ({avg_render:.1f}ms)，建议优化UI组件或减少复杂动画")

        # 动画性能建议
        if 'animation_time' in summary:
            avg_animation = summary['animation_time']['average']
            if avg_animation > self.performance_thresholds[MetricType.ANIMATION_TIME]:
                suggestions.append(f"动画性能不佳 ({avg_animation:.1f}ms)，建议简化动画效果")

        # UI响应建议
        if 'ui_response' in summary:
            avg_response = summary['ui_response']['average']
            if avg_response > self.performance_thresholds[MetricType.UI_RESPONSE]:
                suggestions.append(f"UI响应较慢 ({avg_response:.1f}ms)，建议优化事件处理逻辑")

        return suggestions

    def optimize_memory(self):
        """内存优化"""
        try:
            # 强制垃圾回收
            collected = gc.collect()

            # 记录垃圾回收
            self._add_metric(MetricType.GC_COUNT, collected, "count")

            logger.info(f"内存优化完成，回收了 {collected} 个对象")
            return collected

        except Exception as e:
            logger.error(f"内存优化失败: {e}")
            return 0

    def optimize_ui_components(self):
        """UI组件优化"""
        try:
            optimized_count = 0

            def optimize_widget(widget):
                nonlocal optimized_count
                try:
                    # 清理不可见的组件
                    if widget.winfo_exists() and not widget.winfo_viewable():
                        if hasattr(widget, 'pack_forget'):
                            widget.pack_forget()
                        optimized_count += 1

                    # 递归优化子组件
                    for child in widget.winfo_children():
                        optimize_widget(child)
                except:
                    pass

            # 优化根组件
            if self.root_widget.winfo_exists():
                optimize_widget(self.root_widget)

            logger.info(f"UI组件优化完成，优化了 {optimized_count} 个组件")
            return optimized_count

        except Exception as e:
            logger.error(f"UI组件优化失败: {e}")
            return 0

    def add_performance_warning_callback(self, callback: Callable[[str, float], None]):
        """添加性能警告回调"""
        self.performance_warning_callbacks.append(callback)

    def add_optimization_callback(self, callback: Callable[[], None]):
        """添加优化回调"""
        self.optimization_callbacks.append(callback)

    def _monitoring_loop(self):
        """监控循环"""
        while self.is_monitoring:
            try:
                # 监控内存使用
                process = psutil.Process()
                memory_info = process.memory_info()
                memory_usage = memory_info.rss
                self._add_metric(MetricType.MEMORY, memory_usage, "bytes")

                # 监控CPU使用率
                cpu_percent = process.cpu_percent()
                self._add_metric(MetricType.CPU, cpu_percent, "%")

                # 检查性能阈值
                self._check_performance_thresholds()

                # 等待下一次监控
                time.sleep(self.monitor_interval)

            except Exception as e:
                logger.error(f"监控循环错误: {e}")
                time.sleep(self.monitor_interval)

    def _add_metric(self, metric_type: MetricType, value: float, unit: str):
        """添加性能指标"""
        metric = PerformanceMetric(
            name=metric_type.value,
            value=value,
            unit=unit,
            timestamp=time.time(),
            category=metric_type
        )
        self.metrics_history[metric_type].append(metric)

    def _check_performance_thresholds(self):
        """检查性能阈值"""
        current_metrics = {}

        # 获取当前指标值
        for metric_type, history in self.metrics_history.items():
            if history:
                current_metrics[metric_type] = history[-1].value

        # 检查阈值并触发警告
        for metric_type, threshold in self.performance_thresholds.items():
            if metric_type in current_metrics:
                current_value = current_metrics[metric_type]
                if current_value > threshold:
                    self._trigger_performance_warning(metric_type, current_value)

    def _trigger_performance_warning(self, metric_type: MetricType, value: float):
        """触发性能警告 - 添加冷却机制"""
        current_time = time.time()

        # 检查冷却时间
        if metric_type in self.last_warning_time:
            time_since_last = current_time - self.last_warning_time[metric_type]
            if time_since_last < self.warning_cooldown:
                # 在冷却期内，不触发警告
                return

        # 更新最后警告时间
        self.last_warning_time[metric_type] = current_time

        warning_message = f"性能警告: {metric_type.value} 超过阈值 ({value})"
        logger.warning(warning_message)

        # 调用警告回调
        for callback in self.performance_warning_callbacks:
            try:
                callback(metric_type.value, value)
            except Exception as e:
                logger.error(f"性能警告回调失败: {e}")

        # 自动优化 - 降低频率
        if metric_type == MetricType.MEMORY:
            # 只有在内存使用严重超标时才优化
            if value > self.performance_thresholds[metric_type] * 1.5:
                self.optimize_memory()
        elif metric_type == MetricType.RENDER_TIME:
            # 渲染时间超标时优化
            self.optimize_ui_components()

    def get_performance_report(self) -> str:
        """生成性能报告"""
        summary = self.get_performance_summary()
        suggestions = self.get_optimization_suggestions()

        report = "📊 性能监控报告\n"
        report += "=" * 50 + "\n\n"

        # 性能指标
        for metric_name, data in summary.items():
            report += f"🔍 {metric_name.upper()}:\n"
            report += f"  当前值: {data['current']:.2f} {data['unit']}\n"
            report += f"  平均值: {data['average']:.2f} {data['unit']}\n"
            report += f"  最小值: {data['min']:.2f} {data['unit']}\n"
            report += f"  最大值: {data['max']:.2f} {data['unit']}\n"
            report += f"  样本数: {data['count']}\n\n"

        # 优化建议
        if suggestions:
            report += "💡 优化建议:\n"
            for i, suggestion in enumerate(suggestions, 1):
                report += f"  {i}. {suggestion}\n"
            report += "\n"

        # 性能评分
        score = self._calculate_performance_score(summary)
        report += f"🏆 性能评分: {score}/100\n"

        return report

    def _calculate_performance_score(self, summary: Dict[str, Any]) -> int:
        """计算性能评分"""
        score = 100

        # 内存评分 (权重: 20%)
        if 'memory' in summary:
            memory_usage = summary['memory']['current']
            memory_score = max(0, 100 - (memory_usage / (1024 * 1024 * 100)))  # 每100MB扣1分
            score = score * 0.8 + memory_score * 0.2

        # CPU评分 (权重: 20%)
        if 'cpu' in summary:
            cpu_usage = summary['cpu']['average']
            cpu_score = max(0, 100 - cpu_usage)  # 每1%扣1分
            score = score * 0.8 + cpu_score * 0.2

        # 渲染性能评分 (权重: 30%)
        if 'render_time' in summary:
            render_time = summary['render_time']['average']
            render_score = max(0, 100 - (render_time / 2))  # 每2ms扣1分
            score = score * 0.7 + render_score * 0.3

        # UI响应评分 (权重: 30%)
        if 'ui_response' in summary:
            ui_response = summary['ui_response']['average']
            ui_score = max(0, 100 - (ui_response / 5))  # 每5ms扣1分
            score = score * 0.7 + ui_score * 0.3

        return int(score)


class PerformanceProfiler:
    """性能分析器 - 用于深入分析特定功能的性能"""

    def __init__(self):
        """初始化性能分析器"""
        self.profiles = {}
        self.active_profiling = {}

    def start_profiling(self, name: str):
        """开始性能分析"""
        self.active_profiling[name] = {
            'start_time': time.time(),
            'start_memory': psutil.Process().memory_info().rss,
            'events': []
        }

    def record_event(self, name: str, event: str):
        """记录事件"""
        if name in self.active_profiling:
            self.active_profiling[name]['events'].append({
                'event': event,
                'timestamp': time.time()
            })

    def end_profiling(self, name: str) -> Dict[str, Any]:
        """结束性能分析"""
        if name not in self.active_profiling:
            return {}

        profile_data = self.active_profiling[name]
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss

        profile = {
            'name': name,
            'duration': end_time - profile_data['start_time'],
            'memory_delta': end_memory - profile_data['start_memory'],
            'events': profile_data['events'],
            'end_time': end_time
        }

        self.profiles[name] = profile
        del self.active_profiling[name]

        return profile

    def get_profile_summary(self, name: str) -> str:
        """获取分析摘要"""
        if name not in self.profiles:
            return f"未找到分析数据: {name}"

        profile = self.profiles[name]
        summary = f"📈 性能分析报告: {name}\n"
        summary += "=" * 40 + "\n"
        summary += f"⏱️ 执行时间: {profile['duration']:.3f} 秒\n"
        summary += f"💾 内存变化: {profile['memory_delta'] / 1024:.1f} KB\n"
        summary += f"📅 结束时间: {time.ctime(profile['end_time'])}\n"

        if profile['events']:
            summary += "\n🔍 事件序列:\n"
            for i, event in enumerate(profile['events'], 1):
                event_time = event['timestamp'] - profile_data['start_time']
                summary += f"  {i}. {event['event']} (+{event_time:.3f}s)\n"

        return summary