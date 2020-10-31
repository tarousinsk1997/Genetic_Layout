import random as rnd
import xlrd
rrmin = 0.5
rrmax = 1


class Rect:
    def __init__(self, x0, y0, width=0, height=0):
        self.width = width
        self.height = height
        self.x0 = x0
        self.y0 = y0

class Facility(Rect):
    def __init__(self, x0, y0, width, height):
        super().__init__(x0, y0, width, height)

    SubAreaList = list()


class SubArea(Rect):
    def __init__(self, x0, y0, width, height):
        super().__init__(x0, y0, width, height)

    SiteList = list()


class Site(Rect):
    def __init__(self, S, name, x0, y0, width, height):
        super().__init__(x0, y0, width, height)
        self.name = name
        self.S = S


class Random_object_generator: #создание всех объектов
    def __init__(self):
        self.fcl = Facility(0,0, 72, 144)

        self.Sub_Area_list = [] #список объектов подпространств цеха
        self.Site_list = [] #список объектов участков цеха
        self.area_sitenamelist = [] #список значений имен участков цеха
        self.area_sitespacelist = [] #список значений площадей цеха
        self.cargo_matrix = [] #список объектов подпространств цеха
        self.ZipList_area = zip([], []) #zip Площадей и названий




    def create_sub_Area(self): #создание
        self.SubArea_1 = SubArea(0, 0, 72, 72) # создание подпространств
        self.SubArea_2 = SubArea(72, 0, 72, 72)



    def excelparser(self):  #парсер excel Cargo, Area
        self.cargo = xlrd.open_workbook('Cargo1.xlsx')
        self.Area = xlrd.open_workbook('Area1.xlsx')

        self.area_sheet = self.Area.sheet_by_index(0)   #листы Excel
        self.cargo_sheet = self.cargo.sheet_by_index(0) #листы Excel



        for rows in range(1, 5): #заполнение списков названий участкой и площадей участков
            self.area_sitenamelist.append(self.area_sheet.cell_value(rows, 0))
            self.area_sitespacelist.append(self.area_sheet.cell_value(rows, 1))



        self.cargo_matrix = [[0] * (self.cargo_sheet.nrows - 1) for i in range(self.cargo_sheet.nrows - 1)]

        for rows in range(0, self.cargo_sheet.nrows - 1):
            for colounmns in range(0, self.cargo_sheet.nrows - 1):
                self.cargo_matrix[rows][colounmns] = self.cargo_sheet.cell_value(rows + 1, colounmns + 1)

        self.ZipList_area = zip(self.area_sitenamelist, self.area_sitespacelist)
        #print(list(self.ZipList_area),'\n', self.cargo_matrix)

        for i in range(len(self.area_sitenamelist)):
            self.Site_list.append(Site(self.area_sitespacelist[i], self.area_sitenamelist[i], 0, 0, 20, 20))

        #print(list(self.ZipList_area))


rog = Random_object_generator()
rog.excelparser()







