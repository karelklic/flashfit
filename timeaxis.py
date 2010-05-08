from PyQt4 import QtCore, QtGui
import math
import variables

class TimeAxis(QtGui.QGraphicsItemGroup):
    def __init__(self, parent = None):
        super(TimeAxis, self).__init__(parent)
        self.child = QtGui.QGraphicsItemGroup()
        self.child.setParentItem(self)
        self.width = 100 # random initial value

    def setWidth(self, width):
        """
        Sets time axis width in pixels.
        """
        self.width = width

    def setTime(self, minTime, maxTime):
        """
        Sets minimum and maximum time displayed on axis (in seconds).
        """
        self.minTime = minTime
        self.maxTime = maxTime

    def mapTimeToPixels(self, time):
        """
        The only parameter is a time value in seconds.
        From input time, minimum and maximum time displayed on the axis,
        and from axis width in pixels, calculates the position of certain
        time on axis in pixels. This pixel offset is returned.

        Note that the returned value is not the X offset in the scene,
        because there is a free space (padding) on the left of the axis.
        The width of this space must be added to the returned value
        to obtain X position in the scene.
        """
        assert(time >= self.minTime)
        assert(time <= self.maxTime)
        timeSpan = float(self.maxTime - self.minTime)
        assert(timeSpan > 0)
        # Map the position to the range 0..1
        percents = float(time - self.minTime) / timeSpan
        assert(percents >= 0 and percents <= 1)
        # Map to pixels
        return self.width * percents

    def mapPixelsToTime(self, pixelOffset):
        assert(pixelOffset >= 0)
        assert(pixelOffset <= self.width)
        # Map the pixel offset to the range 0..1
        percents = pixelOffset / float(self.width)
        assert(percents >= 0 and percents <= 1)
        # Map to time
        return self.minTime + percents * (self.maxTime - self.minTime)

    def update(self):
        # Remove the old axis.
        self.removeFromGroup(self.child)
        self.scene().removeItem(self.child)
        self.child = QtGui.QGraphicsItemGroup()
        self.child.setParentItem(self)

        line = QtGui.QGraphicsLineItem(QtCore.QLineF(0, 0, self.width, 0))
        line.setParentItem(self.child)

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
        maxValuesHeight = 0
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
                text.setFont(variables.timeAxisValuesFont.value())
                text.setPos(ticx - text.boundingRect().width() / 2, 13)
                maxValuesHeight = max(maxValuesHeight, text.boundingRect().height())
                text.setParentItem(self.child)

                ticlen = 15

            tic = QtGui.QGraphicsLineItem(QtCore.QLineF(ticx, 0, ticx, ticlen))
            tic.setParentItem(self.child)
            time += ticSpan
            count += 1

        # Sets and displays axis label.
        if variables.timeAxisCaptionEnabled.value():
            text = QtGui.QGraphicsTextItem(variables.timeAxisCaption.value())
            text.setFont(variables.timeAxisCaptionFont.value())
            text.setPos(self.width - text.boundingRect().width(), maxValuesHeight)
            text.setParentItem(self.child)
