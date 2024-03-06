import copy
import random
import numpy as np
import xlrd
import time
from poi_map import G


def initializtion(s, e, G, l):
    x = []
    k = 0
    while k < l/2:
        t = [s]
        while t[-1] != e:
            neighbors = []
            for i in G[t[-1]]:
                if i not in t:
                    neighbors.append(i)
            if len(neighbors) == 0:
                break
            r = random.randint(0, len(neighbors) - 1)
            t.append(neighbors[r])
        if t[-1] != e:
            continue
        x.append(t)
        k += 1
    delete_index = []
    for i in range(0, len(x)):
        if len(x[i]) >= 2 * l:
            delete_index.append(i)
    x = [n for i, n in enumerate(x) if i not in delete_index]

    return x


def insertion(x, p_num, max_len):
    if len(x) <= max_len:
        k = 0
        while k == 0:
            p = random.randint(0, p_num - 1)
            if p in x:
                continue
            else:
                index = random.randint(1, len(x) - 1)
                x.insert(index, p)
                k = 1


def deletion(x):
    if len(x) > 3:
        index = random.randint(1, len(x) - 2)
        x.remove(x[index])


def fitness(x, P, G, speed, oil_price, st):
    gain = 0
    time = st
    if P[x[0]][1] <= st <= P[x[0]][2]:
        gain = gain + P[x[0]][0]
    for i in range(1, len(x)):
        if x[i] not in G[x[i - 1]]:
            gain = -100
            break
        else:
            gain = gain - G[x[i - 1]][x[i]] * oil_price
            time = time + G[x[i - 1]][x[i]] / speed

            if P[x[i]][1] <= time <= P[x[i]][2]:
                gain = gain + P[x[i]][0]

    return gain


def DEOMPR(satrt_p, end_p, G, P, L, ST):
    P = P
    G = G
    p_num = 59
    s = satrt_p
    e = end_p
    st = ST
    l_max = L
    k = 0
    speed = 0.5
    oil_price = 0.6

    x = initializtion(s, e, G, l_max)  # 得到一些可行路径
    gain = []

    # 获取这些路径的收益
    for i in range(0, len(x)):
        gain.append(fitness(x[i], P, G, speed, oil_price, st))

    while k < 100:
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
                delete_index = []
                for i in range(0, len(x)):
                    if f >= gain[i] and l == len(x[i]):
                        delete_index.append(i)
                x = [n for i, n in enumerate(x) if i not in delete_index]  # 一次性删除被选中的个体
                gain = [n for i, n in enumerate(gain) if i not in delete_index]
                x.append(xr)
                gain.append(f)

        k = k + 1

    fit = 0
    index = 0
    for j in range(0, len(x)):
        if len(x[j]) <= l_max and gain[j] > fit:
            index = j
            fit = gain[j]


    time = st
    for j in range(1, len(x[index])):
        time = time + G[x[index][j - 1]][x[index][j]] / speed


    return x[index], fit


P = []
G=[]
L = 10
satrt_p = 0
end_p = 10
ST = 0

DEOMPR(satrt_p, end_p, G, P, L, ST)