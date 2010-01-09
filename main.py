#!/usr/bin/python

import sys, csv, math
from PyQt4 import QtCore, QtGui
from data import Data
from graphicsscene import GraphicsScene
from graphicsview import GraphicsView

class SpinBox(QtGui.QSpinBox):
    valueChangeFinished = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        QtGui.QDockWidget.__init__(self, parent)
        self.editingFinished.connect(self.__editingFinished)
        
    def __editingFinished(self):
        self.valueChangeFinished.emit(self.value())

class Settings(QtGui.QDockWidget):
    def __init__(self, parent=None):
        QtGui.QDockWidget.__init__(self, parent)
        #self.setWindowTitle("Settings")
        self.setTitleBarWidget(QtGui.QWidget())
        self.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea)
        self.setFeatures(QtGui.QDockWidget.NoDockWidgetFeatures)
        
        mainWidget = QtGui.QWidget(self)
        layout = QtGui.QVBoxLayout(mainWidget)
        mainWidget.setLayout(layout)

        # Add model settings
        model = QtGui.QGroupBox("Model", self)
        modelLayout = QtGui.QVBoxLayout(model)
        abc = QtGui.QRadioButton("ABC", self)
        abc.setChecked(True)
        modelLayout.addWidget(abc)
        sfo = QtGui.QRadioButton("Single First Order", self)
        modelLayout.addWidget(sfo)
        dfo = QtGui.QRadioButton("Dual First Order", self)
        modelLayout.addWidget(dfo)
        model.setLayout(modelLayout)
        layout.addWidget(model)

        k1 = QtGui.QDoubleSpinBox(self)
        layout.addWidget(k1)
        k2 = QtGui.QDoubleSpinBox(self)
        layout.addWidget(k2)

        # Add Time Axis Length control
        model = QtGui.QGroupBox("Time Axis Length", self)
        modelLayout = QtGui.QHBoxLayout(model)
        self.timeAxisLength = SpinBox()
        self.timeAxisLength.setRange(GraphicsScene.MIN_WIDTH, GraphicsScene.MAX_WIDTH)
        self.timeAxisLength.setValue(GraphicsScene.DEFAULT_WIDTH)
        modelLayout.addWidget(self.timeAxisLength)
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

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setWindowTitle("flashfit")

        fileMenu = self.menuBar().addMenu("&File")

        openAct = QtGui.QAction("&Open", self)
        openAct.setShortcut("Ctrl+O")
        openAct.triggered.connect(self.openFile)
        fileMenu.addAction(openAct)

        saveAct = QtGui.QAction("&Save as image", self)
        saveAct.setShortcut("Ctrl+S")
        fileMenu.addAction(saveAct)
        fileMenu.addSeparator()

        # Recent Files
        self.recentFileActs = []
        for i in range(0, 5):
            act = QtGui.QAction(self)
            act.setVisible(False)
            act.triggered.connect(self.openRecentFile)
            fileMenu.addAction(act)
            self.recentFileActs.append(act)

        self.separatorAct = fileMenu.addSeparator() # used by RecentFile
        self.updateRecentFileActions()

        # The rest of File Menu
        quitAct = QtGui.QAction("&Quit", self)
        quitAct.setShortcut("Ctrl+Q")
        quitAct.triggered.connect(self.close)
        fileMenu.addAction(quitAct)       

        self.settings = Settings(self)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.settings)

        self.data = Data()
        self.scene = GraphicsScene(self)
        self.scene.sceneRectChanged.connect(self.settings.onSceneRectChanged)
        self.settings.timeAxisLength.valueChangeFinished.connect(self.scene.changeWidth)
        self.settings.usedPoints.valueChangeFinished.connect(self.reloadFromOriginalData)
        self.view = GraphicsView(self.scene)
        self.setCentralWidget(self.view)

    def openFile(self, bool):
        name = QtGui.QFileDialog.getOpenFileName(self, "Open file", "", "Oscilloscope Data (*.csv)")
        self.loadFile(name)

    def openRecentFile(self):
        if self.sender():
            self.loadFile(self.sender().data().toString())

    def updateRecentFileActions(self):
        settings = QtCore.QSettings("Karel Klic", "flashfit")
        files = settings.value("recentFileList").toStringList()
        numRecentFiles = min(len(files), len(self.recentFileActs))
        for i in range(0, numRecentFiles):
            text = "&" + str(i) + " " + QtCore.QFileInfo(files[i]).fileName()
            self.recentFileActs[i].setText(text)
            self.recentFileActs[i].setData(files[i])
            self.recentFileActs[i].setVisible(True)

        self.separatorAct.setVisible(numRecentFiles > 0)

    def loadFile(self, name):
        fi = QtCore.QFileInfo(name)
        if not fi.isFile() or not fi.isReadable():
            return

        # Load data
        reader = csv.reader(open(name))
        try:
            self.data.originalData.readFromCsvReader(reader)
        except (StopIteration, csv.Error):
            QtGui.QMessageBox.critical(self, "Error while loading file", \
                                           "Error occured when loading " + name)
            return

        self.data.maxPoints = Data.DEFAULT_USED_POINTS_COUNT
        self.data.copyFromOriginalData()
        self.settings.onDataLoaded(self.data)
        self.data.guessFullLightVoltagePointerValue() # sets fullLightVoltage
        self.data.recalculateAbsorbances()
        
        # Refresh GUI
        self.scene.updateFromData(self.data)
        self.setWindowTitle(QtCore.QFileInfo(name).fileName() + " - flashfit")
    
        # Recent files
        settings = QtCore.QSettings("Karel Klic", "flashfit")
        files = settings.value("recentFileList").toStringList()
        files.removeAll(name)
        files.prepend(name)
        while len(files) > len(self.recentFileActs):
            files.removeLast()
        settings.setValue("recentFileList", files)
        self.updateRecentFileActions()

    def reloadFromOriginalData(self, points):
        # Do not act on timeAxisLength changes when loading.
        self.settings.timeAxisLength.valueChangeFinished.disconnect(self.scene.changeWidth)

        # TODO: save fulllightvoltage pointer and other pointers time and recover after loading

        self.data.maxPoints = points
        self.data.copyFromOriginalData()
        # TODO: next line to be removed
        self.data.guessFullLightVoltagePointerValue() # sets fullLightVoltage
        self.data.recalculateAbsorbances()
        self.scene.updateFromData(self.data)

        # Connect it back.
        self.settings.timeAxisLength.valueChangeFinished.connect(self.scene.changeWidth)

application = QtGui.QApplication(sys.argv)
window = MainWindow()
window.show()

application.lastWindowClosed.connect(application.quit)
application.exec_()
