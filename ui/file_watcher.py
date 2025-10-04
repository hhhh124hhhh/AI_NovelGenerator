"""
文件监控器 - 监控文件夹中的文件变化并通知相关组件更新
"""

import os
import time
import threading
from typing import Dict, Any, Callable, Optional, List
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class FileWatcher:
    """
    文件监控器

    功能：
    - 监控指定文件夹中的文件变化
    - 通知相关组件更新显示内容
    - 支持多种文件类型监控
    """

    def __init__(self, watch_interval: float = 2.0):
        """
        初始化文件监控器

        Args:
            watch_interval: 监控间隔（秒）
        """
        self.watch_interval = watch_interval
        self.watched_paths: Dict[str, Dict[str, float]] = defaultdict(dict)  # {path: {filename: mtime}}
        self.callbacks: Dict[str, List[Callable[[str, str], None]]] = defaultdict(list)  # {path: [callback]}
        self.is_watching = False
        self.watch_thread: Optional[threading.Thread] = None

    def add_watch_path(self, path: str, callback: Optional[Callable[[str, str], None]] = None) -> None:
        """
        添加监控路径

        Args:
            path: 要监控的文件夹路径
            callback: 文件变化回调函数，参数为 (filepath, change_type)
        """
        if not os.path.exists(path):
            logger.warning(f"监控路径不存在: {path}")
            return

        # 记录当前文件的修改时间
        self._scan_path(path)
        
        # 添加回调函数
        if callback:
            self.callbacks[path].append(callback)
            
        logger.info(f"添加文件监控路径: {path}")

    def remove_watch_path(self, path: str) -> None:
        """
        移除监控路径

        Args:
            path: 要移除的监控路径
        """
        if path in self.watched_paths:
            del self.watched_paths[path]
        if path in self.callbacks:
            del self.callbacks[path]
            
        logger.info(f"移除文件监控路径: {path}")

    def start_watching(self) -> None:
        """开始监控"""
        if self.is_watching:
            logger.warning("文件监控已在运行")
            return

        self.is_watching = True
        self.watch_thread = threading.Thread(target=self._watch_loop, daemon=True)
        self.watch_thread.start()
        
        logger.info("文件监控已启动")

    def stop_watching(self) -> None:
        """停止监控"""
        if not self.is_watching:
            return

        self.is_watching = False
        if self.watch_thread:
            self.watch_thread.join(timeout=2.0)
            
        logger.info("文件监控已停止")

    def _scan_path(self, path: str) -> None:
        """扫描路径中的文件并记录修改时间"""
        try:
            if not os.path.exists(path):
                return
                
            if os.path.isfile(path):
                # 单个文件
                mtime = os.path.getmtime(path)
                self.watched_paths[os.path.dirname(path)][os.path.basename(path)] = mtime
            else:
                # 文件夹
                for filename in os.listdir(path):
                    filepath = os.path.join(path, filename)
                    if os.path.isfile(filepath):
                        mtime = os.path.getmtime(filepath)
                        self.watched_paths[path][filename] = mtime
                        
        except Exception as e:
            logger.error(f"扫描路径失败 {path}: {e}")

    def _watch_loop(self) -> None:
        """监控循环"""
        while self.is_watching:
            try:
                self._check_file_changes()
                time.sleep(self.watch_interval)
            except Exception as e:
                logger.error(f"文件监控循环错误: {e}")
                time.sleep(self.watch_interval)

    def _check_file_changes(self) -> None:
        """检查文件变化"""
        for path, files in self.watched_paths.items():
            try:
                if not os.path.exists(path):
                    continue
                    
                # 获取当前文件状态
                current_files = {}
                for filename in os.listdir(path):
                    filepath = os.path.join(path, filename)
                    if os.path.isfile(filepath):
                        current_files[filename] = os.path.getmtime(filepath)
                
                # 检查新增文件
                for filename, mtime in current_files.items():
                    if filename not in files:
                        self._notify_file_change(path, filename, "created")
                        files[filename] = mtime
                    elif files[filename] != mtime:
                        self._notify_file_change(path, filename, "modified")
                        files[filename] = mtime
                
                # 检查删除文件
                for filename in list(files.keys()):
                    if filename not in current_files:
                        self._notify_file_change(path, filename, "deleted")
                        del files[filename]
                        
            except Exception as e:
                logger.error(f"检查文件变化失败 {path}: {e}")

    def _notify_file_change(self, path: str, filename: str, change_type: str) -> None:
        """
        通知文件变化

        Args:
            path: 文件路径
            filename: 文件名
            change_type: 变化类型 (created, modified, deleted)
        """
        filepath = os.path.join(path, filename)
        logger.info(f"文件变化: {filepath} ({change_type})")
        
        # 调用回调函数
        if path in self.callbacks:
            for callback in self.callbacks[path]:
                try:
                    callback(filepath, change_type)
                except Exception as e:
                    logger.error(f"文件变化回调失败: {e}")


# 全局文件监控器实例
_file_watcher = FileWatcher()


def get_file_watcher() -> FileWatcher:
    """获取文件监控器实例"""
    return _file_watcher