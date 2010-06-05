from PyQt4 import QtCore, QtGui

class ResidualsGraph(QtGui.QGraphicsItemGroup):
    def __init__(self, data, parent=None):
        super(ResidualsGraph, self).__init__(parent)
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

        # Do nothing if no data are loaded.
        if self.data.timeSpan == None:
            return
        if len(self.data.fitdata.residuals.values) == 0:
            return

        timeModifier = self.width / float(self.data.timeSpan)
        residualsModifier = self.height / float(self.data.fitdata.residuals.span)
        lastTime = None
        lastResidual = None
        for t in range(0, self.data.fitAbsorbanceTimePointer[1] - self.data.fitAbsorbanceTimePointer[0] + 1):
            time = (self.data.time[self.data.fitAbsorbanceTimePointer[0] + t] - self.data.minTime) * timeModifier
            residual = self.height - (self.data.fitdata.residuals.values[t] - self.data.fitdata.residuals.min) * residualsModifier
            if lastTime != None and lastResidual != None:
                line = QtGui.QGraphicsLineItem(QtCore.QLineF(lastTime, lastResidual, time, residual))
                line.setParentItem(self.child)
            lastTime = time
            lastResidual = residual

        # Draw zero line
        zeroResidualY = self.height + self.data.fitdata.residuals.min * residualsModifier
        if zeroResidualY >= 0 and zeroResidualY < self.height:
            line = QtGui.QGraphicsLineItem(QtCore.QLineF(0, zeroResidualY, self.width, zeroResidualY))
            line.setParentItem(self.child)

    def resizeFromData(self):
        # Do nothing if no data are loaded.
        if self.data.timeSpan == None:
            return
        if len(self.data.fitdata.residuals.values) == 0:
            return

        timeModifier = self.width / float(self.data.timeSpan)
        residualsModifier = self.height / float(self.data.fitdata.residuals.span)
        lastTime = None
        lastResidual = None
        children = self.child.childItems()
        for t in range(0, self.data.fitAbsorbanceTimePointer[1] - self.data.fitAbsorbanceTimePointer[0] + 1):
            time = (self.data.time[self.data.fitAbsorbanceTimePointer[0] + t] - self.data.minTime) * timeModifier
            residual = self.height - (self.data.fitdata.residuals.values[t] - self.data.fitdata.residuals.min) * residualsModifier
            if lastTime != None and lastResidual != None:
                line = QtCore.QLineF(lastTime, lastResidual, time, residual)
                children[t - 1].setLine(line)
            lastTime = time
            lastResidual = residual

        # Update zero line
        oldLine = children[-1].line()
        line = QtCore.QLineF(oldLine.x1(), oldLine.y1(), self.width, oldLine.y2())
        children[-1].setLine(line)
