from PyQt4 import QtCore, QtGui

class SpinBox(QtGui.QSpinBox):
    valueChangeFinished = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        QtGui.QDockWidget.__init__(self, parent)
        self.editingFinished.connect(self.onEditingFinished)
        
    def onEditingFinished(self):
        self.valueChangeFinished.emit(self.value())
