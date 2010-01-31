from PyQt4 import QtCore, QtGui
from numpy import matrix, matlib, linalg
import numpy
import math
from ngml import ModelABC

class OriginalData:
    """
    Data loaded from input file.
    """

    def __init__(self):
        # The time values from input file.
        # The array might contain several million values.
        # It is used as a source of data.
        self.time = []
        
        # The voltage values measired in time.
        # The array might contain several million values.
        # It is used just as a source of data.
        # The value count is the same as time value count in time array.
        self.voltage = []
        self.minVoltage = None
        self.maxVoltage = None
        self.voltageSpan = None

    def readFromCsvReader(self, reader, logger = None):
        """
        The reader must be opened and valid.
        The method might raise csv.Error
        """
        self.time = []
        self.voltage = []
        self.minVoltage = None
        self.maxVoltage = None
        self.voltageSpan = None

        reader.next() # Row 1 - record length, points
        reader.next() # Row 2 - sample interval
        reader.next() # Row 3 - trigger point, samples
        reader.next() # Row 4 - trigger time
        reader.next() # Row 5 - unknown?
        reader.next() # Row 6 - horizontal offset

        # Read measured data.
        rowCount = 0
        for row in reader:
            rowCount += 1
            if rowCount % 20000 == 0 and logger:
                logger("Loaded %d rows from the input file." % rowCount)
            self.time.append(float(row[3]))
            voltage = float(row[4])
            self.voltage.append(voltage)
            if self.minVoltage == None or self.minVoltage > voltage:
                self.minVoltage = voltage
            if self.maxVoltage == None or self.maxVoltage < voltage:
                self.maxVoltage = voltage

        # Calculate voltageSpan only if some data were present in the input.
        if self.minVoltage != None and self.maxVoltage != None:
            self.voltageSpan = self.maxVoltage - self.minVoltage
                    
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

        # Data loaded from input file.
        self.originalData = OriginalData()
        self.maxPoints = self.DEFAULT_USED_POINTS_COUNT
        self.fileName = "" # Full Path
        self.fileCreated = QtCore.QDateTime()
        
        # Subset of originalData.time
        self.time = []
        self.minTime = None
        self.maxTime = None
        self.timeSpan = None
        # Subset of originalData.voltage
        self.voltage = []
        self.clearAbsorbance()
        # Absorbance fit in time.
        self.absorbanceFitFunction = ModelABC()
        self.clearAbsorbanceFit()
        # Full light voltage
        # Used to calculate absorbance from voltage.
        self.fullLightVoltage = None
        # No light voltage
        # Used to calculate absorbance from voltage.
        self.noLightVoltage = 0.0
        # Full Light Voltage time pointer
        # Both values are offsets to self.time array.
        # self.fullLightVoltage is calculated from this pointers
        self.fullLightVoltagePointer = None
        # Fit Absorbance time pointer
        # Both values are offsets to self.time array.
        self.fitAbsorbanceTimePointer = None

    def clearAbsorbance(self):
        # Absorbance in time.
        self.absorbance = []
        self.minAbsorbance = None
        self.maxAbsorbance = None
        self.absorbanceSpan = None
        self.clearAbsorbanceFit()

    def clearAbsorbanceFit(self):
        self.absorbanceFit = []
        self.p = [] # parameters, also called "k"
        self.sigma_p = [] # accuracy of parameters
        # Residuals in time.
        self.residuals = []
        self.minResiduals = None
        self.maxResiduals = None
        self.residualsSpan = None
        
    def copyFromOriginalData(self):
        """
        numberOfPoints is a maximum number of points to be copied 
        from original data
        """
        maxPoints = len(self.originalData.time)
        idealRatio = maxPoints / float(self.maxPoints)
        self.time = []
        self.minTime = None
        self.maxTime = None
        self.timeSpan = None
        self.voltage = []
        ratio = float('inf')
        for offs in range(0, maxPoints):
            if len(self.time) > 0:
                ratio = offs / float(len(self.time))

            if ratio >= idealRatio:
                #print "copy " + str(offs) + "ratio " + str(ratio) + " ideal " + str(idealRatio)
                # Copy time.
                time = self.originalData.time[offs]
                self.time.append(time)
                if self.minTime == None or self.minTime > time:
                    self.minTime = time
                if self.maxTime == None or self.maxTime < time:
                    self.maxTime = time
                # Copy voltage
                self.voltage.append(self.originalData.voltage[offs])

        if self.maxTime != None and self.minTime != None:
            self.timeSpan = self.maxTime - self.minTime

        # Clear invalid data.
        self.absorbance = None
        self.minAbsorbance = None
        self.maxAbsorbance = None
        self.residuals = None
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
        if self.fullLightVoltage == None:
            return

        vdiff = self.fullLightVoltage - self.noLightVoltage
        if vdiff != 0: # Divide by zero.
            for v in self.voltage: # v is the voltage in time t
                absorbance = -math.log10((v - self.noLightVoltage) / vdiff)
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
        self.dataChanged.emit(self.DATA_CHANGED_ABSORBANCE | self.DATA_CHANGED_FULL_LIGHT_VOLTAGE_TIME_POINTER)

    def setFullLightVoltageTime2(self, time):
        """
        Recalculates absorbance values.
        """
        if len(self.time) < 2:
            return
        stop = self.findClosestTimeOffset(time, 0, len(self.time) - 1)
        self.setFullLightVoltagePointer(self.fullLightVoltagePointer[0], stop)
        self.recalculateAbsorbances()
        self.dataChanged.emit(self.DATA_CHANGED_ABSORBANCE | self.DATA_CHANGED_FULL_LIGHT_VOLTAGE_TIME_POINTER)

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
            self.dataChanged.emit(self.DATA_CHANGED_ABSORBANCE | self.DATA_CHANGED_FULL_LIGHT_VOLTAGE_TIME_POINTER)

    def setFitAbsorbanceTimePointer(self, start, stop):
        """
        Parameters start and stop are offsets to self.time array.
        """
        if start > stop:
            start, stop = stop, start
        
        self.fitAbsorbanceTimePointer = [start, stop]
        self.clearAbsorbanceFit()

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
        self.dataChanged.emit(self.DATA_CHANGED_FIT_ABSORBANCE | self.DATA_CHANGED_FIT_ABSORBANCE_TIME_POINTER)

    def setFitAbsorbanceTime2(self, time):
        if len(self.time) < 2:
            return
        stop = self.findClosestTimeOffset(time, 0, len(self.time) - 1)
        self.setFitAbsorbanceTimePointer(self.fitAbsorbanceTimePointer[0], stop)
        self.dataChanged.emit(self.DATA_CHANGED_FIT_ABSORBANCE | self.DATA_CHANGED_FIT_ABSORBANCE_TIME_POINTER)

    def setFitAbsorbanceTimes(self, times, emitDataChangedSignal=True):
        if len(self.time) < 2:
            return
        start = self.findClosestTimeOffset(times[0], 0, len(self.time) - 1)
        stop = self.findClosestTimeOffset(times[1], 0, len(self.time) - 1)
        self.setFitAbsorbanceTimePointer(start, stop)
        if emitDataChangedSignal:
            self.dataChanged.emit(self.DATA_CHANGED_FIT_ABSORBANCE | self.DATA_CHANGED_FIT_ABSORBANCE_TIME_POINTER)

    def setAbsorbanceFitFunction(self, function):
        self.absorbanceFitFunction = function
        self.clearAbsorbanceFit()
        self.dataChanged.emit(self.DATA_CHANGED_FIT_ABSORBANCE)
                
    def fitAbsorbances(self, logger):
        # Do nothing if no data is loaded.
        if self.fitAbsorbanceTimePointer == None:
            return
        # Prepare input
        # "+ 1" is here to get a slice which also includes pointer[1]
        time = self.time[self.fitAbsorbanceTimePointer[0]:(self.fitAbsorbanceTimePointer[1] + 1)]
        absorbance = self.absorbance[self.fitAbsorbanceTimePointer[0]:(self.fitAbsorbanceTimePointer[1] + 1)]

        (self.p, self.sigma_p, self.absorbanceFit, self.residuals) = self.absorbanceFitFunction.calculate(time, absorbance, logger)
        self.minResiduals = min(self.residuals)
        self.maxResiduals = max(self.residuals)
        self.residualsSpan = self.maxResiduals - self.minResiduals
