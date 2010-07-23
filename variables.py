from PyQt4 import QtCore, QtGui
from font import Font
import pickle
import numbers

class Variable:
    def __init__(self, key, defaultValue):
        self._key = key
        self._defaultValue = defaultValue
        self.type = "normal"
        if isinstance(self._defaultValue, Font):
            self.type = "font"
        elif defaultValue == True or defaultValue == False:
            self.type = "bool"
        elif isinstance(self._defaultValue, numbers.Integral):
            self.type = "int"

    def key(self):
        return self._key;

    def value(self, default=False):
        if default:
            return self._defaultValue

        settings = QtCore.QSettings()

        defaultValue = self._defaultValue
        if self.type == "font":
            defaultValue = self._defaultValue.toStorableString()

        value = settings.value(self._key, defaultValue)
        if self.type == "font":
            f = Font()
            f.fromStorableString(value.toString())
            return f
        elif self.type == "bool":
            return value.toBool()
        elif self.type == "int":
            return value.toInt()[0]

        return value.toPyObject()

    def setValue(self, value):
        settings = QtCore.QSettings()
        if self.type == "font":
            value = value.toStorableString()
        settings.setValue(self._key, QtCore.QVariant(value))

absorbanceAxisValuesFont = Variable("absorbanceAxisValuesFont", Font())
absorbanceAxisCaptionFont = Variable("absorbanceAxisCaptionFont", Font(pointSize = 30))
absorbanceAxisCaptionEnabled = Variable("absorbanceAxisCaptionEnabled", True)
absorbanceAxisCaption = Variable("absorbanceAxisCaption", "absorbance")
timeAxisValuesFont = Variable("timeAxisValuesFont", Font())
timeAxisCaptionFont = Variable("timeAxisCaptionFont", Font(pointSize = 30))
timeAxisCaptionEnabled = Variable("timeAxisCaptionEnabled", True)
timeAxisCaption = Variable("timeAxisCaption", "time")

fullLightBarsVisible = Variable("fullLightBarsVisible", True)
fullLightBarsFont = Variable("fullLightBarsFont", Font(pointSize = 18))
fullLightBarsCaptionEnabled = Variable("fullLightBarsCaptionEnabled", True)
fullLightBarsCaption = Variable("fullLightBarsCaption", "Full light")

absorbanceFitBarsVisible = Variable("absorbanceFitBarsVisible", True)
absorbanceFitBarsFont = Variable("absorbanceFitBarsFont", Font(pointSize = 18))
absorbanceFitBarsCaptionEnabled = Variable("absorbanceFitBarsCaptionEnabled", True)
absorbanceFitBarsCaption = Variable("absorbanceFitBarsCaption", "Absorbance fit")

legendFont = Variable("legendFont", Font(pointSize = 26))
legendDisplayedPrecision = Variable("legendDisplayedPrecision", 6)
