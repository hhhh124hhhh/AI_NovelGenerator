# ui/components/project_manager.py
# -*- coding: utf-8 -*-
"""
统一项目管理器 - 解决1.0和2.0项目管理差异
结合1.0的简单性和2.0的现代化界面
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime

logger = logging.getLogger(__name__)


class ProjectManager:
    """
    统一项目管理器

    功能：
    - 统一管理项目路径和文件
    - 为所有组件提供统一的项目信息
    - 兼容1.0的简单路径管理和2.0的项目文件管理
    - 自动同步配置和项目状态
    """

    def __init__(self, state_manager=None):
        """
        初始化项目管理器

        Args:
            state_manager: 状态管理器引用
        """
        self.state_manager = state_manager

        # 项目信息
        self.current_project_path = None
        self.project_info = {}
        self.project_files = {}

        # 回调函数
        self.project_changed_callbacks = []

        # 初始化
        self._initialize_project()

    def _initialize_project(self):
        """初始化项目信息"""
        try:
            # 尝试从配置中获取项目路径
            config = self._load_config()

            # 检查配置中的路径设置
            if config and 'other_params' in config and 'filepath' in config['other_params']:
                project_path = config['other_params']['filepath']
                if os.path.exists(project_path):
                    # 智能检测项目目录
                    detected_path = self._detect_project_directory(project_path)
                    if detected_path:
                        self.current_project_path = detected_path
                        logger.info(f"从配置中检测到项目路径: {detected_path}")
                    else:
                        self.current_project_path = project_path
                        logger.info(f"从配置中加载项目路径: {project_path}")

            # 尝试加载最近的快速加载项目
            if not self.current_project_path:
                self._try_load_recent_project()

            # 如果还是没有，尝试智能检测默认目录
            if not self.current_project_path:
                default_path = os.path.join(os.getcwd(), "novel_output")
                if os.path.exists(default_path):
                    detected_path = self._detect_project_directory(default_path)
                    if detected_path:
                        self.current_project_path = detected_path
                        logger.info(f"智能检测到项目路径: {detected_path}")
                    else:
                        self.current_project_path = default_path
                        logger.info(f"使用默认项目路径: {default_path}")
                else:
                    self.current_project_path = default_path
                    logger.info(f"创建并使用默认项目路径: {default_path}")

            # 扫描项目文件
            self._scan_project_files()

        except Exception as e:
            logger.error(f"初始化项目管理器失败: {e}")
            # 回退到默认路径
            self.current_project_path = os.path.join(os.getcwd(), "novel_output")

    def _detect_project_directory(self, base_path: str) -> Optional[str]:
        """
        智能检测项目目录

        Args:
            base_path: 基础路径（如 novel_output）

        Returns:
            检测到的项目路径，如果没有找到则返回None
        """
        try:
            # 首先检查基础路径是否就是项目目录
            if self._is_project_directory(base_path):
                logger.info(f"基础路径本身是项目目录: {base_path}")
                return base_path

            # 如果基础路径存在，检查其子目录
            if os.path.exists(base_path) and os.path.isdir(base_path):
                # 获取所有子目录，按修改时间排序，优先选择最新的
                subdirs = []
                for item in os.listdir(base_path):
                    item_path = os.path.join(base_path, item)
                    if os.path.isdir(item_path):
                        # 检查是否是项目目录
                        if self._is_project_directory(item_path):
                            # 获取修改时间
                            mod_time = os.path.getmtime(item_path)
                            subdirs.append((item_path, mod_time))

                # 按修改时间排序，最新的在前
                subdirs.sort(key=lambda x: x[1], reverse=True)

                if subdirs:
                    latest_project = subdirs[0][0]
                    logger.info(f"检测到最新项目目录: {latest_project}")
                    return latest_project

            return None

        except Exception as e:
            logger.debug(f"项目目录检测失败: {e}")
            return None

    def _is_project_directory(self, path: str) -> bool:
        """
        判断给定路径是否是有效的项目目录

        Args:
            path: 目录路径

        Returns:
            是否是有效的项目目录
        """
        try:
            if not os.path.exists(path) or not os.path.isdir(path):
                return False

            # 检查关键项目文件
            required_files = [
                "Novel_architecture.txt",
                "Novel_directory.txt",
                "character_state.txt"
            ]

            found_files = 0
            for filename in required_files:
                file_path = os.path.join(path, filename)
                if os.path.exists(file_path):
                    found_files += 1

            # 如果找到至少2个关键文件，认为是有效项目目录
            is_valid = found_files >= 2

            if is_valid:
                logger.debug(f"项目目录验证通过: {path} (找到 {found_files}/{len(required_files)} 个关键文件)")

            return is_valid

        except Exception as e:
            logger.debug(f"项目目录验证失败: {e}")
            return False

    def _load_config(self) -> Optional[Dict[str, Any]]:
        """加载配置文件"""
        try:
            from config_manager import load_config
            return load_config("config.json")
        except Exception as e:
            logger.debug(f"加载配置文件失败: {e}")
            return None

    def _try_load_recent_project(self):
        """尝试加载最近的快速加载项目"""
        try:
            recent_file = os.path.join(os.getcwd(), ".recent_project.json")
            if os.path.exists(recent_file):
                with open(recent_file, 'r', encoding='utf-8') as f:
                    recent_data = json.load(f)

                if 'project_path' in recent_data:
                    project_path = recent_data['project_path']
                    if os.path.exists(project_path):
                        self.current_project_path = project_path
                        logger.info(f"加载最近项目: {project_path}")
                        return True
        except Exception as e:
            logger.debug(f"加载最近项目失败: {e}")

        return False

    def _scan_project_files(self):
        """扫描项目文件"""
        if not self.current_project_path:
            return

        try:
            self.project_files = {}

            # 扫描常见的项目文件
            common_files = [
                "Novel_architecture.txt",
                "Novel_directory.txt",
                "character_state.txt",
                "global_summary.txt",
                "project.json"
            ]

            for filename in common_files:
                file_path = os.path.join(self.current_project_path, filename)
                if os.path.exists(file_path):
                    self.project_files[filename] = {
                        'path': file_path,
                        'exists': True,
                        'modified': os.path.getmtime(file_path),
                        'size': os.path.getsize(file_path)
                    }
                else:
                    self.project_files[filename] = {
                        'path': file_path,
                        'exists': False,
                        'modified': None,
                        'size': 0
                    }

            logger.info(f"项目文件扫描完成，找到 {sum(1 for f in self.project_files.values() if f['exists'])} 个文件")

        except Exception as e:
            logger.error(f"扫描项目文件失败: {e}")

    def set_project_path(self, project_path: str):
        """
        设置项目路径

        Args:
            project_path: 新的项目路径
        """
        try:
            # 确保路径存在
            if not os.path.exists(project_path):
                os.makedirs(project_path, exist_ok=True)

            old_path = self.current_project_path
            self.current_project_path = project_path

            # 更新配置
            self._update_config_path()

            # 保存最近项目
            self._save_recent_project()

            # 重新扫描文件
            self._scan_project_files()

            # 通知回调
            self._notify_project_changed(old_path, project_path)

            logger.info(f"项目路径已更新: {old_path} -> {project_path}")

        except Exception as e:
            logger.error(f"设置项目路径失败: {e}")

    def _update_config_path(self):
        """更新配置文件中的路径"""
        try:
            from config_manager import save_config

            config = self._load_config() or {}
            if 'other_params' not in config:
                config['other_params'] = {}

            config['other_params']['filepath'] = self.current_project_path

            save_config(config, "config.json")
            logger.info("配置文件路径已更新")

        except Exception as e:
            logger.error(f"更新配置路径失败: {e}")

    def _save_recent_project(self):
        """保存最近项目信息"""
        try:
            recent_file = os.path.join(os.getcwd(), ".recent_project.json")
            recent_data = {
                'project_path': self.current_project_path,
                'timestamp': datetime.now().isoformat()
            }

            with open(recent_file, 'w', encoding='utf-8') as f:
                json.dump(recent_data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"保存最近项目失败: {e}")

    def get_project_path(self) -> Optional[str]:
        """获取当前项目路径"""
        return self.current_project_path

    def get_file_path(self, filename: str) -> Optional[str]:
        """
        获取项目文件的完整路径

        Args:
            filename: 文件名

        Returns:
            完整的文件路径
        """
        if not self.current_project_path:
            return None

        # 首先尝试当前项目路径
        file_path = os.path.join(self.current_project_path, filename)
        if os.path.exists(file_path):
            return file_path

        # 如果当前路径找不到，尝试智能搜索
        search_paths = self._generate_search_paths(filename)
        for path in search_paths:
            if os.path.exists(path):
                logger.info(f"在智能搜索中找到文件: {path}")
                return path

        # 返回默认路径（即使文件不存在）
        return os.path.join(self.current_project_path, filename)

    def _generate_search_paths(self, filename: str) -> List[str]:
        """
        生成可能的文件搜索路径

        Args:
            filename: 文件名

        Returns:
            可能的文件路径列表
        """
        search_paths = []
        current_dir = os.getcwd()

        # 基于当前项目路径的搜索
        if self.current_project_path:
            search_paths.append(os.path.join(self.current_project_path, filename))

        # 如果当前项目路径在novel_output下，也尝试直接在novel_output中搜索
        if "novel_output" in self.current_project_path:
            novel_output_path = os.path.join(current_dir, "novel_output")
            if novel_output_path != self.current_project_path:
                search_paths.append(os.path.join(novel_output_path, filename))

        # 尝试在所有子目录中搜索
        novel_output_path = os.path.join(current_dir, "novel_output")
        if os.path.exists(novel_output_path):
            for item in os.listdir(novel_output_path):
                item_path = os.path.join(novel_output_path, item)
                if os.path.isdir(item_path):
                    search_paths.append(os.path.join(item_path, filename))

        # 尝试在当前目录直接搜索
        search_paths.append(os.path.join(current_dir, filename))

        # 去重并返回
        return list(dict.fromkeys(search_paths))

    def find_files_smart(self, filename: str) -> List[str]:
        """
        智能查找文件的所有可能位置

        Args:
            filename: 文件名

        Returns:
            找到的文件路径列表
        """
        found_files = []
        search_paths = self._generate_search_paths(filename)

        for path in search_paths:
            if os.path.exists(path):
                found_files.append(path)

        return found_files

    def file_exists(self, filename: str) -> bool:
        """
        检查项目文件是否存在

        Args:
            filename: 文件名

        Returns:
            文件是否存在
        """
        file_path = self.get_file_path(filename)
        return file_path and os.path.exists(file_path)

    def read_file_smart(self, filename: str) -> Optional[str]:
        """
        智能读取文件内容

        Args:
            filename: 文件名

        Returns:
            文件内容，如果读取失败返回None
        """
        try:
            # 首先尝试标准路径
            file_path = self.get_file_path(filename)
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                logger.info(f"成功读取文件: {file_path}")
                return content

            # 如果标准路径找不到，进行智能搜索
            found_files = self.find_files_smart(filename)
            if found_files:
                # 使用第一个找到的文件
                file_path = found_files[0]
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                logger.info(f"通过智能搜索读取文件: {file_path}")
                return content

            logger.warning(f"未找到文件: {filename}")
            return None

        except Exception as e:
            logger.error(f"读取文件失败 {filename}: {e}")
            return None

    def get_project_files(self) -> Dict[str, Dict[str, Any]]:
        """获取项目文件信息"""
        return self.project_files.copy()

    def add_project_changed_callback(self, callback: Callable[[str, str], None]):
        """
        添加项目变更回调

        Args:
            callback: 回调函数，参数为(old_path, new_path)
        """
        self.project_changed_callbacks.append(callback)

    def _notify_project_changed(self, old_path: str, new_path: str):
        """通知项目变更"""
        for callback in self.project_changed_callbacks:
            try:
                callback(old_path, new_path)
            except Exception as e:
                logger.error(f"项目变更回调失败: {e}")

    def create_new_project(self, project_name: str, base_path: Optional[str] = None) -> str:
        """
        创建新项目

        Args:
            project_name: 项目名称
            base_path: 基础路径，如果为None则使用当前目录

        Returns:
            新项目路径
        """
        try:
            if base_path is None:
                base_path = os.getcwd()

            # 清理项目名称
            safe_name = "".join(c for c in project_name if c.isalnum() or c in (' ', '-', '_')).strip()
            if not safe_name:
                safe_name = f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            project_path = os.path.join(base_path, safe_name)

            # 创建项目目录
            os.makedirs(project_path, exist_ok=True)

            # 设置为当前项目
            self.set_project_path(project_path)

            logger.info(f"新项目创建成功: {project_path}")
            return project_path

        except Exception as e:
            logger.error(f"创建新项目失败: {e}")
            raise

    def load_project(self, project_path: str) -> bool:
        """
        加载项目

        Args:
            project_path: 项目路径

        Returns:
            是否加载成功
        """
        try:
            if not os.path.exists(project_path):
                logger.error(f"项目路径不存在: {project_path}")
                return False

            self.set_project_path(project_path)
            logger.info(f"项目加载成功: {project_path}")
            return True

        except Exception as e:
            logger.error(f"加载项目失败: {e}")
            return False

    def save_project_info(self, project_info: Dict[str, Any]):
        """
        保存项目信息

        Args:
            project_info: 项目信息
        """
        try:
            project_file = self.get_file_path("project.json")
            if project_file:
                with open(project_file, 'w', encoding='utf-8') as f:
                    json.dump(project_info, f, ensure_ascii=False, indent=2)

                self.project_info = project_info
                logger.info("项目信息已保存")

        except Exception as e:
            logger.error(f"保存项目信息失败: {e}")

    def load_project_info(self) -> Dict[str, Any]:
        """
        加载项目信息

        Returns:
            项目信息
        """
        try:
            project_file = self.get_file_path("project.json")
            if project_file and os.path.exists(project_file):
                with open(project_file, 'r', encoding='utf-8') as f:
                    self.project_info = json.load(f)
                return self.project_info
            else:
                return {}

        except Exception as e:
            logger.error(f"加载项目信息失败: {e}")
            return {}

    def get_project_status(self) -> Dict[str, Any]:
        """
        获取项目状态

        Returns:
            项目状态信息
        """
        return {
            'project_path': self.current_project_path,
            'project_name': os.path.basename(self.current_project_path) if self.current_project_path else None,
            'files': self.project_files,
            'total_files': sum(1 for f in self.project_files.values() if f['exists']),
            'is_valid': self.current_project_path and os.path.exists(self.current_project_path)
        }

    def validate_project(self) -> Dict[str, Any]:
        """
        验证项目状态并返回详细信息

        Returns:
            项目验证结果
        """
        result = {
            'is_valid': False,
            'project_path': self.current_project_path,
            'issues': [],
            'recommendations': [],
            'found_files': {},
            'missing_files': []
        }

        if not self.current_project_path:
            result['issues'].append("未设置项目路径")
            result['recommendations'].append("请在主页设置保存路径或打开现有项目")
            return result

        if not os.path.exists(self.current_project_path):
            result['issues'].append(f"项目路径不存在: {self.current_project_path}")
            result['recommendations'].append("请检查路径设置或创建新项目")
            return result

        # 检查关键文件
        key_files = ["Novel_architecture.txt", "Novel_directory.txt", "character_state.txt"]
        for filename in key_files:
            file_path = self.get_file_path(filename)
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                result['found_files'][filename] = {
                    'path': file_path,
                    'size': file_size,
                    'exists': True
                }
            else:
                result['missing_files'].append(filename)

        # 判断项目有效性
        found_count = len(result['found_files'])
        if found_count >= 2:
            result['is_valid'] = True
            result['recommendations'].append("项目状态良好，所有功能可用")
        elif found_count == 1:
            result['recommendations'].append("项目部分完整，建议生成缺失的文件")
        else:
            result['issues'].append("项目不完整，缺少关键文件")
            result['recommendations'].append("建议先生成小说架构和目录文件")

        return result

    def get_project_info_detailed(self) -> Dict[str, Any]:
        """
        获取详细的项目信息，用于诊断

        Returns:
            详细项目信息
        """
        info = {
            'current_path': self.current_project_path,
            'base_directory': os.getcwd(),
            'available_projects': [],
            'file_search_results': {},
            'project_found': bool(self.current_project_path),
            'project_name': os.path.basename(self.current_project_path) if self.current_project_path else '未知项目',
            'file_count': len(self.project_files)
        }

        # 扫描可用项目
        try:
            novel_output_path = os.path.join(os.getcwd(), "novel_output")
            if os.path.exists(novel_output_path):
                for item in os.listdir(novel_output_path):
                    item_path = os.path.join(novel_output_path, item)
                    if os.path.isdir(item_path) and self._is_project_directory(item_path):
                        info['available_projects'].append({
                            'name': item,
                            'path': item_path,
                            'modified': os.path.getmtime(item_path)
                        })

            # 按修改时间排序
            info['available_projects'].sort(key=lambda x: x['modified'], reverse=True)

        except Exception as e:
            logger.debug(f"扫描可用项目失败: {e}")

        # 搜索关键文件
        for filename in ["character_state.txt", "Novel_directory.txt", "Novel_architecture.txt"]:
            found_files = self.find_files_smart(filename)
            info['file_search_results'][filename] = found_files

        return info


# 全局项目管理器实例
_project_manager = None


def get_project_manager(state_manager=None) -> ProjectManager:
    """
    获取全局项目管理器实例

    Args:
        state_manager: 状态管理器

    Returns:
        项目管理器实例
    """
    global _project_manager
    if _project_manager is None:
        _project_manager = ProjectManager(state_manager)
    return _project_manager


def initialize_project_manager(state_manager=None):
    """
    初始化项目管理器

    Args:
        state_manager: 状态管理器
    """
    global _project_manager
    _project_manager = ProjectManager(state_manager)