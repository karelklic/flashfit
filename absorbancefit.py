from PyQt4 import QtCore, QtGui

class AbsorbanceFit(QtGui.QGraphicsItemGroup):
    def __init__(self, parent=None):
        super(AbsorbanceFit, self).__init__(parent)
        self.data = None
        self.pen = QtGui.QPen()
        self.pen.setWidth(3)
        self.pen.setColor(QtGui.QColor("#882222"))

    def setSize(self, width, height):
        self.width = width
        self.height = height

    def setData(self, data):
        self.data = data

    def recreateFromData(self):
        for item in self.children():
            self.removeFromGroup(item)
            self.scene().removeItem(item)
            del item

        timeModifier = self.width / float(self.data.timeSpan)
        absorbanceModifier = self.height / float(self.data.absorbanceSpan)
        lastTime = None
        lastAbsorbance = None
        for t in range(0, self.data.fitAbsorbanceTimePointer[1] - self.data.fitAbsorbanceTimePointer[0]):
            time = (self.data.time[self.data.fitAbsorbanceTimePointer[0] + t] - self.data.minTime) * timeModifier
            #print "t", t
            #print "af", self.data.absorbanceFit
            fit = self.height - (self.data.absorbanceFit[t] - self.data.minAbsorbance) * absorbanceModifier
            if lastTime != None and lastFit != None:
                line = QtGui.QGraphicsLineItem(QtCore.QLineF(lastTime, lastFit, time, fit))
                line.setPen(self.pen)
                line.setParentItem(self)
            lastTime = time
            lastFit = fit
