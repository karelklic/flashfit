from PyQt4 import QtCore, QtGui

class Param(QtGui.QWidget):
    """
    Represents one parameter in the Compatible tab.
    """
    def __init__(self, name):
        QtGui.QWidget.__init__(self)
        line1Layout = QtGui.QHBoxLayout()
        line1Layout.setSpacing(0)
        line1Layout.setContentsMargins(0, 0, 0, 0)
        self.enabled = QtGui.QCheckBox(name, self)
        self.enabled.setChecked(True)
        self.enabled.toggled.connect(self.onEnabledToggled)
        line1Layout.addWidget(self.enabled)
        self.value = QtGui.QLineEdit(self)
        self.value.setAlignment(QtCore.Qt.AlignRight)
        self.value.setMaximumWidth(90) # 10 characters
        line1Layout.addWidget(self.value)
        line1 = QtGui.QWidget()
        line1.setLayout(line1Layout)
        line2Layout = QtGui.QHBoxLayout()
        line2Layout.setSpacing(0)
        line2Layout.setContentsMargins(0, 0, 0, 0)
        self.fixed = QtGui.QCheckBox("fixed", self)
        line2Layout.addWidget(self.fixed)
        self.firstOrder = QtGui.QCheckBox("first order", self)
        line2Layout.addWidget(self.firstOrder)
        line2 = QtGui.QWidget()
        line2.setLayout(line2Layout)
        linesLayout = QtGui.QVBoxLayout()
        linesLayout.setSpacing(0)
        linesLayout.setContentsMargins(0, 0, 0, 0)
        linesLayout.addWidget(line1)
        linesLayout.addWidget(line2)
        self.setLayout(linesLayout)

    def onEnabledToggled(self, enabled):
        self.fixed.setEnabled(enabled)
        self.firstOrder.setEnabled(enabled)
        self.value.setEnabled(enabled)
 
class Tab(QtGui.QWidget):
    def __init__(self, mainWindow):
        QtGui.QWidget.__init__(self)
        self.mainWindow = mainWindow
        layout = QtGui.QVBoxLayout(self)
        layout.setSpacing(0)
        self.params = [ Param("Param 1"),
                        Param("Param 2"),
                        Param("Param 3"),
                        Param("Param 4") ]
        for param in self.params:
            layout.addWidget(param)
        self.fit = QtGui.QPushButton("Fit")
        self.fit.clicked.connect(self.onFitClicked)
        layout.addWidget(self.fit)
        self.setLayout(layout)

    def onFitClicked(self):
        self.mainWindow.data.setFitModel(
            self.mainWindow.data.MODEL_COMPATIBLE)
