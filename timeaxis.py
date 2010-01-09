from PyQt4 import QtCore, QtGui
import math

class TimeAxis(QtGui.QGraphicsItemGroup):
    def __init__(self, parent=None):
        super(TimeAxis, self).__init__(parent)

    def setWidth(self, width):
        self.width = width

    def setTime(self, minTime, maxTime):
        self.minTime = minTime
        self.maxTime = maxTime

    def update(self):
        # Remove the old axis.
        for item in self.children():
            self.removeFromGroup(item)
            del item

        line = QtGui.QGraphicsLineItem(QtCore.QLineF(0, 0, self.width, 0))
        line.setParentItem(self)

        # Calculate and draw tics.
        timeSpan = float(self.maxTime - self.minTime)
        bigTicSpan = float(1e10)
        while math.fmod(timeSpan, bigTicSpan) == timeSpan:
            bigTicSpan /= 10
        if timeSpan / bigTicSpan < 2:
            bigTicSpan /= 10
        ticSpan = bigTicSpan / 10
        ticTime = self.minTime - math.fmod(self.minTime, ticSpan)
        if ticTime < self.minTime:
            ticTime += ticSpan
        bigTicTime = self.minTime + bigTicSpan - math.fmod(self.minTime, bigTicSpan)
        count = 10 - int((bigTicTime - self.minTime) / ticSpan)
        time = ticTime
        while time < self.maxTime:
            ticlen = 10
            ticx = ((time - self.minTime) * self.width) / timeSpan
            if count % 10 == 0:
                # Normalize time
                diff = math.fmod(time, ticSpan)
                time = time - diff
                if diff > ticSpan / 2.0:
                    time = time + ticSpan
                elif -diff > ticSpan / 2.0:
                    time = time - ticSpan

                text = QtGui.QGraphicsTextItem(str(time))
                text.setPos(ticx - text.boundingRect().width() / 2, 13)
                text.setParentItem(self)
                ticlen = 15
            tic = QtGui.QGraphicsLineItem(QtCore.QLineF(ticx, 0, ticx, ticlen))
            tic.setParentItem(self)
            time += ticSpan
            count += 1

        text = QtGui.QGraphicsTextItem("time")
        text.setPos(self.width - 75, 24)
        font = QtGui.QFont()
        font.setPixelSize(28)
        text.setFont(font)
        text.setParentItem(self)
