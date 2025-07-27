import os
import sys

# 当前程序执行路径为
PROGRAM_EXE_PATH = os.path.dirname(os.path.abspath(sys.argv[0]))

APP_NAME = "knotpen2"
APP_VERSION = "2.4.0" # 不要删除这行内容，因为脚本会从这里抓取

DIRNOW = os.path.dirname(os.path.abspath(__file__))
AUTOSAVE_FOLDER = os.path.join(PROGRAM_EXE_PATH, "auto_save")
AUTOSAVE_FILE = os.path.join(AUTOSAVE_FOLDER, "auto_save.json") # 自动保存位置

ANSWER_FOLDER = os.path.join(PROGRAM_EXE_PATH, "answer") # 答案存储位置
ERROR_LOG_FOLDER = os.path.join(PROGRAM_EXE_PATH, "error_log")

CIRCLE_RADIUS = 12
LINE_WIDTH = 8

BACKUP_TIME = 180 # 每三分钟自动保存一次，如果和上次自动保存内容完全一致，则删除最新的自动保存
STRIDE = 50

# i18n 文件夹位置
LOCALE_DIR = os.path.join(PROGRAM_EXE_PATH, "i18n", "locales")
LANG_CODE_SET = ['zh_CN', 'en_US'] # 可以使用的所有语言翻译

# 图标位置
PYGAME_ICON_PATH = os.path.join(DIRNOW, "logo.ico")

# 字体文件加载目录
FONT_TTF = os.path.join(DIRNOW, "font", "SourceHanSansSC-VF.ttf")
MAX_MESSAGE_CNT = 40
MESSAGE_SIZE = 18
SMALL_TEXT_SIZE = 14
def MESSAGE_POSITION(i:int):
    return (10 , 10 + (MESSAGE_SIZE + 2) * i)

# SVG 绘图属性
SVG_STROKE_COLOR = "black"
SVG_STROKE_WIDTH = 3
SVG_FONT_SIZE = SMALL_TEXT_SIZE
SVG_TEXT_DELTA_Y = 15 # 对 SVG 文件中的文字位置进行微调
ARROW_SIZE = 5 # SVG 图片中箭头的大小
SVG_EXPAND_RATIO = 1 # 放大倍数

DOUBLE_CLICK_TIME = 0.25 # 双击时两次点击的最大间隔

LEFT_KEY_ID  = 1
MID_KEY_ID   = 2
RIGHT_KEY_ID = 3

WHITE = (255, 255, 255)
GREY = (128, 128, 128)
YELLOW = (128, 128, 0)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 192, 0)
BLUE = (0, 0, 255)