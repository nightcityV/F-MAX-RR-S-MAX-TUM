import copy
import random
import numpy as np
import xlrd
import time
from poi_map import G


def initializtion(s, e, G, l):  # 初始化，生成一些可行路径
    x = []
    k = 0
    while k < l/2:
        t = [s]
        while t[-1] != e:
            neighbors = []
            for i in G[t[-1]]:
                if i not in t:  # 是否存在邻接点并且该点不在序列中
                    neighbors.append(i)
            if len(neighbors) == 0:  # 路径无法继续生成，则重新从起点开始生成
                break
            r = random.randint(0, len(neighbors) - 1)
            t.append(neighbors[r])
        if t[-1] != e:
            continue
        x.append(t)
        k += 1
    # 删除长度大于2*l的路径（认为这些路径不可行）
    delete_index = []
    for i in range(0, len(x)):
        if len(x[i]) >= 2 * l:
            delete_index.append(i)
    x = [n for i, n in enumerate(x) if i not in delete_index]

    return x


def insertion(x, p_num, max_len):  # 插入操作
    if len(x) <= max_len:  # 保证经过的结点数量不超过允许值
        k = 0  # 记录是否已经插入节点
        while k == 0:
            p = random.randint(0, p_num - 1)
            if p in x:
                continue
            else:
                index = random.randint(1, len(x) - 1)
                x.insert(index, p)
                k = 1


def deletion(x):  # 删除操作
    if len(x) > 3:  # 保证至少经过一个结点（除起点和终点外）
        index = random.randint(1, len(x) - 2)
        x.remove(x[index])


def fitness(x, P, G, speed, oil_price, st):  # P；POI矩阵 G：兴趣点之间的距离矩阵 speed：车速 oil_price：每公里油费 st：从起点出发的时间
    gain = 0
    time = st
    if P[x[0]][1] <= st <= P[x[0]][2]:
        gain = gain + P[x[0]][0]
    for i in range(1, len(x)):
        if x[i] not in G[x[i - 1]]:  # 路径不通，则此路径不可行
            gain = -100
            break
        else:
            gain = gain - G[x[i - 1]][x[i]] * oil_price
            time = time + G[x[i - 1]][x[i]] / speed

            if P[x[i]][1] <= time <= P[x[i]][2]:  # 判断经过兴趣点时是否在时间窗内
                gain = gain + P[x[i]][0]

    return gain


def DEOMPR(satrt_p, end_p, G, P, L, ST):
    P = P
    G = G  # 记录任意两点间的距离。列表里嵌套字典，例如G = [{1: 2, 3: 3, 6: 9}, {2: 3, 5: 6}]，0号点到3号点距离为3；1号点到5号点距离为6
    p_num = 59  # POI数量
    s = satrt_p  # 起点
    e = end_p  # 终点
    st = ST  # 到达起点的时间
    l_max = L  # 每个用户最多经过l个点
    k = 0  # 记录迭代次数
    speed = 0.5  # 行驶速度,km/min
    oil_price = 0.6  # 每公里油费

    x = initializtion(s, e, G, l_max)  # 得到一些可行路径
    gain = []

    # 获取这些路径的收益
    for i in range(0, len(x)):
        gain.append(fitness(x[i], P, G, speed, oil_price, st))

    while k < 500:
        i = random.randint(0, len(x) - 1)  # 种群中随机选一个个体
        r = np.random.poisson(lam=1)  # 产生泊松随机数，
        xr = copy.deepcopy(x[i])
        for j in range(0, r):
            ran = random.random()
            if ran < 0.5:
                insertion(xr, p_num, 2 * l_max)
            else:
                deletion(xr)
        f = fitness(xr, P, G, speed, oil_price, st)
        l = len(xr)

        # xr与种群中的个体一一比较，先判断weakly dominates（弱支配），再判断是不是dominate（支配）。若种群中不存在支配xr的个体，
        # 则删除被xr弱支配的个体，并将xr加入种群

        exist = 0
        """""
        for i in range(0, len(x)):
            if gain[i] >= f and len(x[i]) <= l:
                if gain[i] > f or len(x[i]) < l:
                    exist = 1
                    break
"""""
        if exist == 1:
            k += 1
            continue
        else:
            if f > 0:
                delete_index = []  # 记录要删除的个体的索引,只需要删除与xr长度相等的个体
                for i in range(0, len(x)):
                    if f >= gain[i] and l == len(x[i]):
                        delete_index.append(i)
                x = [n for i, n in enumerate(x) if i not in delete_index]  # 一次性删除被选中的个体
                gain = [n for i, n in enumerate(gain) if i not in delete_index]
                x.append(xr)
                gain.append(f)

        k = k + 1

    # 获得迭代结束后的最优解
    fit = 0
    index = 0
    for j in range(0, len(x)):
        if len(x[j]) <= l_max and gain[j] > fit:
            index = j
            fit = gain[j]

    # 计算执行时间
    time = st
    for j in range(1, len(x[index])):
        time = time + G[x[index][j - 1]][x[index][j]] / speed

    print('收益为：')
    print(fit)
    print('路径为：')
    print(x[index])
    print('执行时间为：')
    print(time)

    return x[index], fit

start = time.perf_counter()
P = []  # 记录POI信息，矩阵大小为p_num*3，每行为（收益，开始时间，截止时间）
data = xlrd.open_workbook("data.xlsx")  # 读取文件
table = data.sheet_by_index(0)  # 按索引获取工作表，0就是工作表1(sheet1)
for i in range(table.nrows):  # table.nrows表示总行数
    line = table.row_values(i)  # 读取每行数据，保存在line里面，line是list
    P.append(line)  # 将line加入到resArray中，resArray是二维list
L = 10
satrt_p = 38
end_p = 49
ST = 0

DEOMPR(satrt_p, end_p, G, P, L, ST)

