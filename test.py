import numpy as np
import course, os
from deap import creator, tools, base


list1 = [1,2,3,4,5,6,7,8,9]

str1 = 'corrected'

list1[:int(len(list1) / 2 - 1)] = [str1 for elem in list1[:int(len(list1) / 2 - 1)]]
print(list1)