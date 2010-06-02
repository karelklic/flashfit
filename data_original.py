
class Data:
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
