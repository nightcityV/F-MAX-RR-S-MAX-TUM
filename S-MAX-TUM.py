import xlrd
import copy
import random


def Value(x, V, m):  # 计算加入一个用户的兴趣点后的总价值。x:某个用户采集的兴趣点集合，V：产生的总价值，m：poi的覆盖信息（大小为2*poi数量，每行为（还允许覆盖的次数，对服务提供商的价值））
    V_x = V
    for i in x:
        if m[i][0] > 0:
            V_x = V_x + m[i][1]

    return V_x


def get_max(N, x, b, V, m):  # 选出边际价值密度最大者， N：用户编号集合，x：所有用户的兴趣点集合的列表，b:每个用户的竞价，V：产生的总价值，m：兴趣点覆盖信息
    max_marginal_value_density = (Value(x[N[0]], V, m) - V) / b[N[0]]
    index = N[0]
    for i in N:
        if (Value(x[i], V, m) - V) / b[i] > max_marginal_value_density:
            index = i

    return index


def O_PSM(M, N, B, b, x):
    # 分配阶段
    A = []  # 胜者集合
    m = copy.deepcopy(M)
    n = copy.deepcopy(N)
    V = 0  # 实际总价值
    i = get_max(n, x, b, V, m)
    V_i = Value(x[i], V, m)  # 加入用户i后的总价值
    while b[i] <= B / 2 * (V_i - V) / V_i and len(n) > 0:
        A.append(i)
        for j in x[i]:  # 更新poi覆盖信息
            m[j][0] -= 1
        V = V_i  # 更新总价值
        n.remove(i)
        if len(n) > 0:
            i = get_max(n, x, b, V, m)
            V_i = Value(x[i], V, m)

    # 初始化所有用户的报酬
    p = []
    for i in range(0, len(N)):
        p.append(0)

    # 支付阶段
    for i in A:
        if i == A[-1]:
            p[i] = b[i]
            break
        m = copy.deepcopy(M)
        n = copy.deepcopy(N)
        n.remove(i)  # N\{i}
        A_i = []  # A'
        V = 0  # 实际总价值
        V_pre = V
        j = get_max(n, x, b, V_pre, m)  # 获得边际价值密度最大的用户
        V_i = Value(x[i], V_pre, m) - V_pre  # 计算用户i的支付阶段，用户i取代用户j时的边际价值
        V_j = Value(x[j], V_pre, m) - V_pre  # 计算用户i的支付阶段，用户j的边际价值
        b_ij = V_i * b[j] / V_j
        rou_ij = V_i / Value(x[i], V, m) * B / 2
        p[i] = max(p[i], min(b_ij, rou_ij))
        A_i.append(j)
        V = Value(x[j], V_pre, m)
        while b[j] <= B / 2 * (V - V_pre) / V and len(n) > 0:

            V_pre = V
            for k in x[j]:  # 更新poi覆盖次数
                m[k][0] -= 1
            n.remove(j)
            if len(n) > 0:
                j = get_max(n, x, b, V_pre, m)
                V_i = Value(x[i], V_pre, m) - V_pre  # 计算用户i的支付阶段，用户i取代用户j时的边际价值
                V_j = Value(x[j], V_pre, m) - V_pre  # 计算用户i的支付阶段，用户j的边际价值
                if V_j == 0:
                    break
                b_ij = V_i * b[j] / V_j
                rou_ij = V_i / Value(x[i], V_pre, m) * B / 2
                p[i] = max(p[i], min(b_ij, rou_ij))
                A_i.append(j)
                V = Value(x[j], V_pre, m)

    # 计算这些用户带来的总价值
    V = 0
    m = copy.deepcopy(M)
    for i in A:
        for j in x[i]:
            V += m[j][1]
            m[j][0] -= 1


    return V,p,A


M = []  # 兴趣点的实时信息（大小为2*poi数量，每行为（还可以覆盖的次数，对服务提供商的价值））
data = xlrd.open_workbook("data.xlsx")  # 读取文件
table = data.sheet_by_index(1)  # 按索引获取工作表，0就是工作表1(sheet1)
for i in range(table.nrows):  # table.nrows表示总行数
    line = table.row_values(i)  # 读取每行数据，保存在line里面，line是list
    M.append(line)  # 将line加入到resArray中，resArray是二维list

user_num = 20  # 用户数量
N = []
for i in range(0, user_num):
    N.append(i)

x = []
data = xlrd.open_workbook("route.xlsx")
table = data.sheet_by_index(0)
for i in range(0,user_num):
    line = table.row_values(random.randint(0,49))
    new_line = []
    for j in line:
        if j:
            j = int(j)
            new_line.append(j)
    print(new_line)
    x.append(new_line)


b = [32, 22, 28, 30, 30, 29, 30, 26, 20, 31, 28, 19, 34, 27, 31, 32, 22, 33, 25, 28]  # 每个用户的竞价


B = 1000  # 服务提供商总预算

V,P,Winners = O_PSM(M, N, B, b, x)



