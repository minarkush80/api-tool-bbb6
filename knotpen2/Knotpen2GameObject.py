import pygame
import numpy
import time
import functools
import os

# 相对导入
import i18n
from i18n import _
import GameObject
import MemoryObject
import MyAlgorithm
import constant_config
import pygame_utils
import math_utils

STATUS_LIST = [
    "free",        # 自由状态
    "select_dot",  # 选中了一个结点
    "quit",        # 退出程序
    "move_dot",    # 移动一个节点
]

class Knotpen2GameObject(GameObject.GameObject):
    def __init__(self, memory_object:MemoryObject.MemoryObject, algo:MyAlgorithm.MyAlgorithm) -> None:
        super().__init__()

        self.font    = pygame.font.Font(constant_config.FONT_TTF, constant_config.MESSAGE_SIZE)
        self.msg_txt = [
            self.font.render("0: %s %s" % (_("欢迎使用"), self.get_window_caption()), True, constant_config.BLACK)
        ]
        self.msg_line_id = 1

        self.node_font = pygame.font.Font(constant_config.FONT_TTF, constant_config.SMALL_TEXT_SIZE)
        @functools.cache
        def get_small_text(s:str, color): # 用于避免小文本的重复绘制
            return self.node_font.render(s, True, color)
        self.get_small_text  = get_small_text

        self.memory_object   = memory_object
        self.algo            = algo
        self.status          = "free"
        self.focus_dot       = None
        self.left_mouse_down = False
        self.actually_moved  = False
        self.last_click      = -1          # 上次鼠标左键抬起的时刻
        self.last_c_down     = -1          # 上次键盘按下 c 键
        self.last_l_down     = -1          # 上次键盘按下 l 键
        self.last_n_down     = -1          # 上次键盘按下 n 键
        self.last_r_down     = -1          # 键盘上一次按下按键 r 的时刻
        self.last_backup     = time.time() # 上次自动保存时间
        self.notice_node     = []          # 用红色标出一些节点编号
    
    def get_window_caption(self) -> str:
        return constant_config.APP_NAME + "_" + constant_config.APP_VERSION

    def handle_quit(self):
        self.leave_message(_("自动保存中，请不要关闭窗口 ..."), constant_config.YELLOW)
        self.memory_object.dump_object(constant_config.AUTOSAVE_FILE) # 自动保存
        self.leave_message(_("自动保存成功"), constant_config.GREEN)

        self.status = "quit"
    
    def handle_mouse_down(self, button, x, y): # 鼠标按下
        super().handle_mouse_down(button, x, y)
        
        if button == constant_config.LEFT_KEY_ID:
            self.handle_left_mouse_down(x, y)

    def leave_message(self, s, color=constant_config.BLACK, replace=False): # 在屏幕上绘制信息
        if replace and len(self.msg_txt) >= 1: # 替换最后一条消息
            self.msg_txt = self.msg_txt[:-1]

        text_now = "%d: %s" % (self.msg_line_id, s)
        print(text_now)

        self.msg_txt.append(self.font.render(text_now, True, color))

        if not replace: # 替换最后一条消息的时候，不需要增加 id
            self.msg_line_id += 1

        while len(self.msg_txt) > constant_config.MAX_MESSAGE_CNT:
            self.msg_txt = self.msg_txt[1:]

    def save_answer(self, s:str):
        os.makedirs(constant_config.ANSWER_FOLDER, exist_ok=True)
        foldername  = os.path.basename(constant_config.ANSWER_FOLDER) # 文件夹名称
        outter_name = os.path.basename(os.path.dirname(constant_config.ANSWER_FOLDER))
        filename    = math_utils.get_formatted_datetime() + ".txt"
        filepath    = os.path.join(constant_config.ANSWER_FOLDER, filename)

        with open(filepath, "w") as fp:
            fp.write(s)

        return "%s/%s/%s" % (outter_name, foldername, filename)

    def save_svg_answer(self, svg_filename:str, s):
        os.makedirs(constant_config.ANSWER_FOLDER, exist_ok=True)
        foldername  = os.path.basename(constant_config.ANSWER_FOLDER) # 文件夹名称
        outter_name = os.path.basename(os.path.dirname(constant_config.ANSWER_FOLDER))
        filename    = svg_filename
        filepath    = os.path.join(constant_config.ANSWER_FOLDER, filename)

        with open(filepath, "w") as fp:
            fp.write(s)

        return "%s/%s/%s" % (outter_name, foldername, filename)

    def output_answer(self):
        self.leave_message(_("开始计算 PD_CODE"), constant_config.YELLOW)
        degree_check_list = self.algo.degree_check()
        if len(degree_check_list) > 0: # 发现了有些节点度不为 2
            self.leave_message(_("%d 个节点度数不为 2，请注意灰色标出的节点") % len(degree_check_list), constant_config.RED)
            return
        adj_list, block_list        = self.algo.get_connected_components()           # 计算出所有连通分支
        suc, msg, baseL, dirL, nntc = self.algo.check_base_dir(adj_list, block_list) # 检查每个连通分支是否都有 base 和 dir 节点，检查节点数是否大于等于 3
        self.notice_node            = nntc
        if not suc:
            self.leave_message(msg, constant_config.RED)
            return
        # pd_code_to_show 中记录的是最终计算得到的 pd_code
        # pd_code_final 中记录的是用于在屏幕上显示 pd_code 弧线编号的相关信息
        # parts 记录的是每个连通分量上的交叉点构成的序列，parts 对连通分量的处理顺序与 block_list 一致
        pd_code_to_show, pd_code_final, parts = self.algo.solve_pd_code(adj_list, block_list, baseL, dirL, self.leave_message)
        self.memory_object.set_pd_code_final_info(pd_code_final)

        # 保存文本文件的 PD_CODE
        filename = self.save_answer(str(pd_code_to_show))
        self.leave_message(_("PD_CODE 计算成功"), constant_config.GREEN)
        self.leave_message(_("保存在 %s") % filename, constant_config.GREEN)

        # 生成 svg 文件格式的扭结图片（不带有弧线编号信息）
        svg_filename = filename.split("/")[-1].replace(".txt", ".nonum.svg")
        svg_text = self.algo.calculate_svg(block_list, parts, False, False)
        svg_return_name = self.save_svg_answer(svg_filename, svg_text)
        self.leave_message(_("扭结图像（不带弧线编号信息）生成成功"), constant_config.GREEN)
        self.leave_message(_("保存在 %s") % svg_return_name, constant_config.GREEN)

        # 生成 svg 文件格式的扭结图片（带有弧线编号信息）
        svg_filename = filename.split("/")[-1].replace(".txt", ".num.svg")
        svg_text = self.algo.calculate_svg(block_list, parts, True, False)
        svg_return_name = self.save_svg_answer(svg_filename, svg_text)
        self.leave_message(_("扭结图像（带弧线编号信息）生成成功"), constant_config.GREEN)
        self.leave_message(_("保存在 %s") % svg_return_name, constant_config.GREEN)

        # 生成 svg 文件格式的扭结图片（带有弧线方向信息）
        svg_filename = filename.split("/")[-1].replace(".txt", ".arrow.svg")
        svg_text = self.algo.calculate_svg(block_list, parts, False, True)
        svg_return_name = self.save_svg_answer(svg_filename, svg_text)
        self.leave_message(_("扭结图像（带弧线方向信息）生成成功"), constant_config.GREEN)
        self.leave_message(_("保存在 %s") % svg_return_name, constant_config.GREEN)
    
    def handle_key_down(self, key, mod, unicode): # 处理键盘事件
        super().handle_key_down(key, mod, unicode)

        key_name = pygame.key.name(key)
        if key_name == 'a':
            self.memory_object.shift_position(-constant_config.STRIDE, 0)

        elif key_name == 'b': # set base point

            if self.status == "select_dot":
                if self.focus_dot is not None:
                    self.memory_object.set_base_dot(self.focus_dot)
                    self.status = "free"
                    self.focus_dot = None # 回退到常规模式

        elif key_name == 'c':
            if time.time() - self.last_c_down < constant_config.DOUBLE_CLICK_TIME:
                self.memory_object.auto_backup()
                self.memory_object.clear()
            self.last_c_down = time.time()

        elif key_name == 'd':
            self.memory_object.shift_position(+constant_config.STRIDE, 0)

        elif key_name == 'l':
            if time.time() - self.last_l_down < constant_config.DOUBLE_CLICK_TIME:
                self.output_answer()
            self.last_l_down = time.time()

        elif key_name == 'n': # 切换语言
            if time.time() - self.last_n_down < constant_config.DOUBLE_CLICK_TIME:
                i18n.set_next_language(self.leave_message)
            self.last_n_down = time.time()

        elif key_name == 'r':
            if time.time() - self.last_r_down < constant_config.DOUBLE_CLICK_TIME:
                self.memory_object.load_last_auto_save()
            self.last_r_down = time.time()

        elif key_name == 's':
            self.memory_object.shift_position(0, +constant_config.STRIDE)

        elif key_name == 't': # set dir point
            if self.status == "select_dot":
                if self.focus_dot is not None:
                    self.memory_object.set_dir_dot(self.focus_dot)
                    self.status = "free"
                    self.focus_dot = None # 回退到常规模式
        
        elif key_name == 'w':
            self.memory_object.shift_position(0, -constant_config.STRIDE)

        elif key_name == 'delete' or key_name == 'backspace':
            if self.status == "select_dot" and self.focus_dot is not None: # 删除节点并回退到正常模式
                self.memory_object.erase_dot(self.focus_dot)
                self.status = "free"
                self.focus_dot = None # 回退到常规模式

    
    def handle_left_mouse_down(self, x, y):
        self.left_mouse_down = True
        mouse_on_dot_id = self.get_mouse_on_dot_id(x, y)
        
        if self.status == "free":
            if mouse_on_dot_id is not None: # 开始移动节点
                self.focus_dot = mouse_on_dot_id
                self.status = "move_dot"
                self.actually_moved = False

    
    def handle_mouse_move(self, x, y, show_log=False):
        super().handle_mouse_move(x, y, show_log)

        if self.status == "move_dot" and self.focus_dot is not None:
            self.memory_object.set_dot_position(self.focus_dot, x, y)
            self.actually_moved = True

    def get_mouse_on_dot_id(self, x, y):
        mouse_on_dot_id = None
        dot_dict = self.memory_object.get_dot_dict() # 绘制所有节点
        for dot_id in dot_dict:
            x_dot, y_dot = dot_dict[dot_id]
            if numpy.linalg.norm(numpy.array([x_dot - x, y_dot - y])) <= constant_config.CIRCLE_RADIUS + 1:
                mouse_on_dot_id = dot_id
                break
        return mouse_on_dot_id

    def handle_left_mouse_up(self, x, y):
        self.left_mouse_down = False
        mouse_on_dot_id = self.get_mouse_on_dot_id(x, y)

        if self.status == "move_dot": # 移动节点结束
            self.status = "free"
        
        if self.status == "free":
            if mouse_on_dot_id is None:
                line_pair_list = self.memory_object.find_nearest_lines(x, y)

                if len(line_pair_list) == 2: # 左键交换上下关系
                    self.memory_object.swap_line_order(line_pair_list[0][0], line_pair_list[1][0])

                elif len(line_pair_list) == 0: # 自由状态创建点
                    self.memory_object.new_dot(x, y)

                elif len(line_pair_list) == 1 and time.time() - self.last_click < constant_config.DOUBLE_CLICK_TIME:
                    self.memory_object.split_line_at(line_pair_list[0][0], x, y)
            
            elif not self.actually_moved: # 刚刚结束拖动的时候不可以选中
                self.focus_dot = mouse_on_dot_id
                self.status = "select_dot"

        elif self.status == "select_dot":
            if mouse_on_dot_id is not None: # 选中点的前提下点击空地
                if self.focus_dot is not None and mouse_on_dot_id != self.focus_dot:
                    self.memory_object.new_line(mouse_on_dot_id, self.focus_dot)
                self.status = "free"
                self.focus_dot = None
            else:
                if mouse_on_dot_id is None and self.focus_dot is not None: # 传递一个新的 focus
                    dot_id = self.memory_object.new_dot(x, y)
                    self.memory_object.new_line(dot_id, self.focus_dot)
                    self.status    = "select_dot"
                    self.focus_dot = dot_id # 焦点传递
        
        self.last_click = time.time() # 设置上次鼠标左键抬起的时刻

    
    def handle_mouse_up(self, button, x, y):
        super().handle_mouse_up(button, x, y)
        if button == constant_config.LEFT_KEY_ID: # 点击左键可以添加结点
            self.handle_left_mouse_up(x, y)

        elif button == constant_config.RIGHT_KEY_ID: # 右键单击可以删除结点
            self.handle_right_mouse_up(x, y)


    def handle_right_mouse_up(self, x, y):
        if self.status == "free":
            mouse_on_dot_id = self.get_mouse_on_dot_id(x, y)

            if mouse_on_dot_id is not None: # 右键删除节点
                self.memory_object.erase_dot(mouse_on_dot_id)

            else: # 右键点击可以删除线
                line_pair_list = self.memory_object.find_nearest_lines(x, y)

                if len(line_pair_list) == 1: # 删除一个边
                    self.memory_object.erase_line(line_pair_list[0][0])
        
        elif self.status == "select_dot": # 退出节点选择模式
            self.status = "free"

    
    def draw_screen(self, screen): # 绘制屏幕内容
        super().draw_screen(screen)

        time_now = time.time()
        if time_now - self.last_backup > constant_config.BACKUP_TIME:     # 自动保存
            self.leave_message(_("正在自动保存请不要关闭软件 ..."), constant_config.YELLOW)
            self.memory_object.auto_backup()                              # 保存一个时间戳对应的文件
            self.memory_object.dump_object(constant_config.AUTOSAVE_FILE) # 保存一个 auto_save
            self.leave_message(_("自动保存成功"), constant_config.GREEN, replace=True)
            self.last_backup = time_now

        if self.memory_object.base_dot is not None: # 绘制起始点
            for base_dot_id in self.memory_object.base_dot:
                x, y = self.memory_object.dot_dict[base_dot_id]
                pygame_utils.draw_empty_circle(screen, constant_config.BLUE, x, y, constant_config.CIRCLE_RADIUS + 3)

        if self.memory_object.dir_dot is not None: # 绘制方向点
            for dir_dot_id in self.memory_object.dir_dot:
                x, y = self.memory_object.dot_dict[dir_dot_id]
                pygame_utils.draw_empty_circle(screen, constant_config.GREEN, x, y, constant_config.CIRCLE_RADIUS + 3)

        dot_dict  = self.memory_object.get_dot_dict()
        line_dict = self.memory_object.get_line_dict()
        for line_id in line_dict:
            dot_from, dot_to = line_dict[line_id]
            pos_from = dot_dict[dot_from]
            pos_to   = dot_dict[dot_to]
            pygame_utils.draw_thick_line(screen, pos_from, pos_to, constant_config.LINE_WIDTH, constant_config.BLACK)

        for dot_id in dot_dict: # 绘制所有节点
            x, y = dot_dict[dot_id]

            color = constant_config.BLACK
            if self.status == "select_dot" and dot_id == self.focus_dot:
                color = constant_config.RED
            pygame_utils.draw_empty_circle(screen, color, x, y, constant_config.CIRCLE_RADIUS)

            if self.memory_object.get_degree()[dot_id] != 2:
                pygame_utils.draw_full_circle(screen, constant_config.GREY, x, y, constant_config.CIRCLE_RADIUS - 3)

        # 重新绘制所有逆向边遮挡
        for item in self.memory_object.get_inverse_pairs():
            line_id1, line_id2 = item
            dot_11, dot_12 = self.memory_object.get_line_dict()[line_id1]
            dot_21, dot_22 = self.memory_object.get_line_dict()[line_id2]
            pos_11 = dot_dict[dot_11]
            pos_12 = dot_dict[dot_12]
            pos_21 = dot_dict[dot_21]
            pos_22 = dot_dict[dot_22]
            pygame_utils.draw_line_on_line(screen, pos_11, pos_12, pos_21, pos_22, constant_config.BLACK)

        # 绘制全局消息
        for i in range(len(self.msg_txt)):
            screen.blit(self.msg_txt[i], constant_config.MESSAGE_POSITION(i))

        # 绘制节点编号
        for dot_id in dot_dict:
            posx, posy = dot_dict[dot_id]
            
            color = constant_config.BLACK
            if dot_id in self.notice_node:
                color = constant_config.RED

            text_now = self.get_small_text(dot_id.split("_")[-1], color)
            screen.blit(text_now, (posx - constant_config.CIRCLE_RADIUS + 1, posy - constant_config.CIRCLE_RADIUS + 1))

        # 绘制 pd_code_final_info
        # 这段代码的用途是对每个交叉点，将数字绘制到交叉点附近
        pd_code_final_info = self.memory_object.get_pd_code_final_info()
        if pd_code_final_info is not None:
            
            # 计算屏幕上需要显示的编号
            number_postion_pairs = self.memory_object.get_number_position_pairs()

            # 将这些编号输出到屏幕上
            for number_str, pos_to_show in number_postion_pairs:
                txt_val = self.get_small_text(number_str, constant_config.RED)
                screen.blit(txt_val, pos_to_show)
    
    def die_check(self):
        return self.status == "quit"
