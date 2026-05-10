"""
番茄钟 Windows 安装/卸载脚本
"""
import os
import sys
import shutil
import ctypes
from pathlib import Path

APP_NAME = '番茄钟'
APP_VERSION = '1.0.0'
APP_GUID = '{A8B2C3D4-E5F6-7890-ABCD-EF1234567890}'

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_install_dir():
    program_files = os.environ.get('ProgramFiles', 'C:\\Program Files')
    return os.path.join(program_files, APP_NAME)

def get_user_install_dir():
    appdata = os.environ.get('LOCALAPPDATA', os.path.expanduser('~\\AppData\\Local'))
    return os.path.join(appdata, APP_NAME)

def create_shortcut(source, link_path):
    """创建快捷方式"""
    import pythoncom
    from win32com.shell import shell
    from win32com.client import Dispatch
    
    shortcut = Dispatch('WScript.Shell').CreateShortcut(link_path)
    shortcut.TargetPath = source
    shortcut.WorkingDirectory = os.path.dirname(source)
    shortcut.IconLocation = source + ',0'
    shortcut.Save()

def get_desktop_path():
    from win32com.shell import shell, shellcon
    return shell.SHGetFolderPath(0, shellcon.CSIDL_DESKTOP, 0, 0)

def get_start_menu_path():
    from win32com.shell import shell, shellcon
    return shell.SHGetFolderPath(0, shellcon.CSIDL_PROGRAMS, 0, 0)

def get_appdata_path():
    from win32com.shell import shell, shellcon
    return shell.SHGetFolderPath(0, shellcon.CSIDL_APPDATA, 0, 0)

def register_uninstall(install_dir):
    """注册卸载程序到 Windows"""
    import winreg
    
    uninstall_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\%s' % APP_GUID
    if sys.maxsize > 2**32:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, uninstall_key)
    else:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, uninstall_key)
    
    winreg.SetValueEx(key, 'DisplayName', 0, winreg.REG_SZ, APP_NAME)
    winreg.SetValueEx(key, 'DisplayVersion', 0, winreg.REG_SZ, APP_VERSION)
    winreg.SetValueEx(key, 'Publisher', 0, winreg.REG_SZ, APP_NAME)
    winreg.SetValueEx(key, 'InstallLocation', 0, winreg.REG_SZ, install_dir)
    winreg.SetValueEx(key, 'UninstallString', 0, winreg.REG_SZ, '"%s\\uninstall.exe"' % install_dir)
    winreg.SetValueEx(key, 'DisplayIcon', 0, winreg.REG_SZ, '"%s\\番茄钟.exe"' % install_dir)
    winreg.SetValueEx(key, 'NoModify', 0, winreg.REG_DWORD, 1)
    winreg.SetValueEx(key, 'NoRepair', 0, winreg.REG_DWORD, 1)
    winreg.CloseKey(key)

def install():
    print('=' * 50)
    print('番茄钟 %s 安装程序' % APP_VERSION)
    print('=' * 50)
    
    install_dir = get_user_install_dir()
    
    print('\n安装位置: %s' % install_dir)
    
    if os.path.exists(install_dir):
        choice = input('该目录已存在，是否覆盖安装? [Y/n]: ')
        if choice.lower() != 'y' and choice != '':
            print('安装已取消')
            return False
    
    # 创建安装目录
    os.makedirs(install_dir, exist_ok=True)
    
    # 复制主程序
    source_exe = os.path.join('dist', '番茄钟.exe')
    if not os.path.exists(source_exe):
        print('错误: 找不到 %s' % source_exe)
        return False
    
    dest_exe = os.path.join(install_dir, '番茄钟.exe')
    shutil.copy2(source_exe, dest_exe)
    print('已复制: 番茄钟.exe')
    
    # 复制图标
    source_icon = os.path.join('assets', 'icon.ico')
    if os.path.exists(source_icon):
        dest_icon = os.path.join(install_dir, 'icon.ico')
        shutil.copy2(source_icon, dest_icon)
        print('已复制: icon.ico')
    
    # 创建卸载程序
    uninstall_script = os.path.join(install_dir, 'uninstall.exe')
    # 创建一个自卸载脚本
    uninstall_content = '''import os, sys, shutil, ctypes
install_dir = os.path.dirname(os.path.abspath(__file__))
try:
    shutil.rmtree(install_dir)
    ctypes.windll.user32.MessageBoxW(0, '卸载完成', '番茄钟', 0x40)
except Exception as e:
    ctypes.windll.user32.MessageBoxW(0, f'卸载失败: {e}', '番茄钟', 0x10)
'''
    with open(os.path.join(install_dir, 'uninstall.py'), 'w', encoding='utf-8') as f:
        f.write(uninstall_content)
    
    # 创建快捷方式
    try:
        desktop = get_desktop_path()
        start_menu = get_start_menu_path()
        
        # 桌面快捷方式
        desktop_link = os.path.join(desktop, '%s.lnk' % APP_NAME)
        create_shortcut(dest_exe, desktop_link)
        print('已创建: 桌面快捷方式')
        
        # 开始菜单
        start_menu_link = os.path.join(start_menu, '%s.lnk' % APP_NAME)
        create_shortcut(dest_exe, start_menu_link)
        print('已创建: 开始菜单快捷方式')
        
        # 注册卸载
        register_uninstall(install_dir)
        print('已注册: 卸载程序')
        
    except ImportError:
        print('警告: 无法创建快捷方式 (需要 pywin32)')
        print('请手动创建快捷方式指向: %s' % dest_exe)
    
    print('\n安装完成!')
    print('程序位置: %s' % dest_exe)
    print('卸载方式: 控制面板 -> 程序和功能 -> %s' % APP_NAME)
    
    choice = input('\n是否立即运行? [Y/n]: ')
    if choice.lower() != 'n':
        os.startfile(dest_exe)
    
    return True

def uninstall():
    install_dir = get_user_install_dir()
    
    if not os.path.exists(install_dir):
        print('未找到安装目录: %s' % install_dir)
        return False
    
    print('正在卸载 %s...' % APP_NAME)
    
    # 从注册表移除
    try:
        import winreg
        uninstall_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\%s' % APP_GUID
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, uninstall_key)
        print('已移除: 注册表项')
    except Exception as e:
        print('警告: 无法移除注册表项: %s' % e)
    
    # 删除安装目录
    try:
        shutil.rmtree(install_dir)
        print('已删除: 安装目录')
    except Exception as e:
        print('错误: 无法删除安装目录: %s' % e)
        return False
    
    # 删除快捷方式
    try:
        desktop = get_desktop_path()
        start_menu = get_start_menu_path()
        
        desktop_link = os.path.join(desktop, '%s.lnk' % APP_NAME)
        if os.path.exists(desktop_link):
            os.remove(desktop_link)
            print('已删除: 桌面快捷方式')
        
        start_menu_link = os.path.join(start_menu, '%s.lnk' % APP_NAME)
        if os.path.exists(start_menu_link):
            os.remove(start_menu_link)
            print('已删除: 开始菜单快捷方式')
    except Exception as e:
        print('警告: 无法删除快捷方式: %s' % e)
    
    print('\n卸载完成!')
    return True

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'uninstall':
        uninstall()
    else:
        install()
