#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志查看工具 - AI小说生成器调试辅助
方便查看和分析日志文件
"""

import os
import sys
import argparse
from datetime import datetime
from typing import List, Dict, Any
import json

def get_log_files() -> List[str]:
    """获取所有日志文件"""
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        print(f"❌ 日志目录不存在: {logs_dir}")
        return []

    log_files = []
    for file_name in os.listdir(logs_dir):
        if file_name.endswith('.log') or file_name.endswith('.json'):
            log_files.append(os.path.join(logs_dir, file_name))

    return sorted(log_files, key=os.path.getmtime, reverse=True)

def show_log_file(file_path: str, lines: int = 50):
    """显示日志文件内容"""
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return

    print(f"\n📄 显示文件: {file_path}")
    print("=" * 80)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content_lines = f.readlines()

        if not content_lines:
            print("(空文件)")
            return

        # 显示最后N行
        start_line = max(0, len(content_lines) - lines)
        for i, line in enumerate(content_lines[start_line:], start=start_line + 1):
            print(f"{i:5d}: {line.rstrip()}")

        print(f"\n📊 总行数: {len(content_lines)} (显示最后 {len(content_lines) - start_line} 行)")

    except Exception as e:
        print(f"❌ 读取文件失败: {e}")

def show_error_reports():
    """显示错误报告"""
    logs_dir = "logs"
    error_reports = []

    for file_name in os.listdir(logs_dir):
        if file_name.startswith('error_report_') and file_name.endswith('.json'):
            error_reports.append(os.path.join(logs_dir, file_name))

    if not error_reports:
        print("📝 没有找到错误报告")
        return

    print("\n🚨 错误报告:")
    print("=" * 80)

    for report_file in sorted(error_reports, reverse=True):
        try:
            with open(report_file, 'r', encoding='utf-8') as f:
                report = json.load(f)

            print(f"\n📅 时间: {report['timestamp']}")
            print(f"🔧 错误类型: {report['error_type']}")
            print(f"📝 错误消息: {report['error_message']}")
            print(f"🎯 上下文: {report['context']}")
            print(f"📁 文件: {os.path.basename(report_file)}")

        except Exception as e:
            print(f"❌ 读取错误报告失败 {report_file}: {e}")

def show_log_summary():
    """显示日志摘要"""
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        print(f"❌ 日志目录不存在: {logs_dir}")
        return

    print("\n📊 日志摘要:")
    print("=" * 80)

    total_size = 0
    log_info = []

    for file_name in sorted(os.listdir(logs_dir)):
        file_path = os.path.join(logs_dir, file_name)
        if os.path.isfile(file_path):
            try:
                stat = os.stat(file_path)
                size = stat.st_size
                mtime = datetime.fromtimestamp(stat.st_mtime)

                total_size += size
                log_info.append({
                    'name': file_name,
                    'size': size,
                    'mtime': mtime,
                    'size_mb': size / (1024 * 1024)
                })
            except Exception:
                continue

    # 按大小排序
    log_info.sort(key=lambda x: x['size'], reverse=True)

    print(f"📁 日志目录: {logs_dir}")
    print(f"📦 总大小: {total_size / (1024 * 1024):.2f} MB")
    print(f"📄 文件数量: {len(log_info)}")
    print()

    print(f"{'文件名':<25} {'大小':<10} {'修改时间':<20}")
    print("-" * 55)

    for info in log_info:
        size_str = f"{info['size_mb']:.2f}MB" if info['size_mb'] >= 1 else f"{info['size']:.0f}B"
        mtime_str = info['mtime'].strftime('%Y-%m-%d %H:%M:%S')
        print(f"{info['name']:<25} {size_str:<10} {mtime_str:<20}")

def search_logs(keyword: str, file_pattern: str = "*.log"):
    """在日志中搜索关键词"""
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        print(f"❌ 日志目录不存在: {logs_dir}")
        return

    import fnmatch

    matches = []

    for file_name in os.listdir(logs_dir):
        if fnmatch.fnmatch(file_name, file_pattern):
            file_path = os.path.join(logs_dir, file_name)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                for line_num, line in enumerate(lines, 1):
                    if keyword.lower() in line.lower():
                        matches.append({
                            'file': file_name,
                            'line_num': line_num,
                            'content': line.strip()
                        })
            except Exception:
                continue

    if not matches:
        print(f"🔍 没有找到包含 '{keyword}' 的内容")
        return

    print(f"\n🔍 搜索结果 (关键词: '{keyword}'):")
    print("=" * 80)

    current_file = None
    for match in matches:
        if match['file'] != current_file:
            current_file = match['file']
            print(f"\n📁 {current_file}:")
            print("-" * 40)

        print(f"  {match['line_num']:5d}: {match['content']}")

def clear_logs():
    """清空日志文件"""
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        print(f"❌ 日志目录不存在: {logs_dir}")
        return

    import glob

    # 清空所有.log文件
    log_files = glob.glob(os.path.join(logs_dir, "*.log"))
    cleared_count = 0

    for log_file in log_files:
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write("")
            cleared_count += 1
            print(f"✅ 已清空: {os.path.basename(log_file)}")
        except Exception as e:
            print(f"❌ 清空失败 {log_file}: {e}")

    print(f"\n📊 总共清空了 {cleared_count} 个日志文件")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='AI小说生成器日志查看工具')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # 列出日志文件
    list_parser = subparsers.add_parser('list', help='列出所有日志文件')

    # 显示日志文件
    show_parser = subparsers.add_parser('show', help='显示日志文件内容')
    show_parser.add_argument('file', help='日志文件名')
    show_parser.add_argument('-n', '--lines', type=int, default=50, help='显示最后N行 (默认50)')

    # 显示摘要
    summary_parser = subparsers.add_parser('summary', help='显示日志摘要')

    # 搜索
    search_parser = subparsers.add_parser('search', help='搜索日志内容')
    search_parser.add_argument('keyword', help='搜索关键词')
    search_parser.add_argument('-p', '--pattern', default='*.log', help='文件模式 (默认*.log)')

    # 错误报告
    errors_parser = subparsers.add_parser('errors', help='显示错误报告')

    # 清空日志
    clear_parser = subparsers.add_parser('clear', help='清空所有日志文件')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    print("🔍 AI小说生成器日志查看工具")
    print("=" * 50)

    if args.command == 'list':
        log_files = get_log_files()
        if log_files:
            print("\n📁 日志文件:")
            for i, file_path in enumerate(log_files, 1):
                print(f"  {i}. {os.path.basename(file_path)}")
        else:
            print("📝 没有找到日志文件")

    elif args.command == 'show':
        log_files = get_log_files()
        if not log_files:
            print("📝 没有找到日志文件")
            return

        # 查找匹配的文件
        matching_files = [f for f in log_files if args.file in os.path.basename(f)]
        if not matching_files:
            print(f"❌ 没有找到包含 '{args.file}' 的日志文件")
            return

        if len(matching_files) > 1:
            print(f"📝 找到多个匹配的文件:")
            for i, file_path in enumerate(matching_files, 1):
                print(f"  {i}. {os.path.basename(file_path)}")
            print(f"📄 显示第一个匹配的文件: {os.path.basename(matching_files[0])}")

        show_log_file(matching_files[0], args.lines)

    elif args.command == 'summary':
        show_log_summary()

    elif args.command == 'search':
        search_logs(args.keyword, args.pattern)

    elif args.command == 'errors':
        show_error_reports()

    elif args.command == 'clear':
        confirm = input("⚠️ 确定要清空所有日志文件吗? (y/N): ").lower()
        if confirm == 'y':
            clear_logs()
        else:
            print("🚫 操作已取消")

if __name__ == "__main__":
    main()