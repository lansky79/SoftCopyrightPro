"""
文本处理工具模块

提供文本格式化和处理的辅助功能。
"""

import re
from typing import List, Optional


def remove_empty_lines(text: str) -> str:
    """
    移除文本中的空行
    
    Args:
        text: 输入文本
    
    Returns:
        移除空行后的文本
    """
    # 移除只包含空白字符的行
    return '\n'.join(line for line in text.splitlines() if line.strip())


def remove_empty_lines_from_list(lines: List[str]) -> List[str]:
    """
    移除行列表中的空行
    
    Args:
        lines: 行列表
    
    Returns:
        移除空行后的行列表
    """
    return [line for line in lines if line.strip()]


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    截断文本到指定长度
    
    Args:
        text: 输入文本
        max_length: 最大长度
        suffix: 截断后添加的后缀
    
    Returns:
        截断后的文本
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def count_non_empty_lines(text: str) -> int:
    """
    计算文本中的非空行数
    
    Args:
        text: 输入文本
    
    Returns:
        非空行数
    """
    return len([line for line in text.splitlines() if line.strip()])


def format_file_header(file_path: str, line_length: int = 80) -> str:
    """
    格式化文件头部标识
    
    Args:
        file_path: 文件路径
        line_length: 分隔线长度
    
    Returns:
        格式化后的文件头部标识
    """
    separator = "=" * line_length
    return f"{separator}\n文件: {file_path}\n{separator}"


def split_text_into_chunks(text: str, chunk_size: int) -> List[str]:
    """
    将文本分割成固定大小的块
    
    Args:
        text: 输入文本
        chunk_size: 块大小（字符数）
    
    Returns:
        文本块列表
    """
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]


def split_lines_into_pages(lines: List[str], lines_per_page: int) -> List[List[str]]:
    """
    将行列表分割成页面
    
    Args:
        lines: 行列表
        lines_per_page: 每页的行数
    
    Returns:
        页面列表，每个页面是一个行列表
    """
    pages = []
    total_lines = len(lines)
    
    for i in range(0, total_lines, lines_per_page):
        end = min(i + lines_per_page, total_lines)
        pages.append(lines[i:end])
    
    return pages


def sanitize_filename(filename: str) -> str:
    """
    清理文件名，移除不允许的字符
    
    Args:
        filename: 原始文件名
    
    Returns:
        清理后的文件名
    """
    # 移除不允许的字符
    sanitized = re.sub(r'[\\/*?:"<>|]', '_', filename)
    
    # 移除前导和尾随空格
    sanitized = sanitized.strip()
    
    # 如果文件名为空，使用默认名称
    if not sanitized:
        sanitized = "unnamed_file"
    
    return sanitized


def extract_extension(file_path: str) -> Optional[str]:
    """
    提取文件扩展名
    
    Args:
        file_path: 文件路径
    
    Returns:
        文件扩展名（包括点），如果没有扩展名则返回None
    """
    match = re.search(r'\.([^.\\/:*?"<>|]+)$', file_path)
    if match:
        return f".{match.group(1)}"
    return None 