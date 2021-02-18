from deap import base
from deap import creator
from deap import tools
from deap import algorithms
from matplotlib import pyplot as plt
import random as rnd
import numpy as np
import random
from PyQt5.QtCore import QCoreApplication


import math


class Genetic_implement:
    def __init__(self, fclIndividual):
    # гиперпараметры алгоритма
        self.P_MUTATION = 0.45  # вероятность мутации
        self.MAX_GENERATIONS = 1500  # число поколоений
        self.P_CROSSOVER = 0.9  # вероятность скрещивания
        self.HOF_K = 0.4
        self.POPULATION_SIZE = 50 # размер популяции
        self.HALL_OF_FAME_SIZE =int(self.POPULATION_SIZE * self.HOF_K)  # число хранимых лучших особей
        self.CROWDING_FACTOR = 15  # коэффициент скученности
        self.TOURNSIZE = 3  # турнирный отбор
        self.kmin = 0.7
        self.kmax = 1.3
        self.Rect_ind = fclIndividual # ИЗВНЕ ПЕРЕДАЕМ любой ОБЪЕКТ Цеха c ВЫПОЛНЕННЫМИ МЕТОДАМИ в MAIN!!!
        self.toolbox = base.Toolbox()
        self.low = []
        self.up = []
        self.Stop = False
        self.counter_UI = 0 #счетчик поколений для UI
        for i in range(0, len(self.Rect_ind.Site_list)):
            self.low.extend([self.Rect_ind.fcl.x(), self.Rect_ind.fcl.y(), self.kmin])
            self.up.extend([self.Rect_ind.fcl.x() + self.Rect_ind.fcl.width(), self.Rect_ind.fcl.y() + self.Rect_ind.fcl.height(), self.kmax])
    # гиперпараметры алгоритма

    # дополнительные методы
    def draw(self):
        gen = self.logbook.select("gen")
        fit_mins = self.logbook.select("min")
        size_avgs = self.logbook.select('avg')
        fig, ax1 = plt.subplots()
        line1 = ax1.plot(gen, fit_mins, "b-", label="Minimum Fitness")
        ax1.set_xlabel("Generation")
        ax1.set_ylabel("Fitness", color="b")
        for tl in ax1.get_yticklabels():
            tl.set_color("b")

        ax2 = ax1.twinx()
        line2 = ax2.plot(gen, size_avgs, "r-", label="Average Size")
        ax2.set_ylabel("Size", color="r")
        for tl in ax2.get_yticklabels():
            tl.set_color("r")

        lns = line1 + line2
        labs = [l.get_label() for l in lns]
        ax1.legend(lns, labs, loc="center right")

        plt.show()

    def MinFitness(self, individual): # функция вычисления приспособленности

        x_list = np.array(individual[0::3])
        y_list = np.array(individual[1::3])
        k_list = np.array(individual[2::3])
        cargo = np.array(self.Rect_ind.cargo_matrix).reshape((len(x_list), len(y_list)))
        self.recalculate_WH(k_list)
        fit = (self.Interception_criteria(x_list, y_list), self.bounds_criteria(x_list, y_list), self.compact_criteria(x_list,y_list), self.mincargo_criteria(cargo, x_list, y_list))
        if fit[0] == 0  and fit[1] == 0:
            print(fit)
        return fit

    def mincargo_criteria(self, cargo, x_list, y_list): #здесь определяем мощность грузопотока ВНИМАНИЕ ПРОСЛЕДИТЬ ЧТОБЫ БЫЛО СООТВЕТСТВИЕ
        distance_matrix = np.zeros((len(self.Rect_ind.Site_list),len(self.Rect_ind.Site_list)))
        for i in range(distance_matrix.shape[0]):
            for j in range(distance_matrix.shape[0]):
                if i < j:
                    x1_center = x_list[i] + self.Rect_ind.Site_list[i].width() / 2
                    y1_center = y_list[i] + self.Rect_ind.Site_list[i].height() / 2
                    x2_center = x_list[j] + self.Rect_ind.Site_list[j].width() / 2
                    y2_center = y_list[j] + self.Rect_ind.Site_list[j].height() / 2
                    distance_matrix[i][j] = math.sqrt((x1_center - x2_center) ** 2 + (y1_center - y2_center) ** 2)
                else:
                    distance_matrix[i,j] = 0

        return np.sum(np.multiply(cargo, distance_matrix))

    def bounds_criteria(self, x_list, y_list): #здесь определяем, что прямоугольники внутри Sub_Area
        error = 0
        intercept = 0
        for i in range(len(x_list)):
            # if (x_list[i] < self.Rect_ind.Site_list[i].parent.x()) or (x_list[i] + self.Rect_ind.Site_list[i].width() > self.Rect_ind.Site_list[i].parent.x() + self.Rect_ind.Site_list[i].parent.width()):
            #     error +=1
            # if (y_list[i] < (self.Rect_ind.Site_list[i].parent.y()) or (y_list[i] + self.Rect_ind.Site_list[i].height() > self.Rect_ind.Site_list[i].parent.y() + self.Rect_ind.Site_list[i].parent.height())):
            #     error +=1
            x1 = x_list[i]
            y1 = y_list[i]
            x2 = x1 + self.Rect_ind.Site_list[i].width()
            y2 = y1 + self.Rect_ind.Site_list[i].height()
            x3 = self.Rect_ind.fcl.x()
            y3 = self.Rect_ind.fcl.y()
            x4 = x3 + self.Rect_ind.fcl.width()
            y4 = y3 + self.Rect_ind.fcl.height()
            left = max(x1, x3)
            top = min(y2, y4)
            right = min(x2, x4)
            bottom = max(y1, y3)
            width = right - left
            height = top - bottom
            if not (width < 0 or height < 0):
                intercept += width * height
        return intercept

    def Interception_criteria(self, x_list, y_list): #здесь определяем пересечение прямоугольников
        error = 0
        intercept = 0
        for i in range(0, len(x_list)):
            for j in range(0, len(x_list)):
                if i !=j:
                    # x1_min = x_list[i]
                    # x2_min = x_list[j]
                    # y1_min = y_list[i]
                    # y2_min = y_list[j]
                    # r_ymin = max(y1_min, y2_min)
                    # r_xmin = max(x1_min, x2_min)
                    # r_ymax = min(y1_min + self.Rect_ind.Site_list[i].height(), y2_min + self.Rect_ind.Site_list[j].height())
                    # r_xmax = min(x1_min + self.Rect_ind.Site_list[i].width(), x2_min + self.Rect_ind.Site_list[j].width())
                    # if (r_ymax >= r_ymin) and (r_xmax >= r_xmin):
                    #     error += 1

                    x1 = x_list[i]
                    y1 = y_list[i]
                    x2 = x_list[i] + self.Rect_ind.Site_list[i].width()
                    y2 = y_list[i] + self.Rect_ind.Site_list[i].height()
                    x3 = x_list[j]
                    y3 = y_list[j]
                    x4 = x_list[j] + self.Rect_ind.Site_list[j].width()
                    y4 = y_list[j] + self.Rect_ind.Site_list[i].height()
                    left = max(x1, x3)
                    top = min(y2, y4)
                    right = min(x2, x4)
                    bottom = max(y1, y3)
                    width = right - left
                    height = top - bottom
                    if not (width < 0 or height < 0):
                        intercept += width * height
        return intercept

    def recalculate_WH(self, k_list): #перевычисление ширины и высоты Site
        for i in range(len(k_list)):
            self.Rect_ind.Site_list[i].setWidth(int(math.sqrt(self.Rect_ind.Site_list[i].S) * k_list[i]))
            self.Rect_ind.Site_list[i].setHeight(int(self.Rect_ind.Site_list[i].S / self.Rect_ind.Site_list[i].width()))

    def compact_criteria(self, x_list, y_list):
        x_max = max(x_list)
        y_max = max(y_list)
        x_min = min(x_list)
        y_min = min(y_list)
        return (x_max - x_min) * (y_max - y_min)



    # Переопределение классов
    def Overload_classes(self): # НЕСОВСЕМ ЯСНО МОЖНО ЛИ ПРОСТО БРАТЬ ГРАНИЦЫ ЗДАНИЯ В КАЧЕСТВЕ АРГУМЕНТОВ МУТАЦИИ И СКРЕЩИВАНИЯ
        creator.create("FitnessMin", base.Fitness, weights=(-1, +1, -1, -5)) #НУЖЕН ЛИ crator'у self
        creator.create("Individual", list, fitness=creator.FitnessMin)
        self.toolbox.register("Fill_k", rnd.uniform, self.kmin, self.kmax)
        self.toolbox.register("Fill_x", rnd.randint, 0, self.Rect_ind.fcl.width() / 2)
        self.toolbox.register("Fill_y", rnd.randint, 0, self.Rect_ind.fcl.height() / 2)
        self.toolbox.register("individualCreator", tools.initCycle, creator.Individual, (self.toolbox.Fill_x,
                                                                                            self.toolbox.Fill_y,
                                                                                            self.toolbox.Fill_k),
                                                                                            n=len(self.Rect_ind.Site_list))

        self.toolbox.register("populationCreator", tools.initRepeat, list, self.toolbox.individualCreator)
        self.toolbox.register("evaluate", self.MinFitness)

        self.toolbox.register("select", tools.selTournament, tournsize=self.TOURNSIZE)
        self.toolbox.register("mate", tools.cxSimulatedBinaryBounded,
                                                        low=self.low,
                                                        up=self.up,
                                                        eta=self.CROWDING_FACTOR)

        self.toolbox.register("mutate", tools.mutPolynomialBounded,
                                                        low=self.low,
                                                        up=self.up,
                                                        eta=self.CROWDING_FACTOR,
                                                        indpb=1.0 / (len(self.Rect_ind.Site_list) * 3))

        self.stats = tools.Statistics(lambda ind: ind.fitness.values)
        self.stats.register("min", np.min)
        self.stats.register("avg", np.mean)
        self.stats.register('criterions', np.array)
        self.hof = tools.HallOfFame(self.HALL_OF_FAME_SIZE)
    # Переопределение классов

    # выполнение библиотечного алгоритма
    def Main_autoga(self):
        self.population = self.toolbox.populationCreator(n= self.POPULATION_SIZE)
        self.population, self.logbook = eaSimple(self.population, self.toolbox,
                                                  cxpb=self.P_CROSSOVER,
                                                  mutpb = self.P_MUTATION,
                                                  ngen=self.MAX_GENERATIONS, ga_obj=self,
                                                  halloffame=self.hof,
                                                  stats=self.stats, verbose=True)

        maxFitnessValues, meanFitnessValue = self.logbook.select("min", "mean")

        pass
    # выполнение библиотечного алгоритма


def eaSimple(population, toolbox, cxpb, mutpb, ngen, ga_obj, stats=None,
             halloffame=None, verbose=__debug__,):
    stop_flag = False
    gen = 0
    logbook = tools.Logbook()
    logbook.header = ['gen', 'nevals'] + (stats.fields if stats else [])

    # Evaluate the individuals with an invalid fitness
    invalid_ind = [ind for ind in population if not ind.fitness.valid]
    fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit

    if halloffame is not None:
        halloffame.update(population)

    record = stats.compile(population) if stats else {}
    logbook.record(gen=0, nevals=len(invalid_ind), **record)
    if verbose:
        print(logbook.stream)

    # Begin the generational process
    while not ga_obj.Stop: #gen < ngen
        QCoreApplication.processEvents()
        gen += 1
        # Select the next generation individuals
        offspring = toolbox.select(population, len(population))

        # Vary the pool of individuals
        offspring = varAnd(offspring, toolbox, cxpb, mutpb)

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        # Update the hall of fame with the generated individuals
        if halloffame is not None:
            halloffame.update(offspring)

        # Replace the current population by the offspring
        population[:] = offspring

        # Append the current generation statistics to the logbook
        record = stats.compile(population) if stats else {}
        logbook.record(gen=gen, nevals=len(invalid_ind), **record)
        if verbose:
            print(logbook.stream)

    return population, logbook

def varAnd(population, toolbox, cxpb, mutpb):

    offspring = [toolbox.clone(ind) for ind in population]

    # Apply crossover and mutation on the offspring
    for i in range(1, len(offspring), 2):
        if random.random() < cxpb:
            offspring[i - 1], offspring[i] = toolbox.mate(offspring[i - 1],
                                                          offspring[i])
            del offspring[i - 1].fitness.values, offspring[i].fitness.values

    for i in range(len(offspring)):
        if random.random() < mutpb:
            offspring[i], = toolbox.mutate(offspring[i])
            del offspring[i].fitness.values

    return offspring
def getpartelem(array,n):
    array = np.array(array)
    elem = array[n]
    return elem



