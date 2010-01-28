#!/usr/bin/python

import sys, csv, math
from PyQt4 import QtCore, QtGui
from data import Data
from graphicsscene import GraphicsScene
from graphicsview import GraphicsView
from settings import Settings
from menubar import MenuBar

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("flashfit")

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
        self.settings.modelFunctionChanged.connect(self.onModelFunctionChanged)
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
        self.data.guessFitAbsorbanceTimePointer()
        self.data.fitAbsorbances()
        
        # Refresh GUI
        self.scene.updateFromData()
        self.setWindowTitle(QtCore.QFileInfo(name).fileName() + " - flashfit")
    
        # Update Recent files in the Main Menu
        self.menuBar().addRecentFile(name)        

    def reloadFromOriginalData(self, points):
        """
        Changes the number of measured points used from all points loaded from input file.
        """
        # Do nothing if the number of points hasn't changed.
        if self.data.maxPoints == points:
            return

        # Do not act on timeAxisLength changes when loading.
        self.settings.timeAxisLength.valueChangeFinished.disconnect(self.scene.changeWidth)

        # Save fulllightvoltage pointer and fit absorbance pointer time, to be recovered after loading
        fullLightVoltageTimes = self.data.fullLightVoltageTimes()
        fitAbsorbanceTimes = self.data.fitAbsorbanceTimes()

        self.data.maxPoints = points
        self.data.copyFromOriginalData()

        # Recover fulllightvoltage pointer and fit absorbance pointer times
        self.data.setFullLightVoltageTimes(fullLightVoltageTimes, False)
        self.data.setFitAbsorbanceTimes(fitAbsorbanceTimes, False)

        self.scene.updateFromData()

        # Connect it back.
        self.settings.timeAxisLength.valueChangeFinished.connect(self.scene.changeWidth)

    def onModelFunctionChanged(self):
        # This method is called twice per every change.
        # Do not recalculate absorbances twice.
        if self.data.absorbanceFitFunction == self.settings.modelFunction():
            return

        self.data.absorbanceFitFunction = self.settings.modelFunction()
        self.data.fitAbsorbances()
        self.scene.updateAbsorbanceFit()
        self.scene.updateResidualsGraph()
        self.scene.updateInformationTable()
        
application = QtGui.QApplication(sys.argv)
QtCore.QCoreApplication.setOrganizationName("flashfit")
QtCore.QCoreApplication.setOrganizationDomain("")
QtCore.QCoreApplication.setApplicationName("flashfit");
window = MainWindow()
window.show()
application.lastWindowClosed.connect(application.quit)
application.exec_()
