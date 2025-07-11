import sys
from module.register_context_menu import register, unregister

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] in ('--uninstall', '-u'):
        unregister()
    else:
        register()
