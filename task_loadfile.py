import csv
import PyQt4
import data
import task

class Task(task.Task):
    def __init__(self, name, mainWindow, parent=None):
        """
        Parameters
        name: name of the opened file.
        """
        super(Task, self).__init__(mainWindow, parent)
        self.name = name

    def run(self):
        """
        The code in this method is run in another thread.
        """
        # Load data
        data = self.mainWindow.data
        odata = data.originalData
        try:
            odata.readFromCsvFile(self.name, self.messageAdded.emit)
        except (StopIteration, csv.Error):
            PyQt4.QtGui.QMessageBox.critical(self, "Error while loading file",
                                             "Error occured when loading " + name)
            return

        data.maxPoints = data.DEFAULT_USED_POINTS_COUNT
        self.messageAdded.emit("Copying {0} points from loaded data...".format(self.mainWindow.data.maxPoints))
        data.fileName = self.name # full path
        data.fileCreated = PyQt4.QtCore.QFileInfo(self.name).lastModified()
        data.copyFromOriginalData()
        data.guessFullLightVoltagePointerValue() # sets fullLightVoltage

        self.messageAdded.emit("Computing values...")
        data.recalculateValues()

        self.messageAdded.emit("Setting fitting pointers")
        data.guessFitTimePointer()

    def postRun(self):
        """
        The code in this method is run in GUI thread.
        """
        # Refresh GUI
        self.mainWindow.scene.updateFromData(True)
        self.mainWindow.setLoadedFilePath(self.name)
        self.mainWindow.settings.onDataLoaded(self.mainWindow.data)
        # Update Recent files in the Main Menu
        if len(self.name) > 0:
            self.mainWindow.menuBar().addRecentFile(self.name)
        self.mainWindow.menuBar().absorbanceModeAct.setChecked(self.mainWindow.data.originalData.type == self.mainWindow.data.originalData.ABSORBANCE)
        self.mainWindow.menuBar().luminiscenceModeAct.setChecked(self.mainWindow.data.originalData.type == self.mainWindow.data.originalData.LUMINISCENCE)

    def postTerminated(self):
        """
        The code in this method is run in GUI thread.
        """
        self.mainWindow.data.clear()
        self.name = ""
