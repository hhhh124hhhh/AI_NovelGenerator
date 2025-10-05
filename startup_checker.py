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
import subprocess
import shutil
from typing import List, Dict, Any

# Windows编码修复
def setup_windows_encoding():
    """修复Windows环境下的编码问题"""
    if sys.platform == 'win32':
        # 设置控制台编码为UTF-8
        try:
            import subprocess
            subprocess.run(['chcp', '65001'], shell=True, capture_output=True)
        except:
            pass

        # 设置环境变量
        os.environ['PYTHONIOENCODING'] = 'utf-8'

        # 修复标准输出编码
        try:
            if hasattr(sys.stdout, 'reconfigure'):
                sys.stdout.reconfigure(encoding='utf-8')
            if hasattr(sys.stderr, 'reconfigure'):
                sys.stderr.reconfigure(encoding='utf-8')
        except:
            pass

# 立即执行编码修复
setup_windows_encoding()

def safe_print(text):
    """安全打印函数，避免编码错误"""
    try:
        print(text)
    except UnicodeEncodeError:
        # 移除或替换Unicode字符
        try:
            # 替换常见emoji为ASCII字符
            replacements = {
                '🚀': '[启动]',
                '🔍': '[诊断]',
                '✅': '[OK]',
                '❌': '[FAIL]',
                '⚠️': '[WARN]',
                '💡': '[提示]',
                '📋': '[清单]',
                '🔧': '[修复]',
                '🎯': '[目标]',
                '🎉': '[成功]',
                '📍': '[路径]',
                '🟡': '[黄色]',
                '🔴': '[红色]',
                '🤖': '[AI]'
            }
            safe_text = text
            for unicode_char, ascii_char in replacements.items():
                safe_text = safe_text.replace(unicode_char, ascii_char)
            print(safe_text)
        except:
            # 最后的备选方案：完全移除非ASCII字符
            try:
                print(text.encode('ascii', 'ignore').decode('ascii'))
            except:
                print("Encoding error - message cannot be displayed")

# 设置日志 - 使用简单的文本格式避免Unicode问题
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def is_uv_environment():
    """检测是否在 uv 环境中运行"""
    # 检查是否使用 uv run 命令运行
    return 'UV' in os.environ or 'uv' in sys.argv[0].lower()


def is_virtual_environment():
    """检测是否在虚拟环境中运行"""
    return (
        hasattr(sys, 'real_prefix') or  # virtualenv
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) or  # venv
        os.environ.get('VIRTUAL_ENV') or os.environ.get('CONDA_DEFAULT_ENV')  # 其他虚拟环境
    )


def get_environment_info():
    """获取环境信息"""
    info = {
        'is_uv': is_uv_environment(),
        'is_venv': is_virtual_environment(),
        'python_version': sys.version,
        'platform': sys.platform,
        'python_executable': sys.executable,
        'venv_prefix': getattr(sys, 'prefix', None),
        'base_prefix': getattr(sys, 'base_prefix', None)
    }
    return info


def check_uv_available():
    """检查 uv 是否可用"""
    try:
        result = subprocess.run(['uv', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, "uv 命令执行失败"
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        return False, "uv 未安装或不可用"


class StartupDiagnostic:
    """启动诊断器"""

    def __init__(self):
        self.issues = []
        self.warnings = []
        self.suggestions = []
        self.env_info = get_environment_info()

    def check_environment(self) -> bool:
        """检查运行环境"""
        safe_print("检查运行环境...")

        # 显示环境信息
        safe_print(f"[路径] Python路径: {self.env_info['python_executable']}")
        if self.env_info['is_uv']:
            safe_print("[OK] 检测到 uv 环境")
            uv_available, uv_info = check_uv_available()
            if uv_available:
                safe_print(f"[OK] {uv_info}")
            else:
                self.warnings.append(f"uv环境检测异常: {uv_info}")
        elif self.env_info['is_venv']:
            safe_print("[OK] 检测到虚拟环境")
            if self.env_info['base_prefix']:
                safe_print(f"[路径] 基础Python: {self.env_info['base_prefix']}")
        else:
            self.warnings.append("未检测到虚拟环境，建议使用虚拟环境运行")
            safe_print("[WARN] 运行在全局Python环境中")

        return True

    def check_python_version(self) -> bool:
        """检查Python版本"""
        safe_print("检查Python版本...")

        version_info = sys.version_info
        if version_info < (3, 9):
            self.issues.append(f"Python版本过低: {version_info.major}.{version_info.minor}.{version_info.micro} (需要3.9+)")
            return False
        elif version_info >= (3, 13):
            self.warnings.append(f"Python版本较新: {version_info.major}.{version_info.minor}.{version_info.micro} (可能存在兼容性问题)")
            return True
        else:
            safe_print(f"[OK] Python版本: {version_info.major}.{version_info.minor}.{version_info.micro}")
            return True

    def check_required_packages(self) -> bool:
        """检查必需的包"""
        safe_print("检查必需的包...")

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
                safe_print(f"[OK] 核心包: {package}")
            else:
                all_good = False

        # 检查增强包
        for package in enhanced_packages:
            if self._check_package(package, critical=False):
                safe_print(f"[OK] 增强包: {package}")
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
        safe_print("检查文件结构...")

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
                safe_print(f"[OK] 必需文件: {file_path}")
            else:
                self.issues.append(f"缺少必需文件: {file_path}")
                all_good = False

        # 检查版本文件
        v1_exists = all(os.path.exists(f) for f in v1_files)
        v2_exists = all(os.path.exists(f) for f in v2_files)

        if v1_exists:
            safe_print("[OK] 检测到1.0版本文件")
        if v2_exists:
            safe_print("[OK] 检测到2.0版本文件")

        if not v1_exists and not v2_exists:
            self.issues.append("未找到任何版本的主窗口文件")
            all_good = False

        return all_good

    def check_configuration(self) -> bool:
        """检查配置文件"""
        safe_print("检查配置...")

        config_files = [
            'config.json',
            'config_manager.py',
        ]

        all_good = True

        for config_file in config_files:
            if os.path.exists(config_file):
                safe_print(f"[OK] 配置文件: {config_file}")
            else:
                self.warnings.append(f"配置文件不存在: {config_file}")

        return all_good

    def generate_recommendations(self) -> List[str]:
        """生成修复建议"""
        recommendations = []

        if self.issues:
            recommendations.append("[红色] 严重问题需要立即解决:")
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
            recommendations.append("[黄色] 警告信息:")
            for warning in self.warnings:
                recommendations.append(f"   注意: {warning}")

        # 环境特定建议
        if self.env_info['is_uv']:
            recommendations.extend([
                "",
                "[启动] UV环境启动选项:",
                "uv run python main.py                    # 自动选择最佳版本",
                "uv run python main.py --version 1.0     # 强制使用1.0版本",
                "uv run python main.py --version 2.0     # 强制使用2.0版本",
                "uv run python launch.py                 # 使用启动器",
            ])
        elif self.env_info['is_venv']:
            recommendations.extend([
                "",
                "[启动] 虚拟环境启动选项:",
                "python main.py                    # 自动选择最佳版本",
                "python main.py --version 1.0     # 强制使用1.0版本",
                "python main.py --version 2.0     # 强制使用2.0版本",
                "python launch.py                 # 使用启动器",
            ])
        else:
            recommendations.extend([
                "",
                "[提示] 环境建议:",
                "1. UV环境 (推荐):",
                "   uv venv                          # 创建UV虚拟环境",
                "   uv pip install -r requirements-uv.txt  # 安装依赖",
                "   uv run python main.py            # 运行程序",
                "",
                "2. 传统虚拟环境:",
                "   python -m venv venv",
                "   source venv/bin/activate (Linux/Mac) 或 venv\\Scripts\\activate (Windows)",
                "   pip install -r requirements.txt",
                "",
                "3. 直接运行 (不推荐):",
                "   pip install -r requirements.txt",
                "   python main.py",
            ])

        # 通用建议
        recommendations.extend([
            "",
            "[清单] 其他可用选项:",
            "python launch.py                     # 图形化启动选择器",
            "python run.py                        # 运行脚本",
            "python startup_checker.py            # 环境诊断",
            "",
            "[修复] 依赖文件选项:",
            "requirements.txt                     # 标准依赖",
            "requirements-uv.txt                  # UV优化依赖",
            "requirements-uv-full.txt             # UV完整依赖",
        ])

        return recommendations

    def run_diagnostic(self) -> Dict[str, Any]:
        """运行完整诊断"""
        safe_print("[诊断] 开始启动诊断...")
        safe_print("=" * 50)

        results = {
            'environment_ok': self.check_environment(),
            'python_ok': self.check_python_version(),
            'packages_ok': self.check_required_packages(),
            'files_ok': self.check_file_structure(),
            'config_ok': self.check_configuration(),
            'issues': self.issues,
            'warnings': self.warnings,
            'environment_info': self.env_info,
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

        safe_print("=" * 50)
        safe_print("[诊断结果] 诊断结果:")

        if results['can_start_2_0']:
            safe_print("[OK] 可以启动2.0版本 (推荐)")
        elif results['can_start_1_0']:
            safe_print("[WARN] 可以启动1.0版本 (兼容模式)")
        else:
            safe_print("[FAIL] 无法启动，需要修复问题")

        # 显示建议
        recommendations = self.generate_recommendations()
        safe_print("\n" + "\n".join(recommendations))

        return results


def main():
    """主函数"""
    safe_print("[启动] AI小说生成器启动诊断器")
    safe_print("=" * 50)

    diagnostic = StartupDiagnostic()
    results = diagnostic.run_diagnostic()

    # 根据结果决定下一步
    env_info = results['environment_info']

    if results['can_start_2_0']:
        if env_info['is_uv']:
            safe_print("[成功] 建议使用: uv run python main.py")
        elif env_info['is_venv']:
            safe_print("[成功] 建议使用: python main.py")
        else:
            safe_print("[成功] 建议使用: python main.py (或考虑使用虚拟环境)")
    elif results['can_start_1_0']:
        if env_info['is_uv']:
            safe_print("[WARN] 建议使用: uv run python main.py --version 1.0")
        elif env_info['is_venv']:
            safe_print("[WARN] 建议使用: python main.py --version 1.0")
        else:
            safe_print("[WARN] 建议使用: python main.py --version 1.0")
    else:
        safe_print("[FAIL] 请先解决上述问题后再尝试启动")
        if not env_info['is_uv'] and not env_info['is_venv']:
            safe_print("[提示] 建议创建虚拟环境后重试")
        sys.exit(1)


if __name__ == "__main__":
    main()