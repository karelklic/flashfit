from PyQt4 import QtCore, QtGui

class MenuBar(QtGui.QMenuBar):
    """
    The menu bar for the main application window.
    This class must not implement actions.
    """
    def __init__(self, parent=None):
        super(MenuBar, self).__init__(parent)

        ### File menu
        self.fileMenu = self.addMenu("&File")

        self.openAct = QtGui.QAction("&Open", self)
        self.openAct.setShortcut("Ctrl+O")
        self.fileMenu.addAction(self.openAct)

        self.saveAct = QtGui.QAction("&Save as PNG image", self)
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

        ### Edit menu
        self.editMenu = self.addMenu("&Settings")
        self.informationBoxSettingsAct = QtGui.QAction("&Information box...", self)
        self.editMenu.addAction(self.informationBoxSettingsAct)
        self.axesSettingsAct = QtGui.QAction("A&xes...", self)
        self.editMenu.addAction(self.axesSettingsAct)
        self.barsSettingsAct = QtGui.QAction("&Bars...", self)
        self.editMenu.addAction(self.barsSettingsAct)

        ### Show menu
        self.showMenu = self.addMenu("&Show")

        self.showInformationBoxAct = QtGui.QAction("&Show information box",
                                                   self)
        self.showInformationBoxAct.setCheckable(True)
        self.showInformationBoxAct.setChecked(True)
        self.showMenu.addAction(self.showInformationBoxAct)

    def updateRecentFileActions(self):
        """
        Updates QActions associated with Recent Files in the main menu from
        application settings.
        """
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

    def setEnabled(self, enabled):
        for item in [self.openAct, self.saveAct, self.editMenu,
                     self.separatorAct, self.showMenu] + self.recentFileActs:
            item.setEnabled(enabled)

    def showMenuToggleConnect(self, function):
        """
        Connects function to signal invoked when an check box in the
        Show menu is checked or unchecked.
        """
        for act in self.showMenu.actions():
            act.toggled.connect(function)
