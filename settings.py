from PyQt4 import QtCore, QtGui
from graphicsscene import GraphicsScene
import ngml
import types

class SpinBox(QtGui.QSpinBox):
    valueChangeFinished = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        QtGui.QDockWidget.__init__(self, parent)
        self.editingFinished.connect(self.onEditingFinished)
        
    def onEditingFinished(self):
        self.valueChangeFinished.emit(self.value())

class Settings(QtGui.QDockWidget):
    modelFunctionChanged = QtCore.pyqtSignal(types.MethodType)

    def __init__(self, parent=None):
        QtGui.QDockWidget.__init__(self, parent)
        self.setTitleBarWidget(QtGui.QWidget())
        self.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea)
        self.setFeatures(QtGui.QDockWidget.NoDockWidgetFeatures)
        
        mainWidget = QtGui.QWidget(self)
        layout = QtGui.QVBoxLayout(mainWidget)
        mainWidget.setLayout(layout)

        # Add model settings
        model = QtGui.QGroupBox("Model", self)
        modelLayout = QtGui.QVBoxLayout(model)
        self.abc = QtGui.QRadioButton("ABC", self)
        self.abc.setChecked(True)
        self.abc.toggled.connect(self.onModelFunctionChanged)
        modelLayout.addWidget(self.abc)
        self.sfo = QtGui.QRadioButton("Single First Order", self)
        self.sfo.toggled.connect(self.onModelFunctionChanged)
        modelLayout.addWidget(self.sfo)
        self.dfo = QtGui.QRadioButton("Dual First Order", self)
        self.dfo.toggled.connect(self.onModelFunctionChanged)
        modelLayout.addWidget(self.dfo)
        self.fit = QtGui.QPushButton("Fit")
        modelLayout.addWidget(self.fit)
        model.setLayout(modelLayout)
        layout.addWidget(model)

        #k1 = QtGui.QDoubleSpinBox(self)
        #layout.addWidget(k1)
        #k2 = QtGui.QDoubleSpinBox(self)
        #layout.addWidget(k2)

        # Add Time Axis Length control
        model = QtGui.QGroupBox("Time Axis Length", self)
        modelLayout = QtGui.QHBoxLayout(model)
        self.timeAxisLength = SpinBox()
        self.timeAxisLength.setRange(GraphicsScene.MIN_WIDTH, GraphicsScene.MAX_WIDTH)
        self.timeAxisLength.setValue(GraphicsScene.DEFAULT_WIDTH)
        modelLayout.addWidget(self.timeAxisLength, 1)
	timeAxisLengthUnits = QtGui.QLabel("px")
	modelLayout.addWidget(timeAxisLengthUnits)
        model.setLayout(modelLayout)
        layout.addWidget(model)

        # Add input data control
        model = QtGui.QGroupBox("Input Data", self)
        modelLayout = QtGui.QVBoxLayout(model)
        measuredPointsLabel = QtGui.QLabel("Measured Point Count:")
        modelLayout.addWidget(measuredPointsLabel)
        self.measuredPoints = QtGui.QLabel("0")
        self.measuredPoints.setAlignment(QtCore.Qt.AlignHCenter)
        modelLayout.addWidget(self.measuredPoints)
        usedPointsLabel = QtGui.QLabel("Used Point Count:")
        modelLayout.addWidget(usedPointsLabel)
        self.usedPoints = SpinBox()
        self.usedPoints.setRange(0, 10000)
        self.usedPoints.setEnabled(False)
        modelLayout.addWidget(self.usedPoints)
        model.setLayout(modelLayout)
        layout.addWidget(model)

        layout.addStretch()
        self.setWidget(mainWidget)

    def onSceneRectChanged(self, rect):
        self.timeAxisLength.setValue(rect.width())

    def onDataLoaded(self, data):
        self.measuredPoints.setText(str(len(data.originalData.time)))
        self.usedPoints.setValue(data.maxPoints)
        self.usedPoints.setRange(10, len(data.originalData.time))
        self.usedPoints.setEnabled(True)

    def onModelFunctionChanged(self):
        if self.abc.isChecked():
            self.modelFunctionChanged.emit(ngml.rcalcABC)
        elif self.sfo.isChecked():
            self.modelFunctionChanged.emit(ngml.rcalcFirst)
        elif self.dfo.isChecked():
            self.modelFunctionChanged.emit(ngml.rcalcFirst2)
        else:
            print "Error while selecting model function."
