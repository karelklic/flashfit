from PyQt4 import QtCore, QtGui
from timebar import TimeBar

class TimeBarPair:
    def __init__(self, barHeight, text, parent):
        self.bar1 = TimeBar(barHeight)
        self.bar2 = TimeBar(barHeight)
        self.setPos(100, 200)
        parent.addItem(self.bar1)
        parent.addItem(self.bar2)
        self.bar1.signals.positionChanged.connect(self.onPositionChanged)
        self.bar2.signals.positionChanged.connect(self.onPositionChanged)

        self.legendLine = QtGui.QGraphicsLineItem()
        self.legendLine.setPen(QtGui.QPen(QtCore.Qt.DotLine))
        parent.addItem(self.legendLine)
        self.legendText = QtGui.QGraphicsSimpleTextItem(text)
        font = QtGui.QFont()
        font.setPointSize(18)
        self.legendText.setFont(font)
        parent.addItem(self.legendText)
        self.updateLegend()

    def setPos(self, bar1, bar2):
        self.bar1.setPos(bar1, 0)
        self.bar2.setPos(bar2, 0)

    def setColor(self, color):
        self.bar1.setColor(color)
        self.bar2.setColor(color)
        # Color legend line
        p = self.legendLine.pen()
        p.setColor(color)
        self.legendLine.setPen(p)
        # Color legend text
        b = self.legendText.brush()
        b.setColor(color)
        self.legendText.setBrush(b)

    def onPositionChanged(self):
        self.updateLegend()

    def updateLegend(self):
        line = QtCore.QLineF( \
            self.bar1.pos().x(), 40, \
            self.bar2.pos().x(), 40)
        self.legendLine.setLine(line)
        textX = abs(line.dx()) / 2 + min(line.x1(), line.x2())
        textX -= self.legendText.boundingRect().width() / 2
        self.legendText.setPos(textX, 12)
        self.legendText.setVisible(abs(line.dx()) > self.legendText.boundingRect().width() + 5)
        
        
