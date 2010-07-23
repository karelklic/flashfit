from PyQt4 import QtCore, QtGui
from gui_graphicsscene import GraphicsScene
from gui_spinbox import SpinBox
import gui_settings_experimental
import gui_settings_compatible

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
        (left, top, right, bottom) = model.getContentsMargins()
        model.setContentsMargins(0, top, 0, bottom)
        modelLayout = QtGui.QVBoxLayout()
        tab = QtGui.QTabWidget(self)
        # Add tabs
        self.experimental = gui_settings_experimental.Tab(parentWindow)
        tab.addTab(self.experimental, "Experimental")
        self.compatible = gui_settings_compatible.Tab(parentWindow)
        tab.addTab(self.compatible, "Compatible")
        modelLayout.addWidget(tab)
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
        self.timeAxisLength.setValue(self.parent().scene.sceneWidth)

    def onDataLoaded(self, data):
        self.measuredPoints.setText(str(len(data.originalData.time)))
        self.usedPoints.setValue(data.maxPoints)
        self.usedPoints.setRange(10, len(data.originalData.time))
        self.usedPoints.setEnabled(True)
