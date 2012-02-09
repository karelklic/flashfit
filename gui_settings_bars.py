# -*- coding: utf-8-unix -*- (Python reads this)
from PyQt4 import QtCore, QtGui
from font import Font
import variables
import sip

class Dialog(QtGui.QDialog):
    """
    Allows user to change Full Light bars settings and Fit bars
    settings.
    """
    def __init__(self, parentWindow):
        QtGui.QDialog.__init__(self, parentWindow)
        self.setWindowTitle("Bars Settings")
        self.create(False)

    def create(self, default):
        fullLightBars = self.createBarBox("Full Light bars",
                                          variables.fullLightBarsVisible.value(default),
                                          variables.fullLightBarsFont.value(default),
                                          variables.fullLightBarsCaptionEnabled.value(default),
                                          variables.fullLightBarsCaption.value(default))

        fitBars = self.createBarBox("Fit bars",
                                    variables.fitBarsVisible.value(default),
                                    variables.fitBarsFont.value(default),
                                    variables.fitBarsCaptionEnabled.value(default),
                                    variables.fitBarsCaption.value(default))

        self.gridWidget = QtGui.QWidget()
        gridLayout = QtGui.QGridLayout(self.gridWidget)
        gridLayout.addWidget(fullLightBars, 0, 0)
        gridLayout.addWidget(fitBars, 0, 1)

        def okPushed():
            variables.fullLightBarsVisible.setValue(fullLightBars.visible.isChecked())
            variables.fullLightBarsFont.setValue(fullLightBars.captionFont)
            variables.fullLightBarsCaptionEnabled.setValue(fullLightBars.captionText.isChecked())
            variables.fullLightBarsCaption.setValue(fullLightBars.captionEdit.text())

            variables.fitBarsVisible.setValue(fitBars.visible.isChecked())
            variables.fitBarsFont.setValue(fitBars.captionFont)
            variables.fitBarsCaptionEnabled.setValue(fitBars.captionText.isChecked())
            variables.fitBarsCaption.setValue(fitBars.captionEdit.text())
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

    def createBarBox(self, groupName, visible, captionFont, captionChecked, captionText):
        group = QtGui.QGroupBox(groupName)
        group.captionFont = captionFont
        layout = QtGui.QFormLayout(group)

        group.visible = QtGui.QCheckBox("Visible")
        group.visible.setChecked(visible)
        layout.addRow(group.visible)

        group.captionText = QtGui.QCheckBox("Caption:")
        group.captionText.setChecked(captionChecked)
        group.captionEdit = QtGui.QLineEdit()
        group.captionEdit.setText(captionText)
        layout.addRow(group.captionText, group.captionEdit)

        group.captionFontLabel = QtGui.QLabel("Caption font:")
        group.captionFontButton = QtGui.QPushButton(captionFont.toUserString())
        layout.addRow(group.captionFontLabel, group.captionFontButton)

        def captionFontButtonPush():
            (font, ok) = QtGui.QFontDialog.getFont(group.captionFont, self)
            if ok:
                group.captionFont = Font(font = font)
                group.captionFontButton.setText(group.captionFont.toUserString())

        def updateState():
            group.captionText.setEnabled(group.visible.checkState() == QtCore.Qt.Checked)
            visible_and_caption = (group.visible.checkState() == QtCore.Qt.Checked and
                                   group.captionText.checkState() == QtCore.Qt.Checked)
            group.captionEdit.setEnabled(visible_and_caption)
            group.captionFontLabel.setEnabled(visible_and_caption)
            group.captionFontButton.setEnabled(visible_and_caption)

        group.captionFontButton.clicked.connect(captionFontButtonPush)
        group.visible.stateChanged.connect(updateState)
        group.captionText.stateChanged.connect(updateState)
        return group
