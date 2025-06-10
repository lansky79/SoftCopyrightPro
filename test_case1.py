"""
测试用例1：Python三引号注释
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from sofcrtpro.code_processor import remove_large_comments

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

print("原始内容:")
for i, line in enumerate(test_case1):
    print(f"  {i}: {line}")

print("\n处理后结果:")
result = remove_large_comments(test_case1)
print(f"结果长度: {len(result)}")
for i, line in enumerate(result):
    print(f"  {i}: {line}") 