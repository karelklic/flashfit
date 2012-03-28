from PyQt4 import QtCore, QtGui
from gui_timeaxis import TimeAxis
from gui_valueaxis import ValueAxis
from gui_valuegraph import ValueGraph
from gui_timebarpair import FullLightBarPair, FitBarPair
from gui_fit import Fit
from gui_residualsgraph import ResidualsGraph
from gui_informationtable import InformationTable
from data import Data
import variables

class GraphicsScene(QtGui.QGraphicsScene):
    """
    The scene containing graph. It's 1000 points high and 1000 or more
    points wide. The width and height does not include borders.
    """
    DEFAULT_WIDTH = 2000
    MIN_WIDTH = 800
    MAX_WIDTH = 20000
    HEIGHT = 1000

    def __init__(self, data, parentWindow):
        super(GraphicsScene, self).__init__(parentWindow)
        self.data = data
        # Create basic objects in the scene
        self.timeAxis = TimeAxis()
        self.addItem(self.timeAxis)
        self.valueAxis = ValueAxis()
        self.addItem(self.valueAxis)
        self.valueGraph = ValueGraph(data)
        self.addItem(self.valueGraph)
        self.fit = Fit(data)
        self.addItem(self.fit)
        self.residualSeparatorAxis = QtGui.QGraphicsLineItem()
        self.addItem(self.residualSeparatorAxis)
        self.residualsGraph = ResidualsGraph(data)
        self.addItem(self.residualsGraph)
        self.informationTable = InformationTable(data,
                                                 parentWindow.menuBar(),
                                                 parentWindow.textItems,
                                                 self.valueGraph)
        self.addItem(self.informationTable)
        self.fullLightBars = FullLightBarPair(self.timeAxis, self)
        self.fullLightBars.setBarPos(100, 400)
        self.fullLightBars.setColor(QtGui.QColor("#333366"))
        self.fitBars = FitBarPair(self.timeAxis, self)
        self.fitBars.setBarPos(500, 1500)
        self.fitBars.setColor(QtGui.QColor("#336633"))

        self.timeAxis.setTime(0, 1.0)
        # Draw the time axis to get proper children bounding rect.
        self.timeAxis.update()
        self.valueAxis.setData(0, 1.0, variables.absorbanceAxisCaption)
        # Draw the absorbance axis to get proper children bounding rect,
        # even when the initial heights are wrong.
        self.valueAxis.update()

        self.recalculateBorders()

        # Set initial scene properties
        self.__setSceneSize(self.DEFAULT_WIDTH)

        # Redraw the axes with proper values set by __setSceneSize
        self.timeAxis.update()
        self.valueAxis.update()

    def updateFromData(self, autoSetWidth=False):
        """
        Updates all parts of the scene.  If autoSetWidth is set to
        True, this method calculates the best width for the data and
        set it. Otherwise the old (previous) width is preserved.
        """
        if autoSetWidth:
            newWidth = min(max(self.MIN_WIDTH, len(self.data.time)), self.MAX_WIDTH)
            self.__setSceneSize(newWidth)

        self.timeAxis.setTime(self.data.minTime, self.data.maxTime)
        self.timeAxis.update()

        self.valueAxis.setData(self.data.minValue,
                               self.data.maxValue,
                               variables.absorbanceAxisCaption if self.data.originalData.type == self.data.originalData.ABSORBANCE else variables.luminiscenceAxisCaption)

        self.valueAxis.update()
        self.updateValueGraph()
        self.updateFit()
        self.updateResidualsGraph()
        self.updateFullLightBars()
        self.updateFitBars()
        self.informationTable.recreateFromData()
        self.informationTable.findPlaceInScene()

    def recalculateBorders(self):
        # Border on the right side of the scene, with blank space, in pixels.
        self.borderRight = 10
        # Border between the left side of the scene and the start of the time axis, in pixels.
        # Absorbance axis label and tics must fit here.
        self.borderLeft = self.valueAxis.childrenBoundingRect().width() + 8
        # Border on the top of the scene, in pixels.
        self.borderTop = 10
        # Border between the time axis line and the bottom of the
        # scene, in pixels.  Time axis label and tics must fit here.
        self.borderBottom = self.timeAxis.childrenBoundingRect().height()

    def updateAppearance(self):
        # Update to get the new width.
        self.valueAxis.update()
        # Update to get the new height.
        self.timeAxis.update()
        # Get the new borders based on axes width height.
        self.recalculateBorders()
        self.informationTable.updateAppearance()
        # Adjust the scene with the new borders.  Sets a new height to
        # the bars.
        self.__setSceneSize(self.sceneWidth)

        self.fullLightBars.updateAppearance()
        self.fitBars.updateAppearance()

    def updateValueGraph(self):
        self.valueGraph.recreateFromData()

    def updateFit(self):
        self.fit.recreateFromData()

    def updateResidualsGraph(self):
        self.residualsGraph.recreateFromData()

    def updateFullLightBars(self):
        # Do nothing when no data are loaded.
        if len(self.data.time) == 0:
            return
        self.fullLightBars.updatePositionFromData(self.data.fullLightVoltageTime1(),
                                                  self.data.fullLightVoltageTime2())

    def updateFitBars(self):
        # Do nothing when no data are loaded.
        if len(self.data.time) == 0:
            return
        self.fitBars.updatePositionFromData(self.data.fitTime1(),
                                            self.data.fitTime2())

    def changeWidth(self, width):
        # Only change the scene width if it really changed.
        if self.sceneWidth == width:
            return
        self.__setSceneSize(width)
        self.timeAxis.update()
        self.valueAxis.update()
        self.valueGraph.resizeFromData()
        self.fit.resizeFromData()
        self.residualsGraph.resizeFromData()
        self.updateFullLightBars()
        self.updateFitBars()

    def __setSceneSize(self, width):
        """
        Not to be called from outside.
        """
        self.sceneWidth = width
        residualsSize = int(self.HEIGHT * 0.15)
        self.setSceneRect(QtCore.QRectF(0, 0,
                                        width + self.borderLeft + self.borderRight,
                                        self.HEIGHT + self.borderTop + self.borderBottom))
        self.timeAxis.setPos(self.borderLeft, self.HEIGHT + self.borderTop)
        self.timeAxis.setWidth(width)
        self.valueAxis.setPos(self.borderLeft, self.borderTop)
        self.valueAxis.setHeights(self.HEIGHT, self.HEIGHT - residualsSize)
        self.valueGraph.setPos(self.borderLeft, self.borderTop)
        self.valueGraph.setSize(width, self.HEIGHT - residualsSize)
        self.fit.setPos(self.borderLeft, self.borderTop)
        self.fit.setSize(width, self.HEIGHT - residualsSize)
        self.residualSeparatorAxis.setPos(self.borderLeft, self.HEIGHT + self.borderTop - residualsSize)
        self.residualSeparatorAxis.setLine(0, 0, width, 0)
        self.residualsGraph.setPos(self.borderLeft, self.HEIGHT + self.borderTop - residualsSize)
        self.residualsGraph.setSize(width, residualsSize)
        self.fullLightBars.setPos(self.borderLeft, 0)
        self.fullLightBars.setHeight(self.HEIGHT + self.borderTop + self.borderBottom)
        self.fitBars.setPos(self.borderLeft, 0)
        self.fitBars.setHeight(self.HEIGHT + self.borderTop + self.borderBottom)

    def onDataChanged(self, change):
        if change & Data.DATA_CHANGED_VALUES:
            self.updateValueGraph()
            self.informationTable.recreateFromData()
        if change & Data.DATA_CHANGED_FULL_LIGHT_VOLTAGE_TIME_POINTER:
            self.updateFullLightBars()
        if change & Data.DATA_CHANGED_FIT:
            # Delete absorbance and residuals, hide params from the information table.
            self.updateFit()
            self.updateResidualsGraph()
            self.informationTable.recreateFromData()

        if change & Data.DATA_CHANGED_FIT_TIME_POINTER:
            self.updateFitBars()
