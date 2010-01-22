from PyQt4 import QtCore, QtGui
import math

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

    def readFromCsvReader(self, reader):
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
        for row in reader:
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

    def __init__(self, parent=None):
        """
        No data is present after init.
        """
        QtCore.QObject.__init__(self, parent)

        # Data loaded from input file.
        self.originalData = OriginalData()

        self.maxPoints = self.DEFAULT_USED_POINTS_COUNT
        
        # Subset of originalData.time
        self.time = []
        self.minTime = None
        self.maxTime = None
        self.timeSpan = None
        # Subset of originalData.voltage
        self.voltage = []
        # Absorbance in time.
        self.absorbance = []
        self.minAbsorbance = None
        self.maxAbsorbance = None
        self.absorbanceSpan = None
        # Residuals in time.
        self.residuals = []
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
        # Recalculate absorbance from voltage.
        self.absorbance = []
        self.minAbsorbance = None
        self.maxAbsorbance = None
        self.absorbanceSpan = None

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
        # TODO: real algorithm here
        self.setFullLightVoltagePointer(0, 10)

    def guessFitAbsorbanceTimePointer(self):
        """
        Takes time and voltage waveform, and tries to determine which part of
        the waveform should be fitted by a curve.
        """
        # TODO: real algorithm here
        self.setFitAbsorbanceTimePointer(15, 30)

    def setFullLightVoltagePointer(self, start, stop):
        if start > stop:
            start, stop = stop, start

        self.fullLightVoltagePointer = (start, stop)
        
        # Calculate the arithmetic mean voltage from it.
        sum = 0.0
        for i in range(start, stop):
            sum += self.voltage[i]
        self.fullLightVoltage = sum / float(stop - start + 1)

    def fullLightVoltageTime1(self):
        """
        In seconds
        """
        return self.time[self.fullLightVoltagePointer[0]]

    def fullLightVoltageTime2(self):
        """
        In seconds
        """
        return self.time[self.fullLightVoltagePointer[1]]

    def setFitAbsorbanceTimePointer(self, start, stop):
        if start > stop:
            start, stop = stop, start
        
        self.fitAbsorbanceTimePointer = (start, stop)

        # Calculate something from it.
        pass

    def fitAbsorbanceTime1(self):
        """
        In seconds
        """
        return self.time[self.fullLightVoltagePointer[0]]

    def fitAbsorbanceTime2(self):
        """
        In seconds
        """
        return self.time[self.fullLightVoltagePointer[1]]
