import xlrd
import copy
import random


def Value(x, V, m):
    V_x = V
    for i in x:
        if m[i][0] > 0:
            V_x = V_x + m[i][1]

    return V_x


def get_max(N, x, b, V, m):
    max_marginal_value_density = (Value(x[N[0]], V, m) - V) / b[N[0]]
    index = N[0]
    for i in N:
        if (Value(x[i], V, m) - V) / b[i] > max_marginal_value_density:
            index = i

    return index


def O_PSM(M, N, B, b, x):

    A = []
    m = copy.deepcopy(M)
    n = copy.deepcopy(N)
    V = 0
    i = get_max(n, x, b, V, m)
    V_i = Value(x[i], V, m)
    while b[i] <= B / 2 * (V_i - V) / V_i and len(n) > 0:
        A.append(i)
        for j in x[i]:
            m[j][0] -= 1
        V = V_i
        n.remove(i)
        if len(n) > 0:
            i = get_max(n, x, b, V, m)
            V_i = Value(x[i], V, m)


    p = []
    for i in range(0, len(N)):
        p.append(0)


    for i in A:
        if i == A[-1]:
            p[i] = b[i]
            break
        m = copy.deepcopy(M)
        n = copy.deepcopy(N)
        n.remove(i)  # N\{i}
        A_i = []
        V = 0
        V_pre = V
        j = get_max(n, x, b, V_pre, m)
        V_i = Value(x[i], V_pre, m) - V_pre
        V_j = Value(x[j], V_pre, m) - V_pre
        b_ij = V_i * b[j] / V_j
        rou_ij = V_i / Value(x[i], V, m) * B / 2
        p[i] = max(p[i], min(b_ij, rou_ij))
        A_i.append(j)
        V = Value(x[j], V_pre, m)
        while b[j] <= B / 2 * (V - V_pre) / V and len(n) > 0:

            V_pre = V
            for k in x[j]:
                m[k][0] -= 1
            n.remove(j)
            if len(n) > 0:
                j = get_max(n, x, b, V_pre, m)
                V_i = Value(x[i], V_pre, m) - V_pre
                V_j = Value(x[j], V_pre, m) - V_pre
                if V_j == 0:
                    break
                b_ij = V_i * b[j] / V_j
                rou_ij = V_i / Value(x[i], V_pre, m) * B / 2
                p[i] = max(p[i], min(b_ij, rou_ij))
                A_i.append(j)
                V = Value(x[j], V_pre, m)


    V = 0
    m = copy.deepcopy(M)
    for i in A:
        for j in x[i]:
            V += m[j][1]
            m[j][0] -= 1


    return V,p,A


M = []
user_num = 10
N = []
x = []
b = []
B = 1200

V,P,Winners = O_PSM(M, N, B, b, x)