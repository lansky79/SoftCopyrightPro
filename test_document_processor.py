#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试文档处理功能
测试document_processor.py中的process_document函数是否能正确生成两个文件：
1. 处理后的文档
2. 删除内容记录文档
"""

import os
import sys
import datetime
from sofcrtpro.document_processor import process_document

print("===========================================================")
print("=============== 测试文档处理器开始执行 =====================")
print("===========================================================")

def test_document_processor():
    """测试文档处理功能"""
    print("开始测试文档处理功能...")
    
    # 设置输入文件路径
    input_file = "output/档案检索系统V1.0_06100111.docx"
    
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"错误: 输入文件 {input_file} 不存在")
        return
    
    # 生成输出文件名，添加时间戳避免文件冲突
    timestamp = datetime.datetime.now().strftime("%m%d%H%M%S")
    output_dir = "output"
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_file = f"{output_dir}/{base_name}_{timestamp}_去注释.docx"
    deleted_content_file = f"{output_dir}/{base_name}_{timestamp}_被删除.docx"
    
    # 处理文档
    print(f"开始处理文档: {input_file}")
    print(f"输出文件: {output_file}")
    print(f"删除内容文件: {deleted_content_file}")
    
    try:
        # 调用处理函数
        output_file, deleted_file, stats = process_document(
            input_file,
            output_file,
            deleted_content_file,
            remove_filenames=True,
            remove_large_comments=True,
            remove_english_comments=True
        )
        
        # 检查输出文件是否生成
        output_exists = os.path.exists(output_file)
        deleted_content_exists = os.path.exists(deleted_file)
        
        print(f"输出文件已生成: {output_exists}")
        print(f"删除内容文件已生成: {deleted_content_exists}")
        
        # 验证文件内容和大小
        if output_exists:
            print(f"输出文件大小: {os.path.getsize(output_file)} 字节")
        
        if deleted_content_exists:
            print(f"删除内容文件大小: {os.path.getsize(deleted_file)} 字节")
        
        # 打印处理统计信息
        print("处理统计:")
        print(f"总行数: {stats['total_lines']}")
        print(f"删除的文件名: {stats['deleted_filenames']}")
        print(f"删除的大段注释: {stats['deleted_large_comments']}")
        print(f"删除的英文注释: {stats['deleted_english_comments']}")
        print(f"删除的随机注释: {stats['deleted_random_comments']}")
        print(f"剩余行数: {stats['remaining_lines']}")
        
    except Exception as e:
        print(f"处理文档时出错: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_document_processor() 