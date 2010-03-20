from PyQt4 import QtCore, QtGui

class ConsoleEdit(QtGui.QTextEdit):
    def __init__(self):
        QtGui.QTextEdit.__init__(self)
        font = QtGui.QFont("courier new", 10)
        font.setStyleHint(QtGui.QFont.TypeWriter)
        self.document().setDefaultFont(font)

    def displayPrompt(self):
        """
        Displays the command prompt at the bottom of the buffer,
        and moves cursor there.
        """
        self.append(">>> ")
        self.moveCursor(QtGui.QTextCursor.End)
        self.promptBlockNumber = self.textCursor().blockNumber()
        self.promptColumnNumber = self.textCursor().columnNumber()
        self.promptPosition = self.textCursor().position()

    def getCurrentCommand(self):
        """
        Gets the current command written on the command prompt.
        """
        # Select the command.
        block = self.document().findBlockByNumber(self.promptBlockNumber)
        return block.text().mid(self.promptColumnNumber)

    def isInEditionZone(self):
        return self.promptBlockNumber == self.textCursor().blockNumber() and \
               self.promptColumnNumber <= self.textCursor().columnNumber()
        
    def keyPressEvent(self, event):
        # Run the command if enter was pressed.
        if event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return:
            event.accept()
            command = self.getCurrentCommand()
            if len(command) > 0:
                result = ""
                try:
                    result = eval(str(command), globals(), locals())
                    #exec str(command) in globals(), locals()
                except Exception as error:
                    result = str(error)
                self.append(str(result));            
                self.moveCursor(QtGui.QTextCursor.End)
            self.displayPrompt()
            return

        if event.key() == QtCore.Qt.Key_Backspace:
            event.accept()
            if not self.isInEditionZone():
                self.moveCursor(QtGui.QTextCursor.End)
                # First backspace just moves the cursor.
                return 
            # If there is something to be deleted, delete it.
            if self.promptColumnNumber < self.textCursor().columnNumber():
                self.textCursor().deletePreviousChar()
            return

        if event.key() == QtCore.Qt.Key_Left:
            event.accept()
            if not self.isInEditionZone():
                self.moveCursor(QtGui.QTextCursor.End)
                # First backspace just moves the cursor.
                return 
            if self.promptColumnNumber < self.textCursor().columnNumber():
                mode = QtGui.QTextCursor.MoveAnchor
                if event.modifiers() & QtCore.Qt.ShiftModifier:
                    mode = QtGui.QTextCursor.KeepAnchor
                self.moveCursor(QtGui.QTextCursor.Left, mode)
            return

        if event.key() == QtCore.Qt.Key_Right:
            event.accept()
            if not self.isInEditionZone():
                self.moveCursor(QtGui.QTextCursor.End)
                # First backspace just moves the cursor.
                return 
            mode = QtGui.QTextCursor.MoveAnchor
            if event.modifiers() & QtCore.Qt.ShiftModifier:
                mode = QtGui.QTextCursor.KeepAnchor
            self.moveCursor(QtGui.QTextCursor.Right, mode)
            return
            
        if len(event.text()) > 0:
            event.accept()
            if not self.isInEditionZone():
                self.moveCursor(QtGui.QTextCursor.End)
            self.textCursor().insertText(event.text())

class Console(QtGui.QDockWidget):
    """
    Console window used for advanced commands, debugging, 
    logging, and profiling.
    """
    def __init__(self, parentWindow):
        QtGui.QDockWidget.__init__(self, parentWindow)
        self.setTitleBarWidget(QtGui.QWidget())
        self.setAllowedAreas(QtCore.Qt.BottomDockWidgetArea)
        self.setFeatures(QtGui.QDockWidget.NoDockWidgetFeatures)
        self.setVisible(False)

        # Add console window
        self.consoleEdit = ConsoleEdit()
        self.consoleEdit.displayPrompt()
        self.setWidget(self.consoleEdit)
        
    def setVisible(self, visible):
        """
        Override to set proper focus.
        """
        QtGui.QDockWidget.setVisible(self, visible)
        if visible:
            self.consoleEdit.setFocus(QtCore.Qt.OtherFocusReason)
