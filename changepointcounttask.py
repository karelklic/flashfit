from PyQt4 import QtCore, QtGui
from data import Data

class ChangePointCountTask(QtCore.QThread):
    messageAdded = QtCore.pyqtSignal(QtCore.QString)
    def __init__(self, pointCount, mainWindow, parent = None):
        """
        """
        super(ChangePointCountTask, self).__init__(parent)
        self.pointCount = pointCount
        self.mainWindow = mainWindow
        self.finished.connect(self.postRun)

        # Set the maxPoints _now_, otherwise two threads are started.
        self.mainWindow.data.maxPoints = self.pointCount

        # Do not act on timeAxisLength changes when loading.
        # Maybe a problem here because it's called from another thread.
        #self.mainWindow.settings.timeAxisLength.valueChangeFinished.disconnect(self.mainWindow.scene.changeWidth)

    def run(self):
        """
        The code in this method is run in another thread.
        """
        # Save fulllightvoltage pointer and fit absorbance pointer time, to be recovered after loading
        fullLightVoltageTimes = self.mainWindow.data.fullLightVoltageTimes()
        fitAbsorbanceTimes = self.mainWindow.data.fitAbsorbanceTimes()

        self.messageAdded.emit("Copying %d points from loaded data..." % self.mainWindow.data.maxPoints)
        self.mainWindow.data.copyFromOriginalData()

        # Recover fulllightvoltage pointer and fit absorbance pointer times
        self.mainWindow.data.setFullLightVoltageTimes(fullLightVoltageTimes, False)
        self.mainWindow.data.setFitAbsorbanceTimes(fitAbsorbanceTimes, False)

        self.messageAdded.emit("Computing absorbance...")
        self.mainWindow.data.recalculateAbsorbances()

    def postRun(self):
        """
        The code in this method is run in GUI thread.
        """
        self.mainWindow.scene.updateFromData()
        # Connect the settings signal back to the slot.
        #self.mainWindow.settings.timeAxisLength.valueChangeFinished.connect(self.mainWindow.scene.changeWidth)
