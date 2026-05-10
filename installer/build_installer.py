"""
构建番茄钟 Windows 安装程序
会生成一个独立的安装 .exe 文件
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path

DIST_DIR = Path('dist')
INSTALLER_DIR = Path('installer')
BUILD_DIR = Path('build_installer')

def check_requirements():
    """检查必要工具"""
    print('检查必要工具...')
    
    # 检查 pyinstaller
    try:
        result = subprocess.run(['pyinstaller', '--version'], capture_output=True, text=True)
        print(f'  PyInstaller: {result.stdout.strip()}')
    except FileNotFoundError:
        print('  错误: 未找到 PyInstaller')
        print('  运行: pip install pyinstaller')
        return False
    
    # 检查 Pillow
    try:
        import PIL
        print(f'  Pillow: {PIL.__version__}')
    except ImportError:
        print('  错误: 未找到 Pillow')
        print('  运行: pip install Pillow')
        return False
    
    # 检查 pystray
    try:
        import pystray
        print('  pystray: 已安装')
    except ImportError:
        print('  错误: 未找到 pystray')
        print('  运行: pip install pystray')
        return False
    
    # 检查主程序文件
    if not Path('main.py').exists():
        print('  错误: 未找到 main.py')
        return False
    
    print('  所有依赖检查通过!')
    return True

def build_exe():
    """使用 PyInstaller 构建 .exe"""
    print('\n构建可执行文件...')
    
    # 使用单文件模式
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name=番茄钟',
        '--icon=assets/icon.ico',
        '--hidden-import=pystray',
        '--hidden-import=pystray._win32',
        '--hidden-import=PIL',
        '--hidden-import=PIL.Image',
        '--hidden-import=PIL.ImageDraw',
        '--add-data=assets/icon.ico;assets',
        'main.py'
    ]
    
    print(f'  执行: {" ".join(cmd)}')
    
    # 清理旧构建
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f'  构建失败: {result.stderr}')
        return False
    
    exe_path = DIST_DIR / '番茄钟.exe'
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f'  构建成功! 文件大小: {size_mb:.1f} MB')
        return True
    else:
        print('  构建失败: 未找到生成的 exe 文件')
        return False

def create_installer_package():
    """创建安装程序包"""
    print('\n创建安装程序包...')
    
    # 创建包目录
    package_dir = DIST_DIR / '番茄钟_安装包'
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir(parents=True)
    
    # 复制 .exe
    exe_src = DIST_DIR / '番茄钟.exe'
    exe_dest = package_dir / '番茄钟.exe'
    shutil.copy2(exe_src, exe_dest)
    
    # 复制图标
    icon_src = Path('assets') / 'icon.ico'
    icon_dest = package_dir / 'icon.ico'
    if icon_src.exists():
        shutil.copy2(icon_src, icon_dest)
    
    # 复制安装脚本
    installer_src = INSTALLER_DIR / 'installer.py'
    installer_dest = package_dir / '安装.py'
    if installer_src.exists():
        shutil.copy2(installer_src, installer_dest)
    
    # 复制运行脚本
    run_src = Path('run.py')
    run_dest = package_dir / '运行.bat'
    with open(run_dest, 'w', encoding='utf-8') as f:
        f.write('@echo off\nchcp 65001 >nul\npython "安装.py"\npause\n')
    
    # 创建 README
    readme_path = package_dir / '安装说明.txt'
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write('番茄钟 - Windows 桌面应用\n')
        f.write('=' * 50 + '\n\n')
        f.write('系统要求:\n')
        f.write('  - Windows 10 或更高版本\n')
        f.write('  - Python 3.12 或更高版本\n\n')
        f.write('安装方法:\n')
        f.write('  方法一: 双击运行 "番茄钟.exe" (便携版)\n')
        f.write('  方法二: 运行 "安装.py" 或 "运行.bat" 进行完整安装\n\n')
        f.write('功能:\n')
        f.write('  - 专注模式 (25分钟可自定义)\n')
        f.write('  - 短休息模式 (5分钟可自定义)\n')
        f.write('  - 长休息模式 (15分钟可自定义)\n')
        f.write('  - 系统托盘支持\n')
        f.write('  - 桌面通知\n')
        f.write('  - 自定义设置\n')
        f.write('  - 番茄计数\n')
        f.write('  - 快捷键支持 (空格键开始/暂停, Ctrl+R 重置)\n\n')
        f.write('卸载方法:\n')
        f.write('  - 控制面板 -> 程序和功能 -> 番茄钟\n')
        f.write('  - 或删除: %LOCALAPPDATA%\\番茄钟 目录\n\n')
        f.write('配置文件位置:\n')
        f.write('  %USERPROFILE%\\.pomodoro_settings.json\n\n')
        f.write('版本: 1.0.0\n')
        f.write('开发: 番茄钟开发团队\n')
    
    print('  安装程序包已创建')
    return True

def print_summary():
    """打印构建总结"""
    print('\n' + '=' * 50)
    print('构建完成!')
    print('=' * 50)
    print('\n文件位置:')
    print(f'  - 可执行文件: {DIST_DIR}\\番茄钟.exe')
    print(f'  - 安装程序包: {DIST_DIR}\\番茄钟_安装包\\')
    print(f'  - 安装说明: {DIST_DIR}\\番茄钟_安装包\\安装说明.txt')
    print('\n使用说明:')
    print('  1. 便携版: 直接运行 "番茄钟.exe"')
    print('  2. 完整版: 运行 "番茄钟_安装包\\运行.bat"')
    print('  3. 查看安装说明: "番茄钟_安装包\\安装说明.txt"')

def main():
    print('番茄钟 - Windows 安装程序构建工具')
    print('=' * 50)
    
    if not check_requirements():
        print('\n请先安装必要的依赖')
        sys.exit(1)
    
    if not build_exe():
        print('\n构建失败')
        sys.exit(1)
    
    if not create_installer_package():
        print('\n创建安装程序包失败')
        sys.exit(1)
    
    print_summary()

if __name__ == '__main__':
    main()
