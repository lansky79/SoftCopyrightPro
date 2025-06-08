"""
命令行界面模块

提供命令行参数解析和主程序入口。
"""

import os
import sys
import click
from typing import List, Dict, Any

from sofcrtpro.config_manager import ConfigManager
from sofcrtpro.file_scanner import scan_directory, classify_files
from sofcrtpro.code_processor import process_code_files
from sofcrtpro.document_generator import generate_document
from sofcrtpro.utils.file_utils import exclude_directories, filter_files_by_extension


@click.command()
@click.option('--source-dir', '-s', type=click.Path(exists=True, file_okay=False, dir_okay=True),
              help='源代码目录路径')
@click.option('--output-path', '-o', default='output/source_code',
              help='输出文件路径，不包括扩展名')
@click.option('--output-format', '-f', type=click.Choice(['docx', 'pdf']), default='docx',
              help='输出格式 (docx 或 pdf)')
@click.option('--font-name', default='Courier New',
              help='字体名称，推荐等宽字体如Courier New')
@click.option('--font-size', type=click.IntRange(8, 14), default=10,
              help='字体大小（磅），范围8-14')
@click.option('--lines-per-page', type=click.IntRange(10, 100), default=50,
              help='每页显示的代码行数')
@click.option('--extensions', '-e', multiple=True,
              help='要包含的文件扩展名，例如 -e .py -e .java')
@click.option('--exclude-dirs', '-x', multiple=True,
              help='要排除的目录，例如 -x venv -x node_modules')
@click.option('--config-file', '-c', type=click.Path(exists=False),
              help='配置文件路径')
@click.option('--save-config', is_flag=True,
              help='保存当前配置到配置文件')
def main(
    source_dir: str,
    output_path: str,
    output_format: str,
    font_name: str,
    font_size: int,
    lines_per_page: int,
    extensions: List[str],
    exclude_dirs: List[str],
    config_file: str,
    save_config: bool
) -> None:
    """
    SoftCopyrightPro - 软件著作权材料生成工具
    
    扫描指定目录中的源代码文件，按照后端到前端的顺序拼接代码，
    并输出为符合要求格式的文档。
    """
    # 初始化配置管理器
    config_manager = ConfigManager(config_file)
    
    # 更新配置
    config_updates = {}
    if source_dir:
        config_updates['source_dir'] = source_dir
    if output_path:
        config_updates['output_path'] = output_path
    if output_format:
        config_updates['output_format'] = output_format
    if font_name:
        config_updates['font_name'] = font_name
    if font_size:
        config_updates['font_size'] = font_size
    if lines_per_page:
        config_updates['lines_per_page'] = lines_per_page
    if extensions:
        config_updates['file_extensions'] = list(extensions)
    if exclude_dirs:
        config_updates['exclude_dirs'] = list(exclude_dirs)
    
    config_manager.update_config(config_updates)
    
    # 获取最终配置
    config = config_manager.get_config()
    
    # 验证配置
    errors = config_manager.validate_config()
    if errors:
        for key, error in errors.items():
            click.echo(f"配置错误 ({key}): {error}", err=True)
        sys.exit(1)
    
    # 如果需要保存配置
    if save_config and config_file:
        if config_manager.save_config(config_file):
            click.echo(f"配置已保存到 {config_file}")
        else:
            click.echo(f"保存配置失败", err=True)
    
    # 开始处理
    click.echo(f"扫描目录: {config['source_dir']}")
    
    # 扫描文件
    all_files = scan_directory(config['source_dir'])
    
    # 排除指定目录
    all_files = exclude_directories(all_files, config_manager.get_exclude_dirs())
    
    # 按扩展名筛选
    filtered_files = filter_files_by_extension(all_files, config_manager.get_file_extensions())
    
    click.echo(f"找到 {len(filtered_files)} 个符合条件的源代码文件")
    
    # 分类文件
    classified_files = classify_files(
        filtered_files,
        config_manager.get_backend_identifiers(),
        config_manager.get_frontend_identifiers()
    )
    
    click.echo(f"后端文件: {len(classified_files['backend'])} 个")
    click.echo(f"前端文件: {len(classified_files['frontend'])} 个")
    
    # 处理代码文件
    merged_content, pages = process_code_files(classified_files, config['lines_per_page'])
    
    click.echo(f"合并后的代码总行数: {len(merged_content)}")
    click.echo(f"分页后的页数: {len(pages)}")
    
    # 生成文档
    output_file = generate_document(
        content=merged_content,
        output_path=config['output_path'],
        output_format=config['output_format'],
        font_name=config['font_name'],
        font_size=config['font_size']
    )
    
    click.echo(f"文档已生成: {output_file}")


if __name__ == '__main__':
    main() 