import sys
from PyQt5 import QtWidgets
from PyQt5.QtGui import  QPainter, QColor, QBrush, QPen
from UI_Form import Ui_MainWindow  # импорт нашего сгенерированного файла
from PyQt5.QtCore import Qt, QObject, QEvent
import Visual, course


#os.system(r'C:\\Users\\tarou\\PycharmProjects\\Genetic_Layout\\convert.bat')

class Mywindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(Mywindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.pushButton.clicked.connect(self.slotnnewwindow)
        self.w = None
        self.ui.widget.paintEvent = self.paintEvent
        #self.installEventFilter(self)


    # def paintEvent_1(self, e):
    #
    #     qp = QPainter()
    #     qp.begin(self.ui.widget)
    #     self.drawRectangles(qp)
    #     qp.end()


    def paintEvent(self, e):

        qp = QPainter()
        qp.begin(self.ui.widget)
        self.drawRectangles(qp)
        qp.end()

    def drawRectangles(self, qp):
        Visual_obj = Visual.Visual_Obj(False, self.ui.widget, 10)
        Visual_obj.koefCulc(rog.fcl)
        Visual_obj.coordCulc(0, rog.fcl.height)
        x_0 = Visual_obj.nc.newx
        y_0 = Visual_obj.nc.newy
        Visual_obj.coordCulc(rog.fcl.width, rog.fcl.height)
        x_1 = Visual_obj.nc.newx
        y_1 = Visual_obj.nc.newy
        Visual_obj.coordCulc(0, 0)
        x_2 = Visual_obj.nc.newx
        y_2 = Visual_obj.nc.newy

        width = x_1 - x_0
        height = y_2 -y_0

        pen = QPen(Qt.black, 1, Qt.SolidLine)
        qp.setPen(pen)
        qp.drawRect(x_0 ,y_0, width, height)


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
rog.excelparser()

application = Mywindow()

application.show()


sys.exit(app.exec())
