import sys
import os
import winreg


def register():
    # Path to MarkdownViewer exe; 第一引数に指定があればそこを使用
    if len(sys.argv) > 1 and not sys.argv[1].lower() in ('--uninstall', '-u'):
        exe_path = os.path.abspath(sys.argv[1])
    else:
        exe_path = os.path.abspath(sys.argv[0])
    if exe_path.lower().endswith('.py'):
        print('Warning: Python スクリプトではなく、ビルド済みの exe を指定して登録してください。')
    key_path = r"Software\Classes\SystemFileAssociations\.md\shell\MarkdownViewer"
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
        winreg.SetValue(key, '', winreg.REG_SZ, 'Markdown Viewer')
    cmd_key = key_path + r"\command"
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, cmd_key) as cmd:
        winreg.SetValue(cmd, '', winreg.REG_SZ, f'"{exe_path}" "%1"')
    print('Context menu registered for .md files.')


def unregister():
    base = r"Software\Classes\SystemFileAssociations\.md\shell"
    try:
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, base + r"\MarkdownViewer\command")
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, base + r"\MarkdownViewer")
        print('Context menu unregistered.')
    except FileNotFoundError:
        print('No registry entries found to remove.')


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] in ('--uninstall', '-u'):
        unregister()
    else:
        register()
