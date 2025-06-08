"""
运行软件著作权生成工具的简单脚本
"""

import os
import sys
from sofcrtpro.cli import main
from sofcrtpro.config_manager import ConfigManager
from sofcrtpro.file_scanner import scan_directory, classify_files
from sofcrtpro.code_processor import process_code_files
from sofcrtpro.document_generator import generate_document
from sofcrtpro.utils.file_utils import exclude_directories, filter_files_by_extension

def run_sofcrtpro():
    """
    运行软件著作权生成工具
    """
    # 配置参数
    source_dir = "."
    output_path = "./output/SoftCopyrightPro-source"
    output_format = "docx"
    font_name = "Courier New"
    font_size = 10
    lines_per_page = 50
    exclude_dirs = [".git", "sofcrtpro.egg-info", "__pycache__"]
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    print(f"扫描目录: {source_dir}")
    
    # 初始化配置管理器
    config_manager = ConfigManager()
    config = {
        'source_dir': source_dir,
        'output_path': output_path,
        'output_format': output_format,
        'font_name': font_name,
        'font_size': font_size,
        'lines_per_page': lines_per_page,
        'exclude_dirs': exclude_dirs,
        'file_extensions': None  # 使用默认值
    }
    config_manager.update_config(config)
    
    # 扫描文件
    all_files = scan_directory(source_dir)
    
    # 排除指定目录
    all_files = exclude_directories(all_files, exclude_dirs)
    
    # 按扩展名筛选
    filtered_files = filter_files_by_extension(all_files, config_manager.get_file_extensions())
    
    print(f"找到 {len(filtered_files)} 个符合条件的源代码文件")
    
    # 分类文件
    classified_files = classify_files(
        filtered_files,
        config_manager.get_backend_identifiers(),
        config_manager.get_frontend_identifiers()
    )
    
    print(f"后端文件: {len(classified_files['backend'])} 个")
    print(f"前端文件: {len(classified_files['frontend'])} 个")
    
    # 处理代码文件
    merged_content, pages = process_code_files(classified_files, lines_per_page)
    
    print(f"合并后的代码总行数: {len(merged_content)}")
    print(f"分页后的页数: {len(pages)}")
    
    # 生成文档
    output_file = generate_document(
        content=merged_content,
        output_path=output_path,
        output_format=output_format,
        font_name=font_name,
        font_size=font_size
    )
    
    print(f"文档已生成: {output_file}")

if __name__ == "__main__":
    run_sofcrtpro() 