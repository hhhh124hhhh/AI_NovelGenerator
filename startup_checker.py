#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动诊断器 - AI小说生成器环境检查工具
使用BMAD方法识别和解决启动问题
"""

import sys
import os
import logging
import importlib
from typing import List, Dict, Any

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class StartupDiagnostic:
    """启动诊断器"""

    def __init__(self):
        self.issues = []
        self.warnings = []
        self.suggestions = []

    def check_python_version(self) -> bool:
        """检查Python版本"""
        logger.info("检查Python版本...")

        version_info = sys.version_info
        if version_info < (3, 9):
            self.issues.append(f"Python版本过低: {version_info.major}.{version_info.minor}.{version_info.micro} (需要3.9+)")
            return False
        elif version_info >= (3, 13):
            self.warnings.append(f"Python版本较新: {version_info.major}.{version_info.minor}.{version_info.micro} (可能存在兼容性问题)")
            return True
        else:
            logger.info(f"✅ Python版本: {version_info.major}.{version_info.minor}.{version_info.micro}")
            return True

    def check_required_packages(self) -> bool:
        """检查必需的包"""
        logger.info("检查必需的包...")

        # 核心依赖包
        core_packages = [
            'customtkinter',
            'langchain',
            'chromadb',
            'tkinter',  # 通常内置，但某些环境可能缺失
        ]

        # 增强功能包
        enhanced_packages = [
            'theme_system.theme_manager',
            'ui.state.state_manager',
            'ui.layout.responsive_manager',
            'ui.performance.performance_monitor',
        ]

        all_good = True

        # 检查核心包
        for package in core_packages:
            if self._check_package(package, critical=True):
                logger.info(f"✅ 核心包: {package}")
            else:
                all_good = False

        # 检查增强包
        for package in enhanced_packages:
            if self._check_package(package, critical=False):
                logger.info(f"✅ 增强包: {package}")
            else:
                self.warnings.append(f"增强功能不可用: {package}")

        return all_good

    def _check_package(self, package_name: str, critical: bool = True) -> bool:
        """检查单个包"""
        try:
            if '.' in package_name:
                # 模块路径
                module_path = package_name.split('.')
                importlib.import_module('.'.join(module_path[:-1]))
            else:
                # 包名
                importlib.import_module(package_name)
            return True
        except ImportError as e:
            if critical:
                self.issues.append(f"缺少关键依赖: {package_name} - {str(e)}")
            return False
        except Exception as e:
            if critical:
                self.issues.append(f"包导入错误: {package_name} - {str(e)}")
            return False

    def check_file_structure(self) -> bool:
        """检查文件结构"""
        logger.info("检查文件结构...")

        required_files = [
            'main.py',
            'config_manager.py',
            'novel_generator/__init__.py',
            'ui/__init__.py',
        ]

        # 检查1.0版本文件
        v1_files = [
            'ui/main_window.py',
        ]

        # 检查2.0版本文件
        v2_files = [
            'ui/modern_main_window.py',
            'theme_system/__init__.py',
        ]

        all_good = True

        # 检查必需文件
        for file_path in required_files:
            if os.path.exists(file_path):
                logger.info(f"✅ 必需文件: {file_path}")
            else:
                self.issues.append(f"缺少必需文件: {file_path}")
                all_good = False

        # 检查版本文件
        v1_exists = all(os.path.exists(f) for f in v1_files)
        v2_exists = all(os.path.exists(f) for f in v2_files)

        if v1_exists:
            logger.info("✅ 检测到1.0版本文件")
        if v2_exists:
            logger.info("✅ 检测到2.0版本文件")

        if not v1_exists and not v2_exists:
            self.issues.append("未找到任何版本的主窗口文件")
            all_good = False

        return all_good

    def check_configuration(self) -> bool:
        """检查配置文件"""
        logger.info("检查配置...")

        config_files = [
            'config.json',
            'config_manager.py',
        ]

        all_good = True

        for config_file in config_files:
            if os.path.exists(config_file):
                logger.info(f"✅ 配置文件: {config_file}")
            else:
                self.warnings.append(f"配置文件不存在: {config_file}")

        return all_good

    def generate_recommendations(self) -> List[str]:
        """生成修复建议"""
        recommendations = []

        if self.issues:
            recommendations.append("🔴 严重问题需要立即解决:")
            for issue in self.issues:
                if "缺少关键依赖" in issue:
                    package = issue.split(":")[1].split(" -")[0].strip()
                    recommendations.append(f"   安装依赖: pip install {package}")
                elif "缺少必需文件" in issue:
                    file_path = issue.split(":")[1].strip()
                    recommendations.append(f"   恢复文件: {file_path}")
                elif "Python版本过低" in issue:
                    recommendations.append("   升级Python到3.9+版本")

        if self.warnings:
            recommendations.append("🟡 警告信息:")
            for warning in self.warnings:
                recommendations.append(f"   注意: {warning}")

        # 通用建议
        recommendations.extend([
            "",
            "💡 通用建议:",
            "1. 使用虚拟环境: python -m venv venv",
            "2. 激活虚拟环境: source venv/bin/activate (Linux/Mac) 或 venv\\Scripts\\activate (Windows)",
            "3. 安装完整依赖: pip install -r requirements.txt",
            "4. 检查Python路径: echo $PYTHONPATH",
            "",
            "🚀 启动选项:",
            "python main.py                    # 自动选择最佳版本",
            "python main.py --version 1.0     # 强制使用1.0版本",
            "python main.py --version 2.0     # 强制使用2.0版本",
            "python main.py --safe-mode       # 安全模式启动",
        ])

        return recommendations

    def run_diagnostic(self) -> Dict[str, Any]:
        """运行完整诊断"""
        logger.info("🔍 开始启动诊断...")
        logger.info("=" * 50)

        results = {
            'python_ok': self.check_python_version(),
            'packages_ok': self.check_required_packages(),
            'files_ok': self.check_file_structure(),
            'config_ok': self.check_configuration(),
            'issues': self.issues,
            'warnings': self.warnings,
        }

        results['can_start_2_0'] = (
            results['python_ok'] and
            results['packages_ok'] and
            results['files_ok']
        )

        results['can_start_1_0'] = (
            results['python_ok'] and
            results['files_ok'] and
            os.path.exists('ui/main_window.py')
        )

        logger.info("=" * 50)
        logger.info("📊 诊断结果:")

        if results['can_start_2_0']:
            logger.info("✅ 可以启动2.0版本 (推荐)")
        elif results['can_start_1_0']:
            logger.info("⚠️ 可以启动1.0版本 (兼容模式)")
        else:
            logger.info("🔴 无法启动，需要修复问题")

        # 显示建议
        recommendations = self.generate_recommendations()
        logger.info("\n" + "\n".join(recommendations))

        return results


def main():
    """主函数"""
    print("🚀 AI小说生成器启动诊断器")
    print("=" * 50)

    diagnostic = StartupDiagnostic()
    results = diagnostic.run_diagnostic()

    # 根据结果决定下一步
    if results['can_start_2_0']:
        logger.info("\n🎉 建议使用: python main.py")
    elif results['can_start_1_0']:
        logger.info("\n⚠️ 建议使用: python main.py --version 1.0")
    else:
        logger.info("\n❌ 请先解决上述问题后再尝试启动")
        sys.exit(1)


if __name__ == "__main__":
    main()