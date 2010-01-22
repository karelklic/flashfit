from PyQt4 import QtCore, QtGui
from timeaxis import TimeAxis
from absorbanceaxis import AbsorbanceAxis
from absorbancegraph import AbsorbanceGraph
from timebarpair import TimeBarPair

class GraphicsScene(QtGui.QGraphicsScene):
    """
    The scene containing graph. It's 1000 points high and 1000 or more 
    points wide.
    """
    DEFAULT_WIDTH = 2000
    MIN_WIDTH = 400
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

    def __init__(self, parent=None):
        super(GraphicsScene, self).__init__(parent)
        # Create basic objects in the scene 
        self.timeAxis = TimeAxis()
        self.addItem(self.timeAxis)
        self.absorbanceAxis = AbsorbanceAxis()
        self.addItem(self.absorbanceAxis)
        self.absorbanceGraph = AbsorbanceGraph()
        self.addItem(self.absorbanceGraph)
        self.absorbanceResidualSeparatorAxis = QtGui.QGraphicsLineItem()
        self.addItem(self.absorbanceResidualSeparatorAxis)
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

    def updateFromData(self, data):
        width = min(max(self.MIN_WIDTH, len(data.time)), self.MAX_WIDTH)
        self.__setSceneSize(width, self.HEIGHT)
        self.timeAxis.setTime(data.minTime, data.maxTime)
        self.timeAxis.update()
        self.absorbanceAxis.setAbsorbance(data.minAbsorbance, data.maxAbsorbance)
        self.absorbanceAxis.update()
        self.absorbanceGraph.setData(data)
        self.absorbanceGraph.recreateFromData()
        self.fullLightBars.updatePositionFromData(data.fullLightVoltageTime1(), data.fullLightVoltageTime2())
        self.fitAbsorbanceBars.updatePositionFromData(data.fitAbsorbanceTime1(), data.fitAbsorbanceTime2())

    def changeWidth(self, width):
        oldWidth = self.width()
        self.__setSceneSize(width, self.HEIGHT)
        self.timeAxis.update()
        self.absorbanceAxis.update()
        self.absorbanceGraph.resizeFromData()
        
    def __setSceneSize(self, width, height):
        """
        Not to be called from outside.
        """
        residualsSize = int(height * 0.15)
        self.setSceneRect(QtCore.QRectF(0, 0, width, height))
        self.timeAxis.setPos(self.BORDER_LEFT, height - self.BORDER_BOTTOM)
        self.timeAxis.setWidth(width - self.BORDER_LEFT - self.BORDER_RIGHT)
        self.absorbanceAxis.setPos(self.BORDER_LEFT, self.BORDER_TOP)
        self.absorbanceAxis.setHeights(height - self.BORDER_TOP - self.BORDER_BOTTOM, \
                                           height - self.BORDER_TOP - self.BORDER_BOTTOM - residualsSize)
        self.absorbanceGraph.setPos(self.BORDER_LEFT, self.BORDER_TOP)
        self.absorbanceGraph.setSize(width - self.BORDER_LEFT - self.BORDER_RIGHT, \
                                         height - self.BORDER_TOP - self.BORDER_BOTTOM - residualsSize)
        self.absorbanceResidualSeparatorAxis.setPos(self.BORDER_LEFT, height - self.BORDER_BOTTOM - residualsSize)
        self.absorbanceResidualSeparatorAxis.setLine(0, 0, width - self.BORDER_LEFT - self.BORDER_RIGHT, 0)
