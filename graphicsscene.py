from PyQt4 import QtCore, QtGui
from timeaxis import TimeAxis
from absorbanceaxis import AbsorbanceAxis
from absorbancegraph import AbsorbanceGraph
from timebarpair import TimeBarPair
from absorbancefit import AbsorbanceFit
from residualsgraph import ResidualsGraph
from informationtable import InformationTable
from data import Data

class GraphicsScene(QtGui.QGraphicsScene):
    """
    The scene containing graph. It's 1000 points high and 1000 or more 
    points wide.
    """
    DEFAULT_WIDTH = 2000
    MIN_WIDTH = 800
    MAX_WIDTH = 20000
    HEIGHT = 1000

    # Border on the right side of the scene, with blank space, in pixels.
    BORDER_RIGHT = 10
    # Border between the left side of the scene and the start of the time axis, in pixels.
    # Absorbance axis label and tics must fit here.
    BORDER_LEFT = 70
    # Border on the top of the scene, in pixels.
    BORDER_TOP = 10
    # Border between the time axis line and the bottom of the scene, in pixels.
    # Time axis label and tics must fit here.
    BORDER_BOTTOM = 58

    def __init__(self, data, parent=None):
        super(GraphicsScene, self).__init__(parent)
        self.data = data
        # Create basic objects in the scene 
        self.timeAxis = TimeAxis()
        self.addItem(self.timeAxis)
        self.absorbanceAxis = AbsorbanceAxis()
        self.addItem(self.absorbanceAxis)
        self.absorbanceGraph = AbsorbanceGraph()
        self.addItem(self.absorbanceGraph)
        self.absorbanceFit = AbsorbanceFit()
        self.addItem(self.absorbanceFit)
        self.absorbanceResidualSeparatorAxis = QtGui.QGraphicsLineItem()
        self.addItem(self.absorbanceResidualSeparatorAxis)
        self.residualsGraph = ResidualsGraph()
        self.addItem(self.residualsGraph)
        self.informationTable = InformationTable(self.absorbanceGraph)
        self.addItem(self.informationTable)
        # Set initial scene properties
        self.__setSceneSize(self.DEFAULT_WIDTH, self.HEIGHT)
        self.timeAxis.setTime(0, 1.0)
        self.timeAxis.update()
        self.absorbanceAxis.setAbsorbance(0, 1.0)
        self.absorbanceAxis.update()
        self.fullLightBars = TimeBarPair( \
            GraphicsScene.HEIGHT, "Full light", \
            self.timeAxis, self.BORDER_LEFT, self)
        self.fullLightBars.setPos(100, 400)
        self.fullLightBars.setColor(QtGui.QColor("#333366"))
        self.fitAbsorbanceBars = TimeBarPair( \
            GraphicsScene.HEIGHT, "Absorbance Fit", \
            self.timeAxis, self.BORDER_LEFT, self)
        self.fitAbsorbanceBars.setPos(500, 1500)
        self.fitAbsorbanceBars.setColor(QtGui.QColor("#336633"))

    def updateFromData(self):
        """
        Updates all parts of the scene.
        """
        width = min(max(self.MIN_WIDTH, len(self.data.time)), self.MAX_WIDTH)
        self.__setSceneSize(width, self.HEIGHT)
        self.timeAxis.setTime(self.data.minTime, self.data.maxTime)
        self.timeAxis.update()
        self.absorbanceAxis.setAbsorbance(self.data.minAbsorbance, self.data.maxAbsorbance)
        self.absorbanceAxis.update()
        self.updateAbsorbanceGraph()
        self.updateAbsorbanceFit()
        self.updateResidualsGraph()
        self.updateFullLightBars()
        self.updateFitAbsorbanceBars()
        self.updateInformationTable()

    def updateAbsorbanceGraph(self):
        self.absorbanceGraph.setData(self.data)
        self.absorbanceGraph.recreateFromData()

    def updateAbsorbanceFit(self):
        self.absorbanceFit.setData(self.data)
        self.absorbanceFit.recreateFromData()

    def updateResidualsGraph(self):
        self.residualsGraph.setData(self.data)
        self.residualsGraph.recreateFromData()

    def updateFullLightBars(self):
        self.fullLightBars.updatePositionFromData(self.data.fullLightVoltageTime1(), self.data.fullLightVoltageTime2())

    def updateFitAbsorbanceBars(self):
        self.fitAbsorbanceBars.updatePositionFromData(self.data.fitAbsorbanceTime1(), self.data.fitAbsorbanceTime2())

    def updateInformationTable(self):
        self.informationTable.setData(self.data)
        self.informationTable.recreateFromData()

    def changeWidth(self, width):
        # Only change the width if it really changed.
        if self.width() == width:
            return        
        self.__setSceneSize(width, self.HEIGHT)
        self.timeAxis.update()
        self.absorbanceAxis.update()
        self.absorbanceGraph.resizeFromData()
        self.absorbanceFit.resizeFromData()
        self.residualsGraph.resizeFromData()
        self.updateFullLightBars()
        self.updateFitAbsorbanceBars()
        
    def __setSceneSize(self, width, height):
        """
        Not to be called from outside.
        """
        residualsSize = int(height * 0.15)
        self.setSceneRect(QtCore.QRectF(0, 0, width, height))
        self.timeAxis.setPos(self.BORDER_LEFT, height - self.BORDER_BOTTOM)
        self.timeAxis.setWidth(width - self.BORDER_LEFT - self.BORDER_RIGHT)
        self.absorbanceAxis.setPos(self.BORDER_LEFT, self.BORDER_TOP)
        self.absorbanceAxis.setHeights(height - self.BORDER_TOP - self.BORDER_BOTTOM,
                                       height - self.BORDER_TOP - self.BORDER_BOTTOM - residualsSize)
        self.absorbanceGraph.setPos(self.BORDER_LEFT, self.BORDER_TOP)
        self.absorbanceGraph.setSize(width - self.BORDER_LEFT - self.BORDER_RIGHT,
                                     height - self.BORDER_TOP - self.BORDER_BOTTOM - residualsSize)
        self.absorbanceFit.setPos(self.BORDER_LEFT, self.BORDER_TOP)
        self.absorbanceFit.setSize(width - self.BORDER_LEFT - self.BORDER_RIGHT,
                                   height - self.BORDER_TOP - self.BORDER_BOTTOM - residualsSize)
        self.absorbanceResidualSeparatorAxis.setPos(self.BORDER_LEFT, 
                                                    height - self.BORDER_BOTTOM - residualsSize)
        self.absorbanceResidualSeparatorAxis.setLine(0, 0, width - self.BORDER_LEFT - self.BORDER_RIGHT, 0)
        self.residualsGraph.setPos(self.BORDER_LEFT, height - self.BORDER_BOTTOM - residualsSize)
        self.residualsGraph.setSize(width - self.BORDER_LEFT - self.BORDER_RIGHT, residualsSize)

    def onDataChanged(self, change):
        if change & Data.DATA_CHANGED_ABSORBANCE:
            self.updateAbsorbanceGraph()
            self.updateInformationTable()
        if change & Data.DATA_CHANGED_FULL_LIGHT_VOLTAGE_TIME_POINTER:
            self.updateFullLightBars()
        if change & Data.DATA_CHANGED_FIT_ABSORBANCE:
            # Delete absorbance and residuals, hide params from the information table.
            self.updateAbsorbanceFit()
            self.updateResidualsGraph()
            self.updateInformationTable()
        if change & Data.DATA_CHANGED_FIT_ABSORBANCE_TIME_POINTER:
            self.updateFitAbsorbanceBars()
