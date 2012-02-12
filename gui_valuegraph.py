from PyQt4 import QtCore, QtGui

class ValueGraph(QtGui.QGraphicsItemGroup):
    def __init__(self, data, parent=None):
        super(ValueGraph, self).__init__(parent)
        self.data = data
        self.child = QtGui.QGraphicsItemGroup()
        self.child.setParentItem(self)

    def setSize(self, width, height):
        self.width = width
        self.height = height

    def recreateFromData(self):
        # Remove all subitems.
        self.removeFromGroup(self.child)
        self.scene().removeItem(self.child)
        self.child = QtGui.QGraphicsItemGroup()
        self.child.setParentItem(self)

        timeModifier = self.width / float(self.data.timeSpan)
        valueModifier = self.height / float(self.data.valueSpan)

        lastTime = None
        lastValue = None
        for t in range(0, len(self.data.time)):
            time = (self.data.time[t] - self.data.minTime) * timeModifier
            value = self.height - (self.data.values[t] - self.data.minValue) * valueModifier
            if lastTime is not None:
                line = QtGui.QGraphicsLineItem(QtCore.QLineF(lastTime, lastValue, time, value))
                line.setParentItem(self.child)
            lastTime = time
            lastValue = value

    def resizeFromData(self):
        timeModifier = self.width / float(self.data.timeSpan)
        valueModifier = self.height / float(self.data.valueSpan)
        lastTime = None
        lastValue = None
        children = self.child.childItems()
        if len(children) < len(self.data.time) - 1:
            print "Error in absorbance graph resize", len(children), len(self.data.time) - 1
        for t in range(0, len(self.data.time)):
            time = (self.data.time[t] - self.data.minTime) * timeModifier
            value = self.height - (self.data.values[t] - self.data.minValue) * valueModifier
            if lastTime is not None:
                line = QtCore.QLineF(lastTime, lastValue, time, value)
                children[t - 1].setLine(line)
            lastTime = time
            lastValue = value
