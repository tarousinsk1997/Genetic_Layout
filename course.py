import random as rnd
import numpy as np
from PyQt5 import QtCore
import xlrd, math, openpyxl
rrmin = 0.5
rrmax = 1.5




class Facility(QtCore.QRectF):
    def __init__(self, x0, y0, width, height, gridW=12, gridH=6):
        super().__init__(x0, y0, width, height)
        self.setX(x0)
        self.setY(y0)
        self.setWidth(width)
        self.setHeight(height)
        self.points_array = []
        self.kx = 0
        self.ky = 0
        self.define_points_array()
        self.grid = [gridW, gridH]
        self.name = 'FCL'

    def define_points_array(self, step=0.5):
        self.points_array = []
        range1 = self.width()
        range2 = self.height()
        stepsW = math.floor(range1 / step)
        stepsH = math.floor(range2 / step)
        for i in range(stepsW):
            for j in range(stepsH):
                self.points_array.append(QtCore.QPointF(i * step, j * step))




class SubArea(QtCore.QRectF):
    def __init__(self, x0, y0, width, height,  name):
        super().__init__(x0, y0, width, height)
        self.name = name
        self.S = width * height


class Site(QtCore.QRectF):
    def __init__(self, S, name, x0, y0, subArea_obj, width=0, height=0):
        super().__init__(x0, y0, width, height)
        self.name = name
        self.S = S
        self.parent = subArea_obj
        self.square_kf = rnd.uniform(rrmin, rrmax)
        self.setWidth(round(math.sqrt(S) * self.square_kf))
        self.setHeight(round(self.S / self.width()))
        self.random_pos_gen()

        self.setWidth(round(math.sqrt(S) * self.square_kf)) #требуется два раза потому что метод на 54 строке меняет предыдущие вызовы на 44, 45
        self.setHeight(round(self.S / self.width()))




    def random_pos_gen(self):
        self.setX(rnd.uniform(self.parent.x(), self.parent.x() + abs(self.parent.width() - self.width() + 1)))
        self.setY(rnd.uniform(self.parent.y(), self.parent.y() + abs(self.parent.height() - self.height() + 1)))


class Individual: #создание всех объектов
    def __init__(self):
        self.fcl = Facility(0, 0, 38, 52)

        self.Sub_Area_list = [] #список объектов подпространств цеха
        self.Site_list = [] #список объектов участков цеха
        self.area_sitenamelist = [] #список значений имен участков цеха
        self.area_sitespacelist = [] #список значений площадей цеха
        self.cargo_matrix = [] #список объектов подпространств цеха
        self.ZipList_area = zip([], []) #zip Площадей и названи
        self.dictName = {}
        self.dictSpace = {}
        self.dictRect = {}



    def excelparser(self, path):  #парсер excel Cargo, Area
        self.cargo = openpyxl.open(path)
        self.Area = openpyxl.open(path)

        self.area_sheet = self.Area['Лист2']  #листы Excel
        self.cargo_sheet = self.cargo['Лист1'] #листы Excel


        for rows in range(1, self.area_sheet.max_row + 1): #заполнение списков названий участкой и площадей участков
            self.area_sitenamelist.append(self.area_sheet.cell(rows, 1).value)
            self.area_sitespacelist.append(self.area_sheet.cell(rows, 2).value)

        self.cargo_matrix = [[0] * (self.cargo_sheet.max_row - 1)  for i in range(self.cargo_sheet.max_row - 1)]


        for rows in range(2, self.cargo_sheet.max_row + 1):
            for colounmns in range(2, self.cargo_sheet.max_row + 1):
                if isinstance(self.cargo_sheet.cell(rows, colounmns).value, int) or isinstance(self.cargo_sheet.cell(rows, colounmns).value, float):
                    self.cargo_matrix[rows - 2][colounmns - 2] = self.cargo_sheet.cell(rows, colounmns).value
                else:
                    self.cargo_matrix[rows - 2][colounmns - 2] = 0


        self.colorgradmatrix = self.setgradmatrix()
        self.ZipList_area = zip(self.area_sitenamelist, self.area_sitespacelist)

    def createSites(self):
        for i in range(0, len(self.area_sitenamelist)):
            self.Site_list.append(Site(self.area_sitespacelist[i],
                                       self.area_sitenamelist[i],
                                       0, 0,
                                       self.fcl))

    def linkSites(self, linklist):
        self.Site_list = []
        for i in range(0, len(self.area_sitenamelist)):
            self.Site_list.append(Site(self.area_sitespacelist[i],
                                       self.area_sitenamelist[i],
                                       0, 0,
                                       linklist[i]))

    def setgradmatrix(self):
        cargo_matrix = np.array(self.cargo_matrix)
        maxelem = cargo_matrix.max()
        gradmatrix = cargo_matrix / maxelem
        gradmatrix.tolist()
        colormatrix = [[0] * (self.cargo_sheet.max_row) for i in range(self.cargo_sheet.max_row)]
        for i in range(len(gradmatrix)):
            for j in range(len(gradmatrix)):
                if i != j:
                    colormatrix[i][j] = LineGradient(gradmatrix[i][j])
        return colormatrix

def LineGradient(ratio):
    if ratio == 0.0:
        return 0
    elif ratio <= 0.5 and ratio > 0.0:
        R = 0
        G = math.floor(2 * 255 * ratio)
        B = math.floor(255 - 2 * 255 * ratio)
    else:
        B = 0
        R = math.floor(255 * (ratio * 2 - 1))
        G = math.floor((1 - ratio) * 2 * 255)
    return (R, G, B)


























