import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QToolTip, QInputDialog
from PyQt5.QtGui import QPainter, QColor, QPen, QFont
from UI_Form import Ui_MainWindow  # импорт нашего сгенерированного файла
from PreProcessWindow import Ui_PreProcessWindow
from PyQt5.QtCore import Qt, QPoint, QRect
import Visual, course, math, time, os, random as rnd

import DEAP_implementation as DI

import  xlwt

# os.system(r'C:\\Users\\tarou\\PycharmProjects\\Genetic_Layout\\convert.bat')


class Mywindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(Mywindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.i = 2
        self.w = None
        self.ui.Execution_GA.clicked.connect(self.execute_ga)
        #self.ui.Execution_GA.clicked.connect(self.execute_with_timer)
        self.ui.StopButton.clicked.connect(self.Stop_ga)
        self.ui.InputData.clicked.connect(self.show_new_window)
        self.counter_label = 0

        self.Pressed = False
        self.Pre_state = True
        self.ui.lineEdit.setText('1')
        #self.ui.Execution_GA.setEnabled(False)
        QToolTip.setFont(QFont('SansSerif', 10))
        self.ui.widget.setMouseTracking(True)

        self.clicked_pos =[]
        self.rect_edit = {}

        self.voidlit = "Пустота"
        self.roadlit = "Дорога"
        self.arealit = "Подпространство"

        self.PreProcessWindow = QtWidgets.QWidget()
        self.ui_1 = Ui_PreProcessWindow()
        self.ui_1.setupUi(self.PreProcessWindow)


        self.ui.widget.installEventFilter(self)

        self.ui_1.tableWidget_3.setMouseTracking(True)
        self.ui_1.tableWidget_3.viewport().setMouseTracking(True)

        self.ui_1.SIte_Table.setMouseTracking(True)
        self.ui_1.SIte_Table.viewport().setMouseTracking(True)

        self.ui_1.tableWidget_3.viewport().setGeometry(QtCore.QRect(460, 20, 361, 331))

        self.ui_1.tableWidget_3.installEventFilter(self)
        self.ui_1.tableWidget_3.viewport().installEventFilter(self)

        self.FCL_Ref = self.generate_initial()



        # self.ui_1.SIte_Table.installEventFilter(self)
        # self.ui_1.SIte_Table.viewport().installEventFilter(self)


    def eventFilter(self, o, e):

        if not self.ui_1.checkBox_spaceedit.isChecked():
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

        else:
            if (o.objectName() == "widget"):
                if e.type() == QtCore.QEvent.Paint:
                    self.paintEvent_editmode(e)
                if (e.type() == QtCore.QEvent.MouseButtonPress):
                    self.Pressed = True
                    self.mousePressedEvent_editmode(e)
                    self.paintEvent_editmode(e)

                if (e.type() == QtCore.QEvent.MouseMove):
                        self.mouseMoveEvent(e)

        return True

    def paintEvent(self, e):
        mt = 2
        qp = QPainter()
        pen = QPen(QColor(0,0,0), 5, Qt.SolidLine)

        qp.begin(self.ui.widget)
        self.drawRectangles(qp, self.FCL_Ref.fcl, pen, QFont("SansSerif", 14))
        self.drawPoints(qp, QColor(128, 128, 128))
        pen = QPen(QColor(0, 0, 0), 2, Qt.SolidLine)

        if not self.Pre_state:
            for qrect, name in zip(self.FCL_Ref.Site_list, self.FCL_Ref.area_sitenamelist):
                self.drawRectangles(qp, qrect, pen, QFont("SansSerif", 10), name=name)

        pen = QPen(QColor(255, 0, 0), 4, Qt.SolidLine)

        if len(self.rect_edit) != 0:
            for i in range(len(self.rect_edit)):
                if len(self.rect_edit) != 0:
                    for i in range(len(self.rect_edit)):
                        if self.rect_edit[f'{i}'][2] == self.roadlit:
                            pen = QPen(QColor(255, 0, 0), mt, Qt.SolidLine)
                        elif self.rect_edit[f'{i}'][2] == self.voidlit:
                            pen = QPen(QColor(0, 255, 0), mt, Qt.SolidLine)
                        elif self.rect_edit[f'{i}'][2] == self.arealit:
                            pen = QPen(QColor(0, 0, 255), mt, Qt.SolidLine)
                        self.drawRectangles(qp, self.rect_edit[f'{i}'][0], pen, QFont("SansSerif", 14), name=self.rect_edit[f'{i}'][1])
        qp.end()
        self.ui.widget.update()

    def paintEvent_editmode(self, e):
        mt = 2 # ТОЛЩИНА ЛИНИИ
        qp = QPainter()
        pen = QPen(QColor(0,0,0), 4, Qt.SolidLine)

        qp.begin(self.ui.widget)

        self.drawRectangles(qp, self.FCL_Ref.fcl,pen, QFont("SansSerif", 14))

        self.drawPoints(qp, QColor(128, 128, 128))

        pen = QPen(QColor(255, 0, 0), mt, Qt.SolidLine)
        if len(self.rect_edit) != 0:
            for i in range(len(self.rect_edit)):
                if self.rect_edit[f'{i}'][2] == self.roadlit:
                    pen = QPen(QColor(255, 0, 0), mt, Qt.SolidLine)
                elif self.rect_edit[f'{i}'][2] == self.voidlit:
                    pen = QPen(QColor(0, 255, 0), mt, Qt.SolidLine)
                elif self.rect_edit[f'{i}'][2] == self.arealit:
                    pen = QPen(QColor(0, 0, 255), mt, Qt.SolidLine)
                self.drawRectangles(qp, self.rect_edit[f'{i}'][0], pen, QFont("SansSerif", 14), name=self.rect_edit[f'{i}'][1])
        qp.end()
        self.ui.widget.update()

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

    def mousePressedEvent_editmode(self, e):
        Visual_obj = Visual.Visual_Obj(False, self.ui.widget, 10)
        Visual_obj.koefCulc(self.FCL_Ref.fcl)
        A = 0
        B = self.ui.widget.width()
        C = self.ui.widget.height()
        self.x = e.x()
        self.y = e.y()
        x = int(((self.x - A) / Visual_obj.k.kx + Visual_obj.k.xmin))
        y = int(((self.y - C) / Visual_obj.k.ky + Visual_obj.k.ymin))
        self.clicked_pos.append((x,y))
        print(self.clicked_pos)
        name = 'None'
        if len(self.clicked_pos) == 2:
            if self.ui_1.radioRoad.isChecked():
               name = QInputDialog.getText(self.ui.widget, "", "Название дороги")
            elif self.ui_1.radioVoid.isChecked():
                name = QInputDialog.getText(self.ui.widget, "", "Название зоны пустоты")
            elif self.ui_1.radioSubArea.isChecked():
                name = QInputDialog.getText(self.ui.widget, "", "Название подпространства")

            name = name[0]

            lenofdict = len(self.rect_edit)

            if self.ui_1.radioRoad.isChecked():
                self.rect_edit[f'{lenofdict}'] = [QRect(QPoint(self.clicked_pos[0][0], self.clicked_pos[0][1]), QPoint(self.clicked_pos[1][0], self.clicked_pos[1][1])), name, self.roadlit]
                print(self.rect_edit[f'{lenofdict}'])
            elif self.ui_1.radioVoid.isChecked():
                self.rect_edit[f'{lenofdict}'] = [QRect(QPoint(self.clicked_pos[0][0], self.clicked_pos[0][1]),
                                                   QPoint(self.clicked_pos[1][0], self.clicked_pos[1][1])), name,
                                             self.voidlit]
                print(self.rect_edit[f'{lenofdict}'])
            elif self.ui_1.radioSubArea.isChecked():
                self.rect_edit[f'{lenofdict}'] = [QRect(QPoint(self.clicked_pos[0][0], self.clicked_pos[0][1]),
                                                   QPoint(self.clicked_pos[1][0], self.clicked_pos[1][1])), name,
                                             self.arealit]
                print(self.rect_edit[f'{lenofdict}'])

            self.clicked_pos = []
            self.ui_1.rect_edit = self.rect_edit

        #Добавление данных в table3 второго окна
        self.ui_1.pastAreaTable(widget=self.ui_1.Areas_Table, info=self.rect_edit, cols= 3, rows=len(self.rect_edit))

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

    def show_new_window(self, checked):
        self.PreProcessWindow.show()

    def Stop_ga(self):
        self.GA.Stop = True

    def execute_ga(self):
        self.ui_1.checkBox_spaceedit.setChecked(False)
        self.Pre_state = False
        self.FCL_Ref = self.generate_initial()
        if  self.ui.TestCheckBox.isChecked() == False:
            rnd.seed(None)
            if len(self.ui_1.linklist) != 0:
                self.FCL_Ref.linkSites(self.ui_1.linklist)
        else:
            rnd.seed(42)
        self.GA = DI.Genetic_implement(self.FCL_Ref)
        self.GA.Overload_classes()
        self.GA.rect_info = self.rect_edit
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
            self.FCL_Ref = self.generate_initial()
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

    def drawRectangles(self, qp, rect_obj, pen, textfont, name=''):

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
        qp.setPen(pen)
        qp.setFont(textfont)
        qp.drawRect(x_0, y_0, width, height)
        if name != '':
            qp.drawText(x_0 + 20, y_0 + 20, name)

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

    def generate_initial(self):
        individ = course.Individual()
        individ.excelparser(os.path.dirname(__file__) + r'\Cargo_test.xls')
        individ.createSites()
        return individ






def main():
    app = QtWidgets.QApplication([])
    application = Mywindow()
    application.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()



