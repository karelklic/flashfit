from PyQt4 import QtCore, QtGui

class Fit(QtGui.QGraphicsItemGroup):
    def __init__(self, data, parent=None):
        super(Fit, self).__init__(parent)
        self.data = data
        self.pen = QtGui.QPen()
        self.pen.setWidth(3)
        self.pen.setColor(QtGui.QColor("#882222"))
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
        # Do nothing if no data are loaded.
        if len(self.data.fitdata.values) == 0:
            return

        timeModifier = self.width / float(self.data.timeSpan)
        absorbanceModifier = self.height / float(self.data.absorbanceData.absorbanceSpan)
        lastTime = None
        lastAbsorbance = None
        for t in range(0, self.data.fitTimePointer[1] - self.data.fitTimePointer[0] + 1):
            time = (self.data.time[self.data.fitTimePointer[0] + t] - self.data.minTime) * timeModifier
            fit = self.height - (self.data.fitdata.values[t] - self.data.absorbanceData.minAbsorbance) * absorbanceModifier
            if lastTime is not None:
                line = QtGui.QGraphicsLineItem(QtCore.QLineF(lastTime, lastFit, time, fit))
                line.setPen(self.pen)
                line.setParentItem(self.child)
            lastTime = time
            lastFit = fit

    def resizeFromData(self):
        # Do nothing if no data are loaded.
        if len(self.data.fitdata.values) == 0:
            return

        timeModifier = self.width / float(self.data.timeSpan)
        absorbanceModifier = self.height / float(self.data.absorbanceData.absorbanceSpan)
        lastTime = None
        lastAbsorbance = None
        children = self.child.childItems()
        for t in range(0, self.data.fitTimePointer[1] - self.data.fitTimePointer[0] + 1):
            time = (self.data.time[self.data.fitTimePointer[0] + t] - self.data.minTime) * timeModifier
            fit = self.height - (self.data.fitdata.values[t] - self.data.absorbanceData.minAbsorbance) * absorbanceModifier
            if lastTime is not None:
                line = QtCore.QLineF(lastTime, lastFit, time, fit)
                children[t - 1].setLine(line)
            lastTime = time
            lastFit = fit
