#!/usr/bin/python

import sys, csv, math
from PyQt4 import QtCore, QtGui
from data import Data
from graphicsscene import GraphicsScene
from graphicsview import GraphicsView
from settings import Settings

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
        saveAct.triggered.connect(self.saveAsImage)
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

    def saveAsImage(self):
        """
        TODO: Design Save image Dialog
        """
        image = QtGui.QFileDialog.getSaveFileName(self, "Save file", "", "PNG Image (*.png)")
        if len(image) == 0:
            return

        pixmap = QtGui.QPixmap(800, 600)
        pixmap.fill() # White background.
        painter = QtGui.QPainter(pixmap)
        self.scene.render(painter)
        painter.end()
        
        pixmap.save(image)

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
        """
        Loads input file and displays its content in graph.
        """
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
        """
        Changes the number of measured points used from all points loaded from input file.
        """
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
