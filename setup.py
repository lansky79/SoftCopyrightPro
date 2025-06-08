"""
SoftCopyrightPro 安装脚本
"""

from setuptools import setup, find_packages
import os

# 读取README.md作为长描述
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 读取requirements.txt中的依赖
with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="sofcrtpro",
    version="0.1.0",
    author="SoftCopyrightPro Team",
    author_email="your.email@example.com",
    description="软件著作权材料生成工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/SoftCopyrightPro",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "sofcrtpro=sofcrtpro.cli:main",
        ],
    },
) 