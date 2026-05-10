"""
番茄钟 - Windows 桌面应用
版本: 1.0.0
Python: 3.12+

使用方法:
    直接运行: python main.py
    或运行: python installer\installer.py 进行安装

打包为 exe:
    pyinstaller pomodoro.spec
    
创建安装程序:
    python installer\build_installer.py
"""
import sys
from pathlib import Path

# 确保项目根目录在 Python 路径中
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

if __name__ == '__main__':
    from main import PomodoroApp
    app = PomodoroApp()
    app.run()
