from PyQt4 import QtCore, QtGui

class AbsorbanceGraph(QtGui.QGraphicsItemGroup):
    def __init__(self, parent=None):
        super(AbsorbanceGraph, self).__init__(parent)
        self.data = None
        self.child = QtGui.QGraphicsItemGroup()
        self.child.setParentItem(self)

    def setSize(self, width, height):
        self.width = width
        self.height = height

    def setData(self, data):
        self.data = data
        
    def recreateFromData(self):
        # Remove all subitems.
        self.removeFromGroup(self.child)
        self.scene().removeItem(self.child)
        self.child = QtGui.QGraphicsItemGroup()
        self.child.setParentItem(self)

        timeModifier = self.width / float(self.data.timeSpan)
        absorbanceModifier = self.height / float(self.data.absorbanceSpan)
        lastTime = None
        lastAbsorbance = None
        for t in range(0, len(self.data.time)):
            time = (self.data.time[t] - self.data.minTime) * timeModifier
            absorbance = self.height - (self.data.absorbance[t] - self.data.minAbsorbance) * absorbanceModifier
            if lastTime != None and lastAbsorbance != None:
                line = QtGui.QGraphicsLineItem(QtCore.QLineF(lastTime, lastAbsorbance, time, absorbance))
                line.setParentItem(self.child)
            lastTime = time
            lastAbsorbance = absorbance
                    
    def resizeFromData(self):
        if self.data == None:
            return
        timeModifier = self.width / float(self.data.timeSpan)
        absorbanceModifier = self.height / float(self.data.absorbanceSpan)
        lastTime = None
        lastAbsorbance = None
        children = self.child.children()
        if len(children) < len(self.data.time) - 1:
            print "Error in absorbance graph resize", len(children), len(self.data.time) - 1
        for t in range(0, len(self.data.time)):
            time = (self.data.time[t] - self.data.minTime) * timeModifier
            absorbance = self.height - (self.data.absorbance[t] - self.data.minAbsorbance) * absorbanceModifier
            if lastTime != None and lastAbsorbance != None:
                line = QtCore.QLineF(lastTime, lastAbsorbance, time, absorbance)
                children[t - 1].setLine(line)
            lastTime = time
            lastAbsorbance = absorbance
