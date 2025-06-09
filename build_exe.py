import os
import sys
import subprocess
import shutil

def build_executable():
    """构建软著源代码管理器的可执行文件"""
    print("开始构建软著源代码管理器可执行文件...")
    
    # 确保输出目录存在
    if not os.path.exists('dist'):
        os.makedirs('dist')
    
    # 构建命令 - 使用spec文件
    print("使用spec文件构建可执行文件...")
    cmd = [
        'pyinstaller',
        '--clean',     # 在构建前清理临时文件
        '--noconfirm', # 不询问覆盖确认
        '软著源代码管理器.spec'
    ]
    
    # 执行构建命令
    try:
        subprocess.run(cmd, check=True)
        print("构建成功！可执行文件位于 dist/软著源代码管理器.exe")
        
        # 复制必要的依赖文件到dist目录
        if os.path.exists('requirements.txt'):
            shutil.copy('requirements.txt', 'dist/')
        
        print("打包完成！")
    except subprocess.CalledProcessError as e:
        print(f"构建失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_executable() 