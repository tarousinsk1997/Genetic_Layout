from deap import base
from deap import creator
from deap import tools
from deap import algorithms
from matplotlib import pyplot as plt
import random as rnd
import numpy as np



import math


class Genetic_implement:
    def __init__(self, fclIndividual):
    # гиперпараметры алгоритма
        self.P_MUTATION = 0.8  # вероятность мутации
        self.MAX_GENERATIONS = 300  # число поколоений
        self.P_CROSSOVER = 0.9  # вероятность скрещивания
        self.HALL_OF_FAME_SIZE = 2  # число хранимых лучших особей
        self.POPULATION_SIZE = 15  # размер популяции
        self.CROWDING_FACTOR = 10  # коэффициент скученности
        self.TOURNSIZE = 2  # турнирный отбор
        self.kmin = 0.7
        self.kmax = 1.3
        self.Rect_ind = fclIndividual # ИЗВНЕ ПЕРЕДАЕМ любой ОБЪЕКТ Цеха c ВЫПОЛНЕННЫМИ МЕТОДАМИ в MAIN!!!
        self.toolbox = base.Toolbox()
        self.low = []
        self.up = []
        for i in range(0, len(self.Rect_ind.Site_list)):
            self.low.extend([self.Rect_ind.fcl.x(), self.Rect_ind.fcl.y(), self.kmin])
            self.up.extend([self.Rect_ind.fcl.x() + self.Rect_ind.fcl.width(), self.Rect_ind.fcl.y() + self.Rect_ind.fcl.height(), self.kmax])
    # гиперпараметры алгоритма

    # дополнительные методы
    def draw(self, max, mean):
        plot1 = plt.figure(1)
        plt.grid(color='black', linestyle='-', linewidth=1)
        plt.xlabel('Поколение')
        plt.ylabel('Приспособленность')
        plt.plot(max, color='red')
        plt.plot(mean, color='green')
        plt.show()

    def MinFitness(self, individual): # функция вычисления приспособленности

        x_list = np.array(individual[0::3])
        y_list = np.array(individual[1::3])
        k_list = np.array(individual[2::3])
        cargo = np.array(self.Rect_ind.cargo_matrix).reshape((len(x_list), len(y_list)))
        self.recalculate_WH(k_list)
        fit = (self.calculate_intercept(x_list, y_list),self.check_bounds(x_list, y_list), self.calculate_CP(cargo, x_list, y_list))
        if fit[0] == 0  and fit[1] == 0:
            print(fit)
        return fit

    def calculate_CP(self, cargo, x_list, y_list): #здесь определяем мощность грузопотока ВНИМАНИЕ ПРОСЛЕДИТЬ ЧТОБЫ БЫЛО СООТВЕТСТВИЕ
        distance_matrix = np.zeros((len(self.Rect_ind.Site_list),len(self.Rect_ind.Site_list)))
        for i in range(distance_matrix.shape[0]):
            for j in range(0, distance_matrix.shape[0]):
                distance_matrix[i][j] = math.sqrt(((x_list[i] + self.Rect_ind.Site_list[i].width()) - (x_list[j] + self.Rect_ind.Site_list[j].width()))**2 + ((y_list[i] + self.Rect_ind.Site_list[i].height()) - (y_list[j] + self.Rect_ind.Site_list[j].height()))**2)
        return np.sum(np.multiply(cargo, distance_matrix)) / 2

    def check_bounds(self, x_list, y_list): #здесь определяем, что прямоугольники внутри Sub_Area
        error = 0
        for i in range(len(x_list)):
            if (x_list[i] < self.Rect_ind.Site_list[i].parent.x()) or (x_list[i] + self.Rect_ind.Site_list[i].width() > self.Rect_ind.Site_list[i].parent.x() + self.Rect_ind.Site_list[i].parent.width()):
                error +=1
            if (y_list[i] < (self.Rect_ind.Site_list[i].parent.y()) or (y_list[i] + self.Rect_ind.Site_list[i].height() > self.Rect_ind.Site_list[i].parent.y() + self.Rect_ind.Site_list[i].parent.height())):
                error +=1
        return error

    def calculate_intercept(self, x_list, y_list): #здесь определяем пересечение прямоугольников
        error =0
        for i in range(0, len(x_list)):
            for j in range(0, len(x_list)):
                if i !=j:
                    x1_min = x_list[i]
                    x2_min = x_list[j]
                    y1_min = y_list[i]
                    y2_min = y_list[j]
                    r_ymin = max(y1_min, y2_min)
                    r_xmin = max(x1_min, x2_min)
                    r_ymax = min(y1_min + self.Rect_ind.Site_list[i].height(), y2_min + self.Rect_ind.Site_list[j].height())
                    r_xmax = min(x1_min + self.Rect_ind.Site_list[i].width(), x2_min + self.Rect_ind.Site_list[j].width())
                    if (r_ymax >= r_ymin) and (r_xmax >= r_xmin):
                        error += 1
        return error

    def recalculate_WH(self, k_list): #перевычисление ширины и высоты Site
        for i in range(len(k_list)):
            self.Rect_ind.Site_list[i].setWidth(round(math.sqrt(self.Rect_ind.Site_list[i].S) * k_list[i]))
            self.Rect_ind.Site_list[i].setHeight(round(self.Rect_ind.Site_list[i].S / self.Rect_ind.Site_list[i].width()))

    # дополнительные методы

    # Переопределение классов
    def Overload_classes(self): # НЕСОВСЕМ ЯСНО МОЖНО ЛИ ПРОСТО БРАТЬ ГРАНИЦЫ ЗДАНИЯ В КАЧЕСТВЕ АРГУМЕНТОВ МУТАЦИИ И СКРЕЩИВАНИЯ
        creator.create("FitnessMin", base.Fitness, weights=(-2, -2000, -1)) #НУЖЕН ЛИ crator'у self
        creator.create("Individual", list, fitness=creator.FitnessMin)
        self.toolbox.register("Fill_k", rnd.uniform, self.kmin, self.kmax)
        self.toolbox.register("Fill_x", rnd.randint, 0, self.Rect_ind.fcl.width())
        self.toolbox.register("Fill_y", rnd.randint, 0, self.Rect_ind.fcl.height())
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
        self.hof = tools.HallOfFame(self.HALL_OF_FAME_SIZE)

    # Переопределение классов

    # выполнение библиотечного алгоритма
    def Main_autoga(self):
        self.population = self.toolbox.populationCreator(n= self.POPULATION_SIZE)
        self.population, self.logbook = algorithms.eaSimple(self.population, self.toolbox,
                                                  cxpb=self.P_CROSSOVER,
                                                  mutpb = self.P_MUTATION,
                                                  ngen=self.MAX_GENERATIONS,
                                                  halloffame=self.hof,
                                                  stats=self.stats, verbose=True)
        maxFitnessValues, meanFitnessValue = self.logbook.select("min", "mean")
        pass
    # выполнение библиотечного алгоритма

    def Main_customga(self):
        population = self.toolbox.populationCreator(n= self.POPULATION_SIZE)
        generationCounter = 0

        fitnessValues = list(map(self.toolbox.evaluate, population))

        for individual, fitnessValue in zip(population, fitnessValues):
            individual.fitness.values = fitnessValue

            #статистика
            fitnessValues = [individual.fitness.values for individual in population]

            while generationCounter < self.MAX_GENERATIONS:
                generationCounter = generationCounter + 1

                offspring = self.toolbox.select(population, len (population))
                offspring = list(map(self.toolbox.clone, offspring))

                for child1, child2 in zip(offspring[::2], offspring[1::2]):
                    if rnd.random()< self.P_CROSSOVER:
                        self.toolbox.mate(child1, child2)
                        del child1.fitness.values
                        del child2.fitness.values

                for mutant in offspring:
                    if rnd.random() < self.P_MUTATION:
                        self.toolbox.mutate(mutant)
                        del mutant.fitness.values

                freshIndividuals = [ind for ind in offspring if not ind.fitness.valid]
                freshFitnessValues = list(map(self.toolbox.evaluate, freshIndividuals))
                for individual, fitnessValue in zip(freshIndividuals, freshFitnessValues):
                    individual.fitness.values = fitnessValue

                population[:] = offspring

                fitnessValues = [ind.fitness.values for ind in population]








