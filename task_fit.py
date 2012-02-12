import task

class Task(task.Task):
    def __init__(self, mainWindow, parent = None):
        super(Task, self).__init__(mainWindow, parent)

    def run(self):
        """
        The code in this method is run in another thread.
        """
        self.messageAdded.emit("Fitting absorbance")
        self.mainWindow.data.fit(self.messageAdded.emit)

    def postRun(self):
        """
        The code in this method is run in GUI thread.
        """
        # Refresh GUI
        self.mainWindow.scene.updateFit()
        self.mainWindow.scene.updateResidualsGraph()
        self.mainWindow.scene.informationTable.recreateFromData()
