from PyQt4 import QtCore, QtGui

class ResidualsGraph(QtGui.QGraphicsItemGroup):
    def __init__(self, parent=None):
        super(ResidualsGraph, self).__init__(parent)
        self.data = None

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
        residualsModifier = self.height / float(self.data.residualsSpan)
        lastTime = None
        lastResidual = None
        for t in range(0, self.data.fitAbsorbanceTimePointer[1] - self.data.fitAbsorbanceTimePointer[0]):
            time = (self.data.time[self.data.fitAbsorbanceTimePointer[0] + t] - self.data.minTime) * timeModifier
            residual = self.height - (self.data.residuals[t] - self.data.minResiduals) * residualsModifier
            if lastTime != None and lastResidual != None:
                line = QtGui.QGraphicsLineItem(QtCore.QLineF(lastTime, lastResidual, time, residual))
                line.setParentItem(self)
            lastTime = time
            lastResidual = residual

        # Draw zero line
        zeroResidualY = self.height + self.data.minResiduals * residualsModifier
        if zeroResidualY >= 0 and zeroResidualY < self.height:
            line = QtGui.QGraphicsLineItem(QtCore.QLineF(0, zeroResidualY, self.width, zeroResidualY))
            line.setParentItem(self)

