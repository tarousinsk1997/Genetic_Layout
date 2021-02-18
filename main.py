import sys, random as rnd
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QToolTip
from PyQt5.QtGui import QPainter, QColor, QPen, QFont
from UI_Form import Ui_MainWindow  # импорт нашего сгенерированного файла
from PyQt5.QtCore import Qt, QObject, QEvent, QPoint
import Visual, course, math, time
from deap import base, creator, tools, algorithms
from matplotlib import pyplot as plt
import DEAP_implementation as DI
import numpy as np
import datetime, xlwt, xlrd, xlwings as xw

# os.system(r'C:\\Users\\tarou\\PycharmProjects\\Genetic_Layout\\convert.bat')


class Mywindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(Mywindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.i = 2
        self.w = None
        self.ui.widget.installEventFilter(self)
        self.ui.Execution_GA.clicked.connect(self.execute_ga)
        #self.ui.Execution_GA.clicked.connect(self.execute_with_timer)
        self.ui.StopButton.clicked.connect(self.Stop_ga)
        self.counter_label = 0
        self.FCL_Ref = generate_initial()
        self.Pressed = False
        self.ui.lineEdit.setText('1')

        QToolTip.setFont(QFont('SansSerif', 10))
        self.ui.widget.setMouseTracking(True)




    def eventFilter(self, o, e):
        if (o.objectName() == "widget"):
            if e.type() == QtCore.QEvent.Paint:
                self.paintEvent(e)
            if (e.type() == QtCore.QEvent.MouseButtonPress):
                self.Pressed = True
                self.mousePressedEvent(e)

            if (e.type() == QtCore.QEvent.MouseButtonRelease):
                self.Pressed = False

            if (e.type() == QtCore.QEvent.MouseMove):
                if not self.Pressed:
                    self.mouseMoveEvent(e)
        return True


    def execute_ga(self):
        self.FCL_Ref = generate_initial()
        self.GA = DI.Genetic_implement(self.FCL_Ref)
        self.GA.Overload_classes()
        self.GA.MAX_GENERATIONS = int(self.ui.lineEdit.text())
        self.GA.Main_autoga()
        QRectSolution = self.generate_Qrect_Solution(self.GA.hof[0])

        self.FCL_Ref.Site_list = QRectSolution
        self.FCL_Ref.dictName, self.FCL_Ref.dictSpace, self.FCL_Ref.dictRect = self.tooltipData()
        self.ui.label_2.setText("Выполнено")

        self.ui.widget.update()
        self.GA.draw()
        del self.GA

    def execute_with_timer(self):
        time_list = []
        for i in range(15):
            self.FCL_Ref = generate_initial()
            start_time = time.time()
            self.GA = DI.Genetic_implement(self.FCL_Ref)
            self.GA.Overload_classes()
            self.GA.MAX_GENERATIONS = int(self.ui.lineEdit.text())
            self.GA.Main_autoga()
            QRectSolution = self.generate_Qrect_Solution(self.GA.hof[0])
            self.FCL_Ref.Site_list = QRectSolution
            self.FCL_Ref.dictName, self.FCL_Ref.dictSpace, self.FCL_Ref.dictRect = self.tooltipData()
            self.ui.label_2.setText("Выполнено")
            self.ui.widget.update()
            stop_time = time.time()
            duration = stop_time - start_time
            time_list.append(str(duration))
            del self.GA, start_time
        book = xlwt.Workbook('Time_stat.xlsx')
        sht = book.add_sheet('sheet1')
        for i in range(len(time_list)):
            sht.write(0, i, str(time_list[i]))
        book.save('Time_stat.xls')


    def Stop_ga(self):
        self.GA.Stop = True


    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self.ui.widget)
        self.drawRectangles(qp, self.FCL_Ref.fcl, QColor(0, 0, 0), 5)
        #self.drawRectangles(qp, FCL_Ref.SubArea_1, QColor(0, 0, 0), 2)
        #self.drawRectangles(qp, FCL_Ref.SubArea_2, QColor(0, 0, 0), 2)
        for qrect, name in zip(self.FCL_Ref.Site_list, self.FCL_Ref.area_sitenamelist):
            self.drawRectangles(qp, qrect, QColor(0,0,0), 2, name=name)
        self.drawPoints(qp, QColor(128, 128, 128))
        qp.end()

    def drawRectangles(self, qp, rect_obj, qcolor, mt, name=''):
        Visual_obj = Visual.Visual_Obj(False, self.ui.widget, 10)
        Visual_obj.koefCulc(self.FCL_Ref.fcl)
        Visual_obj.coordCulc(rect_obj.x(), rect_obj.y() + rect_obj.height())
        x_0 = Visual_obj.nc.newx
        y_0 = Visual_obj.nc.newy

        Visual_obj.coordCulc(rect_obj.x() + rect_obj.width(),rect_obj.y() + rect_obj.height())
        x_1 = Visual_obj.nc.newx
        y_1 = Visual_obj.nc.newy

        Visual_obj.coordCulc(rect_obj.x(), rect_obj.y())
        x_2 = Visual_obj.nc.newx
        y_2 = Visual_obj.nc.newy

        width = x_1 - x_0
        height = y_2 - y_0

        pen = QPen(qcolor, mt, Qt.SolidLine)
        qp.setPen(pen)
        qp.drawRect(x_0, y_0, width, height)
        if name != '':
            qp.drawText(x_0 + 20,y_0 + 20, name)

    def tooltipData(self): #с реверс координатами№
        dictName = {}
        dictSpace = {}
        dictRect = {}

        for i in range(len(self.FCL_Ref.Site_list)):
            dictName[i] = self.FCL_Ref.area_sitenamelist[i]
            dictSpace[i] = self.FCL_Ref.area_sitespacelist[i]
            dictRect[i] = [self.FCL_Ref.Site_list[i].x(), self.FCL_Ref.Site_list[i].y(),
                           self.FCL_Ref.Site_list[i].width(), self.FCL_Ref.Site_list[i].height()]
        return dictName, dictSpace, dictRect

    def drawPoints(self, qp, qcolor):
        pen = QPen(qcolor, 2)
        qp.setPen(pen)
        Visual_obj = Visual.Visual_Obj(False, self.ui.widget, 10)
        Visual_obj.koefCulc(self.FCL_Ref.fcl)
        for point in self.FCL_Ref.fcl.points_array:
            Visual_obj.coordCulc(point.x(), point.y())
            x = Visual_obj.nc.newx
            y = Visual_obj.nc.newy
            qp.drawPoint(x, y)

    def generate_Qrect_Solution(self, hof):
        x_list = hof[0::3]
        y_list = hof[1::3]
        k_list = hof[2::3]
        QrectList = []
        for i in range(len(k_list)):
            width = round(math.sqrt(self.FCL_Ref.Site_list[i].S) * k_list[i])
            height = self.FCL_Ref.Site_list[i].S / width
            QrectList.append(QtCore.QRect(x_list[i], y_list[i], width, height))
        return QrectList

    def mousePressedEvent(self, e):
        Visual_obj = Visual.Visual_Obj(False, self.ui.widget, 10)
        Visual_obj.koefCulc(self.FCL_Ref.fcl)
        A = 0
        B = self.ui.widget.width()
        C = self.ui.widget.height()
        self.x = e.x()
        self.y = e.y()
        x = int(((self.x - A) / Visual_obj.k.kx + Visual_obj.k.xmin))
        y = int(((self.y - C) / Visual_obj.k.ky + Visual_obj.k.ymin))
        p = self.mapToParent(e.pos())
        for i in range(len(self.FCL_Ref.dictRect)):
            if (x >= self.FCL_Ref.dictRect[i][0] and x < self.FCL_Ref.dictRect[i][0] + self.FCL_Ref.dictRect[i][2]) and\
                    (y >= self.FCL_Ref.dictRect[i][1] and y < self.FCL_Ref.dictRect[i][1] + self.FCL_Ref.dictRect[i][3]):
                QToolTip.showText(p, f'Позиция курсора: {x}: {y} \n' 
                                  f'{self.FCL_Ref.dictName[i]}\n площадь: {self.FCL_Ref.dictSpace[i]} кв.м\n'
                                f'ширина: {self.FCL_Ref.dictRect[i][2]} м \n'
                                f' высота: {self.FCL_Ref.dictRect[i][3]} м')
        del Visual_obj

    def mouseMoveEvent(self, e):
        Visual_obj = Visual.Visual_Obj(False, self.ui.widget, 10)
        Visual_obj.koefCulc(self.FCL_Ref.fcl)
        A = 0
        B = self.ui.widget.width()
        C = self.ui.widget.height()
        self.x = e.x()
        self.y = e.y()
        x = int(((self.x - A) / Visual_obj.k.kx + Visual_obj.k.xmin))
        y = int(((self.y - C) / Visual_obj.k.ky + Visual_obj.k.ymin))
        p = self.mapToParent(e.pos())
        QToolTip.showText(p, f'Позиция курсора: {x}: {y}')
        del Visual_obj




def Sitesquare_data_MPP(Fcl_ref):
    Sitesquare_list = []

    for Site in Fcl_ref.Site_list:
        Sitesquare_list.append([Site.width(), Site.height(), Site.S])
    return Sitesquare_list

def cargo_data_MPP(Fcl_ref):
    return Fcl_ref.cargo_matrix

def fcl_square_MPP(Fcl_ref):
    return (Fcl_ref.fcl.x(), Fcl_ref.fcl.y(),Fcl_ref.fcl.width(), Fcl_ref.fcl.height())

class Genetic_implement_MPP: # пока без проверок Sub_Area
    def __init__(self, cargo_MPP, fcl_square_MPP, Site_square_data_MPP):
    # гиперпараметры алгоритма
        self.P_MUTATION = 0.8  # вероятность мутации
        self.MAX_GENERATIONS = 500  # число поколоений
        self.P_CROSSOVER = 0.9  # вероятность скрещивания
        self.HALL_OF_FAME_SIZE = 2  # число хранимых лучших особей
        self.POPULATION_SIZE = 15  # размер популяции
        self.CROWDING_FACTOR = 10  # коэффициент скученности
        self.TOURNSIZE = 2  # турнирный отбор
        self.kmin = 0.7
        self.kmax = 1.3
        self.toolbox = base.Toolbox()
        self.low = []
        self.up = []

        for i in range(len(Site_square_data_MPP)): # заполнение граничных условий для всех Site
            self.low.extend([fcl_square_MPP[0], fcl_square_MPP[1], self.kmin])
            self.up.extend([fcl_square_MPP[0] + fcl_square_MPP[2], fcl_square_MPP[1] + fcl_square_MPP[3], self.kmax])
    # гиперпараметры алгоритма

        #необходимые постоянные данные ссылочной компоновки
        self.cargo_MPP = cargo_MPP
        self.Site_list_MPP = Site_square_data_MPP
        self.fcl_square_MPP = fcl_square_MPP
        # необходимые постоянные данные ссылочной компоновки

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
        cargo = np.array(self.cargo_MPP).reshape((len(x_list), len(y_list)))
        self.recalculate_WH(k_list)
        fit = (self.calculate_intercept(x_list, y_list),
               self.calculate_CP(cargo, x_list, y_list))

        return fit

    def calculate_CP(self, cargo, x_list, y_list): #здесь определяем мощность грузопотока ВНИМАНИЕ ПРОСЛЕДИТЬ ЧТОБЫ БЫЛО СООТВЕТСТВИЕ
        distance_matrix = np.zeros((len(self.Site_list_MPP),len(self.Site_list_MPP)))
        for i in range(distance_matrix.shape[0]):
            for j in range(0, distance_matrix.shape[0]):
                distance_matrix[i][j] = math.sqrt(((x_list[i] + self.Site_list_MPP[i][0]) - (x_list[j] + self.Site_list_MPP[j][0]))**2 + ((y_list[i] + self.Site_list_MPP[i][1]) - (y_list[j] + self.Site_list_MPP[j][1]))**2)
        return np.sum(np.multiply(cargo, distance_matrix)) / 2

    def check_bounds(self, x_list, y_list): #здесь определяем, что прямоугольники внутри Sub_Area
        error = 0
        for i in range(len(x_list)):
            if (x_list[i] < self.fcl_square_MPP[0]) or (x_list[i] + self.Site_list_MPP[0] > self.fcl_square_MPP[0] + self.fcl_square_MPP[2]):
                error +=1
            if (y_list[i] < (self.fcl_square_MPP[1]) or (y_list[i] + self.Site_list_MPP[1] > self.fcl_square_MPP[1] + self.fcl_square_MPP[3])):
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
                    r_ymax = min(y1_min + self.Site_list_MPP[i][1], y2_min + self.Site_list_MPP[j][1])
                    r_xmax = min(x1_min + self.Site_list_MPP[i][0], x2_min + self.Site_list_MPP[j][0])
                    if (r_ymax >= r_ymin) and (r_xmax >= r_xmin):
                        error += 1
        return error

    def recalculate_WH(self, k_list): #перевычисление ширины и высоты Site
        for i in range(len(k_list)):
            self.Site_list_MPP[i][0] = round(math.sqrt(self.Site_list_MPP[i][2]) * k_list[i])
            self.Site_list_MPP[i][1] = round(self.Site_list_MPP[i][2] / self.Site_list_MPP[i][0])

    # дополнительные методы

    # Переопределение классов
    def Overload_classes(self): # НЕСОВСЕМ ЯСНО МОЖНО ЛИ ПРОСТО БРАТЬ ГРАНИЦЫ ЗДАНИЯ В КАЧЕСТВЕ АРГУМЕНТОВ МУТАЦИИ И СКРЕЩИВАНИЯ
        self.toolbox.register("Fill_k", rnd.uniform, self.kmin, self.kmax)
        self.toolbox.register("Fill_x", rnd.randint, 0, self.fcl_square_MPP[2])
        self.toolbox.register("Fill_y", rnd.randint, 0, self.fcl_square_MPP[3])
        self.toolbox.register("individualCreator", tools.initCycle, creator.Individual, (self.toolbox.Fill_x,
                                                                                            self.toolbox.Fill_y,
                                                                                            self.toolbox.Fill_k),
                                                                                            n=len(self.Site_list_MPP))

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
                                                        indpb=1.0 / (len(self.Site_list_MPP) * 3))

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


def generate_initial():
        individ = course.Individual()
        individ.create_sub_Area()
        individ.excelparser()
        individ.createSites()
        return individ

def main():
    app = QtWidgets.QApplication([])
    application = Mywindow()
    application.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()



