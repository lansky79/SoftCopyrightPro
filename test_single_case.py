"""
测试单个用例
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from sofcrtpro.code_processor import remove_large_comments

# 测试用例4：单行注释
test_case = [
    'def single_comment_function():',
    '    # 这是一个单行注释',
    '    return True'
]

print("原始内容:")
for line in test_case:
    print(f"  {line}")

result = remove_large_comments(test_case)
print("\n处理后结果:")
print(f"结果长度: {len(result)}")
for line in result:
    print(f"  {line}") 