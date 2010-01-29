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
        # Do nothing if no data are loaded.
        if self.data.timeSpan == None:
            return

        # Remove all subitems.
        for item in self.childItems():
            self.removeFromGroup(item)
            self.scene().removeItem(item)

        timeModifier = self.width / float(self.data.timeSpan)
        residualsModifier = self.height / float(self.data.residualsSpan)
        lastTime = None
        lastResidual = None
        for t in range(0, self.data.fitAbsorbanceTimePointer[1] - self.data.fitAbsorbanceTimePointer[0] + 1):
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

    def resizeFromData(self):
        if self.data == None:
            return
        timeModifier = self.width / float(self.data.timeSpan)
        residualsModifier = self.height / float(self.data.residualsSpan)
        lastTime = None
        lastResidual = None
        children = self.children()
        for t in range(0, self.data.fitAbsorbanceTimePointer[1] - self.data.fitAbsorbanceTimePointer[0] + 1):
            time = (self.data.time[self.data.fitAbsorbanceTimePointer[0] + t] - self.data.minTime) * timeModifier
            residual = self.height - (self.data.residuals[t] - self.data.minResiduals) * residualsModifier
            if lastTime != None and lastResidual != None:
                line = QtCore.QLineF(lastTime, lastResidual, time, residual)
                children[t - 1].setLine(line)
            lastTime = time
            lastResidual = residual

        # Update zero line
        oldLine = children[-1].line()
        line = QtCore.QLineF(oldLine.x1(), oldLine.y1(), self.width, oldLine.y2())
        children[-1].setLine(line)
