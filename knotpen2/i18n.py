import gettext
import os
import constant_config

# 设置 locale 目录（存放翻译文件的路径）
localedir = constant_config.LOCALE_DIR
assert os.path.isdir(localedir)

# 域名
domain = constant_config.APP_NAME

# 当前语言状态
current_locale = constant_config.LANG_CODE_SET[0]
_raw = lambda x: x  # 默认使用原始字符串(不翻译)

# 默认语言目录
DEFAULT_LANG_FILE = os.path.abspath(os.path.join(constant_config.LOCALE_DIR, "..", "default_lang.txt"))

# 获取当前设置的默认语言
def get_default_lang() -> str:
    return open(DEFAULT_LANG_FILE, "r", encoding="utf-8").read().strip()

def set_language(lang_code: str):
    """动态设置应用语言"""
    global current_locale, _raw

    if lang_code not in constant_config.LANG_CODE_SET: # 忽略不合法的语言设置
        print("set_language: %s is not a feasible lang_code" % lang_code)
        return _raw
    current_locale = lang_code
    
    # 加载对应语言的翻译
    t = gettext.translation(
        domain=domain,
        localedir=localedir,
        languages=[lang_code],
        fallback=False  # 找不到翻译时使用原始字符串
    )
    _raw = t.gettext

    # 缓存默认语言文件
    if get_default_lang() != lang_code:
        with open(DEFAULT_LANG_FILE, "w", encoding="utf-8") as fp:
            fp.write(lang_code)
    return _raw

# 设置默认语言
if not os.path.isfile(DEFAULT_LANG_FILE):
    with open(DEFAULT_LANG_FILE, "w", encoding="utf-8") as fp:
        fp.write(constant_config.LANG_CODE_SET[0])
        
assert os.path.isfile(DEFAULT_LANG_FILE)
set_language(get_default_lang())

# 切换语言
def set_next_language(show_msg_callback):
    assert current_locale in constant_config.LANG_CODE_SET
    idx = constant_config.LANG_CODE_SET.index(current_locale)
    list_len = len(constant_config.LANG_CODE_SET)
    set_language(constant_config.LANG_CODE_SET[(idx + 1) % list_len])

    # 切换语言后调用显示消息
    if show_msg_callback is not None:
        show_msg_callback("Switch language to %s" % current_locale)

# 翻译器
def _(msg:str):
    return _raw(msg)

if __name__ == "__main__": # 测试切换语言
    # 动态切换到中文
    set_language('zh_CN')
    print(_('欢迎使用'))

    # 示例: 初始设置为英文
    set_language('en_US')
    print(_('欢迎使用'))
