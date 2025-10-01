#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Novel Generator - 启动脚本
使用 uv 包管理器运行项目
"""

import subprocess
import sys
import os

def install_dependencies():
    """使用 uv 安装项目依赖"""
    print("正在使用 uv 安装项目依赖...")
    try:
        # 检查是否存在 requirements-uv.txt
        if os.path.exists("requirements-uv.txt"):
            result = subprocess.run([sys.executable, "-m", "uv", "pip", "install", "-r", "requirements-uv.txt"], 
                                  check=True, capture_output=True, text=True)
            print("依赖安装成功!")
            return True
        else:
            print("未找到 requirements-uv.txt 文件")
            return False
    except subprocess.CalledProcessError as e:
        print(f"依赖安装失败: {e}")
        return False
    except FileNotFoundError:
        print("未找到 uv 命令，请确保已安装 uv 包管理器")
        print("安装 uv: https://github.com/astral-sh/uv")
        return False

def run_main():
    """运行主程序"""
    print("正在启动 AI Novel Generator...")
    try:
        # 运行主程序
        subprocess.run([sys.executable, "main.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"程序运行失败: {e}")
    except FileNotFoundError:
        print("未找到 main.py 文件")

def main():
    """主函数"""
    print("AI Novel Generator 启动器")
    print("=" * 30)
    
    # 检查是否需要安装依赖
    install_deps = input("是否需要安装依赖? (y/n): ").lower().strip()
    if install_deps == 'y' or install_deps == 'yes':
        if not install_dependencies():
            print("依赖安装失败，但仍可尝试运行程序...")
    
    # 运行主程序
    run_main()

if __name__ == "__main__":
    main()