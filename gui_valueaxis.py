from PyQt4 import QtCore, QtGui
import math
import variables

class ValueAxis(QtGui.QGraphicsItemGroup):
    def __init__(self, parent = None):
        super(ValueAxis, self).__init__(parent)
        self.child = QtGui.QGraphicsItemGroup()
        self.child.setParentItem(self)
        self.height = 800 # random initial value
        self.residualStart = 200 # random initial value

    def setHeights(self, height, residualStart):
        self.height = height
        self.residualStart = residualStart

    def setData(self, minValue, maxValue, captionVariable):
        self.minValue = minValue
        self.maxValue = maxValue
        self.captionVariable = captionVariable

    def update(self):
        # Remove all subitems.
        self.removeFromGroup(self.child)
        self.scene().removeItem(self.child)
        self.child = QtGui.QGraphicsItemGroup()
        self.child.setParentItem(self)

        line = QtGui.QGraphicsLineItem(QtCore.QLineF(0, 0, 0, self.height))
        line.setParentItem(self.child)

        # Calculate and draw tics.
        valueSpan = float(self.maxValue - self.minValue)
        bigTicSpan = float(1e10)
        while math.fmod(valueSpan, bigTicSpan) == valueSpan:
            bigTicSpan /= 10
        if valueSpan / bigTicSpan < 2:
            bigTicSpan /= 10
        ticSpan = bigTicSpan / 10
        ticValue = self.minValue - math.fmod(self.minValue, ticSpan)
        if ticValue < self.minValue:
            ticValue += ticSpan
        bigTicValue = self.minValue + bigTicSpan - math.fmod(self.minValue, bigTicSpan)
        count = 10 - int((bigTicValue - self.minValue) / ticSpan)
        value = ticValue
        maxValuesWidth = 0
        while value < self.maxValue:
            ticlen = 10
            ticy = self.residualStart - ((value - self.minValue) * self.residualStart) / valueSpan
            if count % 10 == 0:
                # Normalize value
                diff = math.fmod(value, ticSpan)
                value = value - diff
                if diff > ticSpan / 2.0:
                    value = value + ticSpan
                elif -diff > ticSpan / 2.0:
                    value = value - ticSpan

                text = QtGui.QGraphicsTextItem(str(value))
                text.setFont(variables.valueAxisValuesFont.value())
                text.setPos(-12 - text.boundingRect().width(), ticy - text.boundingRect().height() / 2)
                maxValuesWidth = max(maxValuesWidth, text.boundingRect().width())
                text.setParentItem(self.child)

                ticlen = 15

            tic = QtGui.QGraphicsLineItem(QtCore.QLineF(-ticlen, ticy, 0, ticy))
            tic.setParentItem(self.child)
            value += ticSpan
            count += 1

        # Draw the caption
        if variables.valueAxisCaptionEnabled.value():
            text = QtGui.QGraphicsTextItem(self.captionVariable.value())
            text.setFont(variables.valueAxisCaptionFont.value())
            text.setPos(-text.boundingRect().height() - maxValuesWidth, text.boundingRect().width())
            text.rotate(-90)
            text.setParentItem(self.child)
