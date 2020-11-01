import course
class Koef:
    def __init__(self):
        self.kx = 0
        self.ky = 0
        self.xmin = 0
        self.ymin = 0
        self.xmax = 0
        self.ymax = 0


class NewCoord:
    def __init__(self):
        self.newx = 0
        self.newy = 0


class Visual_Obj:

    def __init__(self, prop, widget, d):
        self.k = Koef()
        self.nc = NewCoord() # тут хранятся новые коордниты
        self.prop = prop # пропорциональный рисунок
        self.widget = widget

        self.d = d   # коэф отступа от границ экрана
        return

    def koefCulc(self, Rect):
        A = int(0)
        B = self.widget.width()
        C = self.widget.height()
        D = 0
        xmin = 0
        xmax = Rect.width
        ymin = 0
        ymax = Rect.height

        dx = float(xmax - xmin) / self.d
        dy = float(ymax - ymin) / self.d
        d = max(dx, dy)
        d = float(d)
        xmin -= d
        xmax += d
        ymin -= d
        ymax += d

        self.k.kx = (B - A) / (xmax - xmin)
        self.k.ky = (D - C) / (ymax - ymin)

        self.k.xmin = xmin
        self.k.xmax = xmax
        self.k.ymin = ymin
        self.k.ymax = ymax

        if self.prop:
            self.k.kx = abs(min(self.k.kx, self.k.ky))
            self.k.ky = self.k.kx



    def coordCulc(self, oldx, oldy):
        A = 0
        B = self.widget.width()
        C = self.widget.height()
        self.nc.newx = int(A + self.k.kx * (oldx - self.k.xmin))
        self.nc.newy = int(C + (-1 if self.prop else 1) * self.k.ky * (oldy - self.k.ymin))
    # oldx oldy
    #coordCulc(oldx,oldy)
    #DrowRect(visual.nc.newx...