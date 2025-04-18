"""
QuickText打包脚本
使用PyInstaller将QuickText打包成可执行文件
"""

import os
import sys

# 如果运行此脚本，则使用PyInstaller打包
if __name__ == "__main__":
    try:
        import PyInstaller.__main__
    except ImportError:
        print("PyInstaller未安装，正在安装...")
        os.system(f"{sys.executable} -m pip install pyinstaller")
        import PyInstaller.__main__

    print("开始打包QuickText...")

    # 获取当前脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__)) or "."

    # 图标路径
    icon_path = os.path.join(script_dir, "tool.png")

    # 主脚本路径
    main_script = os.path.join(script_dir, "quick_text.py")

    # PyInstaller参数
    pyinstaller_args = [
        '--name=QuickText',
        '--onefile',
        f'--icon={icon_path}',
        '--windowed',
        '--add-data=presets.json;.',
        '--add-data=tool.png;.',
        main_script
    ]

    # 在Windows上
    if sys.platform.startswith('win'):
        pyinstaller_args = [arg.replace(';', os.pathsep)
                            for arg in pyinstaller_args]

    # 运行PyInstaller
    PyInstaller.__main__.run(pyinstaller_args)

    print("\nQuickText打包完成！")
    print(f"可执行文件位于: {os.path.join(script_dir, 'dist', 'QuickText.exe')}")
