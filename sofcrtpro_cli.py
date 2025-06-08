#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import subprocess
from pathlib import Path

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='软著文档生成工具命令行接口',
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument('-i', '--input', type=str, required=True,
                        help='包含文件列表的文本文件路径')
    parser.add_argument('-n', '--name', type=str, required=True,
                        help='软件名称')
    parser.add_argument('-v', '--version', type=str, default='V1.0',
                        help='软件版本号 (默认: V1.0)')
    parser.add_argument('-o', '--output', type=str, required=True,
                        help='输出文件路径 (不含扩展名)')
    parser.add_argument('--font-size', type=float, default=10.5,
                        help='字体大小 (默认: 10.5)')
    parser.add_argument('--line-spacing', type=float, default=10.5,
                        help='行间距 (默认: 10.5)')
    parser.add_argument('--english-font', type=str, default='Courier New',
                        help='英文字体 (默认: Courier New)')
    parser.add_argument('--chinese-font', type=str, default='SimSun',
                        help='中文字体 (默认: SimSun)')
    parser.add_argument('--page-limit', type=int, default=0,
                        help='每页最少代码行数 (默认: 0, 表示不限制)')
    parser.add_argument('--remove-empty', action='store_true',
                        help='移除空行')
    parser.add_argument('--sort-files', action='store_true',
                        help='按重要性排序文件 (后端优先，前端其次)')
    
    return parser.parse_args()

def read_file_list(file_path):
    """读取文件列表"""
    if not os.path.exists(file_path):
        print(f"错误: 文件 '{file_path}' 不存在")
        sys.exit(1)
        
    files = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # 跳过注释行和空行
            if not line or line.startswith('#'):
                continue
            files.append(line)
    
    return files

def build_command(args, files):
    """构建文档生成命令"""
    # 基本命令
    cmd = [
        'python', 'run_simple.py',
        '-n', args.name,
        '-v', args.version,
        '-o', args.output
    ]
    
    # 添加格式选项
    cmd.extend(['--font-size', str(args.font_size)])
    cmd.extend(['--line-spacing', str(args.line_spacing)])
    cmd.extend(['--english-font', args.english_font])
    cmd.extend(['--chinese-font', args.chinese_font])
    
    # 添加其他选项
    if args.page_limit > 0:
        cmd.extend(['--page-limit', str(args.page_limit)])
    if args.remove_empty:
        cmd.append('--remove-empty')
    if args.sort_files:
        cmd.append('--sort-files')
    
    # 添加文件列表
    for file in files:
        cmd.extend(['--include-file', file])
    
    return cmd

def main():
    """主函数"""
    print("软著文档生成工具命令行接口 v1.0")
    
    # 解析命令行参数
    args = parse_args()
    
    # 读取文件列表
    print(f"从 '{args.input}' 读取文件列表...")
    files = read_file_list(args.input)
    print(f"找到 {len(files)} 个文件")
    
    # 构建命令
    cmd = build_command(args, files)
    cmd_str = ' '.join(cmd)
    print(f"\n将执行命令:\n{cmd_str}")
    
    # 确认执行
    confirm = input("\n是否继续? (y/n): ").lower()
    if confirm != 'y':
        print("操作已取消")
        sys.exit(0)
    
    # 执行命令
    print("\n正在生成文档...")
    try:
        result = subprocess.run(cmd, check=True, text=True, capture_output=True)
        print("\n命令执行成功!")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"\n命令执行失败: {e}")
        print(e.stderr)
        sys.exit(1)
    
    print(f"\n文档已生成: {args.output}.docx")

if __name__ == "__main__":
    main() 