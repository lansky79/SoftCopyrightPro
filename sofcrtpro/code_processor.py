"""
代码处理模块

负责读取源代码文件内容，移除空行，添加文件名标识，并按照规定顺序合并所有代码。
"""

import os
import re
import random
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


def is_comment_line(line: str) -> bool:
    """
    判断一行是否为注释行
    
    Args:
        line: 代码行
    
    Returns:
        是否为注释行
    """
    # 去除前导空格
    stripped_line = line.strip()
    
    # 如果是空行，不是注释
    if not stripped_line:
        return False
    
    # 检查是否为Python注释
    if stripped_line.startswith('#'):
        return True
    
    # 检查是否为Python三引号注释（开始或结束）
    if stripped_line.startswith('"""') or stripped_line.startswith("'''"):
        return True
    if stripped_line.endswith('"""') or stripped_line.endswith("'''"):
        return True
    
    # 检查是否为C/C++/Java/JavaScript/CSS等语言的单行注释
    if stripped_line.startswith('//'):
        return True
    
    # 检查是否为HTML/XML注释
    if stripped_line.startswith('<!--') and stripped_line.endswith('-->'):
        return True
    
    # 检查是否为整行的C/C++/Java多行注释
    if (stripped_line.startswith('/*') and stripped_line.endswith('*/')) or \
       (stripped_line.startswith('/**') and stripped_line.endswith('*/')):
        return True
    
    # 检查是否为多行注释的一部分
    if stripped_line.startswith('*') and not stripped_line.startswith('*/'):
        return True
    
    return False


def is_english_text(text: str) -> bool:
    """
    判断文本是否为英文
    
    Args:
        text: 要判断的文本
    
    Returns:
        是否为英文
    """
    # 移除所有标点符号和数字
    text = re.sub(r'[0-9\!\@\#\$\%\^\&\*\(\)\_\+\-\=\[\]\{\}\;\:\"\'\,\<\.\>\/\?\\\|\`\~]', ' ', text)
    # 分割成单词
    words = [word.strip() for word in text.split() if word.strip()]
    
    if not words:
        return False
    
    # 统计ASCII字符（主要是英文字母）和非ASCII字符
    english_chars = 0
    non_english_chars = 0
    
    for word in words:
        for char in word:
            if ord(char) < 128:  # ASCII范围内的字符
                english_chars += 1
            else:
                non_english_chars += 1
    
    total_chars = english_chars + non_english_chars
    
    # 如果有非英文字符且超过阈值，则不认为是英文
    if non_english_chars > 0 and non_english_chars / total_chars > 0.1:
        return False
    
    # 如果ASCII字符占比超过90%，则认为是英文
    return total_chars > 0 and (english_chars / total_chars) > 0.9


def is_end_of_line_comment(line: str) -> bool:
    """
    判断是否为行尾注释
    
    Args:
        line: 代码行
    
    Returns:
        是否为行尾注释
    """
    # 如果行中包含代码和注释，则为行尾注释
    stripped = line.strip()
    
    # 检查是否为Python行尾注释
    if '#' in line and not stripped.startswith('#'):
        return True
    
    # 检查是否为C/C++/Java等语言的行尾注释
    if '//' in line and not stripped.startswith('//'):
        return True
    
    return False


def remove_large_comments(content: List[str], remove_english_comments: bool = False) -> List[str]:
    """
    删除大段注释（两行及以上连续的注释定义为大段注释）
    
    Args:
        content: 代码内容行列表
        remove_english_comments: 是否删除所有英文注释，默认为False
    
    Returns:
        处理后的代码内容
    """
    if not content:
        return []
    
    # 用于存储结果
    result = []
    
    # 标记注释块的开始和结束
    comment_blocks = []
    in_comment_block = False
    block_start = -1
    
    # 标记是否在多行注释中
    in_py_triple_quotes = False
    in_c_multiline = False
    
    # 第一遍：标记所有非行尾注释块
    for i, line in enumerate(content):
        # 跳过行尾注释，不将其视为注释块的一部分
        if is_end_of_line_comment(line):
            continue
        
        stripped = line.strip()
        is_comment = False
        
        # 处理Python三引号注释
        if in_py_triple_quotes:
            is_comment = True
            if stripped.endswith('"""') or stripped.endswith("'''"):
                in_py_triple_quotes = False
        elif stripped.startswith('"""') or stripped.startswith("'''"):
            is_comment = True
            if not (stripped.endswith('"""') and stripped.count('"""') > 1) and \
               not (stripped.endswith("'''") and stripped.count("'''") > 1):
                in_py_triple_quotes = True
        
        # 处理C风格多行注释
        elif in_c_multiline:
            is_comment = True
            if "*/" in stripped:
                in_c_multiline = False
        elif stripped.startswith('/*'):
            is_comment = True
            if "*/" not in stripped:
                in_c_multiline = True
        
        # 处理单行注释
        elif stripped.startswith('#') or stripped.startswith('//'):
            is_comment = True
        
        # 处理注释块的开始和结束
        if is_comment:
            if not in_comment_block:
                in_comment_block = True
                block_start = i
        else:
            if in_comment_block:
                in_comment_block = False
                comment_blocks.append((block_start, i - 1))
                block_start = -1
    
    # 如果文件以注释块结束，需要添加最后一个块
    if in_comment_block:
        comment_blocks.append((block_start, len(content) - 1))
    
    # 第二遍：处理每一行
    i = 0
    while i < len(content):
        line = content[i]
        
        # 处理行尾注释 - 始终保留
        if is_end_of_line_comment(line):
            result.append(line)
            i += 1
            continue
        
        # 检查当前行是否在任何注释块中
        in_block = False
        block_length = 0
        block_end = -1
        current_block_start = -1
        
        for start, end in comment_blocks:
            if start <= i <= end:
                in_block = True
                block_length = end - start + 1
                block_end = end
                current_block_start = start
                break
        
        if not in_block:
            # 不在任何注释块中，直接添加
            result.append(line)
            i += 1
        else:
            # 在注释块中
            
            # 1. 如果是单行注释，根据语言类型决定是否保留
            if block_length == 1:
                # 如果需要删除英文注释，检查是否为英文
                if remove_english_comments:
                    stripped_line = line.strip()
                    comment_text = ""
                    
                    # 提取注释内容
                    if stripped_line.startswith('#'):
                        comment_text = stripped_line[1:].strip()
                    elif stripped_line.startswith('//'):
                        comment_text = stripped_line[2:].strip()
                    elif stripped_line.startswith('/*') and stripped_line.endswith('*/'):
                        comment_text = stripped_line[2:-2].strip()
                    elif stripped_line.startswith('"""') and stripped_line.endswith('"""'):
                        comment_text = stripped_line[3:-3].strip()
                    elif stripped_line.startswith("'''") and stripped_line.endswith("'''"):
                        comment_text = stripped_line[3:-3].strip()
                    
                    # 如果是英文注释，跳过
                    if comment_text and is_english_text(comment_text):
                        i += 1
                        continue
                
                # 保留单行注释
                result.append(line)
                i += 1
            else:
                # 2. 对于多行注释块，检查是否为英文
                if remove_english_comments:
                    # 提取整个注释块的文本
                    block_text = ""
                    for j in range(current_block_start, block_end + 1):
                        block_line = content[j].strip()
                        # 去除注释符号
                        if block_line.startswith('"""'):
                            block_line = block_line[3:]
                        if block_line.endswith('"""'):
                            block_line = block_line[:-3]
                        if block_line.startswith("'''"):
                            block_line = block_line[3:]
                        if block_line.endswith("'''"):
                            block_line = block_line[:-3]
                        if block_line.startswith('//'):
                            block_line = block_line[2:]
                        if block_line.startswith('#'):
                            block_line = block_line[1:]
                        if block_line.startswith('/*'):
                            block_line = block_line[2:]
                        if block_line.endswith('*/'):
                            block_line = block_line[:-2]
                        if block_line.startswith('*') and not block_line.startswith('*/'):
                            block_line = block_line[1:]
                        block_text += block_line + " "
                    
                    # 如果是英文注释块，跳过整个块
                    if block_text.strip() and is_english_text(block_text.strip()):
                        i = block_end + 1
                        continue
                
                # 默认情况下，删除大段注释
                i = block_end + 1
    
    return result


def remove_single_comments_evenly(content: List[str], remove_ratio: int = 3) -> List[str]:
    """
    随机均匀删除单行注释
    
    Args:
        content: 代码内容行列表
        remove_ratio: 删除比例，例如3表示每3个单行注释删除1个
    
    Returns:
        处理后的代码内容
    """
    result = []
    comment_indices = []
    
    # 找出所有单行注释的索引
    for i, line in enumerate(content):
        if is_comment_line(line):
            # 检查前后行是否也是注释，如果是，则可能是多行注释的一部分
            prev_is_comment = i > 0 and is_comment_line(content[i-1])
            next_is_comment = i < len(content) - 1 and is_comment_line(content[i+1])
            
            # 如果前后都不是注释，或者只有一边是注释，则视为单行注释
            if not (prev_is_comment and next_is_comment):
                comment_indices.append(i)
    
    # 计算要删除的注释数量
    if remove_ratio <= 0:
        remove_ratio = 3  # 默认值
    comments_to_remove = len(comment_indices) // remove_ratio
    
    # 随机选择要删除的注释
    if comments_to_remove > 0 and comment_indices:
        indices_to_remove = set(random.sample(comment_indices, comments_to_remove))
    else:
        indices_to_remove = set()
    
    # 构建结果，跳过要删除的注释
    for i, line in enumerate(content):
        if i not in indices_to_remove:
            result.append(line)
    
    return result


def merge_code_files(files_dict: Dict[str, List[str]], include_filename: bool = True) -> Tuple[List[str], List[str]]:
    """
    按照后端优先、前端其次的顺序合并所有代码文件
    
    Args:
        files_dict: 包含'backend'和'frontend'键的字典，值为对应的文件路径列表
                    如果包含'file_order'键，则使用该顺序合并文件
        include_filename: 是否在代码内容前添加文件名标识，默认为True
    
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
                    if include_filename:
                        merged_content.extend(add_file_header(file_path, content))
                    else:
                        merged_content.extend(content)  # 直接添加内容，不包含文件名
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
                if include_filename:
                    merged_content.extend(add_file_header(file_path, content))
                else:
                    merged_content.extend(content)  # 直接添加内容，不包含文件名
                processed_files.append(file_path)
        
        # 对前端文件按重要性排序
        frontend_files = sort_files_by_importance(files_dict.get('frontend', []))
        
        # 处理前端文件
        for file_path in frontend_files:
            content = read_file_content(file_path)
            if content:
                if include_filename:
                    merged_content.extend(add_file_header(file_path, content))
                else:
                    merged_content.extend(content)  # 直接添加内容，不包含文件名
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


def process_code_files(files_dict: Dict[str, List[str]], lines_per_page: int = 50, include_filename: bool = True, 
                       remove_large_comments_flag: bool = False, remove_comments_ratio: int = 0,
                       remove_english_comments_flag: bool = False) -> Tuple[List[str], List[List[str]], List[str]]:
    """
    处理所有代码文件，合并内容并分页
    
    Args:
        files_dict: 包含'backend'和'frontend'键的字典，值为对应的文件路径列表
        lines_per_page: 每页的最少行数
        include_filename: 是否在代码内容前添加文件名标识，默认为True
        remove_large_comments_flag: 是否删除大段注释，默认为False
        remove_comments_ratio: 随机删除单行注释的比例，0表示不删除
        remove_english_comments_flag: 是否删除所有英文注释，默认为False
    
    Returns:
        元组(合并后的所有代码行, 分页后的代码内容, 处理的文件列表)
    """
    # 合并所有代码文件
    merged_content, processed_files = merge_code_files(files_dict, include_filename)
    
    # 删除大段注释
    if remove_large_comments_flag:
        merged_content = remove_large_comments(merged_content, remove_english_comments_flag)
    
    # 随机均匀删除单行注释
    if remove_comments_ratio > 0:
        merged_content = remove_single_comments_evenly(merged_content, remove_comments_ratio)
    
    # 分页
    pages = split_into_pages(merged_content, lines_per_page)
    
    return merged_content, pages, processed_files 