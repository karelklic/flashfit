from PyQt4 import QtCore, QtGui
import math

class TimeBar(QtGui.QGraphicsItemGroup):
    ARROW_SIZE = 20

    def __init__(self, height, parent=None):
        super(TimeBar, self).__init__(parent)

        polyPen = QtGui.QPen()
        polyPen.setWidth(3)

        poly = QtGui.QPolygonF()
        poly.append(QtCore.QPointF(-TimeBar.ARROW_SIZE/2, 0))
        poly.append(QtCore.QPointF(TimeBar.ARROW_SIZE/2, 0))
        poly.append(QtCore.QPointF(0, TimeBar.ARROW_SIZE))
        topTic = QtGui.QGraphicsPolygonItem(poly)
        topTic.setPen(polyPen)
        topTic.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)
        topTic.setParentItem(self)
        
        poly = QtGui.QPolygonF()
        poly.append(QtCore.QPointF(-TimeBar.ARROW_SIZE/2, height))
        poly.append(QtCore.QPointF(TimeBar.ARROW_SIZE/2, height))
        poly.append(QtCore.QPointF(0, height - TimeBar.ARROW_SIZE))
        bottomTic = QtGui.QGraphicsPolygonItem(poly)
        bottomTic.setPen(polyPen)
        bottomTic.setParentItem(self)

        line = QtGui.QGraphicsLineItem(QtCore.QLineF(0, TimeBar.ARROW_SIZE, 0, height - TimeBar.ARROW_SIZE))
        pen = QtGui.QPen(QtCore.Qt.DashLine)
        line.setPen(pen)
        line.setParentItem(self)
