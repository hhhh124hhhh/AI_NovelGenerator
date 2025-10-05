# ui/project_manager.py
# -*- coding: utf-8 -*-
"""
现代化项目管理器
采用BMAD方法重构的项目管理系统
"""

import os
import json
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class ProjectManager:
    """现代化项目管理器"""

    def __init__(self):
        self.current_project = None
        self.project_history = []
        self.detection_patterns = self._get_detection_patterns()

    def _get_detection_patterns(self) -> List[Dict[str, Any]]:
        """获取项目检测模式"""
        return [
            {
                "name": "modern_project",
                "priority": 1,
                "required_files": [".project/project.json"],
                "optional_files": [
                    "Novel_architecture.txt",
                    "Novel_directory.txt",
                    "Novel_setting.txt",
                    "character_state.txt"
                ]
            },
            {
                "name": "legacy_complete",
                "priority": 2,
                "required_files": ["Novel_architecture.txt"],
                "optional_files": [
                    "Novel_directory.txt",
                    "Novel_setting.txt",
                    "character_state.txt",
                    "global_summary.txt"
                ]
            },
            {
                "name": "legacy_basic",
                "priority": 3,
                "required_files": ["Novel_setting.txt"],
                "optional_files": [
                    "character_state.txt",
                    "global_summary.txt"
                ]
            },
            {
                "name": "minimal_project",
                "priority": 4,
                "required_files": [],  # 不要求任何特定文件
                "optional_files": [
                    "*.txt",
                    "*.md",
                    "*.json"
                ]
            }
        ]

    def detect_project_type(self, path: str) -> Optional[Dict[str, Any]]:
        """智能检测项目类型"""
        if not os.path.exists(path):
            return None

        found_files = []
        all_files = []

        # 扫描所有文件
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(('.txt', '.md', '.json')):
                    all_files.append(file)

        # 按优先级检测项目类型
        for pattern in self.detection_patterns:
            required_found = 0
            required_total = len(pattern["required_files"])

            # 检查必需文件
            for required_file in pattern["required_files"]:
                if os.path.exists(os.path.join(path, required_file)):
                    required_found += 1

            # 检查可选文件
            optional_found = 0
            for optional_file in pattern["optional_files"]:
                if "*" in optional_file:
                    # 处理通配符
                    if any(optional_file.replace("*", "") in f for f in all_files):
                        optional_found += 1
                else:
                    if os.path.exists(os.path.join(path, optional_file)):
                        optional_found += 1

            # 评分：必需文件权重更高
            score = (required_found * 10) + optional_found

            if required_found == required_total or score >= 2:
                return {
                    "type": pattern["name"],
                    "priority": pattern["priority"],
                    "score": score,
                    "required_files": required_found,
                    "optional_files": optional_found,
                    "total_files": len(all_files),
                    "found_files": all_files[:10]  # 只返回前10个文件名
                }

        # 如果没有匹配任何模式，但有文本文件，返回最小项目类型
        if all_files:
            return {
                "type": "text_files_only",
                "priority": 5,
                "score": 1,
                "required_files": 0,
                "optional_files": len(all_files),
                "total_files": len(all_files),
                "found_files": all_files[:10]
            }

        return None

    def validate_project_directory(self, path: str) -> Dict[str, Any]:
        """验证项目目录"""
        result = {
            "is_valid": False,
            "project_type": None,
            "issues": [],
            "found_files": [],
            "recommendations": []
        }

        if not os.path.exists(path):
            result["issues"].append("目录不存在")
            return result

        if not os.path.isdir(path):
            result["issues"].append("路径不是目录")
            return result

        # 检查权限
        if not os.access(path, os.R_OK):
            result["issues"].append("目录没有读取权限")
            return result

        if not os.access(path, os.W_OK):
            result["issues"].append("目录没有写入权限")
            result["recommendations"].append("检查目录权限设置")

        # 检测项目类型
        project_info = self.detect_project_type(path)
        if project_info:
            result["is_valid"] = True
            result["project_type"] = project_info
            result["found_files"] = project_info["found_files"]

            if project_info["score"] < 3:
                result["recommendations"].append("项目文件较少，建议添加更多内容文件")
        else:
            result["issues"].append("未检测到有效的项目文件")
            result["recommendations"].append("请选择包含小说文件的目录")

        return result

    def get_project_files(self, path: str) -> List[str]:
        """获取项目中的所有相关文件"""
        project_files = []

        if not os.path.exists(path):
            return project_files

        # 定义要查找的文件模式
        file_patterns = [
            "Novel_architecture.txt",
            "Novel_directory.txt",
            "Novel_setting.txt",
            "character_state.txt",
            "global_summary.txt",
            "*.txt",
            "*.md",
            "*.json"
        ]

        for pattern in file_patterns:
            if "*" in pattern:
                # 处理通配符
                base_pattern = pattern.replace("*", "")
                for file in os.listdir(path):
                    if base_pattern in file and file.endswith(('.txt', '.md', '.json')):
                        full_path = os.path.join(path, file)
                        if os.path.isfile(full_path):
                            project_files.append(file)
            else:
                full_path = os.path.join(path, pattern)
                if os.path.isfile(full_path):
                    project_files.append(pattern)

        return list(set(project_files))  # 去重

    def create_project_metadata(self, name: str, path: str) -> Dict[str, Any]:
        """创建项目元数据"""
        return {
            "project_info": {
                "name": name,
                "version": "1.0.0",
                "created_at": datetime.now().isoformat(),
                "last_modified": datetime.now().isoformat(),
                "created_by": "AI_NovelGenerator"
            },
            "project_settings": {
                "save_path": path,
                "auto_save": True,
                "backup_enabled": True,
                "last_backup": None
            },
            "content_structure": {
                "has_architecture": False,
                "has_directory": False,
                "has_setting": False,
                "has_characters": False,
                "chapters_count": 0
            }
        }

    def update_project_metadata(self, path: str, metadata: Dict[str, Any]) -> bool:
        """更新项目元数据"""
        try:
            metadata_path = os.path.join(path, ".project")
            os.makedirs(metadata_path, exist_ok=True)

            metadata_file = os.path.join(metadata_path, "project.json")

            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

            return True
        except Exception as e:
            logger.error(f"更新项目元数据失败: {e}")
            return False

    def load_project_metadata(self, path: str) -> Optional[Dict[str, Any]]:
        """加载项目元数据"""
        try:
            metadata_file = os.path.join(path, ".project", "project.json")

            if os.path.exists(metadata_file):
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # 如果没有元数据文件，创建默认元数据
                project_name = os.path.basename(path)
                return self.create_project_metadata(project_name, path)
        except Exception as e:
            logger.error(f"加载项目元数据失败: {e}")
            return None

    def normalize_path(self, path: str) -> str:
        """标准化路径"""
        return os.path.normpath(os.path.abspath(path))

    def is_valid_project_path(self, path: str) -> bool:
        """检查是否为有效的项目路径"""
        try:
            path = self.normalize_path(path)
            return os.path.exists(path) and os.path.isdir(path)
        except Exception:
            return False

    def get_project_summary(self, path: str) -> Dict[str, Any]:
        """获取项目摘要信息"""
        summary = {
            "name": os.path.basename(path),
            "path": path,
            "file_count": 0,
            "file_types": {},
            "last_modified": None,
            "estimated_size": 0
        }

        try:
            if os.path.exists(path):
                # 获取最后修改时间
                summary["last_modified"] = datetime.fromtimestamp(
                    os.path.getmtime(path)
                ).strftime("%Y-%m-%d %H:%M:%S")

                # 统计文件
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if file.endswith(('.txt', '.md', '.json')):
                            summary["file_count"] += 1

                            # 统计文件类型
                            ext = os.path.splitext(file)[1].lower()
                            summary["file_types"][ext] = summary["file_types"].get(ext, 0) + 1

                            # 估算大小
                            try:
                                file_path = os.path.join(root, file)
                                summary["estimated_size"] += os.path.getsize(file_path)
                            except:
                                pass

        except Exception as e:
            logger.error(f"获取项目摘要失败: {e}")

        return summary