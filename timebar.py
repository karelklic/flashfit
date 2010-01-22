from PyQt4 import QtCore, QtGui
import math

class TimeBarTriangle(QtGui.QGraphicsPolygonItem):
    SIZE = 20
    def __init__(self, barHeight, top, parent=None):
        # Create polygon.
        poly = QtGui.QPolygonF()
        if top:
            poly.append(QtCore.QPointF(-self.SIZE/2, 0))
            poly.append(QtCore.QPointF(self.SIZE/2, 0))
            poly.append(QtCore.QPointF(0, self.SIZE))
        else:
            poly.append(QtCore.QPointF(-self.SIZE/2, barHeight))
            poly.append(QtCore.QPointF(self.SIZE/2, barHeight))
            poly.append(QtCore.QPointF(0, barHeight - self.SIZE))

        super(TimeBarTriangle, self).__init__(poly, parent)
        self.setCursor(QtCore.Qt.SizeHorCursor)

        # Setup pens.
        self.normalPen = QtGui.QPen()
        self.normalPen.setWidth(3)
        self.selectedPen = QtGui.QPen()
        self.selectedPen.setWidth(5)
        self.setPen(self.normalPen)

    def setSelectedPen(self, selected):
        if selected:
            self.setPen(self.selectedPen)
        else:
            self.setPen(self.normalPen)

    def setColor(self, color):
        # Color normal pen
        np = self.normalPen
        np.setColor(color)
        self.normalPen = np
        # Color selection pen
        sp = self.selectedPen
        sp.setColor(color)
        self.selectedPen = sp
        # Color current pen
        p = self.pen()
        p.setColor(color)
        self.setPen(p)

class TimeBarLine(QtGui.QGraphicsLineItem):
    SELECTION_X_MARGIN = 15

    def __init__(self, barHeight, parent=None):
        # Create line.
        line = QtCore.QLineF()
        line.setP1(QtCore.QPointF(0, TimeBarTriangle.SIZE))
        line.setP2(QtCore.QPointF(0, barHeight - TimeBarTriangle.SIZE))
        super(TimeBarLine, self).__init__(line, parent)
        self.setCursor(QtCore.Qt.SizeHorCursor)
        self.boundingRect = QtCore.QRectF( \
            line.x1() - self.SELECTION_X_MARGIN / 2, line.y1(), \
                self.SELECTION_X_MARGIN, line.y2() - line.y1())
        self.shape = super(TimeBarLine, self).shape()
        self.shape.addRect(self.boundingRect)

        # Setup pens.
        self.normalPen = QtGui.QPen(QtCore.Qt.DashLine)
        self.selectedPen = QtGui.QPen(QtCore.Qt.DashLine)
        self.selectedPen.setWidth(3)
        self.setPen(self.normalPen)

    def setSelectedPen(self, selected):
        if selected:
            self.setPen(self.selectedPen)
        else:
            self.setPen(self.normalPen)

    def setColor(self, color):
        # Color normal pen
        np = self.normalPen
        np.setColor(color)
        self.normalPen = np
        # Color selection pen
        sp = self.selectedPen
        sp.setColor(color)
        self.selectedPen = sp
        # Color current pen
        p = self.pen()
        p.setColor(color)
        self.setPen(p)

    def boundingRect(self):
        return self.boundingRect

    def shape(self):
        return self.shape
  
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
