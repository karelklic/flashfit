#!/usr/bin/python

import sys, csv, math
from PyQt4 import QtCore, QtGui
from data import Data
from graphicsscene import GraphicsScene
from graphicsview import GraphicsView

class Settings(QtGui.QDockWidget):
    def __init__(self, parent=None):
        QtGui.QDockWidget.__init__(self, parent)
        self.setWindowTitle("Settings")
        self.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea)
        self.setFeatures(QtGui.QDockWidget.NoDockWidgetFeatures)
        
        mainWidget = QtGui.QWidget(self)
        layout = QtGui.QVBoxLayout(mainWidget)
        mainWidget.setLayout(layout)

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

        model = QtGui.QGroupBox("Time Axis Length", self)
        modelLayout = QtGui.QHBoxLayout(model)
        self.timeAxisLength = QtGui.QSpinBox()
        self.timeAxisLength.setRange(GraphicsScene.MIN_WIDTH, GraphicsScene.MAX_WIDTH)
        self.timeAxisLength.setValue(GraphicsScene.DEFAULT_WIDTH)
        modelLayout.addWidget(self.timeAxisLength)
        model.setLayout(modelLayout)
        layout.addWidget(model)
        layout.addStretch()
        self.setWidget(mainWidget)

    def onSceneRectChanged(self, rect):
        self.timeAxisLength.setValue(rect.width())

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
        self.settings.timeAxisLength.valueChanged.connect(self.scene.changeWidth)
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

        self.data.copyFromOriginalData(2000) # 2000 points
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
       

application = QtGui.QApplication(sys.argv)
window = MainWindow()
window.show()

application.lastWindowClosed.connect(application.quit)
application.exec_()
