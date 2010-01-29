import csv
from PyQt4 import QtCore, QtGui
from data import Data

class LoadFileTask(QtCore.QThread):
    messageAdded = QtCore.pyqtSignal(QtCore.QString)
    def __init__(self, name, mainWindow, parent = None):
        """
        Parameters
        name: name of the opened file.
        """
        super(LoadFileTask, self).__init__(parent)
        self.name = name
        self.mainWindow = mainWindow
        self.finished.connect(self.postRun)

    def run(self):
        """
        The code in this method is run in another thread.
        """
        # Load data
        reader = csv.reader(open(self.name))
        try:
            self.mainWindow.data.originalData.readFromCsvReader(reader, self.messageAdded.emit)
        except (StopIteration, csv.Error):
            QtGui.QMessageBox.critical(self, "Error while loading file", \
                                           "Error occured when loading " + name)
            return

        self.mainWindow.data.maxPoints = Data.DEFAULT_USED_POINTS_COUNT
        self.messageAdded.emit("Copying %d points from loaded data..." % self.mainWindow.data.maxPoints)
        self.mainWindow.data.fileName = self.name # full path
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
        self.mainWindow.scene.updateFromData()
        self.mainWindow.setWindowTitle(QtCore.QFileInfo(self.name).fileName() + " - flashfit")
        self.mainWindow.settings.onDataLoaded(self.mainWindow.data)
        # Update Recent files in the Main Menu
        self.mainWindow.menuBar().addRecentFile(self.name)        
