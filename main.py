#!/usr/bin/python
# TODO:
#  - ikonky na roztahovani, stahovani osy X (casu)
#  - osa Y se vzdycky fitne na velikost okna (=1000)

import sys, csv, math
from PyQt4 import QtCore, QtGui

class Data(QtCore.QObject):
    timeChanged = QtCore.pyqtSignal()
    voltageChanged = QtCore.pyqtSignal()
    absorbanceChanged = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        QtCore.QObject.__init__(self, parent)
        self.time = []
        # Voltage in time.
        self.voltage = []
        # Absorbance in time.
        self.absorbance = []
        # Residuals in time.
        self.residuals = []
        # Full light voltage
        # Used to calculate absorbance from voltage.
        self.fullLightVoltage = None
        # No light voltage
        # Used to calculate absorbance from voltage.
        self.noLightVoltage = 0.0
        # Full Light Voltage time pointer
        # Both values are offsets to self.time array.
        # self.fullLightVoltage is calculated from this pointers
        self.fullLightVoltagePointer = (0, 0)
        # Fit Absorbance time pointer
        # Both values are offsets to self.time array.
        self.fitAbsorbanceTimePointer = (0, 0)
        
    def setFullLightVoltage(self, voltage):
        self.fullLightVoltage = voltage
        
        # Recalculate absorbance from voltage.
        self.absorbance = []
        vdiff = self.fullLightVoltage - self.noLightVoltage
        if vdiff != 0: # Divide by zero.
            for v in voltage: # v is the voltage in time t
                self.absorbance.append(-math.log10((v - self.noLightVoltage) / vdiff))
        absorbanceChanged.emit()        

    def guessFullLightVoltagePointerValue(self):
        self.setFullLightVoltagePointer(0, 0)

    def guessFitAbsorbanceTimePointer(self):
        self.fitAbsorbanceTimePointer = (0, 0)

    def setFullLightVoltagePointer(self, start, stop):
        if start > stop:
            start, stop = stop, start

        self.fullLightVoltagePointer = (start, stop)
        
        # Calculate the arithmetic mean voltage from it.
        sum = 0.0
        for i in range(start, stop):
            sum += self.voltage[i]
        self.setFullLightVoltage(sum / float(stop - start))

    def clear(self):
        self.time = []
        self.voltage = []
        self.absorbance = []
        self.residuals = []
        self.fullLightVoltage = None
        self.noLightVoltage = 0.0
        self.fullLightVoltagePointer = (0, 0)
        self.fitAbsorbanceTimePointer = (0, 0)
        
class TimeAxis(QtGui.QGraphicsItemGroup):
    def __init__(self, parent=None):
        super(TimeAxis, self).__init__(parent)

        self.line = QtGui.QGraphicsLineItem(QtCore.QLineF(10, 950, 1990, 950))
        self.addToGroup(self.line)

        for ticx in range(10, 1990, 10):
            tic = QtGui.QGraphicsLineItem(QtCore.QLineF(ticx, 950, ticx, 950 + 10))
            self.addToGroup(tic)

        self.text = QtGui.QGraphicsTextItem("time")
        self.text.setPos(1915, 960)
        font = QtGui.QFont()
        font.setPixelSize(30)
        self.text.setFont(font)
        self.addToGroup(self.text)

class AbsorbanceAxis(QtGui.QGraphicsItemGroup):
    def __init__(self, parent=None):
        super(AbsorbanceAxis, self).__init__(parent)

        self.line = QtGui.QGraphicsLineItem(QtCore.QLineF(10, 10, 10, 950))
        self.addToGroup(self.line)
 

class GraphicsScene(QtGui.QGraphicsScene):
    """
    It's the scene containing graph. It's 1000 points high and 1000 or more points wide.
    """
    def __init__(self, data, parent=None):
        super(GraphicsScene, self).__init__(parent)

        self.setSceneRect(QtCore.QRectF(0, 0, 2000, 1000))
        self.data = data
        self.data.timeChanged.connect(self.timeChanged)

        self.timeAxis = TimeAxis()
        self.addItem(self.timeAxis)

        self.absorbanceAxis = AbsorbanceAxis()
        self.addItem(self.absorbanceAxis)

    def timeChanged(self):
        # Clear.
        #for item in self.timeBar.childItems():
        #    self.timeBar.removeFromGroup(item)

        # Draw the basic line.
        #line = QtGui.QGraphicsLineItem(QtCore.QLineF(0, 0, 800, 0));
        #self.timeBar.addToGroup(line)
        pass

class GraphicsView(QtGui.QGraphicsView):
    def __init__(self, scene, parent=None):
        super(GraphicsView, self).__init__(scene, parent)
        self.setTransformationAnchor(QtGui.QGraphicsView.NoAnchor)
        self.setAlignment(QtCore.Qt.AlignLeft)
        #self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        #self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        # Set initial position and scaling.
        self.resizeLoop = 0
        self.fitInView(self.scene().sceneRect(), QtCore.Qt.KeepAspectRatioByExpanding);
        self.horizontalScrollBar().setValue(self.horizontalScrollBar().minimum())

    def resizeEvent(self, event):
        "Overrides parent implementation"
        if self.resizeLoop == 10:
            self.resizeLoop = 0
            return

        def getScrollBarValue(sb):
            size = sb.maximum() - sb.minimum()
            value = 0
            if size > 0:
                value = (sb.value() - sb.minimum()) / float(size)
            return value
        def setScrollBarValue(sb, value):
            sb.setValue(value * (sb.maximum() - sb.minimum()) + sb.minimum())

        # Save the scroll bar position to set it later.
        hvalue = getScrollBarValue(self.horizontalScrollBar())
        hvisible = self.horizontalScrollBar().isVisible()
        vvalue = getScrollBarValue(self.verticalScrollBar())
        vvisible = self.verticalScrollBar().isVisible()
        self.fitInView(self.scene().sceneRect(), QtCore.Qt.KeepAspectRatioByExpanding);
        self.resizeLoop += 1
        setScrollBarValue(self.horizontalScrollBar(), hvalue)
        setScrollBarValue(self.verticalScrollBar(), vvalue)

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
        layout.addStretch()

        self.setWidget(mainWidget)

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setWindowTitle("flashfit 0.1")

        fileMenu = self.menuBar().addMenu("File")

        openAct = QtGui.QAction("&Open", self)
        openAct.setShortcut("Ctrl+O")
        openAct.triggered.connect(self.openFile)
        fileMenu.addAction(openAct)

        saveAct = QtGui.QAction("&Save as image", self)
        saveAct.setShortcut("Ctrl+S")
        fileMenu.addAction(saveAct)
        fileMenu.addSeparator()

        quitAct = QtGui.QAction("&Quit", self)
        quitAct.setShortcut("Ctrl+Q")
        quitAct.triggered.connect(self.close)
        fileMenu.addAction(quitAct)       

        settings = Settings(self)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, settings)

        self.data = Data()
        self.scene = GraphicsScene(self.data, self)

        self.view = GraphicsView(self.scene)
        self.setCentralWidget(self.view)

    def openFile(self, bool):
        name = QtGui.QFileDialog.getOpenFileName(self, "Open file", "", "Oscilloscope Data (*.csv)")
        fi = QtCore.QFileInfo(name)
        if not fi.isFile() or not fi.isReadable():
            return

        reader = csv.reader(open(name))
        # Clear our data.
        self.data.clear()
        # Row 1
        #  - record length
        #  - points
        row1 = reader.next()
        # Row 2
        #  - sample interval
        row2 = reader.next()
        # Row 3
        #  - trigger point
        #  - samples
        row3 = reader.next()
        # Row 4
        #  - trigger time
        row4 = reader.next()
        # Row 5
        #  - unknown?
        row5 = reader.next()
        # Row 6
        #  - horizontal offset
        row6 = reader.next()

        # Data
        for row in reader:
            self.data.time.append(float(row[3]))
            self.data.voltage.append(float(row[4]))
        self.data.timeChanged.emit()

application = QtGui.QApplication(sys.argv)
window = MainWindow()
window.show()

application.lastWindowClosed.connect(application.quit)
application.exec_()
