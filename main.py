import sys, random as rnd
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen
from UI_Form import Ui_MainWindow  # импорт нашего сгенерированного файла
from PyQt5.QtCore import Qt, QObject, QEvent
import Visual, course

# os.system(r'C:\\Users\\tarou\\PycharmProjects\\Genetic_Layout\\convert.bat')

class Mywindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(Mywindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

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
        self.drawRectangles(qp, rog.fcl, QColor(0, 0, 0), 5)
        self.drawRectangles(qp, rog.SubArea_1, QColor(0, 0, 0), 2)
        self.drawRectangles(qp, rog.SubArea_2, QColor(0, 0, 0), 2)
        self.drawRectangles(qp, rog.Site_list[0], QColor(0, 0, 255), 1)
        self.drawRectangles(qp, rog.Site_list[1], QColor(0, 0, 255), 1)
        self.drawRectangles(qp, rog.Site_list[2], QColor(0, 0, 255), 1)
        self.drawRectangles(qp, rog.Site_list[3], QColor(0, 0, 255), 1)
        self.drawPoints(qp, QColor(128, 128, 128))
        qp.end()

    def drawRectangles(self, qp, rect_obj, qcolor, mt):
        Visual_obj = Visual.Visual_Obj(False, self.ui.widget, 10)
        Visual_obj.koefCulc(rog.fcl)
        Visual_obj.coordCulc(rect_obj.x0,rect_obj.y0+ rect_obj.height)
        x_0 = Visual_obj.nc.newx
        y_0 = Visual_obj.nc.newy

        Visual_obj.coordCulc(rect_obj.x0 + rect_obj.width,rect_obj.y0 + rect_obj.height)
        x_1 = Visual_obj.nc.newx
        y_1 = Visual_obj.nc.newy

        Visual_obj.coordCulc(rect_obj.x0, rect_obj.y0)
        x_2 = Visual_obj.nc.newx
        y_2 = Visual_obj.nc.newy

        width = x_1 - x_0
        height = y_2 - y_0

        pen = QPen(qcolor, mt, Qt.SolidLine)
        qp.setPen(pen)
        qp.drawRect(x_0, y_0, width, height)


    def drawPoints(self, qp, qcolor):
        pen = QPen(qcolor, 2)
        qp.setPen(pen)
        Visual_obj = Visual.Visual_Obj(False, self.ui.widget, 10)
        Visual_obj.koefCulc(rog.fcl)


        for point in rog.fcl.points_array:
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


app = QtWidgets.QApplication([])
rog = course.Random_object_generator()
rog.create_sub_Area()
rog.excelparser()



application = Mywindow()

application.show()

sys.exit(app.exec())
