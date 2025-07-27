# Knotpen2 存储结构

- 注意：存储结构可能在未来发生改变，目前的实现有比较重大的安全隐患。

本文可以被理解为一个协议，描述与 knotpen2 交互的程序如何修改 knotpen2 的存档文件。

## 1. 基本结构

knotpen2 的存档采用类似 json 的格式，文件拓展名为**小写**的 `json`。我们要求作为 knotpen2 存档可以使用 python 的 eval 函数加载，并且使用 utf-8 字符集编码。我们对 json 文件内部的字符串缩进不做任何要求。我们要求该文件中的整体是一个，使用 python 加载后会得到一个 dict 对象。

- 关于 python dict 的概念可以参考：https://docs.python.org/3/library/stdtypes.html#mapping-types-dict
- 关于 python eval 的介绍可以参考：https://docs.python.org/3/library/functions.html#eval

如果我们将 python dict 理解为有限元素的 “键值对（Key-Value Pairs）” 集合，那么我们要求 knotpen2 存档的所有 “键” 都必须是字符串类型（python 的 str 类型）。需要注意的是，**我们的数据类型目前并不是真正的 json 文件**。

## 2. 必要结构

假设 KP2A 是一个 knotpen2 的存档加载到 python 后得到的 dict 类型对象。则 KP2A 中必须有如下结构：

- `KP2A["dot_id_max"]` 必须是一个非负整数：表示链环投影图中的节点个数；
- `KP2A["line_id_max"]` 必须是一个非负整数：表示链环投影图中的边的个数；
- `KP2A["dot_dict"]` 的类型是 dict：描述每个节点在二维空间的位置，将节点编号映射到整数二元组；
- `KP2A["line_dict"]` 的类型是 dict：描述每一条边连接了哪两个节点，将边编号映射到节点编号二元组，同一条边连接的两个节点不能相同；
- `KP2A["inverse_pairs"]` 的类型是一个 dic：用于描述边之间的遮挡关系，键值对的 “值” 必须是 True 或者 None：
  - 如果边 A 与边 B 不作为 “键” 出现在这个 dict 中，则按照编号大小关系，编号大的位于编号小的上方；
  - 如果边 A 与边 B 作为 “键” 出现在这个 dict 中，则编号小的出现在编号大的上方；
  - 具体的代码逻辑可以参考 `MemoryObject.py` 中的函数 `MemoryObject.check_line_under`；
- `KP2A["degree"]` 的类型是 dict：用于描述每个节点的 “度”（即与节点相连的边数）；
- `KP2A["base_dot"]` 的类型是 list：记录哪些节点是 “基节点” （即连通分支定向起点）；
- `KP2A["dir_dot"]` 的类型是 list：记录哪些节点是 “方向节点” （与起点相邻，用于描述前进方向）；

## 3. 可选结构

假设 KP2A 是一个 knotpen2 的存档加载到 python 后得到的 dict 类型对象。则 KP2A 中可以有如下结构：

- `KP2A["pd_code_final"]` 用于显示 pd_code 

