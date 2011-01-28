from PyQt4 import QtCore, QtGui

class Font(QtGui.QFont):
    def __init__(self, font = None, pointSize = 0):
        QtGui.QFont.__init__(self)
        if font:
            self.fromString(font.toString())
        if pointSize > 0:
            self.setPointSize(pointSize)

    def toUserString(self):
        res = self.family() + ", "
        if self.pixelSize() >= 0:
            res += str(self.pixelSize()) + " px"
        else:
            res += str(self.pointSize()) + " pt"
        return res

    def toStorableString(self):
        return "{0},{1}".format(self.family(), self.pointSize())

    def fromStorableString(self, string):
        elems = string.split(",")
        if len(elems) > 0:
            self.setFamily(elems[0])
        if len(elems) > 1:
            self.setPointSize(int(elems[1]))
