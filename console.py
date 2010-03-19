from PyQt4 import QtCore, QtGui

class Console(QtGui.QDockWidget):
    """
    Console window used for advanced commands, debugging, 
    logging, and profiling.
    """
    def __init__(self, parentWindow):
        QtGui.QDockWidget.__init__(self, parentWindow)
        #self.setTitleBarWidget(QtGui.QWidget())
        self.setAllowedAreas(QtCore.Qt.BottomDockWidgetArea)
        self.setFeatures(QtGui.QDockWidget.NoDockWidgetFeatures)
        self.setVisible(False)

        # Add console window
        textBox = QtGui.QTextEdit()
        self.setWidget(textBox)


        
