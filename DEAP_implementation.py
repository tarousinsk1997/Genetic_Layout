from deap import base, creator, tools, algorithms

from matplotlib import pyplot as plt
import random as rnd
import numpy as np

from PyQt5.QtCore import QCoreApplication, QPointF


import math


class Genetic_implement:
    def __init__(self, fclIndividual):
    # гиперпараметры алгоритма
        self.P_MUTATION = 0.7
    # вероятность мутации
        self.MAX_GENERATIONS = 1500  # число поколоений
        self.P_CROSSOVER = 0.9  # вероятность скрещивания
        self.HOF_K = 0.2
        self.POPULATION_SIZE = 200# размер популяции
        self.HALL_OF_FAME_SIZE =int(math.ceil((self.POPULATION_SIZE * self.HOF_K)))  # число хранимых лучших особей
        self.CROWDING_FACTOR = 20  # коэффициент скученности
        self.TOURNSIZE = 2 # турнирный отбор
        self.kmin = 0.75
        self.kmax = 1.33
        self.Rect_ind = fclIndividual # ИЗВНЕ ПЕРЕДАЕМ любой ОБЪЕКТ Цеха c ВЫПОЛНЕННЫМИ МЕТОДАМИ в MAIN!!!
        self.Rect_ind_novelty = self.Rect_ind
        self.toolbox = base.Toolbox()
        self.low = []
        self.up = []
        self.Stop = False
        self.rect_info = {}
        self.alg_flag = 0
        self.globalgencounter = 0
        self.masspoint_hof = QPointF(0,0)
        self.globallogbook = tools.Logbook()
        self.cargo_draw = []
        self.ui_updateFlag =  False

        self.corrected_ind = None


        self.intercept_constraint = 1
        self.bound_constraint = 1
        self.noveltykoef = 1
        self.soft_constraint = 0.01
        self.distancecriteria_koef = 5
        self.distancenoveltycriteria_koef = self.intercept_constraint * 2
        self.searchrectsside = 10
        self.searchrects = []

        for i in range(0, len(self.Rect_ind.Site_list)):
            self.low.extend([self.Rect_ind.fcl.x(), self.Rect_ind.fcl.y(), self.kmin])
            self.up.extend([self.Rect_ind.fcl.x() + self.Rect_ind.fcl.width(), self.Rect_ind.fcl.y() + self.Rect_ind.fcl.height(), self.kmax])
    # гиперпараметры алгоритма

    # Переопределение классов
    def Overload_classes(self): # НЕСОВСЕМ ЯСНО МОЖНО ЛИ ПРОСТО БРАТЬ ГРАНИЦЫ ЗДАНИЯ В КАЧЕСТВЕ АРГУМЕНТОВ МУТАЦИИ И СКРЕЩИВАНИЯ
        self.alg_flag = 0
        if self.alg_flag == 1:
            creator.create("FitnessMin", base.Fitness, weights=(-1.0, 1.0)) #пересечение между собой, внутри parent, войд зоны, грузопоток, обрамляющий
        else:
            creator.create("FitnessMin", base.Fitness, weights=(1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMin)
        self.toolbox.register("Fill_k", rnd.uniform, self.kmin, self.kmax)
        self.toolbox.register("Fill_x", rnd.uniform, 0, self.Rect_ind.fcl.width())
        self.toolbox.register("Fill_y", rnd.uniform, 0, self.Rect_ind.fcl.height())
        self.toolbox.register("individualCreator", tools.initCycle, creator.Individual, (self.toolbox.Fill_x,
                                                                                            self.toolbox.Fill_y,
                                                                                            self.toolbox.Fill_k),
                                                                                            n=len(self.Rect_ind.Site_list))

        self.toolbox.register("individual_corrected", self.correctedindividual_mtd, creator.Individual)

        self.toolbox.register("populationCreator", tools.initRepeat, list, self.toolbox.individualCreator)
        self.toolbox.register("evaluate", self.MinFitness)
        self.toolbox.register("mate", tools.cxSimulatedBinaryBounded,
                              low=self.low,
                              up=self.up,
                              eta=self.CROWDING_FACTOR)

        self.toolbox.register("mutate", tools.mutPolynomialBounded,
                              low=self.low,
                              up=self.up,
                              eta=self.CROWDING_FACTOR,
                              indpb=1.0 / (len(self.Rect_ind.Site_list) * 3))


        if self.alg_flag == 0:
            #self.toolbox.register("select", tools.selRoulette)
            #self.toolbox.register('select', tools.selStochasticUniversalSampling)
            self.toolbox.register("select", tools.selTournament, tournsize=self.TOURNSIZE)
            self.hof = tools.HallOfFame(self.HALL_OF_FAME_SIZE)
        elif self.alg_flag == 1:
            self.toolbox.register("select", tools.selNSGA2)
            self.hof = tools.ParetoFront()


        self.stats = tools.Statistics(lambda ind: ind.fitness.values)
        self.stats.register("min", np.min)
        self.stats.register("avg", np.mean)
        #self.stats.register('criterions', np.array)

    # Переопределение классов

    def correctedindividual_mtd(self, icls):
        return icls(self.corrected_ind)

    def MinFitness(self, individual): # функция вычисления приспособленности
        x_list = np.array(individual[0::3])
        y_list = np.array(individual[1::3])
        k_list = np.array(individual[2::3])

        #self.noveltykoef = 0.1 * self.globalgencounter
        cargo = np.array(self.Rect_ind.cargo_matrix).reshape((len(x_list), len(y_list)))
        self.recalculate_WH(k_list)
        if self.alg_flag == 0:
            Fit_intercept = self.Interception_criteria(x_list, y_list) * self.intercept_constraint
            Fit_compact = self.compact_criteria(x_list, y_list) * self.soft_constraint
            Fit_inbounds = self.inbounds_criteria(x_list, y_list) * self.bound_constraint
            Fit_cargo = self.mincargo_criteria(cargo, x_list, y_list)
            Fit_distance = self.distancecriteria(x_list, y_list) * self.distancecriteria_koef


            # if Fit_cargo > Fit_intercept:
            #     self.intercept_constraint += 0.0000000001
            #     self.bound_constraint *= self.intercept_constraint
            #     self.soft_constraint = self.intercept_constraint / 100
            #     self.distancecriteria_koef = self.intercept_constraint
        #if len(self.hof) > 1 and self.Interception_criteria(self.hof[0][0::3], self.hof[0][1::3]) == 0 and self.inbounds_criteria(self.hof[0][0::3], self.hof[0][1::3]) == -sumsquares:
            fit =  Fit_cargo + Fit_distance + Fit_compact + Fit_inbounds + Fit_intercept
            return (-fit,)
        else:
            fit = self.Interception_criteria(x_list, y_list) * self.intercept_constraint + \
                  self.compact_criteria(x_list, y_list) * self.soft_constraint + \
                  self.inbounds_criteria(x_list, y_list) * self.bound_constraint + \
                  self.mincargo_criteria(cargo, x_list, y_list) + \
                  self.distancecriteria(x_list, y_list) * self.distancecriteria_koef
            fitnovelty =  self.distancenoveltycriteria(x_list,y_list) * self.distancenoveltycriteria_koef


            return (fit, fitnovelty)
        #print(f"Критерий: {self.Interception_criteria(x_list, y_list)}")
        #print(f"Критерий: { self.inbounds_criteria(x_list, y_list)}")



        # выполнение библиотечного алгоритма
    def Main_autoga(self):
            self.population = self.toolbox.populationCreator(n=self.POPULATION_SIZE)
            self.population, self.globallogbook = self.eaSimple(self.toolbox, cxpb=self.P_CROSSOVER,
                                                                mutpb=self.P_MUTATION, ngen=self.MAX_GENERATIONS,
                                                                stats=self.stats, halloffame=self.hof, verbose=True)


            # self.population, self.globallogbook = eaMuPlusLambda(self.population, self.toolbox,
            #                                                    mu=256,
            #                                                    lambda_=240,
            #                                                    cxpb=self.P_CROSSOVER,
            #                                                    mutpb=self.P_MUTATION,
            #                                                    ngen=self.MAX_GENERATIONS, ga_obj=self,
            #                                                    halloffame=self.hof,
            #                                                    stats=self.stats, verbose=True)
            pass
        # выполнение библиотечного алгоритма

    def mincargo_criteria(self, cargo, x_list, y_list): #здесь определяем мощность грузопотока ВНИМАНИЕ ПРОСЛЕДИТЬ ЧТОБЫ БЫЛО СООТВЕТСТВИЕ
        distance_matrix = np.zeros((len(self.Rect_ind.Site_list),len(self.Rect_ind.Site_list)))
        for i in range(distance_matrix.shape[0]):
            for j in range(distance_matrix.shape[0]):
                    x1_center = x_list[i] + self.Rect_ind.Site_list[i].width() / 2
                    y1_center = y_list[i] + self.Rect_ind.Site_list[i].height() / 2
                    x2_center = x_list[j] + self.Rect_ind.Site_list[j].width() / 2
                    y2_center = y_list[j] + self.Rect_ind.Site_list[j].height() / 2
                    distance_matrix[i][j] = math.sqrt((x1_center - x2_center) ** 2 + (y1_center - y2_center) ** 2)
        return np.sum(np.multiply(cargo, distance_matrix))

    def novelty(self, x_list, y_list):
        if self.globalgencounter > 1:

            x, y, xhof0, yhof0 = 0, 0, 0, 0
            k_list = self.hof[0][2::3]

            for i in range(len(k_list)):
                self.Rect_ind_novelty.Site_list[i].setWidth(math.sqrt(self.Rect_ind_novelty.Site_list[i].S) * k_list[i])
                self.Rect_ind_novelty.Site_list[i].setHeight(self.Rect_ind_novelty.Site_list[i].S / self.Rect_ind_novelty.Site_list[i].width())

            for i in range(len(x_list)):
                x += x_list[i] + self.Rect_ind.Site_list[i].width()
                y += y_list[i] + self.Rect_ind.Site_list[i].height()
                xhof0 += self.hof[0][0::3][i] + self.Rect_ind_novelty.Site_list[i].width()
                yhof0 += self.hof[0][1::3][i] + self.Rect_ind_novelty.Site_list[i].height()

            masspoint_current = QPointF(x / len(x_list), y / len(y_list))
            self.masspoint_hof = QPointF(xhof0 / len(x_list), yhof0 / len(y_list))

            if pointinquad(self.masspoint_hof, self.Rect_ind.fcl)[1] == 0:
                if masspoint_current.x() < self.masspoint_hof.x() or masspoint_current.y() < self.masspoint_hof.y():
                    return -1
                else:
                    return 0
            elif pointinquad(self.masspoint_hof, self.Rect_ind.fcl)[1] == 1:
                if masspoint_current.x() > self.masspoint_hof.x() or masspoint_current.y() < self.masspoint_hof.y():
                    return -1
                else:
                    return 0
            elif pointinquad(self.masspoint_hof, self.Rect_ind.fcl)[1] == 2:
                if masspoint_current.x() > self.masspoint_hof.x() or masspoint_current.y() > self.masspoint_hof.y():
                    return -1
                else:
                    return 0
            elif pointinquad(self.masspoint_hof, self.Rect_ind.fcl)[1] == 3:
                if masspoint_current.x() < self.masspoint_hof.x() or masspoint_current.y() > self.masspoint_hof.y():
                    return -1
                else:
                    return 0
        return 0
    def inbounds_criteria(self, x_list, y_list): #здесь определяем, что прямоугольники внутри Sub_Area
        intercept = 0
        fit = 0
        for i in range(len(x_list)):
            x1 = x_list[i]
            y1 = y_list[i]
            x2 = x1 + self.Rect_ind.Site_list[i].width()
            y2 = y1 + self.Rect_ind.Site_list[i].height()

            x3 = self.Rect_ind.Site_list[i].parent.x()
            y3 = self.Rect_ind.Site_list[i].parent.y()

            width = self.Rect_ind.Site_list[i].parent.width()
            height = self.Rect_ind.Site_list[i].parent.height()

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
        return  - intercept

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

        intercept1 = 0
        if len(self.rect_info) != 0:
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
                            intercept1 += width * height


        return intercept + intercept1

    def recalculate_WH(self, k_list): #перевычисление ширины и высоты Site
        for i in range(len(k_list)):
            self.Rect_ind.Site_list[i].setWidth(math.sqrt(self.Rect_ind.Site_list[i].S) * k_list[i])
            self.Rect_ind.Site_list[i].setHeight(self.Rect_ind.Site_list[i].S / self.Rect_ind.Site_list[i].width())

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

    def distancecriteria(self, x_list, y_list):
        distance = 0
        counter = 0
        for i in range(len(x_list)):
            if self.Rect_ind.Site_list[i].parent.name != 'FCL':
                x1 = x_list[i]
                y1 = y_list[i]
                x2 = x1 + self.Rect_ind.Site_list[i].width() / 2
                y2 = y1 + self.Rect_ind.Site_list[i].height() / 2
                x3 = self.Rect_ind.Site_list[i].parent.x()
                y3 = self.Rect_ind.Site_list[i].parent.y()

                width = self.Rect_ind.Site_list[i].parent.width()
                height = self.Rect_ind.Site_list[i].parent.height()

                x3, y3, width, height = change_coord(x3, y3, width, height)
                x4 = x3 + width / 2
                y4 = y3 + height / 2
                distance += math.sqrt((x2-x4) ** 2 + (y2 - y4) ** 2)
                counter +=1
        return distance

    def distancenoveltycriteria(self, x_list, y_list):
        distance = 0
        if len(self.hof) != 0:
            hofxlist = self.hof[0][0::3]
            hofylist = self.hof[0][1::3]
            for i in range(len(x_list)):
                pointhof = [hofxlist[i], hofylist[i]]
                pointcurrent = [x_list[i], y_list[i]]
                distance += math.sqrt((pointcurrent[0] - pointhof[0]) ** 2 + (pointcurrent[1] - pointhof[1]) ** 2)
        return distance


    # дополнительные методы
    def draw(self, cargo_fit, q=False):
        gen = self.globallogbook.select("gen")
        del gen[-1]
        fit_mins =cargo_fit
        fig, ax1 = plt.subplots()
        line1 = ax1.plot(gen, fit_mins, "b-", label="Суммарный грузопоток")
        ax1.set_xlabel("Поколение")
        ax1.set_ylabel("Суммарный грузопток", color="b")
        ax1.grid(axis='both', color='k', linestyle='-', linewidth=1)
        for tl in ax1.get_yticklabels():
            tl.set_color("b")
        if not q:
            plt.savefig(f'eaSimple{q}.png')
        plt.show()
    # def drawPareto(self):
    #     fig2, ax2 = plt.subplots()
    #     line1 = ax2.plot(gen, fit_mins, "b-", label="Суммарный грузопоток")
    #     ax2.set_xlabel("Поколение")
    #     ax2.set_ylabel("Суммарный грузопток", color="b")
    #     ax2.grid(axis='both', color='k', linestyle='-', linewidth=1)
    #     for tl in ax2.get_yticklabels():
    #         tl.set_color("b")
    #     if not q:
    #         plt.savefig(f'eaSimple{q}.png')
    #     plt.show()


    def eaSimple(self, toolbox, cxpb, mutpb, ngen, stats=None,
                 halloffame=None, verbose=__debug__,):

        if self.corrected_ind is not None:
            correctedone = self.toolbox.individual_corrected()

            self.population[:int(len(self.population) / 4 - 1)] = [correctedone for elem in self.population[:int(len(self.population) / 4 - 1)]]

            # population[len(population) - 1] = self.toolbox.individual_guess()

        gen = 0
        self.cargo_draw = []
        logbook = tools.Logbook()
        logbook.header = ['gen', 'nevals'] + (stats.fields if stats else [])

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in self.population if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        if halloffame is not None:
            halloffame.update(self.population)

        record = stats.compile(self.population) if stats else {}
        logbook.record(gen=0, nevals=len(invalid_ind), **record)

        if verbose:
            print(logbook.stream)

        # Begin the generational process
        while (not self.Stop) : #gen < ngen and (not stop_flag)
            QCoreApplication.processEvents()
            gen += 1

            self.globalgencounter = gen

            # Select the next generation individuals
            offspring = toolbox.select(self.population, len(self.population))

            # Vary the pool of individuals
            offspring = algorithms.varAnd(offspring, toolbox, cxpb, mutpb)

            # Evaluate the individuals with an invalid fitness
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit

            # Update the hall of fame with the generated individuals
            if halloffame is not None:
                halloffame.update(offspring)

            # Replace the current population by the offspring
            self.population[:] = offspring
            print(self.corrected_ind)


            # Append the current generation statistics to the logbook
            record = stats.compile(self.population) if stats else {}
            logbook.record(gen=gen, nevals=len(invalid_ind), **record)

            self.globallogbook = logbook
            if verbose:
                print(logbook.stream)


            self.cargo_draw.append(self.mincargo_criteria(x_list=self.hof[0][0::3], y_list=self.hof[0][1::3],
                                                              cargo=np.array(self.Rect_ind.cargo_matrix).reshape(
                                                                  (len(self.hof[0][0::3]), len(self.hof[0][0::3])))))

            Fit_intercept = self.Interception_criteria(x_list=self.hof[0][0::3], y_list=self.hof[0][1::3]) * self.intercept_constraint
            Fit_cargo = self.mincargo_criteria(cargo=np.array(self.Rect_ind.cargo_matrix).reshape(
                                                                  (len(self.hof[0][0::3]), len(self.hof[0][0::3]))), x_list=self.hof[0][0::3], y_list=self.hof[0][1::3])

            #print(f'Критерий пересечения= {Fit_intercept}\n Критерий грузопотока={Fit_cargo}\n')
            if Fit_cargo > Fit_intercept:
                self.intercept_constraint += 1
                self.bound_constraint = self.intercept_constraint
                self.soft_constraint = self.intercept_constraint / 10 * 2
                self.distancecriteria_koef = self.intercept_constraint * 2

        return self.population, logbook

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

def getpartelem(array,n):
    array = np.array(array)
    elem = array[n]
    return elem

def pointinquad(point, fcl):
    pointx = point.x()
    pointy = point.y()

    if pointx >= fcl.width() and pointy >= fcl.height():
        return (True, 0)
    elif pointx >= fcl.width() and pointy <= fcl.height():
        return (True, 3)
    elif pointx <= fcl.width() and pointy >= fcl.height():
        return (True, 1)
    else:
        return (True, 2)




