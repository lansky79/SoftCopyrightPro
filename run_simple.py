"""
运行软件著作权生成工具的简单脚本 - 不依赖click库
增强版：格式优化，确保每页至少50行代码，添加页眉和页码（右上角）
支持命令行参数，可以指定源代码目录、项目名称、版本号和输出路径
"""

import os
import sys
import argparse
from sofcrtpro.file_scanner import scan_directory, classify_files
from sofcrtpro.code_processor import process_code_files
from sofcrtpro.document_generator import generate_document

def parse_arguments():
    """
    解析命令行参数
    
    Returns:
        解析后的参数对象
    """
    parser = argparse.ArgumentParser(description='生成软件著作权源代码文件')
    
    parser.add_argument('-s', '--source', dest='source_dir', default='.',
                        help='源代码目录路径 (默认: 当前目录)')
    
    parser.add_argument('-n', '--name', dest='software_name', default='SoftCopyrightPro',
                        help='软件名称 (默认: SoftCopyrightPro)')
    
    parser.add_argument('-v', '--version', dest='software_version', default='v0.1.0',
                        help='软件版本号 (默认: v0.1.0)')
    
    parser.add_argument('-o', '--output', dest='output_path',
                        default='./output/SoftCopyrightPro-source-aligned',
                        help='输出文件路径 (默认: ./output/SoftCopyrightPro-source-aligned)')
    
    parser.add_argument('-f', '--format', dest='output_format', default='docx',
                        choices=['docx', 'pdf'], help='输出文件格式 (默认: docx)')
    
    parser.add_argument('--english-font', dest='font_name_en', default='Courier New',
                        help='英文字体 (默认: Courier New)')
    
    parser.add_argument('--chinese-font', dest='font_name_cn', default='SimSun',
                        help='中文字体 (默认: SimSun)')
    
    parser.add_argument('--font-size', dest='font_size', type=float, default=10.5,
                        help='字体大小 (默认: 10.5pt)')
    
    parser.add_argument('--lines-per-page', dest='lines_per_page', type=int, default=50,
                        help='每页最少行数 (默认: 50)')
    
    parser.add_argument('--list-only', action='store_true',
                        help='仅列出符合条件的源代码文件，不生成文档')
    
    parser.add_argument('--exclude-patterns', dest='exclude_patterns', nargs='+',
                        default=['test_', 'tests', 'debug', 'generated', 'auto_gen', 'temp', 'tmp'],
                        help='排除的文件名模式 (默认: test_ tests debug generated auto_gen temp tmp)')
    
    parser.add_argument('--exclude-dirs', dest='exclude_dirs', nargs='+',
                        default=['.git', 'sofcrtpro.egg-info', '__pycache__', '.vscode', '.idea', 
                                'venv', 'env', 'node_modules', 'tests', 'test', 'debug', 'temp', 'tmp'],
                        help='排除的目录名 (默认: .git sofcrtpro.egg-info __pycache__ .vscode .idea venv env node_modules tests test debug temp tmp)')
    
    parser.add_argument('--include-dir', dest='include_dirs', nargs='+',
                        default=[],
                        help='指定要包含的目录，这些目录下的所有源代码文件都将被包含，即使它们匹配排除模式')
    
    return parser.parse_args()


def should_exclude_file(file_path, exclude_patterns, exclude_dirs, include_dirs):
    """
    判断文件是否应该被排除
    
    Args:
        file_path: 文件路径
        exclude_patterns: 排除的文件名模式
        exclude_dirs: 排除的目录名
        include_dirs: 指定要包含的目录
    
    Returns:
        是否应该排除
    """
    # 检查文件是否在包含目录中，如果是则不排除
    for include_dir in include_dirs:
        if include_dir in file_path:
            return False
    
    # 检查文件是否在排除目录中
    for excluded_dir in exclude_dirs:
        if excluded_dir in file_path.split(os.sep):
            return True
    
    # 检查文件名是否匹配排除模式
    file_name = os.path.basename(file_path)
    for pattern in exclude_patterns:
        if pattern in file_name:
            return True
    
    return False


def count_file_lines(file_path):
    """
    计算文件的代码行数（不包括空行和注释行）
    
    Args:
        file_path: 文件路径
    
    Returns:
        代码行数
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            # 移除空行和纯注释行
            code_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
            return len(code_lines)
    except Exception as e:
        print(f"计算文件行数时出错 {file_path}: {e}")
        return 0


def run_simple():
    """
    运行软件著作权生成工具 - 格式优化版
    """
    # 解析命令行参数
    args = parse_arguments()
    
    # 配置参数
    source_dir = args.source_dir
    output_path = args.output_path
    output_format = args.output_format
    font_name_en = args.font_name_en
    font_name_cn = args.font_name_cn
    font_size = args.font_size
    lines_per_page = args.lines_per_page
    software_name = args.software_name
    software_version = args.software_version
    exclude_dirs = args.exclude_dirs
    exclude_patterns = args.exclude_patterns
    include_dirs = args.include_dirs
    list_only = args.list_only
    
    # 确保输出目录存在
    if not list_only:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    print(f"扫描目录: {source_dir}")
    
    # 扫描文件
    all_files = scan_directory(source_dir)
    
    # 排除指定目录和文件
    filtered_files = []
    for file_path in all_files:
        if not should_exclude_file(file_path, exclude_patterns, exclude_dirs, include_dirs):
            filtered_files.append(file_path)
    
    # 默认的文件扩展名
    backend_identifiers = {'.py', '.java', '.c', '.cpp', '.cs', '.go', '.rb', '.php', '.swift'}
    frontend_identifiers = {'.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.vue', '.scss', '.less'}
    
    # 筛选文件扩展名
    code_files = []
    for file_path in filtered_files:
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext in backend_identifiers or file_ext in frontend_identifiers:
            code_files.append(file_path)
    
    print(f"找到 {len(code_files)} 个符合条件的源代码文件")
    
    # 分类文件
    classified_files = {'backend': [], 'frontend': []}
    
    for file_path in code_files:
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext in backend_identifiers:
            classified_files['backend'].append(file_path)
        elif file_ext in frontend_identifiers:
            classified_files['frontend'].append(file_path)
    
    print(f"后端文件: {len(classified_files['backend'])} 个")
    print(f"前端文件: {len(classified_files['frontend'])} 个")
    
    # 计算每个文件的行数
    file_line_counts = {}
    total_lines = 0
    
    for category in ['backend', 'frontend']:
        for file_path in classified_files[category]:
            line_count = count_file_lines(file_path)
            file_line_counts[file_path] = line_count
            total_lines += line_count
    
    # 如果仅列出文件，则打印文件列表并退出
    if list_only:
        print("\n符合条件的源代码文件列表:")
        
        print("\n后端文件:")
        for i, file_path in enumerate(sorted(classified_files['backend']), 1):
            line_count = file_line_counts[file_path]
            print(f"{i}. {file_path} - {line_count}行")
        
        print("\n前端文件:")
        for i, file_path in enumerate(sorted(classified_files['frontend']), 1):
            line_count = file_line_counts[file_path]
            print(f"{i}. {file_path} - {line_count}行")
        
        # 添加汇总信息区域，使用分隔线使其更加醒目
        print("\n" + "="*50)
        print("文件列表汇总信息:")
        print(f"总文件数: {len(code_files)}个文件")
        print(f"总代码行数: {total_lines}行")
        print("="*50)
        return
    
    # 处理代码文件 - 会自动按重要性排序，去掉空行，简化文件名标识
    merged_content, pages, processed_files = process_code_files(classified_files, lines_per_page)
    
    print(f"合并后的代码总行数: {len(merged_content)}")
    print(f"分页后的页数: {len(pages)}")
    
    # 生成文档
    output_file, stats = generate_document(
        content=merged_content,
        output_path=output_path,
        file_list=processed_files,
        output_format=output_format,
        software_name=software_name,
        software_version=software_version,
        font_name_en=font_name_en,
        font_name_cn=font_name_cn,
        font_size=font_size
    )
    
    print(f"文档已生成: {output_file}")
    print(f"文档格式:")
    print(f"  - 字号: {font_size}pt")
    print(f"  - 行间距: 10.5pt")
    print(f"  - 段前间距: 0pt")
    print(f"  - 段后间距: 2.3pt")
    print(f"  - 页眉: {software_name} {software_version} (带横线)")
    print(f"  - 页码: 右上角")
    print(f"  - 英文字体: {font_name_en}（等宽）")
    print(f"  - 中文字体: {font_name_cn}（等宽）")
    print(f"  - 页眉字体: 与正文一致（等宽字体）")
    print(f"  - 页眉布局: 单行对齐，分割线紧贴页眉")
    print(f"  - 每页至少{lines_per_page}行代码")
    print(f"  - 简化文件名标识")
    print(f"  - 去掉所有空行")
    print(f"  - 按重要性排序(后端优先，前端其次)")
    
    # 显示详细统计信息
    print("\n详细统计信息:")
    print(f"总代码行数: {stats['total_lines']}")
    print(f"总页数: {stats['total_pages']}")
    print(f"处理的文件数量: {len(processed_files)}")
    
    # 显示每个处理文件的详细信息
    print("\n处理的文件列表(按顺序):")
    for i, file_path in enumerate(processed_files, 1):
        file_name = os.path.basename(file_path)
        line_count = file_line_counts.get(file_path, "未知")
        print(f"{i}. {file_path} - {line_count}行")
    
    # 添加汇总信息区域，使用分隔线使其更加醒目
    print("\n" + "="*50)
    print("文档生成汇总信息:")
    print(f"总文件数: {len(processed_files)}个文件")
    print(f"总代码行数: {total_lines}行")
    print(f"总页数: {stats['total_pages']}页")
    print("="*50)

if __name__ == "__main__":
    run_simple() 