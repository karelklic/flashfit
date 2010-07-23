# -*- coding: utf-8-unix -*- (Python reads this)
from PyQt4 import QtCore, QtGui
from font import Font
import variables
import sip

class Dialog(QtGui.QDialog):
    """
    Allows user to change Absorbance Axis settings and Time Axis
    settings.
    """
    def __init__(self, parentWindow):
        QtGui.QDialog.__init__(self, parentWindow)
        self.setWindowTitle("Axes Settings")
        self.create(False)

    def create(self, default):
        absorbanceAxis = self.createAxisBox("Absorbance axis",
                                            variables.absorbanceAxisValuesFont.value(default),
                                            variables.absorbanceAxisCaptionFont.value(default))
        absorbanceAxis.captionText.setChecked(variables.absorbanceAxisCaptionEnabled.value(default))
        absorbanceAxis.captionEdit.setText(variables.absorbanceAxisCaption.value(default))

        timeAxis = self.createAxisBox("Time axis",
                                      variables.timeAxisValuesFont.value(default),
                                      variables.timeAxisCaptionFont.value(default))
        timeAxis.captionText.setChecked(variables.timeAxisCaptionEnabled.value(default))
        timeAxis.captionEdit.setText(variables.timeAxisCaption.value(default))

        self.gridWidget = QtGui.QWidget()
        gridLayout = QtGui.QGridLayout(self.gridWidget)
        gridLayout.addWidget(absorbanceAxis, 0, 0)
        gridLayout.addWidget(timeAxis, 0, 1)

        def okPushed():
            variables.absorbanceAxisValuesFont.setValue(absorbanceAxis.valuesFont)
            variables.absorbanceAxisCaptionFont.setValue(absorbanceAxis.captionFont)
            variables.absorbanceAxisCaptionEnabled.setValue(absorbanceAxis.captionText.isChecked())
            variables.absorbanceAxisCaption.setValue(absorbanceAxis.captionEdit.text())

            variables.timeAxisValuesFont.setValue(timeAxis.valuesFont)
            variables.timeAxisCaptionFont.setValue(timeAxis.captionFont)
            variables.timeAxisCaptionEnabled.setValue(timeAxis.captionText.isChecked())
            variables.timeAxisCaption.setValue(timeAxis.captionEdit.text())
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

    def createAxisBox(self, groupName, valuesFont, captionFont):
        group = QtGui.QGroupBox(groupName)
        group.valuesFont = valuesFont
        group.captionFont = captionFont
        layout = QtGui.QFormLayout(group)

        valuesFontLabel = QtGui.QLabel("Values font:")
        group.valuesFontButton = QtGui.QPushButton(valuesFont.toUserString())
        layout.addRow(valuesFontLabel, group.valuesFontButton)

        def valuesFontButtonPush():
            (font, ok) = QtGui.QFontDialog.getFont(group.valuesFont, self)
            if ok:
                group.valuesFont = Font(font=font)
                group.valuesFontButton.setText(group.valuesFont.toUserString())

        group.valuesFontButton.clicked.connect(valuesFontButtonPush)

        group.captionText = QtGui.QCheckBox("Caption:")
        group.captionText.setChecked(True)
        group.captionEdit = QtGui.QLineEdit()
        layout.addRow(group.captionText, group.captionEdit)

        captionFontLabel = QtGui.QLabel("Caption font:")
        group.captionFontButton = QtGui.QPushButton(group.captionFont.toUserString())
        layout.addRow(captionFontLabel, group.captionFontButton)

        def captionFontButtonPush():
            (font, ok) = QtGui.QFontDialog.getFont(group.captionFont, self)
            if ok:
                group.captionFont = Font(font=font)
                group.captionFontButton.setText(group.captionFont.toUserString())

        group.captionFontButton.clicked.connect(captionFontButtonPush)

        def captionTextStateChanged(state):
            group.captionEdit.setEnabled(state == QtCore.Qt.Checked)
            captionFontLabel.setEnabled(state == QtCore.Qt.Checked)
            group.captionFontButton.setEnabled(state == QtCore.Qt.Checked)

        group.captionText.stateChanged.connect(captionTextStateChanged)
        return group
