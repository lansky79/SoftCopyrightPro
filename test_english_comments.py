"""
测试英文注释删除功能
Test English Comments Removal Feature
"""

import sys
import os
import re

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from sofcrtpro.code_processor import remove_large_comments, is_english_text

# 创建一个优化版的英文文本识别函数
def improved_is_english_text(text: str) -> bool:
    """
    改进的英文文本识别函数
    
    Args:
        text: 要判断的文本
    
    Returns:
        是否为英文文本
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

# 创建测试用例
def create_test_cases():
    """
    创建各种注释类型的测试用例
    Creates various types of comment test cases
    """
    # 测试用例1：中文单行注释
    chinese_single_line = [
        'def chinese_function():',
        '    # 这是一个中文注释',
        '    # 这是第二行中文注释',
        '    print("Hello")'
    ]
    
    # 测试用例2：英文单行注释
    english_single_line = [
        'def english_function():',
        '    # This is an English comment',
        '    # This is a second line of English comment',
        '    print("Hello")'
    ]
    
    # 测试用例3：混合单行注释（中英文混合）
    mixed_single_line = [
        'def mixed_function():',
        '    # 这是中英文混合注释 This is a mixed comment',
        '    # Another mixed comment 另一个混合注释',
        '    print("Hello")'
    ]
    
    # 测试用例4：中文多行注释
    chinese_multi_line = [
        'def chinese_multi_function():',
        '    """',
        '    这是一个中文的多行注释',
        '    包含了多行中文内容',
        '    用于测试多行注释的处理',
        '    """',
        '    print("Hello")'
    ]
    
    # 测试用例5：英文多行注释
    english_multi_line = [
        'def english_multi_function():',
        '    """',
        '    This is a multi-line English comment',
        '    It contains multiple lines of English content',
        '    Used for testing multi-line comment processing',
        '    """',
        '    print("Hello")'
    ]
    
    # 测试用例6：混合多行注释（中英文混合）
    mixed_multi_line = [
        'def mixed_multi_function():',
        '    """',
        '    这是中英文混合的多行注释 This is a mixed multi-line comment',
        '    第二行混合内容 Second line of mixed content',
        '    第三行混合内容 Third line of mixed content',
        '    """',
        '    print("Hello")'
    ]
    
    # 测试用例7：C风格单行注释
    c_style_single_line = [
        'void c_function() {',
        '    // 这是C风格的中文注释',
        '    // This is a C-style English comment',
        '    printf("Hello");',
        '}'
    ]
    
    # 测试用例8：C风格多行注释
    c_style_multi_line = [
        'void c_multi_function() {',
        '    /*',
        '     * 这是C风格的中文多行注释',
        '     * This is a C-style multi-line English comment',
        '     */',
        '    printf("Hello");',
        '}'
    ]
    
    # 测试用例9：源代码中的文本字符串（不应被识别为注释）
    code_strings = [
        'def string_function():',
        '    chinese_text = "这是中文字符串，不是注释"',
        '    english_text = "This is an English string, not a comment"',
        '    print(chinese_text, english_text)'
    ]
    
    # 测试用例10：单行注释中的代码示例
    code_in_comments = [
        'def code_in_comments():',
        '    # 这是一个包含代码示例的注释: x = 10',
        '    # This is a comment with code example: x = 10',
        '    x = 20  # 这是行尾注释',
        '    y = 30  # This is an end-of-line comment',
        '    return x + y'
    ]
    
    return {
        "中文单行注释": chinese_single_line,
        "英文单行注释": english_single_line,
        "混合单行注释": mixed_single_line,
        "中文多行注释": chinese_multi_line,
        "英文多行注释": english_multi_line,
        "混合多行注释": mixed_multi_line,
        "C风格单行注释": c_style_single_line,
        "C风格多行注释": c_style_multi_line,
        "源代码字符串": code_strings,
        "注释中的代码": code_in_comments
    }

def test_is_english_text():
    """测试is_english_text函数的准确性"""
    test_texts = [
        ("This is pure English text", True),
        ("这是纯中文文本", False),
        ("This is mixed text with 中文", False),
        ("80% English text with some 中文词语", False),
        ("20% 英文 with mostly 中文内容测试", False),
        ("# This is a comment", True),
        ("# 这是一个注释", False),
        ("# This is a comment with 中文", False),
        ("# 这是一个带有English的注释", False),
        ("", False)  # 空字符串
    ]
    
    print("测试is_english_text函数:")
    print("-" * 50)
    
    print("原始函数:")
    for i, (text, expected) in enumerate(test_texts, 1):
        result = is_english_text(text)
        status = "✓" if result == expected else "✗"
        print(f"{i}. [{status}] 文本: {text}")
        print(f"   期望结果: {expected}, 实际结果: {result}")
    
    print("\n改进函数:")
    for i, (text, expected) in enumerate(test_texts, 1):
        result = improved_is_english_text(text)
        status = "✓" if result == expected else "✗"
        print(f"{i}. [{status}] 文本: {text}")
        print(f"   期望结果: {expected}, 实际结果: {result}")
    
    print()

def create_custom_test_for_english_comments():
    """创建一个自定义测试，专门用于测试英文注释删除功能"""
    # 测试用例：包含各种类型的注释
    test_code = [
        '"""',
        'This is a file-level docstring in English',
        '这是中文文件级文档字符串',
        '"""',
        '',
        '# 这是中文单行注释',
        '# This is an English single-line comment',
        '',
        'def test_function():',
        '    """',
        '    This is an English function docstring',
        '    这是中文函数文档字符串',
        '    """',
        '    # 这是函数内的中文注释',
        '    # This is an English comment inside a function',
        '    x = 10  # 这是中文行尾注释',
        '    y = 20  # This is an English end-of-line comment',
        '    return x + y',
        '',
        '"""',
        'Another multi-line English comment',
        '另一个多行中文注释',
        '"""',
        '',
        '# 混合注释 with English and 中文',
        '# English comment with 一些中文词语',
        '',
        'class TestClass:',
        '    """',
        '    This is an English class docstring',
        '    这是中文类文档字符串',
        '    """',
        '    def __init__(self):',
        '        """',
        '        This is an English method docstring',
        '        这是中文方法文档字符串',
        '        """',
        '        self.value = 100  # 初始化值',
        '        # This is a comment in a method',
        '        # 这是方法中的注释'
    ]
    
    return test_code

def test_remove_english_comments():
    """测试remove_large_comments函数的英文注释删除功能"""
    test_cases = create_test_cases()
    
    print("测试英文注释删除功能:")
    print("=" * 50)
    
    for case_name, content in test_cases.items():
        print(f"\n测试用例: {case_name}")
        print("-" * 50)
        
        print("原始内容:")
        for line in content:
            print(f"  {line}")
        
        # 测试保留所有注释
        result1 = remove_large_comments(content, remove_english_comments=False)
        
        print("\n结果1（不删除英文注释）:")
        for line in result1:
            print(f"  {line}")
        
        # 测试删除英文注释
        result2 = remove_large_comments(content, remove_english_comments=True)
        
        print("\n结果2（删除英文注释）:")
        for line in result2:
            print(f"  {line}")
        
        print("\n" + "=" * 50)
    
    # 测试自定义测试用例
    print("\n\n自定义测试用例:")
    print("=" * 50)
    
    custom_test = create_custom_test_for_english_comments()
    
    print("原始内容:")
    for line in custom_test:
        print(f"  {line}")
    
    # 测试保留所有注释
    result1 = remove_large_comments(custom_test, remove_english_comments=False)
    
    print("\n结果1（不删除英文注释）:")
    for line in result1:
        print(f"  {line}")
    
    # 测试删除英文注释
    result2 = remove_large_comments(custom_test, remove_english_comments=True)
    
    print("\n结果2（删除英文注释）:")
    for line in result2:
        print(f"  {line}")

def test_single_line_comments():
    """专门测试单行注释的处理"""
    print("\n\n单行注释测试:")
    print("=" * 50)
    
    # 创建一个包含各种单行注释的测试用例
    test_code = [
        '# 这是中文单行注释',
        '# This is an English single-line comment',
        'x = 10  # 这是中文行尾注释',
        'y = 20  # This is an English end-of-line comment',
        '# 混合注释 with English and 中文',
        '# English comment with 一些中文词语',
        'z = x + y  # 计算结果 result calculation'
    ]
    
    print("原始内容:")
    for line in test_code:
        print(f"  {line}")
    
    # 测试保留所有注释
    result1 = remove_large_comments([line for line in test_code], remove_english_comments=False)
    
    print("\n结果1（不删除英文注释）:")
    for line in result1:
        print(f"  {line}")
    
    # 测试删除英文注释
    result2 = remove_large_comments([line for line in test_code], remove_english_comments=True)
    
    print("\n结果2（删除英文注释）:")
    for line in result2:
        print(f"  {line}")
    
    # 对每行进行单独的英文文本判断
    print("\n每行注释的英文判断:")
    for line in test_code:
        if line.strip().startswith('#') or '#' in line:
            # 提取注释部分
            if line.strip().startswith('#'):
                comment = line.strip()[1:].strip()
            else:
                comment = line.split('#', 1)[1].strip()
            
            is_eng_orig = is_english_text(comment)
            is_eng_impr = improved_is_english_text(comment)
            
            print(f"  注释: {comment}")
            print(f"    原始函数判断: {'英文' if is_eng_orig else '非英文'}")
            print(f"    改进函数判断: {'英文' if is_eng_impr else '非英文'}")
            print()

def test_end_of_line_comments():
    """专门测试行尾注释的处理"""
    print("\n\n行尾注释测试:")
    print("=" * 50)
    
    # 创建一个只包含行尾注释的测试用例
    test_code = [
        'x = 10  # 这是中文行尾注释',
        'y = 20  # This is an English end-of-line comment',
        'z = x + y  # 计算结果 result calculation',
        'print(f"结果: {z}")  # 输出结果'
    ]
    
    print("原始内容:")
    for line in test_code:
        print(f"  {line}")
    
    # 测试保留所有注释
    result1 = remove_large_comments([line for line in test_code], remove_english_comments=False)
    
    print("\n结果1（不删除英文注释）:")
    for line in result1:
        print(f"  {line}")
    
    # 测试删除英文注释
    result2 = remove_large_comments([line for line in test_code], remove_english_comments=True)
    
    print("\n结果2（删除英文注释）:")
    for line in result2:
        print(f"  {line}")

if __name__ == "__main__":
    print("英文注释删除功能测试\n")
    
    # 首先测试is_english_text函数
    test_is_english_text()
    
    # 测试单行注释处理
    test_single_line_comments()
    
    # 测试行尾注释处理
    test_end_of_line_comments()
    
    # 然后测试remove_english_comments功能
    test_remove_english_comments() 