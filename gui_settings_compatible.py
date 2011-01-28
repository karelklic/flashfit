import PyQt4
import method_compatible

class Param(PyQt4.QtGui.QWidget):
    """
    Represents one parameter in the Compatible tab.
    """
    def __init__(self, name):
        PyQt4.QtGui.QWidget.__init__(self)
        line1Layout = PyQt4.QtGui.QHBoxLayout()
        line1Layout.setSpacing(0)
        line1Layout.setContentsMargins(0, 0, 0, 0)
        self.enabled = PyQt4.QtGui.QCheckBox(name, self)
        self.enabled.toggled.connect(self.onEnabledToggled)
        line1Layout.addWidget(self.enabled)
        self.value = PyQt4.QtGui.QLineEdit("0", self)
        self.value.setAlignment(PyQt4.QtCore.Qt.AlignRight)
        self.value.setMaximumWidth(90) # 10 characters
        line1Layout.addWidget(self.value)
        line1 = PyQt4.QtGui.QWidget()
        line1.setLayout(line1Layout)
        line2Layout = PyQt4.QtGui.QHBoxLayout()
        line2Layout.setSpacing(0)
        line2Layout.setContentsMargins(0, 0, 0, 0)
        self.fixed = PyQt4.QtGui.QCheckBox("fixed", self)
        line2Layout.addWidget(self.fixed)
        self.order = PyQt4.QtGui.QComboBox(self)
        self.order.addItem("1st order")
        self.order.addItem("2nd order")
        line2Layout.addWidget(self.order)
        line2 = PyQt4.QtGui.QWidget()
        line2.setLayout(line2Layout)
        linesLayout = PyQt4.QtGui.QVBoxLayout()
        linesLayout.setSpacing(0)
        linesLayout.setContentsMargins(0, 0, 0, 0)
        linesLayout.addWidget(line1)
        linesLayout.addWidget(line2)
        self.onEnabledToggled(self.enabled.isChecked())
        self.setLayout(linesLayout)

    def onEnabledToggled(self, checked):
        self.fixed.setEnabled(checked)
        self.order.setEnabled(checked)
        self.value.setEnabled(checked)

class Tab(PyQt4.QtGui.QWidget):
    def __init__(self, mainWindow):
        PyQt4.QtGui.QWidget.__init__(self)
        self.mainWindow = mainWindow
        layout = PyQt4.QtGui.QVBoxLayout(self)
        layout.setSpacing(0)
        self.params = [ Param("Param 1"),
                        Param("Param 2"),
                        Param("Param 3"),
                        Param("Param 4") ]

        self.params[0].enabled.toggle()
        for param in self.params:
            param.enabled.toggled.connect(self.rebuildInput)
            param.value.editingFinished.connect(self.rebuildInput)
            param.fixed.toggled.connect(self.rebuildInput)
            param.order.currentIndexChanged.connect(self.rebuildInput)
            layout.addWidget(param)

        self.fit = PyQt4.QtGui.QPushButton("Fit")
        self.fit.clicked.connect(self.onFitClicked)
        self.rebuildInput()
        layout.addWidget(self.fit)
        self.setLayout(layout)

    def rebuildInput(self):
        params = []
        failure = False
        for guiparam in self.params:
            if not guiparam.enabled.isChecked():
                guiparam.value.setStyleSheet("")
                continue
            param = method_compatible.Parameter()
            try:
                param.value = float(guiparam.value.text())
                guiparam.value.setStyleSheet("")
            except ValueError:
                guiparam.value.setStyleSheet("background-color:red")
                failure = True

            param.fixed = guiparam.fixed.isChecked()
            param.firstOrder = guiparam.order.currentIndex() == 0
            params.append(param)

        failure = failure or len(params) == 0
        self.fit.setEnabled(not failure)
        if not failure:
            fitdata = self.mainWindow.data.fitdata
            fitdata.setInput(params)

    def onFitClicked(self):
        self.rebuildInput()
        fitdata = self.mainWindow.data.fitdata
        fitdata.setModel(fitdata.MODEL_COMPATIBLE)
