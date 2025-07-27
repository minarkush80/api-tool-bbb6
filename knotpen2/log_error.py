import os
import time
import traceback
from functools import wraps

# 相对导入
import constant_config

def log_errors(func):
    """捕获函数异常并将完整堆栈信息保存到日志文件"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            # 创建 log 文件夹
            log_dir = constant_config.ERROR_LOG_FOLDER
            os.makedirs(log_dir, exist_ok=True)
            
            # 生成日志文件名（格式：年月日时分秒.log）
            timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
            log_path = os.path.join(log_dir, f"{timestamp}.log")
            
            # 保存完整的堆栈跟踪信息
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write(traceback.format_exc())
                
            # 可选择继续抛出异常或返回默认值
            # raise  # 取消注释此行将继续抛出异常
            return None  # 默认返回 None，可根据需求修改
    
    return wrapper
