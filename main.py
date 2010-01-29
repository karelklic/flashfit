#!/usr/bin/python

import sys, math
from PyQt4 import QtCore, QtGui
from data import Data
from graphicsscene import GraphicsScene
from graphicsview import GraphicsView
from settings import Settings
from menubar import MenuBar
from loadfiletask import LoadFileTask
from changepointcounttask import ChangePointCountTask
from fittask import FitTask

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("flashfit")
        
        # Create the status bar.
        self.statusBar().showMessage("Ready", 3000)

        # Create and connect Mani Menu Bar
        self.setMenuBar(MenuBar(self))
        self.menuBar().openAct.triggered.connect(self.openFile)
        self.menuBar().saveAct.triggered.connect(self.saveAsImage)
        for act in self.menuBar().recentFileActs:
            act.triggered.connect(self.openRecentFile)
        self.menuBar().quitAct.triggered.connect(self.close)

        self.settings = Settings(self)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.settings)

        self.data = Data()
        self.scene = GraphicsScene(self.data, self)
        self.scene.sceneRectChanged.connect(self.settings.onSceneRectChanged)
        self.settings.timeAxisLength.valueChangeFinished.connect(self.scene.changeWidth)
        self.settings.usedPoints.valueChangeFinished.connect(self.reloadFromOriginalData)
        self.settings.modelFunctionChanged.connect(self.data.setAbsorbanceFitFunction)
        self.settings.fit.clicked.connect(self.fitAbsorbances)
        self.scene.fullLightBars.bar1.signals.positionChangeFinished.connect(self.data.setFullLightVoltageTime1)
        self.scene.fullLightBars.bar2.signals.positionChangeFinished.connect(self.data.setFullLightVoltageTime2)
        self.scene.fitAbsorbanceBars.bar1.signals.positionChangeFinished.connect(self.data.setFitAbsorbanceTime1)
        self.scene.fitAbsorbanceBars.bar2.signals.positionChangeFinished.connect(self.data.setFitAbsorbanceTime2)
        self.data.dataChanged.connect(self.scene.onDataChanged)
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

        if not image.endsWith(".png") and not image.endsWith(".PNG"):
            image = image + ".png"

        BORDER_WIDTH = 50 # pixels
        imageWidth = self.scene.width() + 2 * BORDER_WIDTH
        imageHeight = self.scene.height() + 2 * BORDER_WIDTH
        pixmap = QtGui.QPixmap(imageWidth, imageHeight)
        pixmap.fill() # White background.
        targetRect = QtCore.QRectF(BORDER_WIDTH, BORDER_WIDTH, \
                                       self.scene.width(), \
                                       self.scene.height())
        painter = QtGui.QPainter(pixmap)
        self.scene.render(painter, targetRect)
        painter.end()
        
        pixmap.save(image)

    def loadFile(self, name):
        """
        Loads input file and displays its content in graph.
        """
        fi = QtCore.QFileInfo(name)
        if not fi.isFile() or not fi.isReadable():
            return

        # The task must be stored in self to prevent Python from
        # deleting it.
        self.task = LoadFileTask(name, self)
        self.runTask(self.task)

    def reloadFromOriginalData(self, pointCount):
        """
        Changes the number of measured points used from all points loaded from input file.
        """
        # Do nothing if the number of points hasn't changed.
        if self.data.maxPoints == pointCount:
            return

        # The task must be stored in self to prevent Python from
        # deleting it.
        self.task = ChangePointCountTask(pointCount, self)
        self.runTask(self.task)

    def fitAbsorbances(self):
        self.task = FitTask(self)
        self.runTask(self.task)

    def onModelFunctionChanged(self):
        # This method is called twice per every change.
        self.data.setAbsorbanceFitFunction(self.settings.modelFunction())

    def runTask(self, task):
        """
        Runs a task. This involves disabling most of the UI during the task.
        """
        self.settings.setEnabled(False)
        self.menuBar().setEnabled(False)
        self.scene.fullLightBars.setEnabled(False)
        self.scene.fitAbsorbanceBars.setEnabled(False)
        self.scene.setBackgroundBrush(QtGui.QBrush(QtGui.QColor("#e0e0e0")));

        task.finished.connect(self.onTaskFinished)
        task.messageAdded.connect(self.statusBar().showMessage)
        task.start()

    def onTaskFinished(self):
        self.settings.setEnabled(True)
        self.menuBar().setEnabled(True)
        self.scene.fullLightBars.setEnabled(True)
        self.scene.fitAbsorbanceBars.setEnabled(True)
        self.statusBar().showMessage("Done", 3000)
        self.scene.setBackgroundBrush(QtGui.QBrush(QtCore.Qt.NoBrush));

application = QtGui.QApplication(sys.argv)
QtCore.QCoreApplication.setOrganizationName("flashfit")
QtCore.QCoreApplication.setOrganizationDomain("")
QtCore.QCoreApplication.setApplicationName("flashfit");
window = MainWindow()
window.show()
application.lastWindowClosed.connect(application.quit)
application.exec_()
