"""
测试注释删除功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from sofcrtpro.code_processor import remove_large_comments

def print_test_case(case_num, lines):
    print(f"测试用例{case_num}原始内容:")
    for i, line in enumerate(lines):
        print(f"  {i}: {repr(line)}")

def test_comment_removal():
    """
    测试删除大段注释的功能
    """
    # 测试用例1：Python三引号注释（5行注释）
    test_case1 = [
        '"""',
        '1. 分析当前系统中存储注册信息的多个位置',
        '2. 评估这种设计是否存在冗余',
        '3. 提供更合理的设计建议',
        '"""',
        'def test_function():',
        '    # 这是一个单行注释',
        '    print("Hello, World!")'
    ]
    
    # 测试用例2：两行单行注释
    test_case2 = [
        '# 这是第一行注释',
        '# 这是第二行注释',
        'def another_function():',
        '    pass'
    ]
    
    # 测试用例3：混合注释
    test_case3 = [
        '"""',
        '这是一个多行注释',
        '"""',
        '# 这是一个单行注释',
        '# 这是另一个单行注释',
        '# 这是第三个单行注释',
        'def third_function():',
        '    pass'
    ]
    
    # 测试用例4：单行注释
    test_case4 = [
        'def single_comment_function():',
        '    # 这是一个单行注释',
        '    return True'
    ]
    
    # 测试用例1
    print_test_case(1, test_case1)
    print("测试用例1结果:")
    result1 = remove_large_comments(test_case1)
    print(f"结果长度: {len(result1)}")
    for i, line in enumerate(result1):
        print(f"  {i}: {repr(line)}")
    
    # 测试用例2
    print("\n" + "-"*30)
    print_test_case(2, test_case2)
    print("测试用例2结果:")
    result2 = remove_large_comments(test_case2)
    print(f"结果长度: {len(result2)}")
    for i, line in enumerate(result2):
        print(f"  {i}: {repr(line)}")
    
    # 测试用例3
    print("\n" + "-"*30)
    print_test_case(3, test_case3)
    print("测试用例3结果:")
    result3 = remove_large_comments(test_case3)
    print(f"结果长度: {len(result3)}")
    for i, line in enumerate(result3):
        print(f"  {i}: {repr(line)}")
    
    # 测试用例4
    print("\n" + "-"*30)
    print_test_case(4, test_case4)
    print("测试用例4结果:")
    result4 = remove_large_comments(test_case4)
    print(f"结果长度: {len(result4)}")
    for i, line in enumerate(result4):
        print(f"  {i}: {repr(line)}")

if __name__ == "__main__":
    test_comment_removal() 