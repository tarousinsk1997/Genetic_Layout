import random as rnd
from PyQt5 import QtCore
from bitstring import BitStream, BitArray
import xlrd, math
rrmin = 0.5
rrmax = 1.5




class Facility(QtCore.QRect):
    def __init__(self, x0, y0, width, height):
        super().__init__(x0, y0, width, height)
        self.setX(x0)
        self.setY(y0)
        self.setWidth(width)
        self.setHeight(height)
        self.points_array = []
        self.kx = 0
        self.ky = 0
        self.define_points_array()

    def define_points_array(self):
        for i in range(self.x(), self.width() + 1):
            for j in range(self.y(), self.height() + 1):
                self.points_array.append(QtCore.QPoint(i, j))
    SubAreaList = list()


class SubArea(QtCore.QRect):
    def __init__(self, x0, y0, width, height):
        super().__init__(x0, y0, width, height)

    SiteList = list()


class Site(QtCore.QRect):
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
        self.setX(rnd.randrange(self.parent.x(), self.parent.x() +  self.parent.width() - self.width() + 1))
        self.setY(rnd.randrange(self.parent.y(), self.parent.y() + self.parent.height() - self.height() + 1))


class Individual: #создание всех объектов
    def __init__(self):
        self.fcl = Facility(0, 0, 48, 48)

        self.Sub_Area_list = [] #список объектов подпространств цеха
        self.Site_list = [] #список объектов участков цеха
        self.area_sitenamelist = [] #список значений имен участков цеха
        self.area_sitespacelist = [] #список значений площадей цеха
        self.cargo_matrix = [] #список объектов подпространств цеха
        self.ZipList_area = zip([], []) #zip Площадей и названи
        self.chromosome = ''
        self.graycode = ''


    def create_sub_Area(self): #создание
        self.SubArea_1 = SubArea(0, 0, 48, 48) # создание подпространств
        self.SubArea_2 = SubArea(24, 0, 24, 48)



    def excelparser(self):  #парсер excel Cargo, Area
        self.cargo = xlrd.open_workbook('Cargo_test.xlsx')
        self.Area = xlrd.open_workbook('Cargo_test.xlsx')

        self.area_sheet = self.Area.sheet_by_index(1)   #листы Excel
        self.cargo_sheet = self.cargo.sheet_by_index(0) #листы Excel



        for rows in range(1, self.area_sheet.nrows): #заполнение списков названий участкой и площадей участков
            self.area_sitenamelist.append(self.area_sheet.cell_value(rows, 0))
            self.area_sitespacelist.append(self.area_sheet.cell_value(rows, 1))



        self.cargo_matrix = [[0] * (self.cargo_sheet.nrows - 1) for i in range(self.cargo_sheet.nrows - 1)]

        for rows in range(0, self.cargo_sheet.nrows - 1):
            for colounmns in range(0, self.cargo_sheet.nrows - 1):
                self.cargo_matrix[rows][colounmns] = self.cargo_sheet.cell_value(rows + 1, colounmns + 1)

        self.ZipList_area = zip(self.area_sitenamelist, self.area_sitespacelist)

    def createSites(self):
        for i in range(0, len(self.area_sitenamelist)):
            self.Site_list.append(Site(self.area_sitespacelist[i],
                                       self.area_sitenamelist[i],
                                       0, 0,
                                       self.SubArea_1 if i < len(self.area_sitenamelist) else self.SubArea_2))



















