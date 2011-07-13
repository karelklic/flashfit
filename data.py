from PyQt4 import QtCore, QtGui
from numpy import matrix, matlib, linalg
import numpy
import math
import sys
import data_original
import data_fit

class Data(QtCore.QObject):
    DEFAULT_USED_POINTS_COUNT = 2000

    # Qt Signals
    DATA_CHANGED_ABSORBANCE = 0x01
    DATA_CHANGED_FULL_LIGHT_VOLTAGE_TIME_POINTER = 0x02
    DATA_CHANGED_FIT_ABSORBANCE = 0x04
    DATA_CHANGED_FIT_ABSORBANCE_TIME_POINTER = 0x08
    dataChanged = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        """
        No data is present after init.
        """
        QtCore.QObject.__init__(self, parent)
        self.clear()

    def clear(self):
        """
        Sets nice initial state of the data.
        """
        self.maxPoints = self.DEFAULT_USED_POINTS_COUNT
        self.fileName = "" # Full Path
        self.fileCreated = QtCore.QDateTime()

        # Absorbance fit in time.
        self.fitdata = data_fit.Fit()
        self.fitdata.changed.connect(self.onFitChanged)
        # No light voltage
        # Used to calculate absorbance from voltage.
        self.noLightVoltage = 0.0

        # Data loaded from input file.
        self.originalData = data_original.Data()
        POINT_COUNT = 2000
        self.originalData.time = [(x / float(POINT_COUNT)) for x in range(0, POINT_COUNT)]
        self.originalData.voltage = [100] * int(POINT_COUNT * 0.2)
        self.originalData.voltage += [40 + (60 * i) / (POINT_COUNT * 0.6) for i in range(0, int(POINT_COUNT * 0.6))]
        self.originalData.voltage += [100] * int(POINT_COUNT - len(self.originalData.voltage))
        self.originalData.minVoltage = 40
        self.originalData.maxVoltage = 100
        self.originalData.voltageSpan = 60
        self.copyFromOriginalData()

        # Full Light Voltage time pointer
        # Both values are offsets to self.time array.
        # self.fullLightVoltage is calculated from this pointers
        # Full light voltage is used to calculate absorbance from voltage.
        self.setFullLightVoltagePointer(int(0.05 * POINT_COUNT),
                                        int(0.15 * POINT_COUNT))
        self.recalculateAbsorbances()
        # Fit Absorbance time pointer
        # Both values are offsets to self.time array.
        self.setFitAbsorbanceTimePointer(int(0.25 * POINT_COUNT),
                                         int(0.70 * POINT_COUNT))

    def clearAbsorbance(self):
        # Absorbance in time.
        self.absorbance = []
        self.minAbsorbance = None
        self.maxAbsorbance = None
        self.absorbanceSpan = None
        self.fitdata.clear()

    def copyFromOriginalData(self):
        """
        numberOfPoints is a maximum number of points to be copied
        from original data
        """
        maxPoints = len(self.originalData.time)
        idealRatio = maxPoints / float(self.maxPoints)
        self.time = []
        self.minTime = float("inf")
        self.maxTime = float("-inf")
        self.timeSpan = float("inf")
        self.voltage = []
        ratio = float('inf')
        for offs in range(0, maxPoints):
            if len(self.time) > 0:
                ratio = offs / float(len(self.time))

            if ratio >= idealRatio:
                # Copy time.
                time = self.originalData.time[offs]
                self.time.append(time)
                if self.minTime > time:
                    self.minTime = time
                if self.maxTime < time:
                    self.maxTime = time
                # Copy voltage
                self.voltage.append(self.originalData.voltage[offs])

        self.timeSpan = self.maxTime - self.minTime

        # Clear invalid data.
        self.clearAbsorbance()
        self.fullLightVoltage = None
        self.fullLightVoltagePointer = None
        self.fitAbsorbanceTimePointer = None

    def recalculateAbsorbances(self):
        """
        Recalculates all absorbance values!
        Also updates minAbsorbance and maxAbsorbance values
        Slow!
        """
        self.clearAbsorbance()

        # If we do not know full light voltage, we are done.
        if self.fullLightVoltage is None:
            return

        vdiff = self.fullLightVoltage - self.noLightVoltage
        if vdiff != 0: # Divide by zero.
            for v in self.voltage: # v is the voltage in time t
                try:
                    absorbance = -math.log10((v - self.noLightVoltage) / vdiff)
                except ValueError as error:
                    print error
                    print "Voltage:", v - self.noLightVoltage, "vdiff:", vdiff
                self.absorbance.append(absorbance)
                if self.minAbsorbance == None or self.minAbsorbance > absorbance:
                    self.minAbsorbance = absorbance
                if self.maxAbsorbance == None or self.maxAbsorbance < absorbance:
                    self.maxAbsorbance = absorbance

        if self.minAbsorbance != None and self.maxAbsorbance != None:
            self.absorbanceSpan = self.maxAbsorbance - self.minAbsorbance

    def guessFullLightVoltagePointerValue(self):
        """
        Takes time and voltage waveform, and tries to determine which part of
        the waveform contains voltage corresponding to the full light.
        The full light should be at the beginning of the waveform, followed
        by a flash.
        """
        start = 0
        end = 0
        sum = self.voltage[0]
        for i in range(start + 1, len(self.voltage) - 1):
            if (self.voltage[i] - sum / i) > self.originalData.voltageSpan * 0.5:
                end = i - max(1, int(i * 0.1))
                break
            sum += self.voltage[i]
        if end == start:
            end = len(self.voltage) / 2

        self.setFullLightVoltagePointer(start, end)

    def guessFitAbsorbanceTimePointer(self):
        """
        Takes time and voltage waveform, and tries to determine which part of
        the waveform should be fitted by a curve.
        """
        start = len(self.voltage) - 1
        end = len(self.voltage) - 1
        # The start point is the point with the highest voltage.
        highest = self.voltage[start]
        for i in range(0, end - 1):
            if self.voltage[i] > highest:
                highest = self.voltage[i]
                start = i
        self.setFitAbsorbanceTimePointer(start, end)

    def setFullLightVoltagePointer(self, start, stop):
        """
        Parameters start and stop are offsets to self.time array.
        """
        if start > stop:
            start, stop = stop, start
        self.fullLightVoltagePointer = [start, stop]

        # Calculate the arithmetic mean voltage from it.
        sum = 0.0
        for i in range(start, stop):
            sum += self.voltage[i]
        self.fullLightVoltage = sum / float(stop - start + 1)
        self.clearAbsorbance()

    def findClosestTimeOffset(self, time, minOffset, maxOffset):
        if maxOffset - minOffset == 1:
            if (time - self.time[minOffset]) < (self.time[maxOffset] - time):
                return minOffset
            else:
                return maxOffset

        middleOffset = minOffset + (maxOffset - minOffset) / 2
        middleTime = self.time[middleOffset]
        if time < middleTime:
            return self.findClosestTimeOffset(time, minOffset, middleOffset)
        else:
            return self.findClosestTimeOffset(time, middleOffset, maxOffset)

    def fullLightVoltageTime1(self):
        """
        Returns time in seconds.
        """
        assert self.fullLightVoltagePointer[0] >= 0 and self.fullLightVoltagePointer[0] < len(self.time), "FullLight pointer invalid: %d, time length %d" % (self.fullLightVoltagePointer[0], len(self.time))
        return self.time[self.fullLightVoltagePointer[0]]

    def fullLightVoltageTime2(self):
        """
        Returns time in seconds.
        """
        return self.time[self.fullLightVoltagePointer[1]]

    def fullLightVoltageTimes(self):
        """
        Returns two time values in seconds.
        """
        return (self.fullLightVoltageTime1(), self.fullLightVoltageTime2())

    def setFullLightVoltageTime1(self, time):
        """
        Recalculates absorbance values.
        """
        if len(self.time) < 2:
            return
        start = self.findClosestTimeOffset(time, 0, len(self.time) - 1)
        self.setFullLightVoltagePointer(start, self.fullLightVoltagePointer[1])
        self.recalculateAbsorbances()
        self.dataChanged.emit(self.DATA_CHANGED_ABSORBANCE |
                              self.DATA_CHANGED_FULL_LIGHT_VOLTAGE_TIME_POINTER)

    def setFullLightVoltageTime2(self, time):
        """
        Recalculates absorbance values.
        """
        if len(self.time) < 2:
            return
        stop = self.findClosestTimeOffset(time, 0, len(self.time) - 1)
        self.setFullLightVoltagePointer(self.fullLightVoltagePointer[0], stop)
        self.recalculateAbsorbances()
        self.dataChanged.emit(self.DATA_CHANGED_ABSORBANCE |
                              self.DATA_CHANGED_FULL_LIGHT_VOLTAGE_TIME_POINTER)

    def setFullLightVoltageTimes(self, times, emitDataChangedSignal=True):
        """
        Recalculates absorbance values.
        """
        if len(self.time) < 2:
            return
        start = self.findClosestTimeOffset(times[0], 0, len(self.time) - 1)
        stop = self.findClosestTimeOffset(times[1], 0, len(self.time) - 1)
        self.setFullLightVoltagePointer(start, stop)
        self.recalculateAbsorbances()
        if emitDataChangedSignal:
            self.dataChanged.emit(self.DATA_CHANGED_ABSORBANCE |
                                  self.DATA_CHANGED_FULL_LIGHT_VOLTAGE_TIME_POINTER)

    def setFitAbsorbanceTimePointer(self, start, stop):
        """
        Parameters start and stop are offsets to self.time array.
        """
        if start > stop:
            start, stop = stop, start

        self.fitAbsorbanceTimePointer = [start, stop]
        self.fitdata.clear()

    def fitAbsorbanceTime1(self):
        """
        In seconds
        """
        return self.time[self.fitAbsorbanceTimePointer[0]]

    def fitAbsorbanceTime2(self):
        """
        In seconds
        """
        return self.time[self.fitAbsorbanceTimePointer[1]]

    def fitAbsorbanceTimes(self):
        """
        Returns two time values in seconds.
        """
        return (self.fitAbsorbanceTime1(), self.fitAbsorbanceTime2())

    def setFitAbsorbanceTime1(self, time):
        if len(self.time) < 2:
            return
        start = self.findClosestTimeOffset(time, 0, len(self.time) - 1)
        self.setFitAbsorbanceTimePointer(start, self.fitAbsorbanceTimePointer[1])
        self.dataChanged.emit(self.DATA_CHANGED_FIT_ABSORBANCE |
                              self.DATA_CHANGED_FIT_ABSORBANCE_TIME_POINTER)

    def setFitAbsorbanceTime2(self, time):
        if len(self.time) < 2:
            return
        stop = self.findClosestTimeOffset(time, 0, len(self.time) - 1)
        self.setFitAbsorbanceTimePointer(self.fitAbsorbanceTimePointer[0], stop)
        self.dataChanged.emit(self.DATA_CHANGED_FIT_ABSORBANCE |
                              self.DATA_CHANGED_FIT_ABSORBANCE_TIME_POINTER)

    def setFitAbsorbanceTimes(self, times, emitDataChangedSignal=True):
        if len(self.time) < 2:
            return
        start = self.findClosestTimeOffset(times[0], 0, len(self.time) - 1)
        stop = self.findClosestTimeOffset(times[1], 0, len(self.time) - 1)
        self.setFitAbsorbanceTimePointer(start, stop)
        if emitDataChangedSignal:
            self.dataChanged.emit(self.DATA_CHANGED_FIT_ABSORBANCE |
                                  self.DATA_CHANGED_FIT_ABSORBANCE_TIME_POINTER)

    def onFitChanged(self):
        self.dataChanged.emit(self.DATA_CHANGED_FIT_ABSORBANCE)

    def fit(self, logger):
        self.fitdata.fit(self.fitAbsorbanceTimePointer,
                         self.time,
                         self.absorbance,
                         logger)
