"""
代码处理模块

负责读取源代码文件内容，移除空行，添加文件名标识，并按照规定顺序合并所有代码。
"""

import os
from typing import List, Dict, Tuple

# 添加调试开关，与main.py保持一致
DEBUG = True

def debug_print(*args, **kwargs):
    """调试打印函数"""
    if DEBUG:
        print("[DEBUG]", *args, **kwargs)

def read_file_content(file_path: str) -> List[str]:
    """
    读取文件内容，返回所有非空行
    
    Args:
        file_path: 文件路径
    
    Returns:
        文件内容的非空行列表
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            # 读取所有非空行
            return [line.rstrip() for line in f if line.strip()]
    except Exception as e:
        debug_print(f"无法读取文件 {file_path}: {e}")
        return []


def add_file_header(file_path: str, content: List[str]) -> List[str]:
    """
    在代码内容前添加文件名标识
    
    Args:
        file_path: 文件路径
        content: 代码内容行列表
    
    Returns:
        添加了文件名标识的代码内容
    """
    # 获取相对路径作为文件标识
    file_name = os.path.basename(file_path)
    
    # 创建文件标识行 - 简化标识，只保留文件名
    header = [file_name]
    
    # 合并标识和内容
    return header + content


def sort_files_by_importance(files: List[str]) -> List[str]:
    """
    按重要性对文件进行排序
    
    Args:
        files: 文件路径列表
    
    Returns:
        排序后的文件路径列表
    """
    # 定义文件重要性评分函数
    def get_importance_score(file_path: str) -> int:
        # 文件名和路径
        file_name = os.path.basename(file_path).lower()
        file_path_lower = file_path.lower()
        
        # 初始分数
        score = 0
        
        # 根据文件名关键词增加分数
        important_keywords = ['main', 'core', 'app', 'index', 'server', 'api', 'config', 'model', 'controller']
        for i, keyword in enumerate(important_keywords):
            if keyword in file_name:
                score += (10 - i)  # 越靠前的关键词权重越高
        
        # 根据目录结构增加分数
        if 'core' in file_path_lower:
            score += 5
        if 'model' in file_path_lower:
            score += 4
        if 'service' in file_path_lower:
            score += 3
        if 'controller' in file_path_lower:
            score += 2
        if 'util' in file_path_lower:
            score += 1
            
        return score
    
    # 按重要性分数降序排序
    return sorted(files, key=get_importance_score, reverse=True)


def merge_code_files(files_dict: Dict[str, List[str]]) -> Tuple[List[str], List[str]]:
    """
    按照后端优先、前端其次的顺序合并所有代码文件
    
    Args:
        files_dict: 包含'backend'和'frontend'键的字典，值为对应的文件路径列表
                    如果包含'file_order'键，则使用该顺序合并文件
    
    Returns:
        元组(合并后的所有代码行, 处理的文件列表)
    """
    merged_content = []
    processed_files = []
    
    # 检查是否提供了自定义文件顺序
    if 'file_order' in files_dict and files_dict['file_order']:
        debug_print(f"使用自定义文件顺序合并代码 ({len(files_dict['file_order'])}个文件)")
        
        # 直接按照file_order中的顺序处理文件
        for file_path in files_dict['file_order']:
            # 检查文件是否在backend或frontend列表中
            if (file_path in files_dict.get('backend', []) or 
                file_path in files_dict.get('frontend', [])):
                content = read_file_content(file_path)
                if content:
                    merged_content.extend(add_file_header(file_path, content))
                    processed_files.append(file_path)
                    debug_print(f"处理文件: {file_path}")
    else:
        debug_print("使用自动排序合并代码")
        # 对后端文件按重要性排序
        backend_files = sort_files_by_importance(files_dict.get('backend', []))
        
        # 处理后端文件
        for file_path in backend_files:
            content = read_file_content(file_path)
            if content:
                merged_content.extend(add_file_header(file_path, content))
                processed_files.append(file_path)
        
        # 对前端文件按重要性排序
        frontend_files = sort_files_by_importance(files_dict.get('frontend', []))
        
        # 处理前端文件
        for file_path in frontend_files:
            content = read_file_content(file_path)
            if content:
                merged_content.extend(add_file_header(file_path, content))
                processed_files.append(file_path)
    
    return merged_content, processed_files


def split_into_pages(content: List[str], lines_per_page: int = 50) -> List[List[str]]:
    """
    将代码内容分割成固定行数的页面，确保每页不少于指定行数
    
    Args:
        content: 代码内容行列表
        lines_per_page: 每页的最少行数
    
    Returns:
        分页后的代码内容，每个元素是一页的内容
    """
    pages = []
    total_lines = len(content)
    
    for i in range(0, total_lines, lines_per_page):
        end = min(i + lines_per_page, total_lines)
        pages.append(content[i:end])
    
    return pages


def process_code_files(files_dict: Dict[str, List[str]], lines_per_page: int = 50) -> Tuple[List[str], List[List[str]], List[str]]:
    """
    处理所有代码文件，合并内容并分页
    
    Args:
        files_dict: 包含'backend'和'frontend'键的字典，值为对应的文件路径列表
        lines_per_page: 每页的最少行数
    
    Returns:
        元组(合并后的所有代码行, 分页后的代码内容, 处理的文件列表)
    """
    # 合并所有代码文件
    merged_content, processed_files = merge_code_files(files_dict)
    
    # 分页
    pages = split_into_pages(merged_content, lines_per_page)
    
    return merged_content, pages, processed_files 