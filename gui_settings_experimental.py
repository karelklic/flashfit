import PyQt4
import method_experimental

class Model(PyQt4.QtGui.QWidget):
    def __init__(self, model, parent):
        PyQt4.QtGui.QWidget.__init__(self)
        self.model = model
        layout = PyQt4.QtGui.QVBoxLayout(self)
        for parameter in self.model.parameters:
            lineLayout = PyQt4.QtGui.QHBoxLayout()
            lineLayout.setSpacing(0)
            lineLayout.setContentsMargins(0, 0, 0, 0)
            parameter.guivalue = PyQt4.QtGui.QLineEdit("0", self)
            parameter.guivalue.setAlignment(PyQt4.QtCore.Qt.AlignRight)
            parameter.guivalue.setMaximumWidth(90) # 10 characters
            parameter.guivalue.editingFinished.connect(self.updateModel)
            lineLayout.addWidget(parameter.guivalue)
            parameter.guifixed = PyQt4.QtGui.QCheckBox("fixed", self)
            parameter.guifixed.toggled.connect(self.updateModel)
            lineLayout.addWidget(parameter.guifixed)
            line = PyQt4.QtGui.QWidget(self)
            line.setLayout(lineLayout)
            layout.addWidget(line)
        self.setLayout(layout)

    def updateModel(self):
        failure = False
        for parameter in self.model.parameters:
            try:
                parameter.value = float(parameter.guivalue.text())
                parameter.guivalue.setStyleSheet("")
            except ValueError:
                parameter.guivalue.setStyleSheet("background-color:red")
                failure = True
            parameter.fixed = parameter.guifixed.isChecked()
        self.parent().fit.setEnabled(not failure)

class Tab(PyQt4.QtGui.QWidget):
    def __init__(self, mainWindow):
        PyQt4.QtGui.QWidget.__init__(self)
        self.mainWindow = mainWindow
        self.models = [ method_experimental.ModelAtoBtoC(),
                        method_experimental.ModelAtoB(),
                        method_experimental.ModelAtoBCtoD() ]
        layout = PyQt4.QtGui.QVBoxLayout(self)
        #
        # Model Selection combo box
        #
        self.selection = PyQt4.QtGui.QComboBox()
        layout.addWidget(self.selection)
        for model in self.models:
            self.selection.addItem(model.NAME, model)
            model.widget = Model(model, self)
            layout.addWidget(model.widget)
            model.widget.hide()
        self.selection.currentIndexChanged.connect(self.onModelChanged)
        model = self.selection.itemData(self.selection.currentIndex()).toPyObject()
        model.widget.show()
        #
        # Fit button
        #
        self.fit = PyQt4.QtGui.QPushButton("Fit")
        self.fit.clicked.connect(self.onFitClicked)
        layout.addStretch(0)
        layout.addWidget(self.fit)
        self.setLayout(layout)

    def onModelChanged(self):
        for model in self.models:
            model.widget.hide()
        model = self.selection.itemData(self.selection.currentIndex()).toPyObject()
        model.widget.show()
        model.widget.updateModel()
        self.mainWindow.data.fitdata.setInput(model)

    def onFitClicked(self):
        self.onModelChanged()
        fitdata = self.mainWindow.data.fitdata
        fitdata.setModel(fitdata.MODEL_EXPERIMENTAL)
