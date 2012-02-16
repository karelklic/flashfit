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
    DATA_CHANGED_VALUES = 0x01
    DATA_CHANGED_FULL_LIGHT_VOLTAGE_TIME_POINTER = 0x02
    DATA_CHANGED_FIT = 0x04
    DATA_CHANGED_FIT_TIME_POINTER = 0x08
    dataChanged = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        """
        No data is present after init.
        """
        QtCore.QObject.__init__(self, parent)
        self.absorbanceData = AbsorbanceData(self)
        self.luminiscenceData = LuminiscenceData(self)
        self.clear()

    def clear(self):
        """
        Sets nice initial state of the data.
        """
        self.maxPoints = self.DEFAULT_USED_POINTS_COUNT
        self.fileName = "" # Full Path
        self.fileCreated = QtCore.QDateTime()

        # Absorbance/luminiscence fit in time.
        self.fitdata = data_fit.Fit()
        self.fitdata.changed.connect(self.onFitChanged)

        # Data loaded from input file. When empty, initialize it to show some simple curve.
        self.originalData = data_original.Data()
        POINT_COUNT = 2000
        self.originalData.time = [(x / float(POINT_COUNT)) for x in range(0, POINT_COUNT)]
        self.originalData.voltage = [100] * int(POINT_COUNT * 0.2)
        self.originalData.voltage += [40 + (60 * i) / (POINT_COUNT * 0.6) for i in range(0, int(POINT_COUNT * 0.6))]
        self.originalData.voltage += [100] * int(POINT_COUNT - len(self.originalData.voltage))
        self.originalData.minVoltage = 40
        self.originalData.maxVoltage = 100
        self.originalData.voltageSpan = 60
        self.originalData.type = self.originalData.ABSORBANCE
        self.copyFromOriginalData()

        self.fullLightVoltage = None
        self.fullLightVoltagePointer = None

        self.clearValues()

        # Full Light Voltage time pointer
        # Both values are offsets to self.time array.
        # self.fullLightVoltage is calculated from this pointers
        # Full light voltage is used to calculate absorbance from voltage.
        self.setFullLightVoltagePointer(int(0.05 * POINT_COUNT),
                                        int(0.15 * POINT_COUNT))

        # Fit time pointer
        # Both values are offsets to self.time array.
        self.setFitTimePointer(int(0.25 * POINT_COUNT),
                               int(0.70 * POINT_COUNT))

        self.absorbanceData.recalculateAbsorbances()

    def clearValues(self):
        """
        Clear values measured in time.
        """
        self.values = []
        self.minValue = float("inf")
        self.maxValue = float("-inf")
        self.valueSpan = float("inf")
        self.fitdata.clear()

    def recalculateValues(self):
        if self.originalData.type == self.originalData.ABSORBANCE:
            self.absorbanceData.recalculateAbsorbances()
        else:
            self.luminiscenceData.recalculateLuminiscence()

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
        self.fitTimePointer = None

        self.fullLightVoltage = None
        self.fullLightVoltagePointer = None

        # Clear invalid data.
        self.clearValues()

    def guessFitTimePointer(self):
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
        self.setFitTimePointer(start, end)

    def findClosestTimeOffset(self, time, minOffset, maxOffset):
        if maxOffset - minOffset == 1:
            if (time - self.time[minOffset]) < (self.time[maxOffset] - time):
                return minOffset
            return maxOffset

        middleOffset = minOffset + (maxOffset - minOffset) / 2
        middleTime = self.time[middleOffset]
        if time < middleTime:
            return self.findClosestTimeOffset(time, minOffset, middleOffset)
        return self.findClosestTimeOffset(time, middleOffset, maxOffset)

    def setFitTimePointer(self, start, stop):
        """
        Parameters start and stop are offsets to self.time array.
        """
        if start > stop:
            start, stop = stop, start

        self.fitTimePointer = [start, stop]
        self.fitdata.clear()

    def fitTime1(self):
        """
        In seconds
        """
        return self.time[self.fitTimePointer[0]]

    def fitTime2(self):
        """
        In seconds
        """
        return self.time[self.fitTimePointer[1]]

    def fitTimes(self):
        """
        Returns two time values in seconds.
        """
        return (self.fitTime1(), self.fitTime2())

    def setFitTime1(self, time):
        if len(self.time) < 2:
            return
        start = self.findClosestTimeOffset(time, 0, len(self.time) - 1)
        self.setFitTimePointer(start, self.fitTimePointer[1])
        self.dataChanged.emit(self.DATA_CHANGED_FIT |
                              self.DATA_CHANGED_FIT_TIME_POINTER)

    def setFitTime2(self, time):
        if len(self.time) < 2:
            return
        stop = self.findClosestTimeOffset(time, 0, len(self.time) - 1)
        self.setFitTimePointer(self.fitTimePointer[0], stop)
        self.dataChanged.emit(self.DATA_CHANGED_FIT |
                              self.DATA_CHANGED_FIT_TIME_POINTER)

    def setFitTimes(self, times, emitDataChangedSignal=True):
        if len(self.time) < 2:
            return
        start = self.findClosestTimeOffset(times[0], 0, len(self.time) - 1)
        stop = self.findClosestTimeOffset(times[1], 0, len(self.time) - 1)
        self.setFitTimePointer(start, stop)
        if emitDataChangedSignal:
            self.dataChanged.emit(self.DATA_CHANGED_FIT |
                                  self.DATA_CHANGED_FIT_TIME_POINTER)

    def onFitChanged(self):
        self.dataChanged.emit(self.DATA_CHANGED_FIT)

    def fit(self, logger):
        self.fitdata.fit(self.fitTimePointer,
                         self.time,
                         self.values,
                         logger)

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

        if self.originalData.type == self.originalData.ABSORBANCE:
            self.clearValues()

    def fullLightVoltageTime1(self):
        """
        Returns time in seconds.
        """
        assert self.fullLightVoltagePointer[0] >= 0 and \
            self.fullLightVoltagePointer[0] < len(self.time), \
            "FullLight pointer invalid: %d, time length %d" % \
            (self.fullLightVoltagePointer[0], len(self.time))
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

        if self.originalData.type == self.originalData.ABSORBANCE:
            self.recalculateAbsorbances()
            self.dataChanged.emit(self.DATA_CHANGED_VALUES |
                                  self.DATA_CHANGED_FULL_LIGHT_VOLTAGE_TIME_POINTER)
        else:
            self.dataChanged.emit(self.DATA_CHANGED_FULL_LIGHT_VOLTAGE_TIME_POINTER)

    def setFullLightVoltageTime2(self, time):
        """
        Recalculates absorbance values.
        """
        if len(self.time) < 2:
            return
        stop = self.findClosestTimeOffset(time, 0, len(self.time) - 1)
        self.setFullLightVoltagePointer(self.fullLightVoltagePointer[0], stop)

        if self.originalData.type == self.originalData.ABSORBANCE:
            self.absorbanceData.recalculateAbsorbances()
            self.dataChanged.emit(self.DATA_CHANGED_VALUES |
                                  self.DATA_CHANGED_FULL_LIGHT_VOLTAGE_TIME_POINTER)
        else:
            self.dataChanged.emit(self.DATA_CHANGED_FULL_LIGHT_VOLTAGE_TIME_POINTER)

    def setFullLightVoltageTimes(self, times, emitDataChangedSignal=True):
        """
        Recalculates absorbance values.
        """
        if len(self.time) < 2:
            return
        start = self.findClosestTimeOffset(times[0], 0, len(self.time) - 1)
        stop = self.findClosestTimeOffset(times[1], 0, len(self.time) - 1)
        self.setFullLightVoltagePointer(start, stop)

        if self.originalData.type == self.originalData.ABSORBANCE:
            self.absorbanceData.recalculateAbsorbances()

            if emitDataChangedSignal:
                self.dataChanged.emit(self.DATA_CHANGED_VALUES |
                                      self.DATA_CHANGED_FULL_LIGHT_VOLTAGE_TIME_POINTER)
        else:
            if emitDataChangedSignal:
                self.dataChanged.emit(self.DATA_CHANGED_FULL_LIGHT_VOLTAGE_TIME_POINTER)

class AbsorbanceData:
    def __init__(self, data):
        # All instance attributes must be initialized here.
        self.data = data
        # No light voltage
        # Used to calculate absorbance from voltage.
        self.noLightVoltage = 0.0

    def recalculateAbsorbances(self):
        """
        Recalculates all absorbance values!
        Also updates minValue and maxValue values
        Slow!
        """
        self.data.clearValues()
        # If we do not know full light voltage, we are done.
        if self.data.fullLightVoltage is None:
            return

        vdiff = self.data.fullLightVoltage - self.noLightVoltage
        if vdiff != 0: # Divide by zero.
            for v in self.data.voltage: # v is the voltage in time t
                try:
                    absorbance = -math.log10((v - self.noLightVoltage) / vdiff)
                except ValueError as error:
                    print error, "; voltage:", v - self.noLightVoltage, "vdiff:", vdiff
                    absorbance = 0

                self.data.values.append(absorbance)
        self.data.minValue = min(self.data.values)
        self.data.maxValue = max(self.data.values)
        self.data.valueSpan = self.data.maxValue - self.data.minValue

class LuminiscenceData:
    def __init__(self, data):
        self.data = data

    def recalculateLuminiscence(self):
        self.data.clearValues()

        maxVoltage = max(self.data.voltage)
        minVoltage = min(self.data.voltage)
        spanVoltage = abs(maxVoltage - minVoltage)
        for v in self.data.voltage:
            luminiscence = (v - minVoltage) / spanVoltage

            luminiscence = -luminiscence + 1.0
            self.data.values.append(luminiscence)

        self.data.minValue = min(self.data.values)
        self.data.maxValue = max(self.data.values)
        self.data.valueSpan = self.data.maxValue - self.data.minValue
