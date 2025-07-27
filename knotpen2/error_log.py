import os

# 相对引入
import constant_config
import math_utils

def error_log(error_info:str) -> str:
    filename = math_utils.get_formatted_datetime() + ".log"
    filepath = os.path.join(constant_config.ERROR_LOG_FOLDER, filename)
    with open(filepath, "w", encoding="utf-8") as fp:
        fp.write(error_info)
    return filepath
