from PyQt4 import QtCore, QtGui
import math
from gui_timebarline import TimeBarLine
from gui_timebartriangle import TimeBarTriangle

class TimeBar(QtGui.QGraphicsItemGroup):
    # Defined here until PyQt includes it.
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

    def __init__(self, timeAxis, parent = None):
        """
        Parameter timeAxis points to Time Axis on which the time bars
        are placed.
        Parameter parent is a parent object in scene where time bars 
        will be displayed.
        """
        super(TimeBar, self).__init__(parent)
        self.timeAxis = timeAxis
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(self.ItemSendsGeometryChanges, True)

        # Create graphical subcomponents.
        self.topTriangle = TimeBarTriangle(True)
        self.topTriangle.setParentItem(self)
        self.bottomTriangle = TimeBarTriangle(False)
        self.bottomTriangle.setParentItem(self)
        self.line = TimeBarLine()
        self.line.setParentItem(self)

        # Support data for drag and drop movement
        self.movingItemsInitialPositions = None

        self.signals = self.Signals()

    def setHeight(self, height):
        self.topTriangle.setHeight(height)
        self.bottomTriangle.setHeight(height)
        self.line.setHeight(height)

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
            time = self.timeAxis.mapPixelsToTime(self.pos().x())
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
                currentParentPos = item.mapToParent(item.mapFromScene(event.scenePos()))
                buttonDownParentPos = item.mapToParent(item.mapFromScene(event.buttonDownScenePos(QtCore.Qt.LeftButton)))

                currentParentPos.setY(0)
                buttonDownParentPos.setY(0)
                pos = self.movingItemsInitialPositions[item] + currentParentPos - buttonDownParentPos
                if pos.x() < 0:
                    pos.setX(0)
                elif pos.x() >= self.timeAxis.width:
                    pos.setX(self.timeAxis.width)
                item.setPos(pos)
