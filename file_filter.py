#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import glob
import argparse
from pathlib import Path
from typing import List, Dict, Set, Tuple


class FileFilter:
    """软著文档文件筛选工具"""

    def __init__(self):
        # 通用排除规则
        self.common_exclude_patterns = [
            # 版本控制
            r'\.git/', r'\.svn/', r'\.hg/',
            r'\.gitignore', r'\.gitattributes',
            # 编辑器/IDE
            r'\.vscode/', r'\.idea/', r'\.eclipse/',
            r'.*\.sublime-project', r'.*\.sublime-workspace',
            # 操作系统
            r'\.DS_Store', r'Thumbs\.db',
            # 备份和临时
            r'.*~', r'.*\.bak', r'.*\.swp', r'.*\.tmp',
            r'.*\.old', r'.*\.backup',
            # 日志和缓存
            r'.*\.log', r'\.cache/', 
            # 敏感信息
            r'.*\.env', r'.*\.key', r'.*\.pem'
        ]

        # Python项目排除规则
        self.python_exclude_patterns = [
            # 必须排除
            r'__pycache__/', 
            r'.*\.pyc', r'.*\.pyo', r'.*\.pyd',
            r'.*\.so', r'.*\.dll', r'.*\.dylib',
            r'dist/', r'build/',
            r'.*\.egg-info/', r'.*\.egg',
            r'\.pytest_cache/', r'\.coverage',
            r'venv/', r'env/', r'\.venv/', r'\.env/',
        ]

        # 前端项目排除规则
        self.frontend_exclude_patterns = [
            # 必须排除
            r'node_modules/',
            r'dist/', r'build/', r'out/',
            r'.*\.min\.js', r'.*\.min\.css',
            r'\.cache/', r'coverage/',
        ]

        # 后端项目排除规则
        self.backend_exclude_patterns = [
            # 必须排除
            r'.*\.class', r'.*\.dll',
            r'target/', r'bin/', r'obj/',
            r'logs/', r'temp/', r'tmp/',
            r'.*\.bak', r'.*\.dump',
        ]

        # 可选排除规则
        self.optional_exclude_patterns = {
            'python': [
                ('__init__.py文件', r'__init__\.py'),
                ('安装配置文件', r'setup\.py|setup\.cfg'),
                ('依赖管理文件', r'requirements\.txt|Pipfile|Pipfile\.lock'),
                ('文档和示例目录', r'docs/|examples/')
            ],
            'frontend': [
                ('依赖配置文件', r'package\.json|package-lock\.json|yarn\.lock'),
                ('代码风格配置文件', r'\.eslintrc|\.prettierrc'),
                ('构建工具配置', r'webpack\.config\.js|babel\.config\.js'),
                ('源码映射文件', r'.*\.map'),
                ('静态资源目录', r'public/|static/'),
                ('环境配置文件', r'\.browserslistrc|\.nvmrc'),
                ('测试文件', r'.*\.test\.js|.*\.spec\.js')
            ],
            'backend': [
                ('配置文件', r'application\.properties|web\.config'),
                ('依赖管理文件', r'pom\.xml|build\.gradle'),
                ('IDE配置目录', r'\.settings/'),
                ('容器配置文件', r'Dockerfile|docker-compose\.yml'),
                ('数据库脚本', r'.*\.sql'),
                ('测试目录', r'test/|tests/')
            ],
            'common': [
                ('项目文档', r'README\.md|CHANGELOG\.md'),
                ('许可证文件', r'LICENSE'),
                ('CI/CD配置文件', r'\.travis\.yml|\.github/workflows/')
            ]
        }

        # 存储所有可选规则的映射，用于显示和管理
        self.all_optional_rules = {}
        self.active_optional_rules = set()  # 使用集合存储当前激活的可选规则
        
        # 基础排除规则（必须排除的）
        self.base_exclude_patterns = []
        self.active_exclude_patterns = []
        self.project_type = None
        self.source_dir = None

    def show_menu(self):
        """显示主菜单"""
        print("\n========= 软著文档文件筛选工具 =========")
        print("1. 选择项目类型")
        print("2. 配置排除规则")
        print("3. 查看当前排除规则")
        print("4. 扫描并显示筛选结果")
        print("5. 导出文件列表")
        print("6. 查看帮助")
        print("0. 退出")
        
        choice = input("\n请选择操作 [0-6]: ")
        return choice

    def select_project_type(self):
        """选择项目类型"""
        print("\n========= 选择项目类型 =========")
        print("1. Python项目")
        print("2. 前端项目")
        print("3. 后端项目")
        print("4. 全栈项目")
        print("0. 返回")
        
        choice = input("\n请选择项目类型 [0-4]: ")
        
        # 重置规则状态
        self.base_exclude_patterns = []
        self.active_optional_rules = set()
        self.all_optional_rules = {}
        
        if choice == '1':
            self.project_type = 'python'
            self.base_exclude_patterns = self.common_exclude_patterns + self.python_exclude_patterns
            print("已选择: Python项目")
        elif choice == '2':
            self.project_type = 'frontend'
            self.base_exclude_patterns = self.common_exclude_patterns + self.frontend_exclude_patterns
            print("已选择: 前端项目")
        elif choice == '3':
            self.project_type = 'backend'
            self.base_exclude_patterns = self.common_exclude_patterns + self.backend_exclude_patterns
            print("已选择: 后端项目")
        elif choice == '4':
            self.project_type = 'fullstack'
            self.base_exclude_patterns = (self.common_exclude_patterns + 
                                        self.python_exclude_patterns + 
                                        self.frontend_exclude_patterns + 
                                        self.backend_exclude_patterns)
            print("已选择: 全栈项目")
        
        # 更新活动排除规则
        self.update_active_exclude_patterns()
        
        # 选择项目目录
        if choice in ['1', '2', '3', '4']:
            self.select_source_directory()
    
    def update_active_exclude_patterns(self):
        """更新活动排除规则列表"""
        # 首先添加基础规则（必须排除的）
        self.active_exclude_patterns = self.base_exclude_patterns.copy()
        
        # 然后添加当前激活的可选规则
        for rule_id in self.active_optional_rules:
            if rule_id in self.all_optional_rules:
                pattern = self.all_optional_rules[rule_id][1]
                if pattern not in self.active_exclude_patterns:
                    self.active_exclude_patterns.append(pattern)
    
    def select_source_directory(self):
        """选择源代码目录"""
        default_dir = os.getcwd()
        dir_input = input(f"\n请输入源代码目录路径 [默认: {default_dir}]: ")
        self.source_dir = dir_input if dir_input.strip() else default_dir
        
        if not os.path.isdir(self.source_dir):
            print(f"错误: 目录 '{self.source_dir}' 不存在")
            self.source_dir = None
            return
            
        print(f"已选择源代码目录: {self.source_dir}")
    
    def configure_exclude_rules(self):
        """配置排除规则"""
        if not self.project_type:
            print("请先选择项目类型")
            return
            
        while True:
            print("\n========= 配置可选排除规则 =========")
            print("当前激活的可选规则: ", end="")
            if not self.active_optional_rules:
                print("无")
            else:
                active_rules = [self.all_optional_rules[rule_id][0] for rule_id in self.active_optional_rules if rule_id in self.all_optional_rules]
                print(", ".join(active_rules))
            
            print("\n选择操作:")
            print("1. 添加排除规则")
            print("2. 移除排除规则")
            print("0. 返回主菜单")
            
            op_choice = input("\n请选择操作 [0-2]: ")
            
            if op_choice == '0':
                return
            elif op_choice == '1':
                self.add_exclude_rules()
            elif op_choice == '2':
                self.remove_exclude_rules()
            else:
                print("无效选择，请重试")
    
    def add_exclude_rules(self):
        """添加排除规则"""
        # 显示可选排除规则
        categories = []
        if self.project_type in ['python', 'fullstack']:
            categories.append('python')
        if self.project_type in ['frontend', 'fullstack']:
            categories.append('frontend')
        if self.project_type in ['backend', 'fullstack']:
            categories.append('backend')
        categories.append('common')
        
        self.all_optional_rules = {}
        option_num = 1
        
        print("\n可添加的排除规则:")
        for category in categories:
            print(f"\n--- {category.capitalize()} 项目可选排除 ---")
            for name, pattern in self.optional_exclude_patterns[category]:
                rule_id = f"{category}_{option_num}"
                status = "√" if rule_id in self.active_optional_rules else " "
                print(f"{option_num}. [{status}] {name} ({pattern})")
                self.all_optional_rules[rule_id] = (name, pattern)
                option_num += 1
        
        choice = input("\n请选择要添加的规则编号 (多个用逗号分隔，0返回): ")
        if choice == '0':
            return
            
        try:
            selected_indices = [int(idx.strip()) for idx in choice.split(',') if idx.strip()]
            for idx in selected_indices:
                if 1 <= idx < option_num:
                    # 找到对应的规则ID
                    for rule_id, (name, pattern) in self.all_optional_rules.items():
                        if rule_id.split('_')[1] == str(idx):
                            self.active_optional_rules.add(rule_id)
                            print(f"已添加规则: {name}")
                            break
                else:
                    print(f"无效的选项: {idx}")
            
            # 更新活动排除规则
            self.update_active_exclude_patterns()
        except ValueError:
            print("输入无效，请输入数字")
    
    def remove_exclude_rules(self):
        """移除排除规则"""
        if not self.active_optional_rules:
            print("当前没有激活的可选规则")
            return
        
        print("\n当前激活的排除规则:")
        active_rules = [(rule_id, self.all_optional_rules[rule_id][0]) 
                        for rule_id in self.active_optional_rules 
                        if rule_id in self.all_optional_rules]
        
        for i, (rule_id, name) in enumerate(active_rules, 1):
            print(f"{i}. {name}")
        
        choice = input("\n请选择要移除的规则编号 (多个用逗号分隔，0返回): ")
        if choice == '0':
            return
            
        try:
            selected_indices = [int(idx.strip()) for idx in choice.split(',') if idx.strip()]
            for idx in selected_indices:
                if 1 <= idx <= len(active_rules):
                    rule_id = active_rules[idx-1][0]
                    name = active_rules[idx-1][1]
                    self.active_optional_rules.remove(rule_id)
                    print(f"已移除规则: {name}")
                else:
                    print(f"无效的选项: {idx}")
            
            # 更新活动排除规则
            self.update_active_exclude_patterns()
        except ValueError:
            print("输入无效，请输入数字")
    
    def show_current_rules(self):
        """显示当前排除规则"""
        if not self.project_type:
            print("请先选择项目类型")
            return
        
        print("\n========= 当前排除规则 =========")
        print(f"项目类型: {self.project_type}")
        
        print("\n基础排除规则 (必须排除):")
        for i, pattern in enumerate(self.base_exclude_patterns, 1):
            print(f"{i}. {pattern}")
        
        print("\n可选排除规则 (当前激活):")
        if not self.active_optional_rules:
            print("无")
        else:
            active_rules = [(rule_id, self.all_optional_rules[rule_id][0], self.all_optional_rules[rule_id][1]) 
                           for rule_id in self.active_optional_rules 
                           if rule_id in self.all_optional_rules]
            
            for i, (_, name, pattern) in enumerate(active_rules, 1):
                print(f"{i}. {name} ({pattern})")
        
        input("\n按任意键返回主菜单...")
    
    def scan_files(self):
        """扫描文件并应用过滤规则"""
        if not self.project_type or not self.source_dir:
            print("请先选择项目类型和源代码目录")
            return [], []
        
        all_files = []
        for root, _, files in os.walk(self.source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, self.source_dir)
                all_files.append(rel_path.replace('\\', '/'))  # 统一使用正斜杠
        
        included_files = []
        excluded_files = []
        
        for file_path in all_files:
            excluded = False
            matching_pattern = None
            
            for pattern in self.active_exclude_patterns:
                if re.search(pattern, file_path):
                    excluded = True
                    matching_pattern = pattern
                    break
            
            if excluded:
                excluded_files.append((file_path, matching_pattern))
            else:
                included_files.append(file_path)
        
        return included_files, excluded_files
    
    def show_scan_results(self):
        """显示扫描结果"""
        if not self.project_type or not self.source_dir:
            print("请先选择项目类型和源代码目录")
            return
            
        included_files, excluded_files = self.scan_files()
        
        print("\n========= 扫描结果 =========")
        print(f"源代码目录: {self.source_dir}")
        print(f"项目类型: {self.project_type}")
        print(f"总文件数: {len(included_files) + len(excluded_files)}")
        print(f"包含文件数: {len(included_files)}")
        print(f"排除文件数: {len(excluded_files)}")
        
        show_details = input("\n是否显示详细文件列表? (y/n): ").lower() == 'y'
        if show_details:
            print("\n--- 包含的文件 ---")
            for file in sorted(included_files):
                print(file)
                
            print("\n--- 排除的文件 ---")
            for file, pattern in sorted(excluded_files):
                print(f"{file} (匹配规则: {pattern})")
    
    def export_file_list(self):
        """导出文件列表"""
        if not self.project_type or not self.source_dir:
            print("请先选择项目类型和源代码目录")
            return
            
        included_files, excluded_files = self.scan_files()
        
        export_dir = os.path.join(os.getcwd(), "export")
        os.makedirs(export_dir, exist_ok=True)
        
        timestamp = os.path.basename(self.source_dir)
        included_file_path = os.path.join(export_dir, f"{timestamp}_included_files.txt")
        excluded_file_path = os.path.join(export_dir, f"{timestamp}_excluded_files.txt")
        
        with open(included_file_path, 'w', encoding='utf-8') as f:
            f.write(f"# 包含的文件列表 - {self.project_type} 项目\n")
            f.write(f"# 源代码目录: {self.source_dir}\n")
            f.write(f"# 总计: {len(included_files)} 文件\n\n")
            for file in sorted(included_files):
                f.write(f"{file}\n")
        
        with open(excluded_file_path, 'w', encoding='utf-8') as f:
            f.write(f"# 排除的文件列表 - {self.project_type} 项目\n")
            f.write(f"# 源代码目录: {self.source_dir}\n")
            f.write(f"# 总计: {len(excluded_files)} 文件\n\n")
            for file, pattern in sorted(excluded_files):
                f.write(f"{file} (匹配规则: {pattern})\n")
        
        print(f"\n文件列表已导出到:")
        print(f"- {included_file_path}")
        print(f"- {excluded_file_path}")
    
    def show_help(self):
        """显示帮助信息"""
        print("\n========= 软著文档文件筛选工具帮助 =========")
        print("本工具用于帮助筛选软件著作权登记文档中应包含的源代码文件。")
        print("\n使用步骤:")
        print("1. 选择项目类型（Python、前端、后端或全栈项目）")
        print("2. 配置可选的排除规则")
        print("3. 查看当前排除规则")
        print("4. 扫描并查看筛选结果")
        print("5. 导出文件列表供后续处理")
        
        print("\n项目类型说明:")
        print("- Python项目: 主要包含Python源代码的项目")
        print("- 前端项目: 主要包含HTML、CSS、JavaScript等前端技术的项目")
        print("- 后端项目: 主要包含Java、C#等后端技术的项目")
        print("- 全栈项目: 同时包含前端和后端代码的综合项目")
        
        print("\n排除规则说明:")
        print("- 必须排除: 默认排除的文件，通常是编译产物、临时文件等")
        print("- 可选排除: 用户可以选择是否排除的文件，如配置文件、测试文件等")
        print("- 可以添加和移除可选排除规则")
        
        print("\n软著文档最佳实践:")
        print("- 优先包含自己编写的核心业务逻辑代码")
        print("- 排除第三方库、框架和工具生成的代码")
        print("- 确保文档页数在合理范围内（通常30-50页为宜）")
        print("- 保持文件的相对路径结构，便于理解代码组织")
        
        input("\n按任意键返回主菜单...")

    def run(self):
        """运行主程序"""
        while True:
            choice = self.show_menu()
            
            if choice == '0':
                print("感谢使用，再见！")
                break
            elif choice == '1':
                self.select_project_type()
            elif choice == '2':
                self.configure_exclude_rules()
            elif choice == '3':
                self.show_current_rules()
            elif choice == '4':
                self.show_scan_results()
            elif choice == '5':
                self.export_file_list()
            elif choice == '6':
                self.show_help()
            else:
                print("无效选择，请重试")


def main():
    """主函数"""
    print("软著文档文件筛选工具 v1.1")
    print("用于帮助筛选软件著作权登记文档中应包含的源代码文件")
    
    file_filter = FileFilter()
    file_filter.run()


if __name__ == "__main__":
    main()