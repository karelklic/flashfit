from PyQt4 import QtCore, QtGui
from data import Data

class FitTask(QtCore.QThread):
    messageAdded = QtCore.pyqtSignal(QtCore.QString)
    def __init__(self, mainWindow, parent = None):
        super(FitTask, self).__init__(parent)
        self.mainWindow = mainWindow
        self.finished.connect(self.postRun)

    def run(self):
        """
        The code in this method is run in another thread.
        """
        self.messageAdded.emit("Fitting absorbance")
        self.mainWindow.data.fitAbsorbances(self.messageAdded.emit)

    def postRun(self):
        """
        The code in this method is run in GUI thread.
        """
        # Refresh GUI
        self.mainWindow.scene.updateAbsorbanceFit()
        self.mainWindow.scene.updateResidualsGraph()
        self.mainWindow.scene.informationTable.recreateFromData()
