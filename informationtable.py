# -*- coding: utf-8 -*- (Python reads this)
from PyQt4 import QtCore, QtGui

class InformationTable(QtGui.QGraphicsItemGroup):
    def __init__(self, data, absorbanceGraph, parent=None):
        super(InformationTable, self).__init__(parent)
        self.data = data
        self.absorbanceGraph = absorbanceGraph
        self.textItem = QtGui.QGraphicsSimpleTextItem("")
        self.textItem.setParentItem(self)
        font = QtGui.QFont()
        font.setPixelSize(26)
        self.textItem.setFont(font)
        self.rect = QtGui.QGraphicsRectItem()
        self.rect.setVisible(False)
        self.rect.setParentItem(self)

    def recreateFromData(self):
        text = self.textFromData()
        self.textItem.setText(text)
        self.rect.setRect(self.textItem.boundingRect().normalized().adjusted(-10, -10, 10, 10))
        self.rect.setVisible(len(text) > 0)
        self.findPlaceInScene()

    def textFromData(self):
        text = ""
        if len(self.data.fileName) > 0:
            text += u"name: %s\n" % QtCore.QFileInfo(self.data.fileName).completeBaseName()
            text += u"measured: %s\n" % self.data.fileCreated.toString("yyyy-MM-dd hh:mm")
        if len(self.data.p) > 0:
            text += u"model: %s\n" % self.data.absorbanceFitFunction.name
        for i in range(0, len(self.data.p)):
            text += u"k(%d) = %e ± %e\n" % (i + 1, self.data.p[i], self.data.sigma_p[i])
        if self.data.fitAbsorbanceTimePointer and len(self.data.absorbance) > self.data.fitAbsorbanceTimePointer[0]:
            text += "A0 = %e\n" % self.data.absorbance[self.data.fitAbsorbanceTimePointer[0]]
        # remove the last newline
        if text.endswith("\n"):
            text = text[0:-1]
        return text

    def findPlaceInScene(self):
        self.setPos(self.absorbanceGraph.pos().x() + 400, self.absorbanceGraph.pos().y() + 80)
        #MIN_WIDTH = self.boundingRect().width()
        #success = False
        #for x in range(10, int(self.absorbanceGraph.width - MIN_WIDTH), int(self.absorbanceGraph.width / 10)):
        #    self.setPos(self.absorbanceGraph.pos().x() + x, self.absorbanceGraph.pos().y() + 80)
        #    if not self.collidesWithItem(self.absorbanceGraph):
        #        success = True
        #        break

        # TODO: change font size when failure occurs
