import math
import numpy as np
import datetime

def ccw(A, B, C):
    return (B[0] - A[0]) * (C[1] - A[1]) - (B[1] - A[1]) * (C[0] - A[0])

def segments_intersect(line1, line2):
    A, B = line1
    C, D = line2

    ccw1 = ccw(A, B, C)
    ccw2 = ccw(A, B, D)
    ccw3 = ccw(C, D, A)
    ccw4 = ccw(C, D, B)

    # 标准相交情况
    if (ccw1 * ccw2 < 0) and (ccw3 * ccw4 < 0):
        return compute_intersection(A, B, C, D)

    # 处理共线情况和端点相交
    if ccw1 == 0 and on_segment(A, B, C):
        return C, calculate_t(A, B, C), 0.0
    if ccw2 == 0 and on_segment(A, B, D):
        return D, calculate_t(A, B, D), 1.0
    if ccw3 == 0 and on_segment(C, D, A):
        return A, 0.0, calculate_t(C, D, A)
    if ccw4 == 0 and on_segment(C, D, B):
        return B, 1.0, calculate_t(C, D, B)

    return None, None, None

def calculate_t(A, B, P):
    """
    计算点 P 在线段 AB 上的参数 t，满足 P = A + t*(B-A)
    
    参数:
    A, B, P -- 二维点，格式为元组 (x, y)
    
    返回:
    t -- 实数参数，若 A=B 则返回 0
    """
    # 检查 A 和 B 是否为同一点
    if A == B:
        return 0.0  # 若 A=B，线段退化为点，t 定义为 0
    
    xA, yA = A
    xB, yB = B
    xP, yP = P
    
    # 优先使用 x 坐标计算 t（避免垂直线段的除零问题）
    if xB != xA:
        t = (xP - xA) / (xB - xA)
    else:
        # 若线段垂直，则使用 y 坐标计算
        t = (yP - yA) / (yB - yA)
    
    return t

def compute_intersection(A, B, C, D):
    """计算两线段的交点坐标"""
    x1, y1 = A
    x2, y2 = B
    x3, y3 = C
    x4, y4 = D

    denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    
    # 如果分母为0，表示线段平行或共线，已在segments_intersect中处理
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denominator
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denominator

    # 检查参数t和u是否在[0,1]范围内，确保交点在线段上
    if 0 <= t <= 1 and 0 <= u <= 1:
        x = x1 + t * (x2 - x1)
        y = y1 + t * (y2 - y1)
        return (x, y), t, u # t是第一条线段上的参数, u 是第二条线段上的参数
    else:
        return None, None, None

def on_segment(A, B, C):
    """检查点C是否在线段AB上"""
    return (min(A[0], B[0]) <= C[0] <= max(A[0], B[0]) and
            min(A[1], B[1]) <= C[1] <= max(A[1], B[1]))


def point_to_line_segment_distance(point, line_start, line_end):
    """
    计算二维点到二维线段的最小距离
    
    Args:
        point (tuple): 待计算的点，格式为 (x, y)
        line_start (tuple): 线段起点，格式为 (x, y)
        line_end (tuple): 线段终点，格式为 (x, y)
    
    Returns:
        float: 点到线段的最小距离
    """
    # 线段的向量
    line_vec = (line_end[0] - line_start[0], line_end[1] - line_start[1])
    # 点到线段起点的向量
    point_vec = (point[0] - line_start[0], point[1] - line_start[1])
    # 线段长度的平方
    line_len_squared = line_vec[0]**2 + line_vec[1]**2
    
    # 如果线段实际上是一个点
    if line_len_squared == 0:
        return math.hypot(point_vec[0], point_vec[1])
    
    # 计算点积
    dot_product = point_vec[0] * line_vec[0] + point_vec[1] * line_vec[1]
    # 计算投影比例 t
    t = max(0, min(1, dot_product / line_len_squared))
    
    # 计算投影点
    projection = (
        line_start[0] + t * line_vec[0],
        line_start[1] + t * line_vec[1]
    )
    
    # 计算点到投影点的距离
    distance = math.hypot(point[0] - projection[0], point[1] - projection[1])
    
    return distance

def get_formatted_datetime() -> str:
    now = datetime.datetime.now()
    formatted = now.strftime("%Y-%m-%d_%H-%M-%S")
    return formatted

def bezier_midpoint_and_tangent(start, control, end):
    """
    计算二次贝塞尔曲线的中点和中点处的切向量
    
    Args:
        start(tuple): 起点坐标 (x, y)
        control(tuple): 控制点坐标 (x, y)
        end(tuple): 终点坐标 (x, y)
    
    Returns:
        (midpoint, tangent)
        midpoint(tuple): 曲线中点坐标 (x, y)
        tangent(tuple): 中点处的切向量 (dx, dy)，已归一化
    """
    # 转换为numpy数组以便计算
    start = np.array(start)
    control = np.array(control)
    end = np.array(end)
    
    # 计算中点 (t=0.5)
    midpoint = 0.25 * start + 0.5 * control + 0.25 * end
    
    # 计算中点处的切向量 (导数)
    tangent = 2 * (0.5 * (control - start) + 0.5 * (end - control))
    
    # 归一化切向量
    if np.linalg.norm(tangent) > 0:
        tangent = tangent / np.linalg.norm(tangent)
    
    return tuple(midpoint), tuple(tangent)
