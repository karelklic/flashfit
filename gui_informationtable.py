# -*- coding: utf-8 -*- (Python reads this)
from PyQt4 import QtCore, QtGui
import variables

class InformationTable(QtGui.QGraphicsItemGroup):
    ItemSendsGeometryChanges = 0x800

    def __init__(self, data, menuBar, textItems, absorbanceGraph, parent=None):
        super(InformationTable, self).__init__(parent)
        self.data = data
        self.menuBar = menuBar
        self.textItems = textItems
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
        self.rect.setRect(self.textItem.boundingRect().normalized().adjusted(-BORDER,
                                                                              -BORDER,
                                                                              BORDER,
                                                                              BORDER))
        self.rect.setVisible(len(text) > 0)
        #self.findPlaceInScene()

    def textFromData(self):
        if not self.menuBar.showInformationBoxAct.isChecked():
            return ""

        lines = []
        for item in variables.legendTable.value(default=False):
            line = self.textItems.all[str(item)].text()
            if line and len(line) > 0:
                lines.append(line)
        return '\n'.join(lines)

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
