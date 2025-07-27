import pygame
import os
import traceback

DIRNOW = os.path.dirname(os.path.abspath(__file__))
import sys; sys.path=[DIRNOW] + sys.path;

# 强制输出 utf-8
import io
sys.stdout = io.TextIOWrapper(
    sys.stdout.buffer, 
    encoding='utf-8',
    line_buffering=True  # 启用行缓冲，恢复每行自动flush的行为
)

# 相对导入
from i18n import _
import constant_config
import error_log
import Knotpen2GameObject
import ClassBinder
import MemoryObject
import MyAlgorithm

def set_pygame_icon(icon_path:str):
    # 加载图标图像（确保图像文件存在）
    try:
        icon = pygame.image.load(icon_path)  # 替换为你的图标文件路径
        pygame.display.set_icon(icon)
    except pygame.error:
        print(_("无法加载图标图像，请检查文件路径和格式！"))

def test_main():
    pygame.init()
    set_pygame_icon(constant_config.PYGAME_ICON_PATH)

    mo   = MemoryObject.MemoryObject()
    algo = MyAlgorithm.MyAlgorithm(mo)
    k2go = Knotpen2GameObject.Knotpen2GameObject(mo, algo)
    cb   = ClassBinder.ClassBinder(k2go)
    cb.mainloop()

if __name__ == "__main__":
    os.makedirs(constant_config.ANSWER_FOLDER, exist_ok=True)
    os.makedirs(constant_config.AUTOSAVE_FOLDER, exist_ok=True)
    os.makedirs(constant_config.ERROR_LOG_FOLDER, exist_ok=True)

    try:
        test_main()
    except:
        error_info = traceback.format_exc()
        print(error_info)

        filepath = error_log.error_log(error_info) # 记录错误信息并退出
        print(_("错误日志信息已经保存到：%s") % filepath)
        sys.exit(1)
