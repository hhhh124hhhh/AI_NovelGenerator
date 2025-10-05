# ui/data_bridge.py
# -*- coding: utf-8 -*-
"""
UI数据桥接器 - BMAD方法的Bridge组件
解决UI 2.0各组件间的数据同步问题
"""

import logging
import json
import os
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime

logger = logging.getLogger(__name__)


class DataBridge:
    """
    UI数据桥接器

    功能：
    - 统一的数据接口
    - 组件间数据同步
    - 状态变化监听
    - 数据格式转换
    """

    def __init__(self):
        """初始化数据桥接器"""
        # 数据存储
        self._data = {
            'characters': [],
            'settings': {},
            'theme': {},
            'novel_info': {},
            'ui_state': {}
        }

        # 监听器注册
        self._listeners = {
            'characters': [],
            'settings': [],
            'theme': [],
            'novel_info': [],
            'ui_state': []
        }

        # 数据转换器
        self._converters = {}

        logger.debug("DataBridge 初始化完成")

    def register_listener(self, data_type: str, callback: Callable[[Dict[str, Any]], None]):
        """
        注册数据变化监听器

        Args:
            data_type: 数据类型 ('characters', 'settings', 'theme', 'novel_info', 'ui_state')
            callback: 回调函数，接收数据变化通知
        """
        if data_type in self._listeners:
            self._listeners[data_type].append(callback)
            logger.debug(f"注册 {data_type} 监听器")

    def unregister_listener(self, data_type: str, callback: Callable):
        """
        注销数据变化监听器

        Args:
            data_type: 数据类型
            callback: 要注销的回调函数
        """
        if data_type in self._listeners and callback in self._listeners[data_type]:
            self._listeners[data_type].remove(callback)
            logger.debug(f"注销 {data_type} 监听器")

    def update_data(self, data_type: str, data: Any, notify: bool = True):
        """
        更新数据并通知监听器

        Args:
            data_type: 数据类型
            data: 新数据
            notify: 是否通知监听器
        """
        old_data = self._data.get(data_type)
        self._data[data_type] = data

        logger.debug(f"更新 {data_type} 数据")

        if notify and old_data != data:
            self._notify_listeners(data_type, data)

    def get_data(self, data_type: str) -> Any:
        """
        获取数据

        Args:
            data_type: 数据类型

        Returns:
            对应类型的数据
        """
        return self._data.get(data_type)

    def _notify_listeners(self, data_type: str, data: Any):
        """
        通知所有监听器

        Args:
            data_type: 数据类型
            data: 数据
        """
        if data_type in self._listeners:
            for callback in self._listeners[data_type]:
                try:
                    callback(data)
                except Exception as e:
                    logger.error(f"监听器回调失败: {e}")

    def convert_character_data(self, raw_data: Any) -> List[Dict[str, Any]]:
        """
        转换角色数据格式

        Args:
            raw_data: 原始角色数据

        Returns:
            标准化的角色数据列表
        """
        if isinstance(raw_data, str):
            # 如果是字符串，尝试解析为JSON
            try:
                parsed_data = json.loads(raw_data)
                return self._normalize_character_data(parsed_data)
            except json.JSONDecodeError:
                # 如果不是JSON，按行分割
                lines = raw_data.strip().split('\n')
                characters = []
                for line in lines:
                    if line.strip():
                        characters.append({
                            'id': len(characters) + 1,
                            'name': line.strip(),
                            'description': '',
                            'traits': [],
                            'background': '',
                            'created_at': datetime.now().isoformat()
                        })
                return characters
        elif isinstance(raw_data, list):
            return self._normalize_character_data(raw_data)
        elif isinstance(raw_data, dict):
            return [self._normalize_character_data(raw_data)]
        else:
            logger.warning(f"未知的角色数据格式: {type(raw_data)}")
            return []

    def _normalize_character_data(self, data: Any) -> List[Dict[str, Any]]:
        """
        标准化角色数据

        Args:
            data: 原始数据

        Returns:
            标准化的角色数据列表
        """
        if isinstance(data, dict):
            data = [data]

        normalized = []
        for i, char in enumerate(data):
            if isinstance(char, dict):
                normalized_char = {
                    'id': char.get('id', i + 1),
                    'name': char.get('name', f'角色{i + 1}'),
                    'description': char.get('description', ''),
                    'traits': char.get('traits', []),
                    'background': char.get('background', ''),
                    'personality': char.get('personality', ''),
                    'appearance': char.get('appearance', ''),
                    'relationships': char.get('relationships', {}),
                    'created_at': char.get('created_at', datetime.now().isoformat()),
                    'updated_at': datetime.now().isoformat()
                }
                normalized.append(normalized_char)

        return normalized

    def load_characters_from_file(self, file_path: str) -> bool:
        """
        从文件加载角色数据

        Args:
            file_path: 文件路径

        Returns:
            是否加载成功
        """
        try:
            if not os.path.exists(file_path):
                logger.warning(f"角色文件不存在: {file_path}")
                return False

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            characters = self.convert_character_data(content)
            self.update_data('characters', characters)

            logger.info(f"从文件加载了 {len(characters)} 个角色")
            return True

        except Exception as e:
            logger.error(f"加载角色文件失败: {e}")
            return False

    def save_characters_to_file(self, file_path: str) -> bool:
        """
        保存角色数据到文件

        Args:
            file_path: 文件路径

        Returns:
            是否保存成功
        """
        try:
            characters = self.get_data('characters')

            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(characters, f, ensure_ascii=False, indent=2)

            logger.info(f"保存了 {len(characters)} 个角色到文件")
            return True

        except Exception as e:
            logger.error(f"保存角色文件失败: {e}")
            return False

    def add_character(self, character_data: Dict[str, Any]) -> bool:
        """
        添加新角色

        Args:
            character_data: 角色数据

        Returns:
            是否添加成功
        """
        try:
            characters = self.get_data('characters').copy()

            # 生成新ID
            new_id = max([c.get('id', 0) for c in characters], default=0) + 1

            # 标准化数据
            normalized_char = self._normalize_character_data(character_data)[0]
            normalized_char['id'] = new_id

            characters.append(normalized_char)
            self.update_data('characters', characters)

            logger.info(f"添加了新角色: {normalized_char.get('name', '未知')}")
            return True

        except Exception as e:
            logger.error(f"添加角色失败: {e}")
            return False

    def update_character(self, character_id: int, updates: Dict[str, Any]) -> bool:
        """
        更新角色信息

        Args:
            character_id: 角色ID
            updates: 更新的数据

        Returns:
            是否更新成功
        """
        try:
            characters = self.get_data('characters').copy()

            for i, char in enumerate(characters):
                if char.get('id') == character_id:
                    # 更新数据
                    char.update(updates)
                    char['updated_at'] = datetime.now().isoformat()
                    characters[i] = char

                    self.update_data('characters', characters)
                    logger.info(f"更新了角色: {char.get('name', '未知')}")
                    return True

            logger.warning(f"未找到角色ID: {character_id}")
            return False

        except Exception as e:
            logger.error(f"更新角色失败: {e}")
            return False

    def delete_character(self, character_id: int) -> bool:
        """
        删除角色

        Args:
            character_id: 角色ID

        Returns:
            是否删除成功
        """
        try:
            characters = self.get_data('characters').copy()

            for i, char in enumerate(characters):
                if char.get('id') == character_id:
                    char_name = char.get('name', '未知')
                    characters.pop(i)

                    self.update_data('characters', characters)
                    logger.info(f"删除了角色: {char_name}")
                    return True

            logger.warning(f"未找到角色ID: {character_id}")
            return False

        except Exception as e:
            logger.error(f"删除角色失败: {e}")
            return False

    def get_character_by_id(self, character_id: int) -> Optional[Dict[str, Any]]:
        """
        根据ID获取角色

        Args:
            character_id: 角色ID

        Returns:
            角色数据，如果未找到则返回None
        """
        characters = self.get_data('characters')
        for char in characters:
            if char.get('id') == character_id:
                return char
        return None

    def search_characters(self, query: str) -> List[Dict[str, Any]]:
        """
        搜索角色

        Args:
            query: 搜索关键词

        Returns:
            匹配的角色列表
        """
        characters = self.get_data('characters')
        query = query.lower()

        results = []
        for char in characters:
            if (query in char.get('name', '').lower() or
                query in char.get('description', '').lower() or
                query in char.get('background', '').lower()):
                results.append(char)

        return results

    def update_characters(self, characters: List[Dict[str, Any]]) -> bool:
        """
        更新角色列表数据

        Args:
            characters: 新的角色列表数据

        Returns:
            bool: 更新是否成功
        """
        try:
            # 验证角色数据
            if not isinstance(characters, list):
                logger.error("角色数据必须是列表格式")
                return False

            # 更新角色数据
            self.update_data('characters', characters)

            logger.info(f"角色数据更新成功，共 {len(characters)} 个角色")
            return True

        except Exception as e:
            logger.error(f"更新角色数据失败: {e}")
            return False


# 全局数据桥接器实例
_data_bridge = None

def get_data_bridge() -> DataBridge:
    """获取全局数据桥接器实例"""
    global _data_bridge
    if _data_bridge is None:
        _data_bridge = DataBridge()
    return _data_bridge