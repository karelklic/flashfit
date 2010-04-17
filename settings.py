from PyQt4 import QtCore, QtGui
from graphicsscene import GraphicsScene
from ngml import ModelABC, ModelFirst, ModelFirst2
from spinbox import SpinBox
import types

class Settings(QtGui.QDockWidget):
    """
    Settings panel docked on the left side of the main window.
    """
    def __init__(self, parentWindow):
        QtGui.QDockWidget.__init__(self, parentWindow)
        self.setTitleBarWidget(QtGui.QWidget())
        self.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea)
        self.setFeatures(QtGui.QDockWidget.NoDockWidgetFeatures)
        
        mainWidget = QtGui.QWidget(self)
        layout = QtGui.QVBoxLayout(mainWidget)
        mainWidget.setLayout(layout)

        # Add model settings
        model = QtGui.QGroupBox("Model", self)
        modelLayout = QtGui.QVBoxLayout(model)
        self.abc = QtGui.QRadioButton(ModelABC.name, self)
        self.abc.setChecked(True)
        self.sfo = QtGui.QRadioButton(ModelFirst.name, self)
        self.dfo = QtGui.QRadioButton(ModelFirst2.name, self)
        for m in [self.abc, self.sfo, self.dfo]:
            m.toggled.connect(self.onModelFunctionChanged)
            modelLayout.addWidget(m)

        self.implementation = QtGui.QCheckBox("Alt. impl.", self)
        self.implementation.setChecked(False)
        self.implementation.toggled.connect(self.onImplementationChanged)
        modelLayout.addWidget(self.implementation)
        self.fit = QtGui.QPushButton("Fit")
        modelLayout.addWidget(self.fit)
        model.setLayout(modelLayout)
        layout.addWidget(model)

        #k1 = QtGui.QDoubleSpinBox(self)
        #layout.addWidget(k1)
        #k2 = QtGui.QDoubleSpinBox(self)
        #layout.addWidget(k2)

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

        # Output
        model = QtGui.QGroupBox("Output", self)
        modelLayout = QtGui.QVBoxLayout(model)
        timeAxisLengthLabel = QtGui.QLabel("Time Axis Length:")
        modelLayout.addWidget(timeAxisLengthLabel)

        # Add Time Axis Length control
        timeAxisLengthModel = QtGui.QWidget()
        timeAxisLengthModelLayout = QtGui.QHBoxLayout(timeAxisLengthModel)
        self.timeAxisLength = SpinBox()
        self.timeAxisLength.setRange(GraphicsScene.MIN_WIDTH, GraphicsScene.MAX_WIDTH)
        self.timeAxisLength.setValue(GraphicsScene.DEFAULT_WIDTH)
        timeAxisLengthModelLayout.addWidget(self.timeAxisLength, 1)
	timeAxisLengthUnits = QtGui.QLabel("px")
	timeAxisLengthModelLayout.addWidget(timeAxisLengthUnits)
        timeAxisLengthModel.setLayout(timeAxisLengthModelLayout)
        modelLayout.addWidget(timeAxisLengthModel)
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
            self.parent().data.setAbsorbanceFitFunction(ModelABC())
        elif self.sfo.isChecked():
            self.parent().data.setAbsorbanceFitFunction(ModelFirst())
        elif self.dfo.isChecked():
            self.parent().data.setAbsorbanceFitFunction(ModelFirst2())
        else:
            print "Error while selecting model function."

    def onImplementationChanged(self):
        impl = 0
        if self.implementation.isChecked():
            impl = 1
        self.parent().data.setAbsorbanceFitImplementation(impl)
