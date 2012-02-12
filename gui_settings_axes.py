# -*- coding: utf-8-unix -*- (Python reads this)
from PyQt4 import QtCore, QtGui
from font import Font
import variables
import sip

class Dialog(QtGui.QDialog):
    """
    Allows user to change Value Axis settings and Time Axis settings.
    """
    def __init__(self, parentWindow):
        QtGui.QDialog.__init__(self, parentWindow)
        self.setWindowTitle("Axes Settings")
        self.create(False)

    def create(self, default):
        valueAxis = self.createAxisBox("Value axis",
                                       variables.valueAxisValuesFont.value(default),
                                       variables.valueAxisCaptionFont.value(default),
                                       True)
        valueAxis.captionTextAbsorbance.setChecked(variables.valueAxisCaptionEnabled.value(default))
        valueAxis.captionEditAbsorbance.setText(variables.absorbanceAxisCaption.value(default))
        valueAxis.captionEditLuminiscence.setText(variables.luminiscenceAxisCaption.value(default))

        timeAxis = self.createAxisBox("Time axis",
                                      variables.timeAxisValuesFont.value(default),
                                      variables.timeAxisCaptionFont.value(default),
                                      False)
        timeAxis.captionText.setChecked(variables.timeAxisCaptionEnabled.value(default))
        timeAxis.captionEdit.setText(variables.timeAxisCaption.value(default))

        self.gridWidget = QtGui.QWidget()
        gridLayout = QtGui.QGridLayout(self.gridWidget)
        gridLayout.addWidget(valueAxis, 0, 0)
        gridLayout.addWidget(timeAxis, 0, 1)

        def okPushed():
            variables.valueAxisValuesFont.setValue(valueAxis.valuesFont)
            variables.valueAxisCaptionFont.setValue(valueAxis.captionFont)
            variables.valueAxisCaptionEnabled.setValue(valueAxis.captionTextAbsorbance.isChecked())
            variables.absorbanceAxisCaption.setValue(valueAxis.captionEditAbsorbance.text())
            variables.luminiscenceAxisCaption.setValue(valueAxis.captionEditLuminiscence.text())

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

    def createAxisBox(self, groupName, valuesFont, captionFont, valueAxis):
        """
        valueAxis - boolean, True for value axis, False for time axis
        """
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

        def captionTextStateChanged(state):
            if valueAxis:
                group.captionEditAbsorbance.setEnabled(state == QtCore.Qt.Checked)
                group.captionEditLuminiscence.setEnabled(state == QtCore.Qt.Checked)
            else:
                group.captionEdit.setEnabled(state == QtCore.Qt.Checked)

            captionFontLabel.setEnabled(state == QtCore.Qt.Checked)
            group.captionFontButton.setEnabled(state == QtCore.Qt.Checked)

        if valueAxis:
            group.captionTextAbsorbance = QtGui.QCheckBox("Absorbance Caption:")
            group.captionTextAbsorbance.setChecked(True)
            group.captionTextAbsorbance.stateChanged.connect(captionTextStateChanged)
            group.captionEditAbsorbance = QtGui.QLineEdit()
            layout.addRow(group.captionTextAbsorbance, group.captionEditAbsorbance)

            group.captionTextLuminiscence = QtGui.QLabel("Luminiscence Caption:")
            group.captionEditLuminiscence = QtGui.QLineEdit()
            layout.addRow(group.captionTextLuminiscence, group.captionEditLuminiscence)
        else:
            group.captionText = QtGui.QCheckBox("Caption:")
            group.captionText.setChecked(True)
            group.captionText.stateChanged.connect(captionTextStateChanged)
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
        return group
