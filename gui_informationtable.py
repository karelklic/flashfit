# -*- coding: utf-8 -*- (Python reads this)
from PyQt4 import QtCore, QtGui
import variables

class InformationTable(QtGui.QGraphicsItemGroup):
    ItemSendsGeometryChanges = 0x800

    def __init__(self, data, menuBar, absorbanceGraph, parent=None):
        super(InformationTable, self).__init__(parent)
        self.data = data
        self.menuBar = menuBar
        self.absorbanceGraph = absorbanceGraph
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QtGui.QGraphicsItem.ItemStacksBehindParent, True)
        self.setFlag(self.ItemSendsGeometryChanges, True)
        self.textItem = QtGui.QGraphicsSimpleTextItem("")
        self.textItem.setParentItem(self)

        # The rectangle around all the text.
        self.rect = QtGui.QGraphicsRectItem()
        self.rect.setVisible(False)
        self.rect.setParentItem(self)
        self.rect.setCursor(QtCore.Qt.SizeAllCursor)

        self.updateAppearance()

        # Support data for drag and drop movement
        self.movingItemsInitialPositions = None
        self.setCursor(QtCore.Qt.SizeAllCursor)

    def updateAppearance(self):
        self.textItem.setFont(variables.legendFont.value())
        self.recreateFromData()

    def recreateFromData(self):
        text = self.textFromData()
        self.textItem.setText(text)
        BORDER = 16 # pixels
        self.rect.setRect(self.textItem.boundingRect().normalized().adjusted(-BORDER, -BORDER, BORDER, BORDER))
        self.rect.setVisible(len(text) > 0)
        #self.findPlaceInScene()

    def textFromData(self):
        if not self.menuBar.showInformationBoxAct.isChecked():
            return ""

        text = ""
        if len(self.data.fileName) > 0:
            if self.menuBar.showNameAct.isChecked():
                text += u"name: %s\n" % QtCore.QFileInfo(self.data.fileName).completeBaseName()
            if self.menuBar.showDateAct.isChecked():
                text += u"measured: %s\n" % self.data.fileCreated.toString("yyyy-MM-dd hh:mm")
        if self.menuBar.showModelAct.isChecked():
            if self.data.fitdata.model == self.data.fitdata.MODEL_EXPERIMENTAL:
                text += u"model: %s\n" % self.data.fitdata.input.NAME
        if self.menuBar.showRateConstantAct.isChecked():
            for i in range(0, len(self.data.fitdata.parameters)):
                prec = variables.legendDisplayedPrecision.value()
                template = u"k(%%d) = %%.%de ± %%.%de\n" % (prec, prec)
                text += template % (i + 1, self.data.fitdata.parameters[i].value, self.data.fitdata.parameters[i].sigma)
        if self.menuBar.showA0Act.isChecked():
            if self.data.fitAbsorbanceTimePointer and len(self.data.absorbance) > self.data.fitAbsorbanceTimePointer[0]:
                text += "A0 = %e\n" % self.data.absorbance[self.data.fitAbsorbanceTimePointer[0]]
        # remove the last newline
        if text.endswith("\n"):
            text = text[0:-1]
        return text

    def findPlaceInScene(self):
        self.setPos(self.absorbanceGraph.pos().x() + 400, self.absorbanceGraph.pos().y() + 80)

    def mousePressEvent(self, event):
        if event.buttons() & QtCore.Qt.LeftButton:
            if not self.isSelected():
                self.scene().clearSelection()
                self.setSelected(True)
            self.clearMovingItemsInitialPositions()

    def mouseReleaseEvent(self, event):
        super(InformationTable, self).mouseReleaseEvent(event)
        self.clearMovingItemsInitialPositions()

    def clearMovingItemsInitialPositions(self):
        """
        Clears movingItemsInitialPositions array that is created on the start of mouse drag.
        """
        self.movingItemsInitialPositions = None

    def mouseMoveEvent(self, event):
        super(InformationTable, self).mouseMoveEvent(event)
        if event.buttons() & QtCore.Qt.LeftButton:
            selectedItems = self.scene().selectedItems();
            if not self.movingItemsInitialPositions:
                self.movingItemsInitialPositions = {}
                for item in selectedItems:
                    self.movingItemsInitialPositions[item] = item.pos()

            for item in selectedItems:
                currentParentPos = item.mapToParent(item.mapFromScene(event.scenePos()))
                buttonDownParentPos = item.mapToParent(item.mapFromScene(event.buttonDownScenePos(QtCore.Qt.LeftButton)))

                pos = self.movingItemsInitialPositions[item] + currentParentPos - buttonDownParentPos
                item.setPos(pos)
