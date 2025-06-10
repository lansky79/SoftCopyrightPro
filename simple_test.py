"""
简单测试注释删除功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from sofcrtpro.code_processor import remove_large_comments

def test_case(name, content):
    print(f"\n{name}")
    print("-" * 40)
    print("原始内容:")
    for line in content:
        print(f"  {line}")
    
    result = remove_large_comments(content)
    print("\n处理后结果:")
    print(f"结果长度: {len(result)}")
    for line in result:
        print(f"  {line}")

# 测试用例1：Python三引号注释（5行）
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

# 运行测试
test_case("测试用例1：Python三引号注释（5行）", test_case1)
test_case("测试用例2：两行单行注释", test_case2)
test_case("测试用例3：混合注释", test_case3)
test_case("测试用例4：单行注释", test_case4) 