import csv
from PyQt4 import QtCore, QtGui
from data import Data
from task import Task

class LoadFileTask(Task):
    def __init__(self, name, mainWindow, parent = None):
        """
        Parameters
        name: name of the opened file.
        """
        super(LoadFileTask, self).__init__(mainWindow, parent)
        self.name = name

    def run(self):
        """
        The code in this method is run in another thread.
        """
        # Load data
        reader = csv.reader(open(self.name))
        try:
            self.mainWindow.data.originalData.readFromCsvReader(reader, self.messageAdded.emit)
        except (StopIteration, csv.Error):
            QtGui.QMessageBox.critical(self, "Error while loading file",
                                       "Error occured when loading " + name)
            return

        self.mainWindow.data.maxPoints = Data.DEFAULT_USED_POINTS_COUNT
        self.messageAdded.emit("Copying %d points from loaded data..." % self.mainWindow.data.maxPoints)
        self.mainWindow.data.fileName = self.name # full path
        self.mainWindow.data.fileCreated = QtCore.QFileInfo(self.name).lastModified()
        self.mainWindow.data.copyFromOriginalData()
        self.messageAdded.emit("Computing absorbance...")
        self.mainWindow.data.guessFullLightVoltagePointerValue() # sets fullLightVoltage
        self.mainWindow.data.recalculateAbsorbances()
        self.messageAdded.emit("Setting fit absorbance pointers")
        self.mainWindow.data.guessFitAbsorbanceTimePointer()

    def postRun(self):
        """
        The code in this method is run in GUI thread.
        """
        # Refresh GUI
        self.mainWindow.scene.updateFromData(True)
        self.mainWindow.setLoadedFilePath(self.name)
        self.mainWindow.settings.onDataLoaded(self.mainWindow.data)
        # Update Recent files in the Main Menu
        self.mainWindow.menuBar().addRecentFile(self.name)
