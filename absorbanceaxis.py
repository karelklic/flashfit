from PyQt4 import QtCore, QtGui
import math
import variables

class AbsorbanceAxis(QtGui.QGraphicsItemGroup):
    def __init__(self, parent = None):
        super(AbsorbanceAxis, self).__init__(parent)
        self.child = QtGui.QGraphicsItemGroup()
        self.child.setParentItem(self)

    def setHeights(self, height, residualStart):
        self.height = height
        self.residualStart = residualStart

    def setAbsorbance(self, minAbsorbance, maxAbsorbance):
        self.minAbsorbance = minAbsorbance
        self.maxAbsorbance = maxAbsorbance

    def update(self):
        # Remove all subitems.
        self.removeFromGroup(self.child)
        self.scene().removeItem(self.child)
        self.child = QtGui.QGraphicsItemGroup()
        self.child.setParentItem(self)
        
        line = QtGui.QGraphicsLineItem(QtCore.QLineF(0, 0, 0, self.height))
        line.setParentItem(self.child)

        # Calculate and draw tics.
        absorbanceSpan = float(self.maxAbsorbance - self.minAbsorbance)
        bigTicSpan = float(1e10)
        while math.fmod(absorbanceSpan, bigTicSpan) == absorbanceSpan:
            bigTicSpan /= 10
        if absorbanceSpan / bigTicSpan < 2:
            bigTicSpan /= 10
        ticSpan = bigTicSpan / 10
        ticAbsorbance = self.minAbsorbance - math.fmod(self.minAbsorbance, ticSpan)
        if ticAbsorbance < self.minAbsorbance:
            ticAbsorbance += ticSpan
        bigTicAbsorbance = self.minAbsorbance + bigTicSpan - math.fmod(self.minAbsorbance, bigTicSpan)
        count = 10 - int((bigTicAbsorbance - self.minAbsorbance) / ticSpan)
        absorbance = ticAbsorbance
        while absorbance < self.maxAbsorbance:
            ticlen = 10
            ticy = self.residualStart - ((absorbance - self.minAbsorbance) * self.residualStart) / absorbanceSpan
            if count % 10 == 0:
                # Normalize absorbance
                diff = math.fmod(absorbance, ticSpan)
                absorbance = absorbance - diff
                if diff > ticSpan / 2.0:
                    absorbance = absorbance + ticSpan
                elif -diff > ticSpan / 2.0:
                    absorbance = absorbance - ticSpan

                text = QtGui.QGraphicsTextItem(str(absorbance))
                text.setFont(variables.absorbanceAxisValuesFont.value())
                text.setPos(-12 - text.boundingRect().width(), ticy - text.boundingRect().height() / 2)
                text.setParentItem(self.child)

                ticlen = 15

            tic = QtGui.QGraphicsLineItem(QtCore.QLineF(-ticlen, ticy, 0, ticy))
            tic.setParentItem(self.child)
            absorbance += ticSpan
            count += 1

        # Draw the caption
        if variables.absorbanceAxisCaptionEnabled.value():
            text = QtGui.QGraphicsTextItem(variables.absorbanceAxisCaption.value())
            text.setFont(variables.absorbanceAxisCaptionFont.value())
            text.setPos(-74, text.boundingRect().width())
            text.rotate(-90)
            text.setParentItem(self.child)
