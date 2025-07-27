import numpy
import os
from i18n import _

# 相对导入
import math_utils
import constant_config

class MemoryObject:
    def __init__(self, auto_load=True) -> None:
        self.clear()
        self.empty_info = self.get_all_info()

        if auto_load and os.path.isfile(constant_config.AUTOSAVE_FILE): # 自动加载存档
            print(_("正在加载自动保存的存档 ..."))
            try:
                self.load_object(constant_config.AUTOSAVE_FILE)
            except:
                print(_("加载失败，自动存档文件故障"))

    def clear(self): # 初始化为空白状态
        self.dot_id_max = 0
        self.line_id_max = 0

        self.dot_dict = {}
        self.line_dict = {}
        self.inverse_pairs = {}
        self.degree = {}

        self.base_dot = [] # 记录起始位置
        self.dir_dot = []  # 记录定向位置
        self.pd_code_final = None # 用于确定 pd_code 渲染信息，任何操作都会导致这个 info 被清空

    def set_pd_code_final_info(self, new_info): # 记录这个 final_info
        self.pd_code_final = new_info

    def get_pd_code_final_info(self) -> dict|None:
        return self.pd_code_final

    def split_line_at(self, line_id, x, y):
        self.pd_code_final = None
        assert self.line_dict.get(line_id) is not None

        dot_id = self.new_dot(x, y)
        from_id, to_id = self.line_dict[line_id]

        self.erase_line(line_id)
        self.new_line(from_id, dot_id) # 拆分一个条边
        self.new_line(dot_id, to_id)

    def get_degree(self):
        return self.degree
    
    def get_all_info(self) -> dict: # 获取对象的完整信息
        return {
            "dot_id_max": self.dot_id_max,
            "line_id_max": self.line_id_max,
            "dot_dict": self.dot_dict,
            "line_dict": self.line_dict,
            "inverse_pairs": self.inverse_pairs,
            "degree": self.degree,
            "base_dot": self.base_dot,
            "dir_dot": self.dir_dot,
            "pd_code_final": self.pd_code_final,
        }
    
    def get_all_auto_save(self):
        arr = []
        for file in os.listdir(constant_config.AUTOSAVE_FOLDER):
            if file != os.path.basename(constant_config.AUTOSAVE_FILE):
                arr.append(file)
        arr = sorted(arr)
        return arr

    def load_last_auto_save(self):
        arr = self.get_all_auto_save()
        if len(arr) >= 1:
            lastfile = os.path.join(constant_config.AUTOSAVE_FOLDER, arr[-1])
            self.load_object(lastfile)

    def auto_delete_duplicate(self):
        arr = self.get_all_auto_save()
        if len(arr) >= 2:
            lastfile = os.path.join(constant_config.AUTOSAVE_FOLDER, arr[-1]) # 倒数第一个
            nextfile = os.path.join(constant_config.AUTOSAVE_FOLDER, arr[-2]) # 倒数第二个

            if open(lastfile).read() == open(nextfile).read():
                try:
                    os.remove(lastfile)
                    print(_("由于没有修改，因此最后一次自动保存被删除"))
                except:
                    pass

    def auto_backup(self): # 自动保存时，不允许保持空白状态，但是退出时的自动保存可以保存空白状态
        if self.get_all_info() != self.empty_info: 
            filename = math_utils.get_formatted_datetime() + ".json"
            folder = constant_config.AUTOSAVE_FOLDER
            filepath = os.path.join(folder, filename)
            self.dump_object(filepath) # 保存一个备份文件，每隔一段时间自动保存一次

            self.auto_delete_duplicate() # 自动删除重复的

    def dump_object(self, filepath:str):
        folder = os.path.dirname(os.path.abspath(filepath)) # 创建文件路径
        os.makedirs(folder, exist_ok=True)
        assert os.path.isdir(folder)

        with open(filepath, "w") as fp:
            fp.write(repr(self.get_all_info())) # 这种序列化方式有点不安全

    def load_object(self, filepath:str):
        assert os.path.isfile(filepath)
        with open(filepath, "r") as fp:
            obj = eval(fp.read()) # 这种序列化方式有点不安全
        self.dot_id_max = obj["dot_id_max"]
        self.line_id_max = obj["line_id_max"]
        self.dot_dict = obj["dot_dict"]
        self.line_dict = obj["line_dict"]
        self.inverse_pairs = obj["inverse_pairs"]
        self.degree = obj["degree"]
        self.base_dot = obj["base_dot"]
        self.dir_dot = obj["dir_dot"]
        self.pd_code_final = obj["pd_code_final"]

    def get_inverse_pairs(self):
        return self.inverse_pairs
    
    def shift_position(self, dx, dy): # 所有点一起移动
        # 需要注意的是，这里需要移动 self.pd_code_final，因为这种移动不会破坏拓扑性质
        if self.pd_code_final is not None:
            for term in self.pd_code_final:
                term["pos"] = (term["pos"][0] + dx, term["pos"][1] + dy)

        for dot_idx in self.dot_dict:
            x, y = self.dot_dict[dot_idx]
            self.dot_dict[dot_idx] = (x + dx, y + dy)

    def set_base_dot(self, dot_idx): # 设置起始位置
        self.pd_code_final = None
        if dot_idx not in self.base_dot:
            self.base_dot.append(dot_idx)

            if dot_idx in self.dir_dot:
                self.dir_dot.remove(dot_idx)
        else:
            self.base_dot.remove(dot_idx)
    
    def set_dir_dot(self, dot_idx): # 设置起始位置的下一个位置，用于确定方向
        self.pd_code_final = None
        if dot_idx not in self.dir_dot:
            self.dir_dot.append(dot_idx)

            if dot_idx in self.base_dot:
                self.base_dot.remove(dot_idx)
        else:
            self.dir_dot.remove(dot_idx)

    def swap_line_order(self, line_idx1, line_idx2):
        self.pd_code_final = None
        assert line_idx1 != line_idx2
        assert self.line_dict.get(line_idx1) is not None
        assert self.line_dict.get(line_idx2) is not None
        
        if int(line_idx1.split("_")[-1]) < int(line_idx2.split("_")[-1]): # 保证 line_idx1 > line_idx2
            line_idx1, line_idx2 = line_idx2, line_idx1

        if self.inverse_pairs.get((line_idx1, line_idx2)) is None: # 如果没有这个逆向对要求，则添加
            self.inverse_pairs[(line_idx1, line_idx2)] = True
        else:                                                      # 如果有这个逆向对要求，则删掉
            del self.inverse_pairs[(line_idx1, line_idx2)]

    def find_nearest_lines(self, x, y, max_dis=constant_config.CIRCLE_RADIUS + constant_config.LINE_WIDTH/2 + 1):
        line_pair_list = []
        for line_id in self.line_dict:
            dot_from, dot_to = self.line_dict[line_id]
            pos_from = self.dot_dict[dot_from]
            pos_to   = self.dot_dict[dot_to]
            dis = math_utils.point_to_line_segment_distance((x, y), pos_from, pos_to)

            if dis <= max_dis:
                line_pair_list.append((line_id, dis))
        return line_pair_list
    
    # 计算一个插值位置
    def get_interpos(self, dot_id_1, dot_id_2, rate:float, shrink_mode=None):
        x1, y1 = self.dot_dict[dot_id_1]
        x2, y2 = self.dot_dict[dot_id_2]

        if shrink_mode is not None: # 留出一小部分的空白区域
            # 计算线长度
            length = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

            # 计算差距比例
            delta_rate = constant_config.CIRCLE_RADIUS / length / 2

            if shrink_mode == "l":
                rate += delta_rate
            elif shrink_mode == "r":
                rate -= delta_rate

        rate = min(max(rate, 0.0), 1.0) # 限制范围
        return (x1 + (x2 - x1) * rate, y1 + (y2 - y1) * rate)

    def get_view_box(self): # 计算所有节点的包围盒
        xmin =  + math_utils.math.inf
        xmax =  - math_utils.math.inf
        ymin =  + math_utils.math.inf
        ymax =  - math_utils.math.inf
        for dot_id in self.dot_dict:
            xpos, ypos = self.dot_dict[dot_id]
            xmin = min(xmin, xpos)
            ymin = min(ymin, ypos)
            xmax = max(xmax, xpos)
            ymax = max(ymax, ypos)
        return (xmin, ymin, xmax, ymax)

    def set_dot_position(self, dot_id, x, y): # 设置节点位置
        self.pd_code_final = None
        conflict = False
        for dot_id_now in self.dot_dict:
            if dot_id_now == dot_id:
                continue
            
            xnow, ynow = self.dot_dict[dot_id_now]
            if numpy.linalg.norm(numpy.array([xnow - x, ynow - y])) <= 2*constant_config.CIRCLE_RADIUS + 1:
                conflict =True
                break

        if not conflict: # 不允许点重合
            self.dot_dict[dot_id] = (x, y)

    def get_dot_dict(self) -> dict: # 获得节点表
        return self.dot_dict

    def get_line_dict(self) -> dict: # 获得边表
        return self.line_dict

    def erase_line(self, line_id:str): # 删除一条边
        self.pd_code_final = None
        if self.line_dict.get(line_id) is not None:
            frm, eto = self.line_dict[line_id]
            self.degree[frm] -= 1
            self.degree[eto] -= 1 # 统计度数
            del self.line_dict[line_id]

        inverse_pair_to_erase = []
        for item in self.inverse_pairs:
            line_id_1, line_id_2 = item
            if line_id_1 == line_id or line_id_2 == line_id:
                inverse_pair_to_erase.append(item)

        for item in inverse_pair_to_erase: # 删除所有无效逆序处理
            del self.inverse_pairs[item]

    # 检查两条线段之间的上下关系（两条线段不一定相交）
    def check_line_under(self, line_id_1:str, line_id_2:str) -> bool:
        def xor(x:bool, y:bool): # 异或运算
            return x != y
        
        invsps = self.get_inverse_pairs()

        # 我们需要判断 line_id_1 和 lind_id_2 谁在下面
        # line_1_under_line_2 = True 表示 line_1 在 line_2 下面
        # 计算时发现了错误
        line_1_under_line_2 = xor(
            (int(line_id_1.split("_")[-1]) < int(line_id_2.split("_")[-1])), # 按照数值大小排序，而不是按照字符串字典序
            (invsps.get((line_id_1, line_id_2)) is not None) or (invsps.get((line_id_2, line_id_1)) is not None))
        
        return line_1_under_line_2


    def new_dot(self, x:int, y:int): # 新增一个节点：不包含共线检查功能
        self.pd_code_final = None
        while self.dot_dict.get("dot_%d" % self.dot_id_max):
            self.dot_id_max += 1
        new_id = "dot_%d" % self.dot_id_max
        self.dot_dict[new_id] = (x, y)
        self.degree[new_id] = 0
        return new_id

    def new_line(self, dot_id_1:str, dot_id_2:str): # 新增一条边：不包含共线检查功能
        self.pd_code_final = None
        assert dot_id_1 != dot_id_2

        if int(dot_id_1.split("_")[-1]) > int(dot_id_2.split("_")[-1]):
            dot_id_1, dot_id_2 = dot_id_2, dot_id_1

        for line_id in self.line_dict:
            frm1, eto1 = self.line_dict[line_id]
            if frm1 == dot_id_1 and eto1 == dot_id_2: # 找到了一个旧的一样的边
                print(_("找到一条原有的边：%s") % line_id)
                return line_id
        
        while self.line_dict.get("line_%d" % self.line_id_max):
            self.line_id_max += 1

        new_id = "line_%d" % self.line_id_max
        self.line_dict[new_id] = (dot_id_1, dot_id_2)
        self.degree[dot_id_1] += 1
        self.degree[dot_id_2] += 1

        print(_("创建了一条新的边: %s") % new_id)
        return new_id

    def erase_dot(self, dot_id:str): # 删除节点的时候，记得删除相应的边，以及边之间的逆序关系
        self.pd_code_final = None
        if self.dot_dict.get(dot_id) is not None:

            if self.base_dot == dot_id: # 删除已经消失的起始点
                self.set_base_dot(None)

            if self.dir_dot == dot_id:
                self.set_dir_dot(None)

            line_list_to_erase = []
            for line_id in self.line_dict:
                dot_id_1, dot_id_2 = self.line_dict[line_id]

                if dot_id in [dot_id_1, dot_id_2]:
                    line_list_to_erase.append(line_id)

            for line_id in line_list_to_erase: # 删除无效线段，以及相应的边关系
                self.erase_line(line_id)

            if dot_id in self.base_dot: # 从两个 list 中删除结点
                self.base_dot.remove(dot_id)

            if dot_id in self.dir_dot:
                self.dir_dot.remove(dot_id)

            del self.dot_dict[dot_id]

            assert self.degree[dot_id] == 0
            del self.degree[dot_id]
    
    # merge 的功能：如果两个相同的数字挨得太近，那就把他们合并成一个数字，并放在中点位置
    def get_number_position_pairs(self, merge=True) -> list:
        def unit(pair_x_y): # 单位化一个向量
            x, y = pair_x_y
            length = (x ** 2 + y ** 2) ** 0.5 # 计算长度
            return (x / length, y / length)

        def mul(pair_x_y, r): # 倍长一个向量
            x, y = pair_x_y
            return (x * r, y * r)
        
        def add(pair_x_y1, pair_x_y2):
            x1, y1 = pair_x_y1
            x2, y2 = pair_x_y2
            return (x1 + x2, y1 + y2)

        # 一个小偏移量，用于让显示更加自然
        delta_pos = (-constant_config.SMALL_TEXT_SIZE/2, -constant_config.SMALL_TEXT_SIZE/2)

        pd_code_final_info = self.get_pd_code_final_info()
        if pd_code_final_info is None:
            assert False
        
        arr = []
        for term in pd_code_final_info: # 按照指定方向绘制四个整数
            x    = term["X"]
            pos  = term["pos"]
            dir0 = mul(unit(term["dir"][0]), constant_config.CIRCLE_RADIUS * 1.7 + 1)
            dir1 = mul(unit(term["dir"][1]), constant_config.CIRCLE_RADIUS * 1.7 + 1)
            dir2 = mul(dir0, -1)
            dir3 = mul(dir1, -1)
            dirs = [dir0, dir1, dir2, dir3]

            for i in range(4):
                pos_to_show = add(add(dirs[i], pos), delta_pos)
                arr.append((str(x[i]), pos_to_show))

        if merge:
            new_arr = []
            num_to_pos_dict = {}
            
            for txt, pos in arr: # 统计每种数值出现的每一个位置
                if num_to_pos_dict.get(txt) is None:
                    num_to_pos_dict[txt] = []
                num_to_pos_dict[txt].append(pos)

            for txt in num_to_pos_dict: # 每个数值，必须出现且恰好出现两次
                assert len(num_to_pos_dict[txt]) == 2

            for txt in num_to_pos_dict:
                pos1 = num_to_pos_dict[txt][0]
                pos2 = num_to_pos_dict[txt][1]

                if numpy.linalg.norm(numpy.array([pos1[0] - pos2[0], pos1[1] - pos2[1]])) <= 2.5 * constant_config.SMALL_TEXT_SIZE:
                    new_arr.append((txt, ((pos1[0] + pos2[0]) / 2, (pos1[1] + pos2[1]) / 2)))
                else:
                    new_arr.append((txt, pos1))
                    new_arr.append((txt, pos2))
            arr = new_arr # 覆盖
        return arr
    