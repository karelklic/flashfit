import csv

class Data:
    """
    Data loaded from input file.
    """

    # Data capturing absorbance over time.
    ABSORBANCE = 1
    # Data capturing luminiscence over time.
    LUMINISCENCE = 2

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
        # Either ABSORBANCE or LUMINISCENCE.
        self.type = None

    def readFromCsvFile(self, path, logger):
        with open(path, "rb") as csvfile:
            dialect = csv.Sniffer().sniff(csvfile.read(2048))
            csvfile.seek(0)
            reader = csv.reader(csvfile, dialect)
            self.readFromCsvReader(reader, logger)

    def readFromCsvReader(self, reader, logger):
        """
        The reader must be opened and valid.
        The method might raise csv.Error
        """
        # Skip file header
        reader.next() # Row 1 - record length, points
        reader.next() # Row 2 - sample interval
        reader.next() # Row 3 - trigger point, samples
        reader.next() # Row 4 - trigger time
        reader.next() # Row 5 - unknown?
        reader.next() # Row 6 - horizontal offset

        # Read measured data.
        self.time = []
        self.voltage = []
        for row in reader:
            if reader.line_num % 20000 == 0:
                logger("Loaded {0} rows from the input file.".format(reader.line_num))
            self.time.append(float(row[3]))
            self.voltage.append(float(row[4]))

        # Save data properties
        self.minVoltage = min(self.voltage)
        self.maxVoltage = max(self.voltage)
        self.voltageSpan = self.maxVoltage - self.minVoltage

        positive = 0
        for value in self.voltage:
            if value > 0:
                positive += 1
        #print "Total:", len(self.voltage), " Positive:", positive
        negative = positive < len(self.voltage) / 2
        self.type = self.ABSORBANCE if negative else self.LUMINISCENCE
