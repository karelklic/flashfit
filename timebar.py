from PyQt4 import QtCore, QtGui
import math
from timebarline import TimeBarLine
from timebartriangle import TimeBarTriangle
  
class TimeBar(QtGui.QGraphicsItemGroup):
    ItemSendsGeometryChanges = 0x800

    class Signals(QtCore.QObject):
        """
        TimeBar is not a subclass of QObject, and it cannot be.
        This helper class contains TimeBar's signals.
        """
        # Qt Signals
        positionChanged = QtCore.pyqtSignal()
        # The parameter is time in seconds.
        positionChangeFinished = QtCore.pyqtSignal(float)

    def __init__(self, height, timeAxis, leftBorder, parent=None):
        """
        Parameter height is a height of the time bar in pixels.
        Parameter timeAxis points to Time Axis on which the time bars
        are placed.
        Parameter leftBorder contains the width of free space between
        the left side of the scene and Time Axis, in pixels.
        Parameter parent is a parent object in scene where time bars 
        will be displayed.
        """
        super(TimeBar, self).__init__(parent)
        self.timeAxis = timeAxis
        self.leftBorder = leftBorder
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(self.ItemSendsGeometryChanges, True)

        # Create graphical subcomponents.
        self.topTriangle = TimeBarTriangle(height, True)
        self.topTriangle.setParentItem(self)
        self.bottomTriangle = TimeBarTriangle(height, False)
        self.bottomTriangle.setParentItem(self)
        self.line = TimeBarLine(height)
        self.line.setParentItem(self)

        # Support data for drag and drop movement
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
            self.clearMovingItemsInitialPositions()

    def mouseReleaseEvent(self, event):
        super(TimeBar, self).mouseReleaseEvent(event)
        self.clearMovingItemsInitialPositions()

    def clearMovingItemsInitialPositions(self):
        """
        Clears movingItemsInitialPositions array that is created on the start of mouse drag.
        Sends the signal about the end of position change.
        """
        if self.movingItemsInitialPositions:
            self.movingItemsInitialPositions = None
            time = self.timeAxis.mapPixelsToTime(self.pos().x() - self.leftBorder)
            self.signals.positionChangeFinished.emit(time)

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
                pos = self.movingItemsInitialPositions[item] + currentParentPos - buttonDownParentPos
                if pos.x() < self.leftBorder:
                    pos.setX(self.leftBorder)
                elif pos.x() >= self.leftBorder + self.timeAxis.width:
                    pos.setX(self.leftBorder + self.timeAxis.width)
                item.setPos(pos);
