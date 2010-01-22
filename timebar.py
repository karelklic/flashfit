from PyQt4 import QtCore, QtGui
import math
from timebarline import TimeBarLine
from timebartriangle import TimeBarTriangle
  
class TimeBar(QtGui.QGraphicsItemGroup):
    ItemSendsGeometryChanges = 0x800

    class Signals(QtCore.QObject):
        # Qt Signal
        positionChanged = QtCore.pyqtSignal()

    def __init__(self, height, parent=None):
        super(TimeBar, self).__init__(parent)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(self.ItemSendsGeometryChanges, True)

        # Create graphical subcomponents.
        self.topTriangle = TimeBarTriangle(height, True)
        self.topTriangle.setParentItem(self)
        self.bottomTriangle = TimeBarTriangle(height, False)
        self.bottomTriangle.setParentItem(self)
        self.line = TimeBarLine(height)
        self.line.setParentItem(self)

        self.movingItemsInitialPositions = None

        self.signals = self.Signals()

    def setColor(self, color):
        for item in [self.line, self.topTriangle, self.bottomTriangle]:
            item.setColor(color)

    def itemChange(self, change, value):
        if change == self.ItemSelectedHasChanged:
            for item in [self.line, self.topTriangle, self.bottomTriangle]:
                item.setSelectedPen(self.isSelected())

        # Emit positionChanged signal if the object is moved
        if change == self.ItemPositionHasChanged:
            self.signals.positionChanged.emit()
        
        return super(TimeBar, self).itemChange(change, value)

    def mousePressEvent(self, event):
        if event.buttons() & QtCore.Qt.LeftButton:
            if not self.isSelected():
                self.scene().clearSelection()
                self.setSelected(True)
            self.movingItemsInitialPositions = None

    def mouseReleaseEvent(self, event):
        super(TimeBar, self).mouseReleaseEvent(event)
        if event.buttons() == 0:
            self.movingItemsInitialPositions = None

    def mouseMoveEvent(self, event):
        super(TimeBar, self).mouseMoveEvent(event)
        if event.buttons() & QtCore.Qt.LeftButton:
            selectedItems = self.scene().selectedItems();
            if not self.movingItemsInitialPositions:
                self.movingItemsInitialPositions = {}
                for item in selectedItems:
                    self.movingItemsInitialPositions[item] = item.pos()

            for item in selectedItems:
                currentParentPos = item.mapToParent(item.mapFromScene(event.scenePos()));
                buttonDownParentPos = item.mapToParent(item.mapFromScene(event.buttonDownScenePos(QtCore.Qt.LeftButton)));

                currentParentPos.setY(0)
                buttonDownParentPos.setY(0)
                item.setPos(self.movingItemsInitialPositions[item] + currentParentPos - buttonDownParentPos);
