from PyQt4 import QtCore, QtGui

class MenuBar(QtGui.QMenuBar):
    def __init__(self, parent=None):
        super(MenuBar, self).__init__(parent)
        
        self.fileMenu = self.addMenu("&File")
        
        self.openAct = QtGui.QAction("&Open", self)
        self.openAct.setShortcut("Ctrl+O")
        self.fileMenu.addAction(self.openAct)

        self.saveAct = QtGui.QAction("&Save as image", self)
        self.saveAct.setShortcut("Ctrl+S")
        self.fileMenu.addAction(self.saveAct)
        self.fileMenu.addSeparator()

        # Recent Files
        self.recentFileActs = []
        for i in range(0, 5):
            act = QtGui.QAction(self)
            act.setVisible(False)
            self.fileMenu.addAction(act)
            self.recentFileActs.append(act)

        self.separatorAct = self.fileMenu.addSeparator() # used by RecentFile
        self.updateRecentFileActions()

        # The rest of File Menu
        self.quitAct = QtGui.QAction("&Quit", self)
        self.quitAct.setShortcut("Ctrl+Q")
        self.fileMenu.addAction(self.quitAct)       

    def updateRecentFileActions(self):
        settings = QtCore.QSettings()
        files = settings.value("recentFileList").toStringList()
        numRecentFiles = min(len(files), len(self.recentFileActs))
        for i in range(0, numRecentFiles):
            text = "&" + str(i) + " " + QtCore.QFileInfo(files[i]).fileName()
            self.recentFileActs[i].setText(text)
            self.recentFileActs[i].setData(files[i])
            self.recentFileActs[i].setVisible(True)

        self.separatorAct.setVisible(numRecentFiles > 0)

    def addRecentFile(self, filename):
        settings = QtCore.QSettings()
        files = settings.value("recentFileList").toStringList()
        files.removeAll(filename)
        files.prepend(filename)
        while len(files) > len(self.recentFileActs):
            # files.removeLast() seems to be nonexistant in PyQt
            files.removeAt(len(files) - 1)
        settings.setValue("recentFileList", files)
        self.updateRecentFileActions()
        
