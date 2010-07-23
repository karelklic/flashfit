# -*- coding: utf-8-unix -*- (Python reads this)
from PyQt4 import QtCore, QtGui
from gui_spinbox import SpinBox
from font import Font
import variables
import sip

class Appearance(QtGui.QDialog):
    """
    Appearance dialog sets fonts, captions, printed precision.
    Loads from QSettings, saves to QSettings.
    """
    def __init__(self, parentWindow):
        QtGui.QDialog.__init__(self, parentWindow)
        self.setWindowTitle("Appearance")
        self.create(False)

    def create(self, default):
        legend = self.createLegendBox("Measured Values box", variables.legendFont.value(default))
        legend.prec.setValue(variables.legendDisplayedPrecision.value(default))

        self.gridWidget = QtGui.QWidget()
        gridLayout = QtGui.QGridLayout(self.gridWidget)
        gridLayout.addWidget(legend, 0, 0)

        def okPushed():
            variables.legendFont.setValue(legend.font)
            variables.legendDisplayedPrecision.setValue(legend.prec.value())
            self.done(QtGui.QDialog.Accepted)

        def cancelPushed():
            self.done(QtGui.QDialog.Rejected)

        def defaultsPushed():
            sip.delete(self.layout())
            sip.delete(self.gridWidget)
            sip.delete(self.buttonWidget)
            self.create(True)

        ok = QtGui.QPushButton("Ok")
        ok.clicked.connect(okPushed)
        cancel = QtGui.QPushButton("Cancel")
        cancel.clicked.connect(cancelPushed)
        defaults = QtGui.QPushButton("Set default values")
        defaults.clicked.connect(defaultsPushed)
        self.buttonWidget = QtGui.QWidget()
        buttonLayout = QtGui.QHBoxLayout(self.buttonWidget)
        buttonLayout.addStretch()
        buttonLayout.addWidget(defaults)
        buttonLayout.addWidget(cancel)
        buttonLayout.addWidget(ok)

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.gridWidget)
        layout.addWidget(self.buttonWidget)

    def createLegendBox(self, groupName, font):
        group = QtGui.QGroupBox(groupName)
        group.font = font
        layout = QtGui.QFormLayout(group)

        fontLabel = QtGui.QLabel("Font:")
        group.fontButton = QtGui.QPushButton(font.toUserString())
        layout.addRow(fontLabel, group.fontButton)

        def fontButtonPush():
            (ffont, ok) = QtGui.QFontDialog.getFont(group.font, self)
            if ok:
                group.font = Font(font=ffont)
                group.fontButton.setText(group.font.toUserString())

        group.fontButton.clicked.connect(fontButtonPush)

        precLabel = QtGui.QLabel("k(x) precision:")
        group.prec = SpinBox()
        group.prec.setRange(0, 6)
        layout.addRow(precLabel, group.prec)
        precExample = QtGui.QLabel()
        layout.addRow(None, precExample)

        def precValueChanged():
            template = u"%%.%de ± %%.%de" % (group.prec.value(), group.prec.value())
            text = template % (2.213062e+07, 1.307115e+05)
            precExample.setText(text)

        group.prec.valueChanged.connect(precValueChanged)
        group.prec.setValue(6)
        return group
