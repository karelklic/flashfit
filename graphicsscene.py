from PyQt4 import QtCore, QtGui
from timeaxis import TimeAxis
from absorbanceaxis import AbsorbanceAxis
from absorbancegraph import AbsorbanceGraph

class GraphicsScene(QtGui.QGraphicsScene):

    DEFAULT_WIDTH = 2000
    MIN_WIDTH = 400
    MAX_WIDTH = 20000
    HEIGHT = 1000

    """
    It's the scene containing graph. It's 1000 points high and 1000 or more points wide.
    """
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

    def updateFromData(self, data):
        width = min(max(self.MIN_WIDTH, len(data.time)), self.MAX_WIDTH)
        self.__setSceneSize(width, self.HEIGHT)
        self.timeAxis.setTime(data.minTime, data.maxTime)
        self.timeAxis.update()
        self.absorbanceAxis.setAbsorbance(data.minAbsorbance, data.maxAbsorbance)
        self.absorbanceAxis.update()
        self.absorbanceGraph.setData(data)
        self.absorbanceGraph.recreateFromData()

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
        borderRight = 10
        borderLeft = 70
        borderTop = 10
        borderBottom = 58
        residualsSize = int(height * 0.15)
        self.setSceneRect(QtCore.QRectF(0, 0, width, height))
        self.timeAxis.setPos(borderLeft, height - borderBottom)
        self.timeAxis.setWidth(width - borderLeft - borderRight)
        self.absorbanceAxis.setPos(borderLeft, borderTop)
        self.absorbanceAxis.setHeights(height - borderTop - borderBottom, \
                                           height - borderTop - borderBottom - residualsSize)
        self.absorbanceGraph.setPos(borderLeft, borderTop)
        self.absorbanceGraph.setSize(width - borderLeft - borderRight, \
                                         height - borderTop - borderBottom - residualsSize)
        self.absorbanceResidualSeparatorAxis.setPos(borderLeft, height - borderBottom - residualsSize)
        self.absorbanceResidualSeparatorAxis.setLine(0, 0, width - borderLeft - borderRight, 0)
