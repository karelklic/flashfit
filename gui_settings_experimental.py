import PyQt4
import method_experimental

class Tab(PyQt4.QtGui.QWidget):
    def __init__(self, mainWindow):
        PyQt4.QtGui.QWidget.__init__(self)
        self.mainWindow = mainWindow
        layout = PyQt4.QtGui.QVBoxLayout(self)
        self.abc = PyQt4.QtGui.QRadioButton(method_experimental.ModelAtoBtoC.NAME, self)
        self.abc.setChecked(True)
        self.sfo = PyQt4.QtGui.QRadioButton(method_experimental.ModelAtoB.NAME, self)
        self.dfo = PyQt4.QtGui.QRadioButton(method_experimental.ModelAtoBCtoD.NAME, self)
        for model in [self.abc, self.sfo, self.dfo]:
            model.toggled.connect(self.onModelFunctionChanged)
            layout.addWidget(model)
        self.fit = PyQt4.QtGui.QPushButton("Fit")
        self.fit.clicked.connect(self.onFitClicked)
        layout.addStretch(0)
        layout.addWidget(self.fit)
        self.setLayout(layout)

    def onModelFunctionChanged(self):
        fitdata = self.mainWindow.data.fitdata
        if self.abc.isChecked():
            fitdata.setInput(method_experimental.ModelAtoBtoC())
        elif self.sfo.isChecked():
            fitdata.setInput(method_experimental.ModelAtoB())
        elif self.dfo.isChecked():
            fitdata.setInput(method_experimental.ModelAtoBCtoD())
        else:
            print "Error while selecting model function."

    def onFitClicked(self):
        self.onModelFunctionChanged()
        fitdata = self.mainWindow.data.fitdata
        fitdata.setModel(fitdata.MODEL_EXPERIMENTAL)
