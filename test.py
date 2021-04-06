import numpy as np
import course, os
from deap import creator, tools, base

creator.create("FitnessMax", base.Fitness, weights=(1.0, 1.0))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
list1 = [1,2,3,4]
def initIndividual(icls):
    list1 = [1,2,3,4]
    return list1

toolbox.register("individual_guess", initIndividual, creator.Individual)



individual = toolbox.individual_guess()
print(individual)