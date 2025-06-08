"""
配置管理模块

负责管理用户输入的配置参数，提供默认配置选项，验证配置的有效性。
"""

import os
import json
from typing import Dict, Any, Set, Optional


class ConfigManager:
    """配置管理类，处理用户配置和默认设置"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径，如果为None则使用默认配置
        """
        # 默认配置
        self.default_config = {
            "source_dir": "",
            "output_path": "output/source_code",
            "output_format": "docx",
            "font_name": "Courier New",
            "font_size": 10,
            "lines_per_page": 50,
            "file_extensions": [".py", ".java", ".js", ".html", ".css", ".c", ".cpp", ".h", ".cs", ".go", ".php", ".rb"],
            "exclude_dirs": ["venv", "node_modules", ".git", "__pycache__", "build", "dist"],
            "backend_identifiers": [".py", ".java", ".c", ".cpp", ".cs", ".go", ".rb", ".php"],
            "frontend_identifiers": [".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".vue", ".scss", ".less"]
        }
        
        # 当前配置
        self.config = self.default_config.copy()
        
        # 如果提供了配置文件，则加载它
        if config_file and os.path.exists(config_file):
            self.load_config(config_file)
    
    def load_config(self, config_file: str) -> bool:
        """
        从文件加载配置
        
        Args:
            config_file: 配置文件路径
        
        Returns:
            加载是否成功
        """
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
                # 更新配置，保留默认值作为后备
                for key, value in loaded_config.items():
                    if key in self.config:
                        self.config[key] = value
            return True
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return False
    
    def save_config(self, config_file: str) -> bool:
        """
        保存配置到文件
        
        Args:
            config_file: 配置文件路径
        
        Returns:
            保存是否成功
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(os.path.abspath(config_file)), exist_ok=True)
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """
        更新配置
        
        Args:
            new_config: 新的配置字典
        """
        for key, value in new_config.items():
            if key in self.config:
                self.config[key] = value
    
    def get_config(self) -> Dict[str, Any]:
        """
        获取当前配置
        
        Returns:
            当前配置字典
        """
        return self.config
    
    def validate_config(self) -> Dict[str, str]:
        """
        验证配置的有效性
        
        Returns:
            错误信息字典，如果为空则表示配置有效
        """
        errors = {}
        
        # 检查源代码目录
        if not self.config["source_dir"]:
            errors["source_dir"] = "源代码目录不能为空"
        elif not os.path.isdir(self.config["source_dir"]):
            errors["source_dir"] = f"源代码目录 '{self.config['source_dir']}' 不存在或不是一个目录"
        
        # 检查输出格式
        if self.config["output_format"] not in ["docx", "pdf"]:
            errors["output_format"] = f"不支持的输出格式: {self.config['output_format']}"
        
        # 检查字体大小
        if not (8 <= self.config["font_size"] <= 14):
            errors["font_size"] = f"字体大小应在8-14磅之间，当前为: {self.config['font_size']}"
        
        # 检查每页行数
        if self.config["lines_per_page"] < 10:
            errors["lines_per_page"] = f"每页行数不应少于10行，当前为: {self.config['lines_per_page']}"
        
        return errors
    
    def get_file_extensions(self) -> Set[str]:
        """
        获取文件扩展名集合
        
        Returns:
            文件扩展名集合
        """
        return set(self.config["file_extensions"])
    
    def get_backend_identifiers(self) -> Set[str]:
        """
        获取后端文件标识集合
        
        Returns:
            后端文件标识集合
        """
        return set(self.config["backend_identifiers"])
    
    def get_frontend_identifiers(self) -> Set[str]:
        """
        获取前端文件标识集合
        
        Returns:
            前端文件标识集合
        """
        return set(self.config["frontend_identifiers"])
    
    def get_exclude_dirs(self) -> Set[str]:
        """
        获取要排除的目录集合
        
        Returns:
            要排除的目录集合
        """
        return set(self.config["exclude_dirs"]) 