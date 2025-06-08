"""
文件操作工具模块

提供文件读写和目录操作的辅助功能。
"""

import os
import shutil
from typing import List, Set, Optional


def ensure_dir_exists(directory: str) -> bool:
    """
    确保目录存在，如果不存在则创建
    
    Args:
        directory: 目录路径
    
    Returns:
        是否成功创建或目录已存在
    """
    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except Exception as e:
        print(f"创建目录失败: {e}")
        return False


def list_files(directory: str, recursive: bool = True) -> List[str]:
    """
    列出目录中的所有文件
    
    Args:
        directory: 目录路径
        recursive: 是否递归搜索子目录
    
    Returns:
        文件路径列表
    """
    files = []
    
    if recursive:
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                files.append(os.path.join(root, filename))
    else:
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isfile(item_path):
                files.append(item_path)
    
    return files


def filter_files_by_extension(files: List[str], extensions: Set[str]) -> List[str]:
    """
    按文件扩展名筛选文件
    
    Args:
        files: 文件路径列表
        extensions: 文件扩展名集合
    
    Returns:
        筛选后的文件路径列表
    """
    if not extensions:
        return files
    
    return [f for f in files if os.path.splitext(f)[1].lower() in extensions]


def exclude_directories(files: List[str], exclude_dirs: Set[str]) -> List[str]:
    """
    排除指定目录中的文件
    
    Args:
        files: 文件路径列表
        exclude_dirs: 要排除的目录名集合
    
    Returns:
        排除后的文件路径列表
    """
    if not exclude_dirs:
        return files
    
    result = []
    for file_path in files:
        # 检查文件路径中是否包含要排除的目录
        if not any(f"/{exclude_dir}/" in file_path.replace("\\", "/") for exclude_dir in exclude_dirs):
            result.append(file_path)
    
    return result


def get_relative_path(file_path: str, base_dir: str) -> str:
    """
    获取相对于基础目录的相对路径
    
    Args:
        file_path: 文件的绝对路径
        base_dir: 基础目录
    
    Returns:
        相对路径
    """
    try:
        return os.path.relpath(file_path, base_dir)
    except:
        return file_path


def copy_file(src: str, dst: str) -> bool:
    """
    复制文件
    
    Args:
        src: 源文件路径
        dst: 目标文件路径
    
    Returns:
        是否成功复制
    """
    try:
        # 确保目标目录存在
        ensure_dir_exists(os.path.dirname(dst))
        
        # 复制文件
        shutil.copy2(src, dst)
        return True
    except Exception as e:
        print(f"复制文件失败: {e}")
        return False


def read_file(file_path: str, encoding: str = 'utf-8') -> Optional[str]:
    """
    读取文件内容
    
    Args:
        file_path: 文件路径
        encoding: 文件编码
    
    Returns:
        文件内容，如果读取失败则返回None
    """
    try:
        with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
            return f.read()
    except Exception as e:
        print(f"读取文件失败: {e}")
        return None


def write_file(file_path: str, content: str, encoding: str = 'utf-8') -> bool:
    """
    写入文件内容
    
    Args:
        file_path: 文件路径
        content: 要写入的内容
        encoding: 文件编码
    
    Returns:
        是否成功写入
    """
    try:
        # 确保目录存在
        ensure_dir_exists(os.path.dirname(file_path))
        
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"写入文件失败: {e}")
        return False 