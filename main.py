import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QToolTip, QInputDialog
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QImage, QIntValidator
from UI_Form import Ui_MainWindow  # импорт нашего сгенерированного файла
from PreProcessWindow import Ui_PreProcessWindow
from PyQt5.QtCore import Qt, QPointF, QRectF
import Visual, course, math, os
import random as rnd
from matplotlib import pyplot as plt

import DEAP_implementation as DI
import numpy as np


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
        self.ui.ResetBtn.clicked.connect(self.Stop_ga)
        self.ui.StopButton.clicked.connect(self.Pause_ga)
        self.ui.InputData.clicked.connect(self.show_new_window)
        self.ui.SetSizes.clicked.connect(self.SetFCLSizes)
        self.ui.cargo_display_btn.clicked.connect(self.cargodisplay_mtd)
        self.ui.CorrectionCheckBox.clicked.connect(self.setcorrectionstate)


        self.counter_label = 0

        self.Passedchecks = False
        self.Pressed = False # При инициализации False
        self.Pre_state = True
        self.cargo_display = False #включение отображения грузопотоков



        #self.PassedChecks = False

        self.ui.fcl_width_input.setValidator(QIntValidator(0, 10000))
        self.ui.fcl_width_input.setText('48')
        self.ui.fcl_height_input.setValidator(QIntValidator(0, 10000))
        self.ui.fcl_height_input.setText('32')
        self.ui.GridW_input.setValidator(QIntValidator(0, 10000))
        self.ui.GridH_input.setValidator(QIntValidator(0, 10000))

        #self.ui.Execution_GA.setEnabled(False)
        QToolTip.setFont(QFont('SansSerif', 10))

        self.ui.widget.setMouseTracking(True)

        self.temppoint = QPointF(0, 0)
        self.point2list = []
        self.rect_edit = {}
        self.DrawRectsList = []
        self.searchrects = []

        self.correction_obj = None
        self.correction_mouse_pos = []
        self.correction_chosen_rect = None
        self.correction_Pressed = False
        self.correction_state = False
        self.corrected_ind = None


        self.poslist = [] # Позиции HOF0 для отрисовки линий грузопотоков


        #self.Image = QImage(self.ui.widget.width(), self.ui.widget.height(), QImage.Format_ARGB32)

        self.voidlit = "Пустота"
        self.roadlit = "Дорога"
        self.arealit = "Подпространство"

        self.PreProcessWindow = QtWidgets.QWidget()
        self.ui_1 = Ui_PreProcessWindow()
        self.ui_1.setupUi(self.PreProcessWindow)
        self.FCL_Ref = self.generate_initial()
        self.GA = DI.Genetic_implement
        self.SetFCLSizes()
        self.ui_1.FCL_rect = self.FCL_Ref.fcl

        self.ui.widget.installEventFilter(self)

        self.ui_1.tableWidget_3.setMouseTracking(True)
        self.ui_1.tableWidget_3.viewport().setMouseTracking(True)

        self.ui_1.SIte_Table.setMouseTracking(True)
        self.ui_1.SIte_Table.viewport().setMouseTracking(True)

        self.ui_1.tableWidget_3.viewport().setGeometry(QtCore.QRect(460, 20, 361, 331))

        self.ui_1.tableWidget_3.installEventFilter(self)
        self.ui_1.tableWidget_3.viewport().installEventFilter(self)

        self.ui.CorrectionCheckBox.setEnabled(False)
        self.ui_1.checkBox_spaceedit.clicked.connect(self.disableCorrectionwhilespaceedit)


    def disableCorrectionwhilespaceedit(self):
        if self.ui_1.checkBox_spaceedit.isChecked():
            self.ui.CorrectionCheckBox.setEnabled(False)
        else:
            self.ui.CorrectionCheckBox.setEnabled(True)

    def saveImage(self):
        self.searchrects = []
        Image = QImage(self.ui.widget.width(), self.ui.widget.height(), QImage.Format_ARGB32)
        Image.fill(Qt.white)
        qp = QPainter(Image)
        pen = QPen(QColor(0,0,0), 5, Qt.SolidLine)
        self.FCL_Ref.fcl.define_points_array()
        self.drawPoints(qp, QColor(128, 128, 128))

        self.drawRectangles(qp, self.FCL_Ref.fcl, pen, QFont("SansSerif", 14))
        pen = QPen(QColor(255, 153, 51), 2, Qt.DashDotDotLine)
        qp.setPen(pen)

        stepsW = math.ceil(self.FCL_Ref.fcl.width() / self.FCL_Ref.fcl.grid[0])
        stepsH = math.ceil(self.FCL_Ref.fcl.height() / self.FCL_Ref.fcl.grid[1])

        Visual_obj = Visual.Visual_Obj(False, self.ui.widget, 10)
        Visual_obj.koefCulc(self.FCL_Ref.fcl)

        #оси
        for i in range(stepsW):
            Visual_obj.coordCulc(i * self.FCL_Ref.fcl.grid[0], 0)
            x = Visual_obj.nc.newx
            y = Visual_obj.nc.newy
            Visual_obj.coordCulc(i * self.FCL_Ref.fcl.grid[0], self.FCL_Ref.fcl.height())
            x1 = Visual_obj.nc.newx
            y1 = Visual_obj.nc.newy
            qp.drawLine(QPointF(x,y), QPointF(x1,y1))

        for i in range(stepsH ) :
            Visual_obj.coordCulc(0, i * self.FCL_Ref.fcl.grid[1])
            x = Visual_obj.nc.newx
            y = Visual_obj.nc.newy
            Visual_obj.coordCulc(self.FCL_Ref.fcl.width(), i * self.FCL_Ref.fcl.grid[1])
            x1 = Visual_obj.nc.newx
            y1 = Visual_obj.nc.newy
            qp.drawLine(QPointF(x,y), QPointF(x1,y1))
        # оси
        pen = QPen(QColor(255, 0, 0), 1, Qt.SolidLine)
        qp.setPen(pen)

        # if hasattr(self.GA, 'searchrectsside'):
        #     self.searchrects.append(QRectF(self.FCL_Ref.fcl.width() / 2,self.FCL_Ref.fcl.height() / 2,self.GA.searchrectsside,self.GA.searchrectsside))
        #     self.searchrects.append(QRectF(self.FCL_Ref.fcl.width() / 2 - self.GA.searchrectsside, self.FCL_Ref.fcl.height() / 2, self.GA.searchrectsside,
        #                            self.GA.searchrectsside))
        #     self.searchrects.append(QRectF(self.FCL_Ref.fcl.width() / 2, self.FCL_Ref.fcl.height() / 2 - self.GA.searchrectsside, self.GA.searchrectsside,
        #                            self.GA.searchrectsside))
        #     self.searchrects.append(QRectF(self.FCL_Ref.fcl.width() / 2 - self.GA.searchrectsside, self.FCL_Ref.fcl.height() / 2 - self.GA.searchrectsside, self.GA.searchrectsside,
        #                            self.GA.searchrectsside))
        #     self.GA.searchrects  = self.searchrects
        #
        #     for rect in self.searchrects:
        #         Visual_obj.coordCulc(rect.x(), rect.y() + rect.height())
        #         x_0 = Visual_obj.nc.newx
        #         y_0 = Visual_obj.nc.newy
        #
        #         Visual_obj.coordCulc(rect.x() + rect.width(), rect.y() + rect.height())
        #         x_1 = Visual_obj.nc.newx
        #         y_1 = Visual_obj.nc.newy
        #
        #         Visual_obj.coordCulc(rect.x(), rect.y())
        #         x_2 = Visual_obj.nc.newx
        #         y_2 = Visual_obj.nc.newy
        #
        #         width = x_1 - x_0
        #         height = y_2 - y_0
        #         qp.setPen(pen)
        #         qp.drawRect(x_0, y_0, width, height)
        Image.save(os.path.dirname(__file__) + '\BackgroundImage.png', "PNG", quality=100)
        self.Image = Image


    def eventFilter(self, o, e):

        if not self.ui_1.checkBox_spaceedit.isChecked():
            if (o.objectName() == "widget"):
                if e.type() == QtCore.QEvent.Paint:
                    self.paintEvent(e)
                if (e.type() == QtCore.QEvent.MouseButtonPress):
                    if not self.ui.CorrectionCheckBox.isChecked():
                        self.Pressed = True
                        self.mousePressedEvent(e)
                    else:
                        self.mousePressedEvent_correction(e)


                if (e.type() == QtCore.QEvent.MouseButtonRelease):
                    self.Pressed = False

                # В работе
                if (e.type() == QtCore.QEvent.MouseMove):

                    if not self.Pressed and not self.ui.CorrectionCheckBox.isChecked():
                        self.mouseMoveEvent(e)
                    else:
                        self.mouseMoveEvent_correction(e)

                if (e.type() == QtCore.QEvent.MouseButtonRelease):
                    self.mouseReleaseEvent_correction()



        else:
            if (o.objectName() == "widget"):
                if e.type() == QtCore.QEvent.Paint:
                    self.paintEvent_editmode(e)
                if (e.type() == QtCore.QEvent.MouseButtonPress):
                    self.Pressed = True
                    self.mousePressedEvent_editmode(e)
                    self.paintEvent_editmode(e)

                if (e.type() == QtCore.QEvent.MouseMove):
                    self.mouseMoveEvent_editmode(e)
                    self.paintEvent_editmode(e)
        return True

    def paintEvent(self, e):
        mt = 2
        qp = QPainter(self.ui.widget)
        pen = QPen(QColor(0,0,0), 5, Qt.SolidLine)

        qp.drawImage(self.ui.widget.rect(), self.Image)
        #self.drawPoints(qp, QColor(128, 128, 128))
        pen = QPen(QColor(0, 0, 0), 2, Qt.SolidLine)


        if self.ui.CorrectionCheckBox.isChecked() and self.correction_obj is not None:
            for qrect, name in zip(self.generate_Qrect_Solution(self.correction_obj), self.FCL_Ref.area_sitenamelist):
                self.drawRectangles(qp, qrect, pen, QFont("SansSerif", 10), name=name)
        else:
            if not self.Pre_state:
                for qrect, name in zip(self.generate_Qrect_Solution(self.GA.hof[0]), self.FCL_Ref.area_sitenamelist):
                    self.drawRectangles(qp, qrect, pen, QFont("SansSerif", 10), name=name)

        Visual_obj = Visual.Visual_Obj(False, self.ui.widget, 10)
        Visual_obj.koefCulc(self.FCL_Ref.fcl)

        if self.cargo_display:
            for i in range(len(self.poslist)):
                for j in range(len(self.poslist)):
                    if i != j:
                        if type(self.FCL_Ref.colorgradmatrix[i][j]) is not int:
                            R = self.FCL_Ref.colorgradmatrix[i][j][0]
                            G = self.FCL_Ref.colorgradmatrix[i][j][1]
                            B = self.FCL_Ref.colorgradmatrix[i][j][2]
                            qp.setPen(QPen(QColor(R, G, B), 2, Qt.SolidLine))

                            Visual_obj.coordCulc(self.poslist[i].x(), self.poslist[i].y())
                            x0 = Visual_obj.nc.newx
                            y0 = Visual_obj.nc.newy
                            Visual_obj.coordCulc(self.poslist[j].x(), self.poslist[j].y())
                            x1 = Visual_obj.nc.newx
                            y1 = Visual_obj.nc.newy
                            qp.drawLine(QPointF(x0, y0), QPointF(x1, y1))



            self.ui.widget.update()


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


        if self.GA is not None:
            if hasattr(self.GA, 'hof'):
                self.drawMC(qp)


        self.ui.widget.update()

    def paintEvent_editmode(self, e):
        mt = 2 # ТОЛЩИНА ЛИНИИ
        qp = QPainter()
        pen = QPen(QColor(0,0,0), mt, Qt.SolidLine)

        qp.begin(self.ui.widget)
        qp.drawImage(self.ui.widget.rect(), self.Image)
        self.drawRectangles(qp, self.FCL_Ref.fcl,pen, QFont("SansSerif", 14))
        if len(self.point2list) == 1:
            self.drawRectangles(qp, QRectF(QPointF(self.x, self.y), QPointF(self.point2list[0].x(), self.point2list[0].y())), pen, QFont("SansSerif", 14))

        #self.drawPoints(qp, QColor(128, 128, 128))
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
        x = ((self.x - A) / Visual_obj.k.kx + Visual_obj.k.xmin)
        y = ((self.y - C) / Visual_obj.k.ky + Visual_obj.k.ymin)
        p = self.mapToParent(e.pos())
        for i in range(len(self.FCL_Ref.dictRect)):
            if (x >= self.FCL_Ref.dictRect[i][0] and x < self.FCL_Ref.dictRect[i][0] + self.FCL_Ref.dictRect[i][2]) and\
                    (y >= self.FCL_Ref.dictRect[i][1] and y < self.FCL_Ref.dictRect[i][1] + self.FCL_Ref.dictRect[i][3]):
                QToolTip.showText(p, f'Позиция курсора: {round(x,2)}: {round(y,2)} \n' 
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
        x = ((self.x - A) / Visual_obj.k.kx + Visual_obj.k.xmin)
        y = ((self.y - C) / Visual_obj.k.ky + Visual_obj.k.ymin)
        self.point2list.append(QPointF(x, y))

        name = 'None'
        if len(self.point2list) == 2:
            if self.ui_1.radioRoad.isChecked():
               name = QInputDialog.getText(self.ui.widget, "", "Название дороги")
            elif self.ui_1.radioVoid.isChecked():
                name = QInputDialog.getText(self.ui.widget, "", "Название зоны пустоты")
            elif self.ui_1.radioSubArea.isChecked():
                name = QInputDialog.getText(self.ui.widget, "", "Название подпространства")

            name = name[0]
            lenofdict = len(self.rect_edit)
            if self.ui_1.radioRoad.isChecked():
                point1 = self.point2list[0]
                point2 = self.point2list[1]
                x,y,w,h = change_coord(point1.x(), point1.y(), point2.x()- point1.x(), point2.y() - point1.y())
                self.rect_edit[f'{lenofdict}'] = [QRectF(x,y,w,h), name, self.roadlit]
                print(self.rect_edit[f'{lenofdict}'])
            elif self.ui_1.radioVoid.isChecked():
                point1 = self.point2list[0]
                point2 = self.point2list[1]
                x, y, w, h = change_coord(point1.x(), point1.y(), point2.x() - point1.x(), point2.y() - point1.y())
                self.rect_edit[f'{lenofdict}'] = [QRectF(x,y,w,h), name,
                                                  self.voidlit]
                print(self.rect_edit[f'{lenofdict}'])
            elif self.ui_1.radioSubArea.isChecked():
                point1 = self.point2list[0]
                point2 = self.point2list[1]
                x, y, w, h = change_coord(point1.x(), point1.y(), point2.x() - point1.x(), point2.y() - point1.y())
                self.rect_edit[f'{lenofdict}'] = [QRectF(x,y,w,h), name,
                                                  self.arealit]
                print(self.rect_edit[f'{lenofdict}'])

            self.ui_1.rect_edit = self.rect_edit

        #Добавление данных в table3 второго окна
        self.ui_1.pastAreaTable(widget=self.ui_1.Areas_Table, info=self.rect_edit, cols= 3, rows=len(self.rect_edit))
        if len(self.point2list) == 2:
            self.point2list = []

    def mouseMoveEvent(self, e):
        Visual_obj = Visual.Visual_Obj(False, self.ui.widget, 10)
        Visual_obj.koefCulc(self.FCL_Ref.fcl)
        A = 0
        B = self.ui.widget.width()
        C = self.ui.widget.height()
        self.x = e.x()
        self.y = e.y()
        x = ((self.x - A) / Visual_obj.k.kx + Visual_obj.k.xmin)
        y = ((self.y - C) / Visual_obj.k.ky + Visual_obj.k.ymin)
        p = self.mapToParent(e.pos())
        QToolTip.showText(p, f'Позиция курсора: {math.ceil(x)}: {math.ceil(y)}')
        del Visual_obj

    def mouseMoveEvent_editmode(self,e):
        Visual_obj = Visual.Visual_Obj(False, self.ui.widget, 10)
        Visual_obj.koefCulc(self.FCL_Ref.fcl)
        square = 0
        A = 0
        B = self.ui.widget.width()
        C = self.ui.widget.height()
        self.x = e.x()
        self.y = e.y()
        self.x = ((self.x - A) / Visual_obj.k.kx + Visual_obj.k.xmin)
        self.y = ((self.y - C) / Visual_obj.k.ky + Visual_obj.k.ymin)

        p = self.mapToParent(e.pos())

        if len(self.point2list) == 1:
            tp2 = self.point2list[0]
            square =abs(self.x - tp2.x()) * abs(self.y - tp2.y())
            QToolTip.showText(p, f'Позиция курсора: {self.x}: {self.y}\n Площадь: {round(square, 2)}')
        else:
            QToolTip.showText(p, f'Позиция курсора: {math.floor(self.x) if math.ceil(self.x) - self.x >0.5 else math.ceil(self.x)}: {math.floor(self.y) if math.ceil(self.y) - self.x >0.5 else math.ceil(self.y)}')
        del Visual_obj

    def mouseMoveEvent_correction(self, e):

        Visual_obj = Visual.Visual_Obj(False, self.ui.widget, 10)
        Visual_obj.koefCulc(self.FCL_Ref.fcl)
        A = 0
        B = self.ui.widget.width()
        C = self.ui.widget.height()


        mouseposx = ((e.x() - A) / Visual_obj.k.kx + Visual_obj.k.xmin)
        mouseposy = ((e.y() - C) / Visual_obj.k.ky + Visual_obj.k.ymin)


        if self.correction_Pressed and self.correction_chosen_rect is not None:
            xlist = self.correction_obj[0::3]
            ylist = self.correction_obj[1::3]
            klist = self.correction_obj[2::3]
            xlist[self.correction_chosen_rect] = mouseposx - self.FCL_Ref.Site_list[self.correction_chosen_rect].width()
            ylist[self.correction_chosen_rect] = mouseposy - self.FCL_Ref.Site_list[self.correction_chosen_rect].height()
            self.correction_obj = []


            for i in range(len(xlist)):
                self.correction_obj.append(xlist[i])
                self.correction_obj.append(ylist[i])
                self.correction_obj.append(klist[i])
            self.corrected_ind = self.correction_obj


    def mousePressedEvent_correction(self,e):
        self.correction_Pressed = True
        Visual_obj = Visual.Visual_Obj(False, self.ui.widget, 10)
        Visual_obj.koefCulc(self.FCL_Ref.fcl)
        A = 0
        B = self.ui.widget.width()
        C = self.ui.widget.height()

        x_list = self.correction_obj[0::3]
        y_list = self.correction_obj[1::3]

        x = ((e.x() - A) / Visual_obj.k.kx + Visual_obj.k.xmin)
        y = ((e.y() - C) / Visual_obj.k.ky + Visual_obj.k.ymin)



        for i in range(len(x_list)):
            if x > x_list[i] and x < x_list[i] + self.FCL_Ref.Site_list[i].width() and y > y_list[i] and y < y_list[i] + self.FCL_Ref.Site_list[i].height():
                self.correction_chosen_rect = i
        print(self.correction_chosen_rect)

        del Visual_obj

    def mouseReleaseEvent_correction(self):
        self.correction_Pressed = False
        # self.GA.recalculate_WH(self.correction_obj[2::3])



    def show_new_window(self, checked):
        self.PreProcessWindow.show()

    def Stop_ga(self):

        self.GA.Stop = True
        self.Pre_state = True
        self.ui.CorrectionCheckBox.setChecked(False)
        self.ui.CorrectionCheckBox.setEnabled(False)
        self.ui.Execution_GA.setEnabled(True)
        self.GA = None
        self.corrected_ind = None


    def Pause_ga(self):
        if self.GA is not None:
            self.GA.Stop = True
        self.ui_1.checkBox_spaceedit.setChecked(False)
        if not self.Pre_state:
            self.ui.CorrectionCheckBox.setEnabled(True)




    def execute_ga(self):
        self.ui.CorrectionCheckBox.setEnabled(False)
        self.ui_1.checkBox_spaceedit.setChecked(False)

        self.FCL_Ref = self.generate_initial()
        self.SetFCLSizes()

        if len(self.ui_1.linklist) != 0:
            self.FCL_Ref.linkSites(self.ui_1.linklist)

        self.GA = DI.Genetic_implement(self.FCL_Ref)
        self.GA.Overload_classes()
        if self.corrected_ind is not None:
            self.GA.corrected_ind = self.corrected_ind # добавление в GA коррекции

        self.GA.rect_info = self.rect_edit

        self.Pre_state = False

        self.GA.Main_autoga()

        QRectSolution = self.generate_Qrect_Solution(self.GA.hof[0])

        #self.FCL_Ref.Site_list = QRectSolution
        self.FCL_Ref.dictName, self.FCL_Ref.dictSpace, self.FCL_Ref.dictRect = self.tooltipData()

        self.ui.widget.update()
        self.GA.draw(self.GA.cargo_draw)


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

    def cargodisplay_mtd(self):
        if self.cargo_display:
            self.cargo_display = not self.cargo_display
        else: self.cargo_display = not self.cargo_display

    def setcorrectionstate(self, correctionTrue):
        if correctionTrue:
            self.correction_state = correctionTrue
            self.ui.Execution_GA.setEnabled(False)
            self.correction_obj = self.GA.hof[0]
        else:
            self.ui.Execution_GA.setEnabled(True)




    def generate_Qrect_Solution(self, hof):

        x_list = hof[0::3]
        y_list = hof[1::3]
        xc_list = hof[0::3]
        yc_list = hof[1::3]
        k_list = hof[2::3]
        self.GA.recalculate_WH(k_list)

        for i in range(len(x_list)):
            xc_list[i] = x_list[i] + self.FCL_Ref.Site_list[i].width() / 2
            yc_list[i] = y_list[i] + self.FCL_Ref.Site_list[i].height() / 2
        def getpoint(x,y):
            return QPointF(x,y)
        self.poslist = list(map(getpoint, xc_list, yc_list))

        QrectList = []


        for i in range(len(k_list)):
            width = math.sqrt(self.FCL_Ref.Site_list[i].S) * k_list[i]
            height = self.FCL_Ref.Site_list[i].S / width
            QrectList.append(QtCore.QRect(x_list[i], y_list[i], width, height))
        return QrectList

    def generate_initial(self):
        individ = course.Individual()
        individ.excelparser(os.path.dirname(__file__) + r'\Cargo_test.xls')
        individ.setgradmatrix()
        individ.createSites()
        return individ

    def Draw_stats(self, time, fitness, iterlist):
        fig, ax1 = plt.subplots()
        line1 = ax1.plot(np.array(iterlist), np.array(time), "o-", label="Время сходимости", color='b')
        ax1.set_xlabel("Прогон алгоритма")
        ax1.set_ylabel("Время выполнения прогона, c", color="b")
        ax1.xaxis.get_major_locator().set_params(integer=True)
        ax1.grid(axis='both', color='k', linestyle='-', linewidth=1)
        for tl in ax1.get_yticklabels():
            tl.set_color("b")
        ax2 = ax1.twinx()
        line2 = ax2.plot(np.array(iterlist), np.array(fitness), "o-", label="Суммарный грузопоток", color='r')
        ax2.set_ylabel("Суммарный грузопоток", color="r")
        ax2.set_yticks(np.linspace(ax2.get_yticks()[0], ax2.get_yticks()[-1], len(ax1.get_yticks())))
        for tl in ax2.get_yticklabels():
            tl.set_color("r")

        lns = line1 + line2
        labs = [l.get_label() for l in lns]
        plt.show()

    def drawMC(self, qp):
        xhof0, yhof0 = 0, 0
        pen = QPen(QColor(255, 0, 0), 4, Qt.SolidLine)
        qp.setPen(pen)
        for i in range(len(self.GA.Rect_ind.Site_list)):
            xhof0 += self.GA.hof[0][0::3][i] + self.GA.Rect_ind.Site_list[i].width()
            yhof0 += self.GA.hof[0][1::3][i] + self.GA.Rect_ind.Site_list[i].height()
        self.masspoint_hof = QPointF(xhof0 / len(self.GA.Rect_ind.Site_list), yhof0 / len(self.GA.Rect_ind.Site_list))

        Visual_obj = Visual.Visual_Obj(False, self.ui.widget, 10)
        Visual_obj.koefCulc(self.FCL_Ref.fcl)
        Visual_obj.coordCulc(self.masspoint_hof.x(), self.masspoint_hof.y())
        x = Visual_obj.nc.newx
        y = Visual_obj.nc.newy

        qp.drawEllipse(QPointF(x, y), 3, 3)

    def SetFCLSizes(self):
        if self.ui.fcl_width_input.text() == '' or self.ui.fcl_height_input.text() == '' or self.ui.fcl_height_input.text() == '' or self.ui.fcl_height_input.text() == '':
            self.FCL_Ref.fcl.grid[0] = 18
            self.FCL_Ref.fcl.grid[1] = 12
            self.FCL_Ref.fcl.setWidth(50)
            self.FCL_Ref.fcl.setHeight(50)
        else:
            self.FCL_Ref.fcl.grid[0] = int(self.ui.GridW_input.text())
            self.FCL_Ref.fcl.grid[1] = int(self.ui.GridH_input.text())
            self.FCL_Ref.fcl.setWidth(int(self.ui.fcl_width_input.text()))
            self.FCL_Ref.fcl.setHeight(int(self.ui.fcl_height_input.text()))
        self.saveImage()

        self.ui.widget.update()


def change_coord(x1, y1, w1, h1):
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
    return x, y, w, h


def main():
    app = QtWidgets.QApplication([])
    application = Mywindow()
    screenresolution = app.desktop().screenGeometry()
    if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    application.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()



