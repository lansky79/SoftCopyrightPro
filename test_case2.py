"""
测试用例2：两行单行注释
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from sofcrtpro.code_processor import remove_large_comments

# 测试用例2：两行单行注释
test_case = [
    '# 这是第一行注释',
    '# 这是第二行注释',
    'def another_function():',
    '    pass'
]

print("原始内容:")
for line in test_case:
    print(f"  {line}")

result = remove_large_comments(test_case)
print("\n处理后结果:")
print(f"结果长度: {len(result)}")
for line in result:
    print(f"  {line}") 