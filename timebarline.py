from PyQt4 import QtCore, QtGui
# The triangle size is read here.
from timebartriangle import TimeBarTriangle

class TimeBarLine(QtGui.QGraphicsLineItem):
    SELECTION_X_MARGIN = 15

    def __init__(self, barHeight, parent=None):
        # Create line.
        line = QtCore.QLineF()
        line.setP1(QtCore.QPointF(0, TimeBarTriangle.SIZE))
        line.setP2(QtCore.QPointF(0, barHeight - TimeBarTriangle.SIZE))
        super(TimeBarLine, self).__init__(line, parent)
        self.setCursor(QtCore.Qt.SizeHorCursor)
        self.boundingRect = QtCore.QRectF( \
            line.x1() - self.SELECTION_X_MARGIN / 2, line.y1(), \
                self.SELECTION_X_MARGIN, line.y2() - line.y1())
        self.shape = super(TimeBarLine, self).shape()
        self.shape.addRect(self.boundingRect)

        # Setup pens.
        self.normalPen = QtGui.QPen(QtCore.Qt.DashLine)
        self.selectedPen = QtGui.QPen(QtCore.Qt.DashLine)
        self.selectedPen.setWidth(3)
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

    def boundingRect(self):
        return self.boundingRect

    def shape(self):
        return self.shape

    def itemChange(self, change, value):
        """
        This virtual function is called by QGraphicsItem to notify custom 
        items that some part of the item's state changes.
        """
        # Set proper cursor for enabled and disabled item.
        if change == self.ItemEnabledChange:
            if self.isEnabled(): # means it will became disabled now
                self.setCursor(QtCore.Qt.ArrowCursor)
            else: # means it will became enabled now
                self.setCursor(QtCore.Qt.SizeHorCursor)

        return super(TimeBarLine, self).itemChange(change, value)
