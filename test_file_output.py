"""
使用文件输出的测试
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from sofcrtpro.code_processor import remove_large_comments

def test_and_write_to_file(test_name, test_case, output_file):
    with open(output_file, 'a', encoding='utf-8') as f:
        f.write(f"\n\n{test_name}\n")
        f.write("-" * 40 + "\n")
        f.write("原始内容:\n")
        for line in test_case:
            f.write(f"  {line}\n")
        
        result = remove_large_comments(test_case)
        f.write("\n处理后结果:\n")
        f.write(f"结果长度: {len(result)}\n")
        for line in result:
            f.write(f"  {line}\n")

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

# 清空输出文件
output_file = "test_results.txt"
with open(output_file, 'w', encoding='utf-8') as f:
    f.write("测试结果\n")
    f.write("=" * 40 + "\n")

# 运行测试
test_and_write_to_file("测试用例1：Python三引号注释（5行）", test_case1, output_file)
test_and_write_to_file("测试用例2：两行单行注释", test_case2, output_file)
test_and_write_to_file("测试用例3：混合注释", test_case3, output_file)
test_and_write_to_file("测试用例4：单行注释", test_case4, output_file)

print(f"测试结果已写入文件: {output_file}") 