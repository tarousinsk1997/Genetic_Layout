from deap import base
from deap import creator
from deap import tools
from deap import algorithms
from matplotlib import pyplot as plt
import random as rnd
import numpy as np
import random
from math import ceil
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
        self.rect_info = {}
        self.alg_flag = 0
        self.hard_constraint = 100
        self.soft_constraint = 1
        self.counter_UI = 0 #счетчик поколений для UI
        for i in range(0, len(self.Rect_ind.Site_list)):
            self.low.extend([self.Rect_ind.fcl.x(), self.Rect_ind.fcl.y(), self.kmin])
            self.up.extend([self.Rect_ind.fcl.x() + self.Rect_ind.fcl.width(), self.Rect_ind.fcl.y() + self.Rect_ind.fcl.height(), self.kmax])
    # гиперпараметры алгоритма

    # Переопределение классов
    def Overload_classes(self): # НЕСОВСЕМ ЯСНО МОЖНО ЛИ ПРОСТО БРАТЬ ГРАНИЦЫ ЗДАНИЯ В КАЧЕСТВЕ АРГУМЕНТОВ МУТАЦИИ И СКРЕЩИВАНИЯ
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,)) #пересечение между собой, внутри parent, войд зоны, грузопоток, обрамляющий
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

        #self.toolbox.register("select", tools.selTournament, tournsize=self.TOURNSIZE)
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
        #self.stats.register('criterions', np.array)
        self.hof = tools.HallOfFame(self.HALL_OF_FAME_SIZE)
    # Переопределение классов

    def MinFitness(self, individual): # функция вычисления приспособленности

        x_list = np.array(individual[0::3])
        y_list = np.array(individual[1::3])
        k_list = np.array(individual[2::3])
        cargo = np.array(self.Rect_ind.cargo_matrix).reshape((len(x_list), len(y_list)))
        self.recalculate_WH(k_list)
        fit = (self.Interception_criteria(x_list, y_list)  + self.inbounds_criteria(x_list, y_list)) * self.hard_constraint + self.mincargo_criteria(cargo, x_list, y_list) + self.compact_criteria(x_list,y_list) * self.soft_constraint
        #print(f'Пересечение прямоугольников =  {self.Interception_criteria(x_list, y_list)}')
        return (fit.item(),)

        # выполнение библиотечного алгоритма
    def Main_autoga(self):
        self.alg_flag = 0
        if self.alg_flag == 0:
            self.population = self.toolbox.populationCreator(n=self.POPULATION_SIZE)
            self.population, self.logbook = eaSimple(self.population, self.toolbox,
                                                         cxpb=self.P_CROSSOVER,
                                                         mutpb=self.P_MUTATION,
                                                         ngen=self.MAX_GENERATIONS, ga_obj=self,
                                                         halloffame=self.hof,
                                                         stats=self.stats, verbose=True)
        elif self.alg_flag == 1:

            self.population, self.logbook = eaMuPlusLambda(self.population, self.toolbox,
                                                               mu=50,
                                                               lambda_=60,
                                                               cxpb=0.7,
                                                               mutpb=0.3,
                                                               ngen=self.MAX_GENERATIONS, ga_obj=self,
                                                               halloffame=self.hof,
                                                               stats=self.stats, verbose=True)
        pass
        # выполнение библиотечного алгоритма

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

    def inbounds_criteria(self, x_list, y_list): #здесь определяем, что прямоугольники внутри Sub_Area
        intercept = 0
        for i in range(len(x_list)):
            x1 = x_list[i]
            y1 = y_list[i]
            x2 = x1 + self.Rect_ind.Site_list[i].width()
            y2 = y1 + self.Rect_ind.Site_list[i].height()


            x3 = self.Rect_ind.Site_list[i].parent.x()
            y3 = self.Rect_ind.Site_list[i].parent.y()

            width = self.Rect_ind.Site_list[i].parent.width()
            height =self.Rect_ind.Site_list[i].parent.height()

           # x3, y3, width, height = change_coord(x3,y3,width,height)

            x4 = x3 + width
            y4 = y3 + height

            left = max(x1, x3)
            top = min(y2, y4)
            right = min(x2, x4)
            bottom = max(y1, y3)
            width = right - left
            height = top - bottom
            if (width < 0 or height < 0):
                intercept += width * height

        return intercept

    def Interception_criteria(self, x_list, y_list): #здесь определяем пересечение прямоугольников
        intercept = 0
        for i in range(0, len(x_list)):
            for j in range(0, len(x_list)):
                if i !=j:
                    x1 = x_list[i]
                    y1 = y_list[i]
                    x2 = x_list[i] + self.Rect_ind.Site_list[i].width()
                    y2 = y_list[i] + self.Rect_ind.Site_list[i].height()

                    x3 = x_list[j]
                    y3 = y_list[j]
                    x4 = x_list[j] + self.Rect_ind.Site_list[j].width()
                    y4 = y_list[j] + self.Rect_ind.Site_list[j].height()

                    left = max(x1, x3)
                    top = min(y2, y4)
                    right = min(x2, x4)
                    bottom = max(y1, y3)
                    width = right - left
                    height = top - bottom
                    if not (width < 0 or height < 0):
                        intercept += width * height
        intercept_1 = 0

        # if len(self.rect_info) != 0:
        #     for i in range(0, len(x_list)):
        #         for j in range(len(self.rect_info)):
        #             if self.rect_info[f'{j}'][2] == 'Дорога' or self.rect_info[f'{j}'][2] == 'Пустота':
        #                 x1 = x_list[i]
        #                 y1 = y_list[i]
        #                 x2 = x1 + self.Rect_ind.Site_list[i].width()
        #                 y2 = x2 + self.Rect_ind.Site_list[i].height()
        #
        #                 x3 = self.rect_info[f'{j}'][0].x()
        #                 y3 = self.rect_info[f'{j}'][0].y()
        #                 width = self.rect_info[f'{j}'][0].width()
        #                 height = self.rect_info[f'{j}'][0].height()
        #
        #                 x3, y3, width, height = change_coord(x3, y3, width, height)
        #
        #                 x4 = x3 + width
        #                 y4 = y3 + height
        #
        #                 left = max(x1, x3)
        #                 top = min(y2, y4)
        #                 right = min(x2, x4)
        #                 bottom = max(y1, y3)
        #                 width = right - left
        #                 height = top - bottom
        #                 if not (width < 0 or height < 0):
        #                     intercept_1 += width * height

        return intercept + self.void_zones(x_list, y_list)

    def recalculate_WH(self, k_list): #перевычисление ширины и высоты Site
        for i in range(len(k_list)):
            self.Rect_ind.Site_list[i].setWidth(ceil(math.sqrt(self.Rect_ind.Site_list[i].S) * k_list[i]))
            self.Rect_ind.Site_list[i].setHeight(ceil(self.Rect_ind.Site_list[i].S / self.Rect_ind.Site_list[i].width()))

    def compact_criteria(self, x_list, y_list):
        x_max = max(x_list)
        y_max = max(y_list)
        x_min = min(x_list)
        y_min = min(y_list)
        return (x_max - x_min) * (y_max - y_min)

    def void_zones(self, x_list, y_list):
        intercept = 0
        if len(self.rect_info) !=0:
            for i in range(0, len(x_list)):
                for j in range(len(self.rect_info)):
                    if self.rect_info[f'{j}'][2] == 'Дорога' or self.rect_info[f'{j}'][2] == 'Пустота':
                        x1 = x_list[i]
                        y1 = y_list[i]
                        x2 = x1 + self.Rect_ind.Site_list[i].width()
                        y2 = x2 + self.Rect_ind.Site_list[i].height()

                        x3 = self.rect_info[f'{j}'][0].x()
                        y3 = self.rect_info[f'{j}'][0].y()
                        width = self.rect_info[f'{j}'][0].width()
                        height = self.rect_info[f'{j}'][0].height()

                        x3, y3, width, height = change_coord(x3, y3, width, height)

                        x4 = x3 + width
                        y4 = y3 + height

                        left = max(x1, x3)
                        top = min(y2, y4)
                        right = min(x2, x4)
                        bottom = max(y1, y3)
                        width = right - left
                        height = top - bottom
                        if not (width < 0 or height < 0):
                            intercept += width * height
        return intercept




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
        line2 = ax2.plot(gen, size_avgs, "r-", label="Average Fitness")
        #ax2.set_ylabel("Size", color="r")
        for tl in ax2.get_yticklabels():
            tl.set_color("r")

        lns = line1 + line2
        labs = [l.get_label() for l in lns]
        ax1.legend(lns, labs, loc="center right")

        plt.show()

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

def eaMuPlusLambda(population, toolbox, mu, lambda_, cxpb, mutpb, ngen, ga_obj,
                   stats=None, halloffame=None, verbose=__debug__):
    """This is the :math:`(\mu + \lambda)` evolutionary algorithm.

    :param population: A list of individuals.
    :param toolbox: A :class:`~deap.base.Toolbox` that contains the evolution
                    operators.
    :param mu: The number of individuals to select for the next generation.
    :param lambda\_: The number of children to produce at each generation.
    :param cxpb: The probability that an offspring is produced by crossover.
    :param mutpb: The probability that an offspring is produced by mutation.
    :param ngen: The number of generation.
    :param stats: A :class:`~deap.tools.Statistics` object that is updated
                  inplace, optional.
    :param halloffame: A :class:`~deap.tools.HallOfFame` object that will
                       contain the best individuals, optional.
    :param verbose: Whether or not to log the statistics.
    :returns: The final population
    :returns: A class:`~deap.tools.Logbook` with the statistics of the
              evolution.

    The algorithm takes in a population and evolves it in place using the
    :func:`varOr` function. It returns the optimized population and a
    :class:`~deap.tools.Logbook` with the statistics of the evolution. The
    logbook will contain the generation number, the number of evaluations for
    each generation and the statistics if a :class:`~deap.tools.Statistics` is
    given as argument. The *cxpb* and *mutpb* arguments are passed to the
    :func:`varOr` function. The pseudocode goes as follow ::

        evaluate(population)
        for g in range(ngen):
            offspring = varOr(population, toolbox, lambda_, cxpb, mutpb)
            evaluate(offspring)
            population = select(population + offspring, mu)

    First, the individuals having an invalid fitness are evaluated. Second,
    the evolutionary loop begins by producing *lambda_* offspring from the
    population, the offspring are generated by the :func:`varOr` function. The
    offspring are then evaluated and the next generation population is
    selected from both the offspring **and** the population. Finally, when
    *ngen* generations are done, the algorithm returns a tuple with the final
    population and a :class:`~deap.tools.Logbook` of the evolution.

    This function expects :meth:`toolbox.mate`, :meth:`toolbox.mutate`,
    :meth:`toolbox.select` and :meth:`toolbox.evaluate` aliases to be
    registered in the toolbox. This algorithm uses the :func:`varOr`
    variation.
    """
    logbook = tools.Logbook()
    logbook.header = ['gen', 'nevals'] + (stats.fields if stats else [])

    # Evaluate the individuals with an invalid fitness
    invalid_ind = [ind for ind in population if not ind.fitness.valid]
    fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit

    if halloffame is not None:
        halloffame.update(population)

    record = stats.compile(population) if stats is not None else {}
    logbook.record(gen=0, nevals=len(invalid_ind), **record)
    if verbose:
        print(logbook.stream)

    # Begin the generational process
    gen = 0
    while not ga_obj.Stop:  # gen < ngen
        QCoreApplication.processEvents()
        gen += 1
        # Vary the population
        offspring = varOr(population, toolbox, lambda_, cxpb, mutpb)

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        # Update the hall of fame with the generated individuals
        if halloffame is not None:
            halloffame.update(offspring)

        # Select the next generation population
        population[:] = toolbox.select(population + offspring, mu)

        # Update the statistics with the new population
        record = stats.compile(population) if stats is not None else {}
        logbook.record(gen=gen, nevals=len(invalid_ind), **record)
        if verbose:
            print(logbook.stream)

    return population, logbook


def change_coord(x1,y1,w1,h1):
    x = x1
    y = y1
    w = w1
    h = h1
    if w < 0 and h > 0:
        x = x + w
    elif w > 0 and h < 0:
        y = y + h
    elif w < 0 and h < 0:
        x = x + w
        y = y + h
    w, h = abs(w), abs(h)
    return x,y,w,h
def varOr(population, toolbox, lambda_, cxpb, mutpb):
    """Part of an evolutionary algorithm applying only the variation part
    (crossover, mutation **or** reproduction). The modified individuals have
    their fitness invalidated. The individuals are cloned so returned
    population is independent of the input population.

    :param population: A list of individuals to vary.
    :param toolbox: A :class:`~deap.base.Toolbox` that contains the evolution
                    operators.
    :param lambda\_: The number of children to produce
    :param cxpb: The probability of mating two individuals.
    :param mutpb: The probability of mutating an individual.
    :returns: The final population.

    The variation goes as follow. On each of the *lambda_* iteration, it
    selects one of the three operations; crossover, mutation or reproduction.
    In the case of a crossover, two individuals are selected at random from
    the parental population :math:`P_\mathrm{p}`, those individuals are cloned
    using the :meth:`toolbox.clone` method and then mated using the
    :meth:`toolbox.mate` method. Only the first child is appended to the
    offspring population :math:`P_\mathrm{o}`, the second child is discarded.
    In the case of a mutation, one individual is selected at random from
    :math:`P_\mathrm{p}`, it is cloned and then mutated using using the
    :meth:`toolbox.mutate` method. The resulting mutant is appended to
    :math:`P_\mathrm{o}`. In the case of a reproduction, one individual is
    selected at random from :math:`P_\mathrm{p}`, cloned and appended to
    :math:`P_\mathrm{o}`.

    This variation is named *Or* because an offspring will never result from
    both operations crossover and mutation. The sum of both probabilities
    shall be in :math:`[0, 1]`, the reproduction probability is
    1 - *cxpb* - *mutpb*.
    """
    assert (cxpb + mutpb) <= 1.0, (
        "The sum of the crossover and mutation probabilities must be smaller "
        "or equal to 1.0.")

    offspring = []
    for _ in range(lambda_):
        op_choice = random.random()
        if op_choice < cxpb:            # Apply crossover
            ind1, ind2 = list(map(toolbox.clone, random.sample(population, 2)))
            ind1, ind2 = toolbox.mate(ind1, ind2)
            del ind1.fitness.values
            offspring.append(ind1)
        elif op_choice < cxpb + mutpb:  # Apply mutation
            ind = toolbox.clone(random.choice(population))
            ind, = toolbox.mutate(ind)
            del ind.fitness.values
            offspring.append(ind)
        else:                           # Apply reproduction
            offspring.append(random.choice(population))

    return offspring
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



