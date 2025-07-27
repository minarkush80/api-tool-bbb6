import numpy as np


# 相对导入
from i18n import _
import MemoryObject
import math_utils
import constant_config

class MyAlgorithm:
    def __init__(self, memory_object:MemoryObject.MemoryObject) -> None:
        self.memory_object = memory_object

    def degree_check(self): # 检查是不是所有节点的度都等于 2
        dot_dict = self.memory_object.get_dot_dict()
        degree   = self.memory_object.get_degree()

        degree_fault_arr = [] # 返回度数不对的节点
        for dot_id in dot_dict:
            if degree[dot_id] != 2:
                degree_fault_arr.append(dot_id)
        return degree_fault_arr
    
    def get_adj_list(self) -> dict: # 获得节点邻接表
        dot_dict  = self.memory_object.get_dot_dict()
        line_dict = self.memory_object.get_line_dict()

        adj_list = {}
        for dot in dot_dict:
            adj_list[dot] = [] # 记录所有后继节点

            for line in line_dict:
                dot_id_1, dot_id_2 = line_dict[line] # 枚举边表
                if dot_id_1 == dot:
                    adj_list[dot].append(dot_id_2)
                elif dot_id_2 == dot:
                    adj_list[dot].append(dot_id_1)
        return adj_list

    def __dfs(self, vis, adj_list, dot_now, block_now):
        vis[dot_now] = True
        block_now.append(dot_now)

        for dot_next in adj_list[dot_now]:
            if vis.get(dot_next) is not True:
                self.__dfs(vis, adj_list, dot_next, block_now)

    def get_connected_components(self): # 获取每个联通分支的 base 和 dir 点
        vis = {}
        adj_list = self.get_adj_list() # 获取邻接表
        block_list = [] # 记录所有连通分支的信息
        for dot_id in self.memory_object.get_dot_dict():
            if vis.get(dot_id) is True: # 避免重复 bfs 同一个节点
                continue
            block_now = []
            self.__dfs(vis, adj_list, dot_id, block_now)
            block_list.append(block_now)
        return adj_list, block_list

    def check_base_dir(self, adj_list, block_list): # 检查每个连通分支是否有 base 和 dir 以及他们是否相邻
        block_id_to_base_dot = {}
        block_id_to_dir_dot = {}

        for i in range(len(block_list)):
            block_id_to_base_dot[i] = []
            block_id_to_dir_dot[i] = []
            block_now = block_list[i]

            for j in range(len(block_now)):
                node_now = block_now[j]

                if node_now in self.memory_object.base_dot: # 记录所有 base_dot
                    block_id_to_base_dot[i].append(node_now)

                if node_now in self.memory_object.dir_dot: # 记录所有 dir_dot
                    block_id_to_dir_dot[i].append(node_now)

        if len(self.memory_object.get_dot_dict()) <= 2:
            return False, _("你至少要放置 3 个节点才能计算 PD_CODE"), None, None, []
    
        for i in range(len(block_list)): # 返回检查到的错误信息
            rep     = block_list[i][0]
            rep_num = int(rep.split("_")[-1]) # 代表元

            if len(block_id_to_base_dot[i]) == 0:
                return False, _("节点 %d 所在的连通分支没有定义起始点") % rep_num, None, None, [rep]
            
            if len(block_id_to_base_dot[i]) >= 2:
                return False, _("节点 %d 所在的连通分支没有定义了太多起始点") % rep_num, None, None, [rep]
            
            if len(block_id_to_dir_dot[i]) == 0:
                return False, _("节点 %d 所在的连通分支没有定义方向点") % rep_num, None, None, [rep]
            
            if len(block_id_to_dir_dot[i]) >= 2:
                return False, _("节点 %d 所在的连通分支没有定义了太多方向点") % rep_num, None, None, [rep]
            
            base = block_id_to_base_dot[i][0]
            dirx  = block_id_to_dir_dot[i][0]

            if dirx not in adj_list[base]:
                base_num = int(base.split("_")[-1])
                dirx_num = int(dirx.split("_")[-1])
                return False, _("起始点 {base_num} 与方向点 {dirx_num} 在同一连通分支但并不相邻").format(base_num=base_num, dirx_num=dirx_num), None, None, [base, dirx]
        
        return True, "", block_id_to_base_dot, block_id_to_dir_dot, [] # 没有检查到错误

    # 计算 pd_code
    # 这个程序可能很慢将来再考虑优化问题
    def solve_pd_code(self, adj_list, block_list, baseL, dirL, leave_msg):
        
        # 调整 block_list 到正确的顺序：base_node -> dir_node -> ...
        for i in range(len(block_list)):
            base_val = baseL[i][0]
            dir_val  = dirL[i][0]

            find = None
            for j in range(len(block_list[i])): # 找到 base 所在的位置
                if block_list[i][j] == base_val:
                    find = j
                    break
            assert find is not None

            block_list[i] = block_list[i][find:] + block_list[i][:find]

            if block_list[i][1] != dir_val: # 这说明 dir_val 在最后
                block_list[i] = block_list[i][::-1] # 先反转
                block_list[i] = [block_list[i][-1]] + block_list[i][:-1] # 再把最后一个挪到最前面
            
            assert block_list[i][0] == base_val # 调整正确的顺序
            assert block_list[i][1] == dir_val

        # 计算新的编号：Ci_Nj 表示一个节点位于连通分量 i、第 j 个节点
        # 这里的 nid 能够反应前进方向，但是并不是最终的弧线编号，而只是一个节点编号
        # debug 中：block_list 的计算为检测到异常
        dot_id_to_new_id = {}
        new_id_to_dot_id = {}
        for i in range(len(block_list)):
            for j in range(len(block_list[i])):
                dot_id_to_new_id[block_list[i][j]] = (i, j)
                new_id_to_dot_id[(i, j)] = block_list[i][j] # 这个过程必须是可逆的

        # 检查 nid1 是否位于 nid2 的后面的一个
        # 要求 nid1 和 nid2 必须在同一个连通分支上且相邻，否则会报错
        def check_after(nid1, nid2, block_list) -> bool: 
            c1, n1 = nid1
            c2, n2 = nid2

            assert c1 == c2
            length = len(block_list[c1])

            if n1 == 0:
                assert n2 == 1 or n2 == length-1
                return n2 == length-1
            
            else:
                if n2 == 0:
                    assert n1 == 1 or n1 == length-1
                    return n1 == 1

                assert abs(n1 - n2) == 1
                return n2 == n1-1

        # 定位所有交叉点的两重身份：(c1, n1, t1), (c2, n2, t2)
        # n1 表示交叉点所在的弧线，位于 c1 连通分支上第 n1 个节点后面的一段弧线
        # t1 表示他在这段弧线上的坐标 \in (0, 1)
        line_dict = self.memory_object.get_line_dict()
        dot_dict = self.memory_object.get_dot_dict()
        crossing_list = []
        for line_id_1 in line_dict:
            for line_id_2 in line_dict:

                if line_id_2 <= line_id_1: # 避免重复计算
                    continue
                d11, d12 = line_dict[line_id_1]
                d21, d22 = line_dict[line_id_2]

                if d21 in [d11, d12] or d22 in [d11, d12]: # 如果有交集，就跑路
                    continue

                p11 = dot_dict[d11] # 找到四个点的空间坐标，现在的顺序还是 line_dict 中的顺序，这里面的顺序一般来说都不对
                p12 = dot_dict[d12]
                p21 = dot_dict[d21]
                p22 = dot_dict[d22]

                nid11 = dot_id_to_new_id[d11] # 找到四个新编号，新编号是 bid 和 bdid 的二元组
                nid12 = dot_id_to_new_id[d12]
                nid21 = dot_id_to_new_id[d21]
                nid22 = dot_id_to_new_id[d22]

                # 注意：n-1 在 0 的前面
                if check_after(nid11, nid12, block_list): # 调整顺序，使得顺序服从原始顺序
                    d11, d12 = d12, d11
                    p11,   p12   =   p12,   p11
                    nid11, nid12 = nid12, nid11

                if check_after(nid21, nid22, block_list): # 调整顺序，使得顺序服从原始顺序
                    d21, d22 = d22, d21
                    p21,   p22   =   p22,   p21
                    nid21, nid22 = nid22, nid21

                # 保证 nid11 在 nid12 前面， 保证 nid21 在 nid22 前面
                assert check_after(nid12, nid11, block_list)
                assert check_after(nid22, nid21, block_list)

                # t1 是线段在 p11, p12 上的参数 
                # t2 是线段在 p21, p22 上的参数
                pos, t1, t2 = math_utils.segments_intersect((p11, p12), (p21, p22))
                if pos is None: # 没有找到交叉点，则返回
                    continue

                assert isinstance(t1, float) and isinstance(t2, float)
                assert 0 < float(t1) < 1
                assert 0 < float(t2) < 1 # 这说明有结点位于其他结点上面，可能会导致错误

                crossing_list.append((pos, nid11, t1, nid21, t2, line_id_1, line_id_2)) # 使用七元组描述所有找到的交叉点

        leave_msg(_("总计找到了 %d 个交叉点") % len(crossing_list))

        # 考虑交叉点所在的弧线段，并给所有弧线段进行编号
        parts = [[] for ignored in range(len(block_list))] # 为每一个连通分支，记录它上面有哪些交点
        for crossing_index, crossing in enumerate(crossing_list):
            pos, nid11, t1, nid21, t2, line_id_1, line_id_2 = crossing  # 拿出一个交叉点来

            line_1_under_line_2 = self.memory_object.check_line_under(line_id_1, line_id_2)
            if line_1_under_line_2: # 记录当前交叉点是在上半部分还是在下半部分
                tag_1 = "below"
                tag_2 = "above"
            else:
                tag_1 = "above"
                tag_2 = "below"

            parts[nid11[0]].append((nid11[1], t1, crossing_index, 0, tag_1)) # 这样可以确定出两个半交点
            parts[nid21[0]].append((nid21[1], t2, crossing_index, 1, tag_2)) # 我们可以为每个半交点计算出，它所在的连通分支以及它是第几个

        cid_half_id_to_bid_arc_id = {}
        for bid in range(len(block_list)): # 对所有分界点进行排序
            parts[bid] = sorted(parts[bid])
            leave_msg(_("连通分支 {bid} 被分割成了 {pts} 段").format(bid=bid, pts=len(parts[bid])))

            for arc_id, half_crossing in enumerate(parts[bid]):
                ignored, ignored, cid, half_id, ignored = half_crossing
                cid_half_id_to_bid_arc_id[(cid, half_id)] = (bid, arc_id)

        def check_left_turn(vec1, vec2): # 检查 vec1 到 vec2 是否是左转
            x1, y1 = vec1
            x2, y2 = vec2
            return x1 * y2 - x2 * y1 > 0

        def np_point_to_tuple(np_point:np.ndarray):
            assert np_point.shape == (2, )
            return (float(np_point[0]), float(np_point[1]))

        # 为每一个交叉点生成字符串形式的 pd_code_raw
        pd_code_raw = []
        for cid in range(len(crossing_list)):
            pos, nid11, t1, nid21, t2, line_id_1, line_id_2  = crossing_list[cid]

            bid1, aid1 = cid_half_id_to_bid_arc_id[(cid, 0)]
            bid2, aid2 = cid_half_id_to_bid_arc_id[(cid, 1)]

            line_1_under_line_2 = self.memory_object.check_line_under(line_id_1, line_id_2)

            if not line_1_under_line_2: # 交换，使得 line_1 总是在 line_2 下面
                nid11, nid21 = nid21, nid11
                t1, t2 = t2, t1
                line_id_1, line_id_2 = line_id_2, line_id_1
                bid1, bid2 = bid2, bid1
                aid1, aid2 = aid2, aid1
                line_1_under_line_2 = True

            # 于是我们知道 line_1 总是在 line_2 下面
            dot_id_11 = new_id_to_dot_id[nid11]
            dot_id_21 = new_id_to_dot_id[nid21]

            # 获得原始位置向量
            pos11 = self.memory_object.get_dot_dict()[dot_id_11]
            pos21 = self.memory_object.get_dot_dict()[dot_id_21]

            # 条件成立，说明 pos21 在 pos11 的左侧
            if check_left_turn(np.array(pos11) - np.array(pos), np.array(pos21) - np.array(pos)):
                pd_code_raw.append({"X":[
                    (bid1, aid1),
                    (bid2, aid2),
                    (bid1, (aid1 + 1) % len(parts[bid1])),
                    (bid2, (aid2 + 1) % len(parts[bid2])), # 需要考虑最后一条 arc
                ], "dir":[
                    np_point_to_tuple(np.array(pos11) - np.array(pos)), # 记录第一个 index 对应的方向和第二个 index 对应的方向，用于未来显示
                    np_point_to_tuple(np.array(pos21) - np.array(pos))
                ], "pos": pos})
            else:
                pd_code_raw.append({"X":[
                    (bid1, aid1),
                    (bid2, (aid2 + 1) % len(parts[bid2])),
                    (bid1, (aid1 + 1) % len(parts[bid1])), # 需要考虑最后一条 arc
                    (bid2, aid2),
                ], "dir":[
                    np_point_to_tuple(np.array(pos11) - np.array(pos)), # 记录第一个 index 对应的方向和第二个 index 对应的方向，用于未来显示
                    np_point_to_tuple(-(np.array(pos21) - np.array(pos)))
                ], "pos": pos})
        
        # 程序运行到这里已经获得了可用的 pd_code_raw 了
        # 我们需要借助排序进一步计算得到具有统一编号的 pd_code
        item_list = []
        for crossing in pd_code_raw: # 拿出所有编号来
            for term in crossing["X"]:
                if term not in item_list:
                    item_list.append(term)

        item_list = sorted(item_list)
        tup_to_real_id = {}
        for idx, val in enumerate(item_list): # 为每一个弧线段赋予一个最终的有效整数 id
            tup_to_real_id[val] = idx + 1

        # 经过这一次处理后得到的 pd_code 将是最终的 pd_code
        # 我们首先对 pd_code_raw 进行一次深拷贝
        pd_code_final = eval(repr(pd_code_raw))
        pd_code_to_show = []
        for pd_code_term in pd_code_final:
            for i in range(4):
                pd_code_term["X"][i] = tup_to_real_id[pd_code_term["X"][i]]

            clock_wise = pd_code_term["X"]
            anti_clock_wise = [clock_wise[0]] + clock_wise[1:][::-1]
            pd_code_to_show.append(anti_clock_wise)
        
        # 返回最终 pd_code
        return sorted(pd_code_to_show), pd_code_final, parts
    
    # block_list 记录了每个连通分支的控制点
    # parts 记录了每个连通分支的交叉点的位置
    # need_number 指出了是否需要在生成的 svg 图片中引入弧线的数字编号
    def calculate_svg(self, block_list, parts, need_number, need_arrow):
        # 根据 block_list 计算节点的前驱后继关系
        # 这里的节点以 dot_id 的形式记录（即节点的默认编号）
        get_next_dot = {}
        get_last_dot = {}
        for i in range(len(block_list)):
            for j in range(len(block_list[i])):
                item_now = block_list[i][j]
                item_last = block_list[i][j-1] # 这样的话，当 j = 0 时，恰好是正确的

                get_next_dot[item_last] = item_now
                get_last_dot[item_now] = item_last
        
        # 为某个指定的连通分支计算其 arc_list
        def get_arc_list_for_zero_crossing_connected_component(bid: int):
            arc_list = []
            for item in block_list[bid]:
                arc_list.append((
                    (get_last_dot[item], item, 0.5), # 为所有节点输出一个四元组
                    (item, get_next_dot[item], 0.0),
                    (item, get_next_dot[item], 0.5),
                    "LR", ## LR, 表示两端都不需要缩短
                ))
            return arc_list

        def get_new_tag(base:str, old_tag:str) -> str:
            assert old_tag in ["below", "above"]
            assert base in ["l", "r", "L", "R"]
            base = base.upper()
            if old_tag == "below": # 小写字母表示需要缩短，大写字母表示不需要缩短
                return base.lower()
            else:
                return base

        def get_arc_list_between_two_crossing(bid:int, begin_arc, end_arc): # 绘制两个交叉点之间的所有弧线段
            nid1, t1, ignored, ignored, tag1 = begin_arc
            nid2, t2, ignored, ignored, tag2 = end_arc

            if nid1 == nid2: # 位于同一个线段的两个交叉点，不需要计算中间节点
                return [
                    (
                        (block_list[bid][nid1], get_next_dot[block_list[bid][nid1]], t1),
                        (block_list[bid][nid1], get_next_dot[block_list[bid][nid1]], (t1 + t2) / 2),
                        (block_list[bid][nid2], get_next_dot[block_list[bid][nid2]], t2),
                        get_new_tag("l", tag1) + get_new_tag("r", tag2)
                    )
                ]

            all_interger_index = [] # 获取两个交叉点之间的所有整数编号
            index_now = nid1
            while True:
                index_now = (index_now + 1) % len(block_list[bid]) # 编号循环
                all_interger_index.append(index_now)
                if index_now == nid2:
                    break
            
            arc_list = []
            if len(all_interger_index) == 1: # 只有一个节点位于两者之间的情况
                new_tag_1 = get_new_tag("L", tag1)
                new_tag_2 = get_new_tag("R", tag2)
                arc_list.append((
                    (block_list[bid][nid1], block_list[bid][all_interger_index[0]],  t1),
                    (block_list[bid][nid1], block_list[bid][all_interger_index[0]], 1.0),
                    (block_list[bid][nid2], get_next_dot[block_list[bid][nid2]],  t2),
                    new_tag_1 + new_tag_2
                ))
            else: # 说明不只有一个节点位于两者之间，因此需要单独考虑最前端和最后段
                new_tag_1 = get_new_tag("L", tag1)
                new_tag_2 = get_new_tag("R", tag2)
                arc_list.append((
                    (block_list[bid][nid1], block_list[bid][all_interger_index[0]],  t1),
                    (block_list[bid][nid1], block_list[bid][all_interger_index[0]], 1.0),
                    (block_list[bid][all_interger_index[0]], get_next_dot[block_list[bid][all_interger_index[0]]],  0.5),
                    new_tag_1 + "R"
                ))

                for idx, item in enumerate(all_interger_index):
                    if idx == 0: # 跳过第一个元素
                        continue
                    if idx == len(all_interger_index) - 1: # 跳过最后一个元素
                        continue
                    item_last = all_interger_index[idx - 1]
                    item_now  = item
                    item_next = all_interger_index[idx + 1] # 下一个元素
                    arc_list.append((
                        (block_list[bid][item_last], block_list[bid][item_now], 0.5),
                        (block_list[bid][item_now], block_list[bid][item_next], 0.0),
                        (block_list[bid][item_now], block_list[bid][item_next], 0.5),
                        "LR"
                    ))

                arc_list.append((
                    (get_last_dot[block_list[bid][all_interger_index[-1]]], block_list[bid][all_interger_index[-1]], 0.5),
                    (block_list[bid][all_interger_index[-1]], block_list[bid][nid2], 0.0), # 中间的点是一个整数位置点
                    (block_list[bid][nid2], get_next_dot[block_list[bid][nid2]],  t2),
                    "L" + new_tag_2,
                ))

            return arc_list

        # 绘制 svg 图像, 特殊处理没有交叉点的连通分支
        arc_list = []
        for i in range(len(parts)):
            if len(parts[i]) == 0: # 这说明这个连通分支没有任何交点
                arc_list += get_arc_list_for_zero_crossing_connected_component(i)
            else:
                # 执行到这个分支说明当前 parts[i] 中至少有一个交点
                for j in range(len(parts[i])):
                    begin_arc = parts[i][j-1] # 需要注意的是，当 j = 0 时，这里 j - 1 等于 -1
                    end_arc = parts[i][j]
                    arc_list += get_arc_list_between_two_crossing(i, begin_arc, end_arc)

        # 生成一个 SVG 二次曲线
        def create_svg_path(pos_from, pos_mid, pos_to, status, need_arrow) -> str:
            shrink_1 = status[0]
            shrink_2 = status[1]
            xfrom, yftom = self.memory_object.get_interpos(pos_from[0], pos_from[1], pos_from[2], shrink_1)
            xmid,  ymid  = self.memory_object.get_interpos(pos_mid [0], pos_mid [1], pos_mid [2])
            xto,   yto   = self.memory_object.get_interpos(pos_to  [0], pos_to  [1], pos_to  [2], shrink_2)
            arc_text = "    " + '<path d="M %f %f Q %f %f, %f %f" fill="none" stroke="%s" stroke-width="%d" />' % (
                xfrom, yftom,
                xmid, ymid,
                xto, yto,
                constant_config.SVG_STROKE_COLOR,
                constant_config.SVG_STROKE_WIDTH,
            )
            if need_arrow: # 在中点附近加小箭头
                midpoint, tangent = math_utils.bezier_midpoint_and_tangent((xfrom, yftom), (xmid, ymid), (xto, yto))
                xm, ym = midpoint
                xt, yt = tangent
                xn, yn = -yt, xt # 法线方向是切线方向的垂直方向
                arrow_text1 = '<line x1="%f" y1="%f" x2="%f" y2="%f" stroke="black" stroke-width="1" />' % (
                    xm, ym, xm + (xn - xt) * constant_config.ARROW_SIZE, ym + (yn - yt) * constant_config.ARROW_SIZE
                )
                arrow_text2 = '<line x1="%f" y1="%f" x2="%f" y2="%f" stroke="black" stroke-width="1" />' % (
                    xm, ym, xm + (-xn - xt) * constant_config.ARROW_SIZE, ym + (-yn - yt) * constant_config.ARROW_SIZE
                )
                arc_text += "\n    " + arrow_text1 + "\n    " + arrow_text2
            return arc_text

        # 基于 arc_list 生成 svg 图像文本格式
        def generate_svg_text_based_on_arc_list(arc_list) -> list:
            xmin, ymin, xmax, ymax = self.memory_object.get_view_box()
            xmin -= constant_config.CIRCLE_RADIUS
            ymin -= constant_config.CIRCLE_RADIUS
            xmax += constant_config.CIRCLE_RADIUS
            ymax += constant_config.CIRCLE_RADIUS
            svg_path_list = []
            for term in arc_list:
                pos_from, pos_mid, pos_to, status = term
                svg_path_list.append(create_svg_path(pos_from, pos_mid, pos_to, status, need_arrow)) # need_arrow 在最外层引入
            return svg_path_list
        
        # 不负责存储，仅仅负责计算
        xmin, ymin, xmax, ymax = self.memory_object.get_view_box()
        header  = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
        header += '<svg xmlns="http://www.w3.org/2000/svg" viewBox="%g %g %g %g" width="%d" height="%d">' % (
            xmin, ymin, xmax-xmin, ymax-ymin, 
            round((xmax-xmin) * constant_config.SVG_EXPAND_RATIO), 
            round((ymax-ymin) * constant_config.SVG_EXPAND_RATIO))
        footer  = '</svg>'
        svg_text_list = [header] + generate_svg_text_based_on_arc_list(arc_list)

        if need_number: # 添加数字
            for txt, pos in self.memory_object.get_number_position_pairs():
                svg_text_list.append(f'    <text x="{pos[0]}" y="{pos[1] + constant_config.SVG_TEXT_DELTA_Y}" font-size="{constant_config.SVG_FONT_SIZE}" fill="red">{txt}</text>\n')

        svg_text_list.append(footer)
        return "\n".join(svg_text_list)
