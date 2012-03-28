from PyQt4 import QtCore, QtGui
from data import Data
from task import Task

class ChangeModeTask(Task):
    def __init__(self, mode, mainWindow, parent = None):
        """
        """
        super(ChangeModeTask, self).__init__(mainWindow, parent)
        self.mode = mode

        # Set the maxPoints _now_, otherwise two threads are started.
        self.mainWindow.data.originalData.type = self.mode

    def run(self):
        """
        The code in this method is run in another thread.
        """
        # Save fulllightvoltage pointer and fit absorbance pointer
        # time, to be recovered after loading.
        fullLightVoltageTimes = self.mainWindow.data.fullLightVoltageTimes()
        fitTimes = self.mainWindow.data.fitTimes()

        self.messageAdded.emit("Copying {0} points from loaded data...".format(self.mainWindow.data.maxPoints))
        self.mainWindow.data.copyFromOriginalData()

        # Recover fulllightvoltage pointer and fit absorbance pointer times
        self.mainWindow.data.setFullLightVoltageTimes(fullLightVoltageTimes, False)
        self.mainWindow.data.setFitTimes(fitTimes, False)

        self.messageAdded.emit("Computing values...")
        self.mainWindow.data.recalculateValues()

    def postRun(self):
        """
        The code in this method is run in GUI thread.
        """
        self.mainWindow.scene.updateFromData()

    def postTerminated(self):
        """
        The code in this method is run in GUI thread.
        """
        self.mainWindow.data.clear()
        self.mainWindow.setLoadedFilePath("")
        self.mainWindow.settings.onDataLoaded(self.mainWindow.data)
