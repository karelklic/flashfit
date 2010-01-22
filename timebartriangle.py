from PyQt4 import QtCore, QtGui

class TimeBarTriangle(QtGui.QGraphicsPolygonItem):
    SIZE = 20

    def __init__(self, barHeight, top, parent=None):
        # Create polygon.
        poly = QtGui.QPolygonF()
        if top:
            poly.append(QtCore.QPointF(-self.SIZE/2, 0))
            poly.append(QtCore.QPointF(self.SIZE/2, 0))
            poly.append(QtCore.QPointF(0, self.SIZE))
        else:
            poly.append(QtCore.QPointF(-self.SIZE/2, barHeight))
            poly.append(QtCore.QPointF(self.SIZE/2, barHeight))
            poly.append(QtCore.QPointF(0, barHeight - self.SIZE))

        super(TimeBarTriangle, self).__init__(poly, parent)
        self.setCursor(QtCore.Qt.SizeHorCursor)

        # Setup pens.
        self.normalPen = QtGui.QPen()
        self.normalPen.setWidth(3)
        self.selectedPen = QtGui.QPen()
        self.selectedPen.setWidth(5)
        self.setPen(self.normalPen)

    def setSelectedPen(self, selected):
        if selected:
            self.setPen(self.selectedPen)
        else:
            self.setPen(self.normalPen)

    def setColor(self, color):
        # Color normal pen
        np = self.normalPen
        np.setColor(color)
        self.normalPen = np
        # Color selection pen
        sp = self.selectedPen
        sp.setColor(color)
        self.selectedPen = sp
        # Color current pen
        p = self.pen()
        p.setColor(color)
        self.setPen(p)
