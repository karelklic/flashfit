from PyQt4 import QtCore, QtGui

class Task(QtCore.QThread):
    messageAdded = QtCore.pyqtSignal(QtCore.QString)

    def __init__(self, mainWindow, parent = None):
        super(Task, self).__init__(parent)
        self.mainWindow = mainWindow
        self.finished.connect(self.postRun)
        self.terminated.connect(self.postTerminated)

    def run(self):
        """
        The code in this method is run in another thread.
        """
        pass

    def postRun(self):
        """
        The code in this method is run in GUI thread.
        """
        pass

    def postTerminated(self):
        """
        The code in this method is run in GUI thread.
        """
        pass
