import pygame
import math
import numpy

# 相对导入
import constant_config
import math_utils

def draw_thick_line(screen, start, end, width, color):
    """绘制有宽度的线（使用多边形）"""
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    length = math.sqrt(dx*dx + dy*dy)
    
    if length == 0:
        return  # 起点和终点相同，无法绘制线
    
    # 计算垂直于线段的方向
    perp_x = -dy / length
    perp_y = dx / length
    
    # 计算四个顶点
    offset = width / 2
    p1 = (start[0] + perp_x * offset, start[1] + perp_y * offset)
    p2 = (start[0] - perp_x * offset, start[1] - perp_y * offset)
    p3 = (end[0] - perp_x * offset, end[1] - perp_y * offset)
    p4 = (end[0] + perp_x * offset, end[1] + perp_y * offset)
    
    # 绘制填充的多边形（白色长方形）
    pygame.draw.polygon(screen, constant_config.WHITE, [p1, p2, p3, p4])
    
    # 绘制边框（无填充的长方形）
    pygame.draw.polygon(screen, color, [p1, p2, p3, p4], 1)

def draw_empty_circle(screen, border_color, x, y, radius):
    pygame.draw.circle(screen, constant_config.WHITE, (x, y), radius)
    pygame.draw.circle(screen, border_color, (x, y), radius, 1)

def draw_full_circle(screen, fill_color, x, y, radius):
    pygame.draw.circle(screen, fill_color, (x, y), radius)

# 把 pos_21 ~ pos_22 画在 pos_11 ~ pos_12 上面
def draw_line_on_line(screen, pos_11, pos_12, pos_21, pos_22, line_color):
    crossing, _, _ = math_utils.segments_intersect((pos_11, pos_12), (pos_21, pos_22))
    if crossing is None:
        return
    
    pos_11 = numpy.array(pos_11).astype(numpy.float64)
    pos_12 = numpy.array(pos_12).astype(numpy.float64)
    pos_21 = numpy.array(pos_21).astype(numpy.float64)
    pos_22 = numpy.array(pos_22).astype(numpy.float64)

    dir_1 = pos_12 - pos_11
    dir_2 = pos_22 - pos_21

    dir_1 /= numpy.linalg.norm(dir_1)
    dir_2 /= numpy.linalg.norm(dir_2)

    norm_1 = numpy.array([-dir_1[1], dir_1[0]])
    norm_2 = numpy.array([-dir_2[1], dir_2[0]])

    p = []
    for i in range(2):
        for j in range(2):
            d1 = 2 * i - 1 # -1 或者 +1
            d2 = 2 * j - 1 # -1 或者 +1
            pos, _, _ = math_utils.compute_intersection(
                pos_11 + d1 * norm_1 * (constant_config.LINE_WIDTH / 2 + 0.5),
                pos_12 + d1 * norm_1 * (constant_config.LINE_WIDTH / 2 + 0.5),
                pos_21 + d2 * norm_2 * (constant_config.LINE_WIDTH / 2 + 0.5),
                pos_22 + d2 * norm_2 * (constant_config.LINE_WIDTH / 2 + 0.5),
            )
            p.append(pos)

    if None not in p:
        p[3], p[2] = p[2], p[3] # 修正顺序
        pygame.draw.polygon(screen, constant_config.WHITE, p)

        pygame.draw.line(screen, line_color, p[2], p[1])
        pygame.draw.line(screen, line_color, p[0], p[3])
