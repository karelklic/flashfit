import sys
import math
import PyQt4
import data
import gui_graphicsscene
import gui_graphicsview
import gui_settings
import gui_settings_bars
import gui_settings_axes
import gui_settings_textualdata
import gui_console
import gui_menubar
import gui_textitems
import task_loadfile
import task_changepointcount
import task_fit

class MenuBarWithActions(gui_menubar.MenuBar):
    """
    Provides the menu bar for the main window. This class connects the
    internals of gui_menubar.MenuBar class with the internals of
    MainWindow class.
    """
    def __init__(self, parent):
        gui_menubar.MenuBar.__init__(self, parent)
        self.openAct.triggered.connect(self.openFile)
        self.saveAct.triggered.connect(parent.saveAsImage)
        for act in self.recentFileActs:
            act.triggered.connect(self.openRecentFile)
        self.quitAct.triggered.connect(self.close)
        self.textualDataSettingsAct.triggered.connect(self.editTextualDataSettings)
        self.barsSettingsAct.triggered.connect(self.editBarsSettings)
        self.axesSettingsAct.triggered.connect(self.editAxesSettings)

    def editTextualDataSettings(self):
        """
        Opens the Appearance editor, where user can select font sizes,
        format details etc.
        """
        dialog = gui_settings_textualdata.Dialog(self.parent())
        if dialog.exec_() == PyQt4.QtGui.QDialog.Accepted:
            self.parent().scene.updateAppearance()
            self.parent().view.fitSceneInView()

    def editBarsSettings(self):
        dialog = gui_settings_bars.Dialog(self.parent())
        if dialog.exec_() == PyQt4.QtGui.QDialog.Accepted:
            self.parent().scene.updateAppearance()
            self.parent().view.fitSceneInView()

    def editAxesSettings(self):
        dialog = gui_settings_axes.Dialog(self.parent())
        if dialog.exec_() == PyQt4.QtGui.QDialog.Accepted:
            self.parent().scene.updateAppearance()
            self.parent().view.fitSceneInView()

    def openFile(self, bool):
        name = PyQt4.QtGui.QFileDialog.getOpenFileName(self.parent(),
                                                       "Open file",
                                                       "",
                                                       "Oscilloscope Data (*.csv)")
        self.parent().loadFile(name)

    def openRecentFile(self):
        if self.sender():
            self.parent().loadFile(self.sender().data().toString())

class MainWindow(PyQt4.QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        # Set initial value of self.loadFilePath
        self.setLoadedFilePath("")

        # Create and connect Main Menu Bar
        self.setMenuBar(MenuBarWithActions(self))

        self.data = data.Data()

        self.textItems = gui_textitems.List(self.data)

        self.settings = gui_settings.Settings(self)
        self.addDockWidget(PyQt4.QtCore.Qt.LeftDockWidgetArea, self.settings)

        self.console = gui_console.Console(self)
        self.addDockWidget(PyQt4.QtCore.Qt.BottomDockWidgetArea, self.console)
        self.setCorner(PyQt4.QtCore.Qt.BottomLeftCorner, PyQt4.QtCore.Qt.LeftDockWidgetArea)

        self.createStatusBar()

        self.scene = gui_graphicsscene.GraphicsScene(self.data, self)
        self.scene.sceneRectChanged.connect(self.settings.onSceneRectChanged)
        self.settings.timeAxisLength.valueChangeFinished.connect(self.scene.changeWidth)
        self.settings.usedPoints.valueChangeFinished.connect(self.reloadFromOriginalData)
        self.settings.experimental.fit.clicked.connect(self.fitAbsorbances)
        self.settings.compatible.fit.clicked.connect(self.fitAbsorbances)
        self.menuBar().showMenuToggleConnect(self.scene.informationTable.recreateFromData)
        self.scene.fullLightBars.bar1.signals.positionChangeFinished.connect(self.data.setFullLightVoltageTime1)
        self.scene.fullLightBars.bar2.signals.positionChangeFinished.connect(self.data.setFullLightVoltageTime2)
        self.scene.fitAbsorbanceBars.bar1.signals.positionChangeFinished.connect(self.data.setFitAbsorbanceTime1)
        self.scene.fitAbsorbanceBars.bar2.signals.positionChangeFinished.connect(self.data.setFitAbsorbanceTime2)
        self.data.dataChanged.connect(self.scene.onDataChanged)
        self.view = gui_graphicsview.GraphicsView(self.scene)
        self.setCentralWidget(self.view)

    def saveAsImage(self):
        """
        TODO: Design Save image Dialog
        """
        fileName = PyQt4.QtCore.QFileInfo(self.loadedFilePath).completeBaseName()
        image = PyQt4.QtGui.QFileDialog.getSaveFileName(self, "Save file", fileName, "PNG Image (*.png)")
        if len(image) == 0:
            return

        if not image.endsWith(".png") and not image.endsWith(".PNG"):
            image = image + ".png"

        if PyQt4.QtCore.QFileInfo(image).exists():
            fileName = PyQt4.QtCore.QFileInfo(image).fileName()
            result = PyQt4.QtGui.QMessageBox.question(self, "Image file already exists",
                                                      "Image file {0} already exists. Overwrite?".format(fileName),
                                                      PyQt4.QtGui.QMessageBox.Yes | PyQt4.QtGui.QMessageBox.No,
                                                      PyQt4.QtGui.QMessageBox.Yes)
            if result != PyQt4.QtGui.QMessageBox.Yes:
                return

        BORDER_WIDTH = 50 # pixels
        imageWidth = self.scene.width() + 2 * BORDER_WIDTH
        imageHeight = self.scene.height() + 2 * BORDER_WIDTH
        pixmap = PyQt4.QtGui.QPixmap(imageWidth, imageHeight)
        pixmap.fill() # White background.
        targetRect = PyQt4.QtCore.QRectF(BORDER_WIDTH, BORDER_WIDTH,
                                         self.scene.width(),
                                         self.scene.height())
        painter = PyQt4.QtGui.QPainter(pixmap)
        self.scene.render(painter, targetRect)
        painter.end()

        pixmap.save(image)

    def loadFile(self, name):
        """
        Loads input file and displays its content in graph.
        """
        fi = PyQt4.QtCore.QFileInfo(name)
        if not fi.isFile() or not fi.isReadable():
            return

        # The task must be stored in self to prevent Python from
        # deleting it.
        self.task = task_loadfile.Task(name, self)
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
        self.task = task_changepointcount.ChangePointCountTask(pointCount, self)
        self.runTask(self.task)

    def fitAbsorbances(self):
        self.task = task_fit.Task(self)
        self.runTask(self.task)

    def runTask(self, task):
        """
        Runs a task. This involves disabling most of the UI during the task.
        """
        self.settings.setEnabled(False)
        self.menuBar().setEnabled(False)
        self.scene.fullLightBars.setEnabled(False)
        self.scene.fitAbsorbanceBars.setEnabled(False)
        self.scene.setBackgroundBrush(PyQt4.QtGui.QBrush(PyQt4.QtGui.QColor("#d0d0d0")));

        task.finished.connect(self.onTaskFinished)
        task.messageAdded.connect(self.statusBar().showMessage)
        task.messageAdded.connect(self.console.showMessage)
        task.start()

    def onTaskFinished(self):
        self.settings.setEnabled(True)
        self.menuBar().setEnabled(True)
        self.scene.fullLightBars.setEnabled(True)
        self.scene.fitAbsorbanceBars.setEnabled(True)
        self.statusBar().showMessage("Done", 3000)
        self.scene.setBackgroundBrush(PyQt4.QtGui.QBrush(PyQt4.QtCore.Qt.NoBrush));

    def setLoadedFilePath(self, path):
        self.loadedFilePath = path
        fileName = PyQt4.QtCore.QFileInfo(path).fileName()
        if len(fileName) == 0:
            self.setWindowTitle("flashfit")
        else:
            self.setWindowTitle(fileName + " - flashfit")

    def createStatusBar(self):
        statusBar = PyQt4.QtGui.QStatusBar();
        self.setStatusBar(statusBar);
        statusBar.showMessage("Ready", 3000)

        consoleButton = PyQt4.QtGui.QPushButton("Console");
        consoleButton.setFlat(True)
        consoleButton.setCheckable(True)

        consoleButton.toggled.connect(self.console.setVisible)
        statusBar.addPermanentWidget(consoleButton)
