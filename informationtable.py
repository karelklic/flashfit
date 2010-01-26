# -*- coding: utf-8 -*- (Python reads this)
from PyQt4 import QtCore, QtGui

class InformationTable(QtGui.QGraphicsItemGroup):
    def __init__(self, absorbanceGraph, parent=None):
        super(InformationTable, self).__init__(parent)
        self.data = None
        self.absorbanceGraph = absorbanceGraph
        self.textItem = QtGui.QGraphicsSimpleTextItem("")
        self.textItem.setParentItem(self)

    def setData(self, data):
        self.data = data

    def recreateFromData(self):
        self.textItem.setText(self.textFromData())
        self.findPlaceInScene()

    def textFromData(self):
        text = ""
        for i in range(0, len(self.data.p)):
            text += "k(" + str(i + 1) + ") = " + str(self.data.p[i]) + u" ± " + str(self.data.sigma_p[i]) + "\n"
        return text

    def findPlaceInScene(self):
        self.setPos(self.absorbanceGraph.pos().x() + 300, self.absorbanceGraph.pos().y() + 80)
        #MIN_WIDTH = self.boundingRect().width()
        #success = False
        #for x in range(10, int(self.absorbanceGraph.width - MIN_WIDTH), int(self.absorbanceGraph.width / 10)):
        #    self.setPos(self.absorbanceGraph.pos().x() + x, self.absorbanceGraph.pos().y() + 80)
        #    if not self.collidesWithItem(self.absorbanceGraph):
        #        success = True
        #        break

        # TODO: change font size when failure occurs

        
