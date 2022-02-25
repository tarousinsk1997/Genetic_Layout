import numpy as np
import course, os
from deap import creator, tools, base


from matplotlib import pyplot as plt

CostNew = 11786.9
FixedNew = 270
VarNew = 1.34
CapitalNew = 23625

CostBase = 13681.5
FixedBase = 25
VarBase = 1.61
CapitalBase = 16500
Economy = 2646
Years = 3.7
Critical = 916
Effect = 469

x = [0, 8000]
x1 = [Critical, 8000]
x2 = [3750, 8000]

#График 1

y1 = [FixedBase, FixedBase] # постоянные базовые
y2 = [FixedNew,FixedNew]# постоянные проектные
y3 = [FixedBase, CostBase]# себестоимость базовые
y4=[FixedNew, CostNew]# себестоимость проектные
y5 = [0, Economy] #экономия

y11 = [0, 1600]
x11 = [Critical, Critical]
x22 = [3800, 3800]
y22 = [0, 5650]
#График 1


#ГРАФИК 2
y6 = [0, CostBase] # Технологическая себестоимость по базовому варианту
y7 = [CapitalNew * 0.2, CapitalNew * 0.2] # Кап затраты по новому варанту приведенные
y8 = [CapitalNew * 0.2, CostNew] #Приведенные затраты по новому варианту
y9 = [0, Effect] #Годовой экономический эффект
#ГРАФИК 2

#ГРАФИК 3
y10 = [CapitalNew * 0.2 , CostNew] #Приведенные затраты по новому варианту
y12 = [CapitalBase * 0.2, CapitalBase * 0.2]
y13 = [CapitalNew * 0.2, CapitalNew * 0.2]
y14 = [CapitalBase * 0.2, CostBase]

#ГРАФИК 3


def graph1():
    fig, ax = plt.subplots()
    ax.grid()
    ax.set_xlabel('Nгод, шт.')
    ax.set_ylabel('тыс. руб.')
    ax.plot(x, y1,color='#00b500', label='Постоянные затраты по базовому варианту', ls='--')
    ax.plot(x,y3,c='#426ca6', label='Технологическая себестоимость по базовому варианту', ls='--')
    ax.plot(x,y2,c='#000000', label='Постоянные затраты по проектному варианту')
    ax.plot(x,y4,c='#8d64a7', label='Технологическая себестоимость по проектному варианту')
    ax.plot(x1,y5,c='#ff0000', label='Годовая экономия')
    ax.plot(x11, y11, ls='--' )
    plt.legend(loc='upper left',borderaxespad=0.)
    plt.show()

def graph2():
    fig, ax = plt.subplots()
    ax.grid()
    ax.set_xlabel('Nгод, шт.')
    ax.set_ylabel('тыс. руб.')
    ax.plot(x,y6, c='#ff0000', label='Технологическая себестоимость по базовому варианту')
    ax.plot(x,y7,color='#00b500', label='Капитальные затраты приведенные по новому варианту')
    ax.plot(x,y8,c='#000000', label='Приведенные затраты по новому варианту')
    ax.plot(x2,y9,c='#426ca6', label='Годовой экономический эффект')
    ax.plot(x22, y22, ls='--' )
    plt.legend(loc='upper left',borderaxespad=0.)
    plt.show()

def graph3():
    fig, ax = plt.subplots()
    ax.grid()
    ax.set_xlabel('Nгод, шт.')
    ax.set_ylabel('тыс. руб.')
    ax.plot(x,y10, c='#ff0000', label='Приведенные затраты по новому варианту')
    ax.plot(x,y13,color='#00b500', label='Капитальные затраты приведенные по новому варианту')
    ax.plot(x,y12,c='#000000', label='Приведенные затраты по базовому варианту', ls='--')
    ax.plot(x,y14,c='#426ca6', label='Капитальные затраты по старому варианту', ls='--')
    #ax.plot(x11, y11, ls='--' )
    plt.legend(loc='upper left',borderaxespad=0.)
    plt.show()

graph1()
