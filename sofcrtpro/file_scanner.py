"""
文件扫描与筛选模块

负责扫描指定目录下的源代码文件，根据后缀名筛选，并将文件分类为前端和后端。
"""

import os
import pathlib
from typing import List, Dict, Set, Tuple


def scan_directory(directory: str, file_extensions: Set[str] = None) -> List[str]:
    """
    扫描指定目录及其子目录，返回符合后缀名要求的文件列表
    
    Args:
        directory: 要扫描的目录路径
        file_extensions: 要包含的文件后缀名集合，如{'.py', '.java', '.js'}
                        如果为None，则包含所有文件
    
    Returns:
        符合条件的文件路径列表
    """
    if file_extensions is None:
        file_extensions = set()
    
    matched_files = []
    
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_ext = os.path.splitext(file)[1].lower()
            
            # 如果file_extensions为空或文件后缀在指定列表中
            if not file_extensions or file_ext in file_extensions:
                matched_files.append(file_path)
    
    return matched_files


def classify_files(
    files: List[str], 
    backend_identifiers: Set[str] = None, 
    frontend_identifiers: Set[str] = None
) -> Dict[str, List[str]]:
    """
    将文件分类为前端和后端
    
    Args:
        files: 文件路径列表
        backend_identifiers: 后端文件的标识（后缀或目录名）
        frontend_identifiers: 前端文件的标识（后缀或目录名）
    
    Returns:
        包含'backend'和'frontend'键的字典，值为对应的文件列表
    """
    if backend_identifiers is None:
        # 默认后端文件后缀
        backend_identifiers = {'.py', '.java', '.c', '.cpp', '.cs', '.go', '.rb', '.php'}
    
    if frontend_identifiers is None:
        # 默认前端文件后缀
        frontend_identifiers = {'.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.vue', '.scss', '.less'}
    
    result = {
        'backend': [],
        'frontend': []
    }
    
    for file_path in files:
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # 检查文件是否为后端文件
        if file_ext in backend_identifiers:
            result['backend'].append(file_path)
        # 检查文件是否为前端文件
        elif file_ext in frontend_identifiers:
            result['frontend'].append(file_path)
        # 如果无法确定，根据路径中的关键词进行判断
        else:
            path_lower = file_path.lower()
            if any(ident in path_lower for ident in ['backend', 'server', 'api']):
                result['backend'].append(file_path)
            elif any(ident in path_lower for ident in ['frontend', 'client', 'ui', 'web']):
                result['frontend'].append(file_path)
            else:
                # 无法确定的文件默认归为后端
                result['backend'].append(file_path)
    
    return result


def get_file_info(files: List[str]) -> List[Tuple[str, int]]:
    """
    获取文件信息，包括文件路径和代码行数（不包括空行）
    
    Args:
        files: 文件路径列表
    
    Returns:
        包含(文件路径, 行数)元组的列表
    """
    file_info = []
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                # 计算非空行数量
                line_count = sum(1 for line in f if line.strip())
            file_info.append((file_path, line_count))
        except Exception as e:
            print(f"无法读取文件 {file_path}: {e}")
            file_info.append((file_path, 0))
    
    return file_info 