from PyQt4 import QtCore, QtGui

class GraphicsView(QtGui.QGraphicsView):
    def __init__(self, scene, parent=None):
        super(GraphicsView, self).__init__(scene, parent)
        self.setTransformationAnchor(QtGui.QGraphicsView.NoAnchor)
        self.setAlignment(QtCore.Qt.AlignLeft)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        # TODO: Fix infinite recursion and remove the following line.
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        # Set initial position and scaling.
        self.fitInView(self.scene().sceneRect());
        self.horizontalScrollBar().setValue(self.horizontalScrollBar().minimum())

    def resizeEvent(self, event):
        "Overrides parent implementation"
        self.fitSceneInView()

    def fitSceneInView(self):
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
        self.fitInView(self.scene().sceneRect())
        setScrollBarValue(self.horizontalScrollBar(), hvalue)

    def fitInView(self, rect):
        unity = self.matrix().mapRect(QtCore.QRectF(0, 0, 1, 1));
        if unity.isEmpty():
            return
        self.scale(1 / unity.width(), 1 / unity.height())
        # Find the ideal x / y scaling ratio to fit \a rect in the view.
        margin = 2
        viewRect = self.viewport().rect().adjusted(margin, margin, -margin, -margin)
        if viewRect.isEmpty():
            return
        sceneRect = self.matrix().mapRect(rect);
        if sceneRect.isEmpty():
            return
        yratio = viewRect.height() / sceneRect.height()
        # Scale and center on the center of a rect.
        self.scale(yratio, yratio)
        self.centerOn(rect.center())
