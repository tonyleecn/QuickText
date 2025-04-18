"""
将PNG图标转换为ICO格式，为PyInstaller打包使用
"""

import os
import sys

try:
    from PIL import Image
except ImportError:
    print("缺少Pillow库，正在安装...")
    os.system(f"{sys.executable} -m pip install pillow")
    from PIL import Image


def png_to_ico(png_file, ico_file, sizes=[(32, 32), (64, 64), (128, 128)]):
    """将PNG文件转换为ICO文件"""
    try:
        img = Image.open(png_file)
        # 创建不同尺寸的图像
        imgs = [img.resize(size) for size in sizes]
        # 保存为ICO
        imgs[0].save(ico_file, format='ICO', sizes=[
                     (img.size[0], img.size[1]) for img in imgs])
        print(f"图标已成功转换，保存为: {ico_file}")
        return True
    except Exception as e:
        print(f"转换图标时出错: {e}")
        return False


if __name__ == "__main__":
    # 获取当前脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__)) or "."
    png_path = os.path.join(script_dir, "tool.png")
    ico_path = os.path.join(script_dir, "tool.ico")

    if not os.path.exists(png_path):
        print(f"错误: 找不到图标文件 {png_path}")
        sys.exit(1)

    if png_to_ico(png_path, ico_path):
        print("图标转换成功!")
    else:
        print("图标转换失败!")
