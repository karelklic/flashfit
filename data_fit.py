import PyQt4
import method_experimental
import method_compatible
import data_fit_parameter

class Residuals:
    def __init__(self, values = None):
        if values == None:
            self.clear()
        else:
            self.setValues(values)

    def clear(self):
        self.values = []
        self.min = None
        self.max = None
        self.span = 0

    def setValues(self, values):
        self.values = values
        self.min = min(self.values)
        self.max = max(self.values)
        self.span = self.max - self.min

class Fit(PyQt4.QtCore.QObject):
    """
    Absorbance fit.
    """
    changed = PyQt4.QtCore.pyqtSignal()

    def __init__(self):
        PyQt4.QtCore.QObject.__init__(self)
        self.residuals = Residuals()
        self.input = 0
        self.model = 0
        self.clear()

    def clear(self):
        self.values = []
        self.parameters = [] # also called "k"
        self.ainf = None
        self.modelName = None
        self.residuals.clear()

    def setInput(self, _input):
        self.input = _input
        self.clear()
        self.changed.emit()

    MODEL_COMPATIBLE = 1
    MODEL_EXPERIMENTAL = 2
    def setModel(self, model):
        self.model = model
        self.clear()
        self.changed.emit()

    def fit(self, fitAbsorbanceTimePointer, time, absorbance, logger):
        # Do nothing if no data is loaded.
        if fitAbsorbanceTimePointer == None:
            return
        # Prepare input
        # "+ 1" is here to get a slice which also includes pointer[1]
        timeSpan = time[fitAbsorbanceTimePointer[0]:(fitAbsorbanceTimePointer[1] + 1)]
        absorbanceSpan = absorbance[fitAbsorbanceTimePointer[0]:(fitAbsorbanceTimePointer[1] + 1)]

        if self.model == self.MODEL_COMPATIBLE:
            out = method_compatible.ngml(timeSpan,
                                         absorbanceSpan,
                                         self.input,
                                         logger)
            self.parameters = out[0]
            self.values = out[1]
            self.residuals = out[2]
            self.ainf = out[3]
        elif self.model == self.MODEL_EXPERIMENTAL:
            self.modelName = self.input.NAME
            out = method_experimental.ngml(timeSpan,
                                           absorbanceSpan,
                                           self.input,
                                           logger)
            self.parameters = out[0]
            self.values = out[1]
            self.residuals = out[2]
            self.ainf = out[3]
