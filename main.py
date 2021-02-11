import sys, random as rnd
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen
from UI_Form import Ui_MainWindow  # импорт нашего сгенерированного файла
from PyQt5.QtCore import Qt, QObject, QEvent
import Visual, course
import time
import multiprocessing
import math
import DEAP_implementation as DI

# os.system(r'C:\\Users\\tarou\\PycharmProjects\\Genetic_Layout\\convert.bat')


class Mywindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(Mywindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.i = 2
        self.ui.pushButton.clicked.connect(self.slotnnewwindow)
        self.w = None
        self.ui.widget.paintEvent = self.paintEvent
        # self.installEventFilter(self)

    # def paintEvent_1(self, e):
    #
    #     qp = QPainter()
    #     qp.begin(self.ui.widget)
    #     self.drawRectangles(qp)
    #     qp.end()


    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self.ui.widget)
        self.drawRectangles(qp, FCL_Ref.fcl, QColor(0, 0, 0), 5)
        #self.drawRectangles(qp, FCL_Ref.SubArea_1, QColor(0, 0, 0), 2)
        #self.drawRectangles(qp, FCL_Ref.SubArea_2, QColor(0, 0, 0), 2)
        for qrect, name  in zip(FCL_Ref.Site_list, FCL_Ref.area_sitenamelist):
            self.drawRectangles(qp, qrect, QColor(rnd.randint(0,255),rnd.randint(0,255),rnd.randint(0,255)), 2, name=name)
        self.drawPoints(qp, QColor(128, 128, 128))
        qp.end()

    def drawRectangles(self, qp, rect_obj, qcolor, mt, name=''):
        Visual_obj = Visual.Visual_Obj(False, self.ui.widget, 10)
        Visual_obj.koefCulc(FCL_Ref.fcl)
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


    def drawPoints(self, qp, qcolor):
        pen = QPen(qcolor, 2)
        qp.setPen(pen)
        Visual_obj = Visual.Visual_Obj(False, self.ui.widget, 10)
        Visual_obj.koefCulc(FCL_Ref.fcl)
        for point in FCL_Ref.fcl.points_array:
            Visual_obj.coordCulc(point.x(), point.y())
            x = Visual_obj.nc.newx
            y = Visual_obj.nc.newy
            qp.drawPoint(x, y)


    # def eventFilter(self, obj, event):
    #     if event.type() == QEvent.Paint:
    #         self.ui.widget.paintEvent = self.paintEvent_1
    #         return True
    #     return False

    def slotnnewwindow(self):
        if self.w is None:
            self.w = SecondWindow()
        self.w.show()


class SecondWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

def generate_initial():
        individ = course.Individual()
        individ.create_sub_Area()
        individ.excelparser()
        individ.createSites()
        return individ

def generate_Qrect_Solution(hof):
    x_list = hof[0::3]
    y_list = hof[1::3]
    k_list = hof[2::3]
    QrectList = []

    for i in range(len(k_list)):
        width = round(math.sqrt(FCL_Ref.Site_list[i].S) * k_list[i])
        height = FCL_Ref.Site_list[i].S/width
        QrectList.append(QtCore.QRect(x_list[i], y_list[i], width, height))
    return QrectList



if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    FCL_Ref = generate_initial()
    GA = DI.Genetic_implement(FCL_Ref)
    GA.Overload_classes()
    pool = multiprocessing.Pool()
    GA.toolbox.register("map", pool.map)
    start_time = time.time()
    GA.Main_autoga()
    pool.close()

    print("--- %s seconds ---" % (time.time() - start_time))
    print(GA.hof[0].fitness.values)
    QRectSolution = generate_Qrect_Solution(GA.hof[0])
    FCL_Ref.Site_list = QRectSolution

    application = Mywindow()
    application.show()
    sys.exit(app.exec())


