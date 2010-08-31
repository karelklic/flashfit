# -*- coding: utf-8-unix -*- (Python reads this)
from PyQt4 import QtCore, QtGui
from gui_spinbox import SpinBox
from font import Font
import variables
import sip

class Dialog(QtGui.QDialog):
    """
    Appearance dialog sets fonts, captions, printed precision.
    Loads from QSettings, saves to QSettings.
    """
    def __init__(self, parentWindow):
        QtGui.QDialog.__init__(self, parentWindow)
        self.setWindowTitle("Textual Data Settings")
        self.create(False)

    def create(self, default):
        legend = self.createBox("Information Box",
                                variables.legendFont.value(default),
                                variables.legendTable.value(default))
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

    def createBox(self, groupName, font, visibleItems):
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

        itemsLabel = QtGui.QLabel("Items:")

        def itemWidgetList(items):
            widgetItems = []
            for item in items:
                textItem = self.parent().textItems.all[str(item)]
                widgetItem = QtGui.QTreeWidgetItem([ textItem.label ])
                widgetItems.append(widgetItem)
            return widgetItems

        itemsLayout = QtGui.QHBoxLayout()
        availableItemsWidget = QtGui.QTreeWidget()
        availableItemsWidget.setColumnCount(1)
        availableItemsWidget.setHeaderLabels(["Available"])
        availableItems = self.parent().textItems.available(visibleItems)
        availableItemsWidget.addTopLevelItems(itemWidgetList(availableItems))
        itemsLayout.addWidget(availableItemsWidget)

        leftRightArrowsLayout = QtGui.QVBoxLayout()
        leftArrow = QtGui.QPushButton("<-")
        leftRightArrowsLayout.addWidget(leftArrow)
        rightArrow = QtGui.QPushButton("->")
        leftRightArrowsLayout.addWidget(rightArrow)
        leftRightArrows = QtGui.QWidget(self)
        leftRightArrows.setLayout(leftRightArrowsLayout)
        itemsLayout.addWidget(leftRightArrows)

        visibleItemsPackLayout = QtGui.QVBoxLayout()
        visibleItemsWidget = QtGui.QTreeWidget()
        visibleItemsWidget.setColumnCount(1)
        visibleItemsWidget.setHeaderLabels(["Visible"])
        visibleItemsWidget.addTopLevelItems(itemWidgetList(visibleItems))
        visibleItemsPackLayout.addWidget(visibleItemsWidget)

        upDownArrowsLayout = QtGui.QHBoxLayout()
        upArrow = QtGui.QPushButton("Up")
        upDownArrowsLayout.addWidget(upArrow)
        downArrow = QtGui.QPushButton("Down")
        upDownArrowsLayout.addWidget(downArrow)
        upDownArrows = QtGui.QWidget(self)
        upDownArrows.setLayout(upDownArrowsLayout)
        visibleItemsPackLayout.addWidget(upDownArrows)

        def updateUpDownArrowsEnable():
            selectedItems = visibleItemsWidget.selectedItems()
            if len(selectedItems) != 1:
                upArrow.setEnabled(False)
                downArrow.setEnabled(False)
                return
            modelIndex = visibleItemsWidget.indexFromItem(selectedItems[0])
            upArrow.setEnabled(modelIndex.row() > 0)
            downArrow.setEnabled(modelIndex.row() < visibleItemsWidget.topLevelItemCount() - 1)

        visibleItemsWidget.itemSelectionChanged.connect(updateUpDownArrowsEnable)
        updateUpDownArrowsEnable()

        def updateLeftArrowEnable():
            leftArrow.setEnabled(len(visibleItemsWidget.selectedItems()) > 0)

        visibleItemsWidget.itemSelectionChanged.connect(updateLeftArrowEnable)
        updateLeftArrowEnable()

        def updateRightArrowEnable():
            rightArrow.setEnabled(len(availableItemsWidget.selectedItems()) > 0)

        availableItemsWidget.itemSelectionChanged.connect(updateRightArrowEnable)
        updateRightArrowEnable()

        def upArrowClicked():
            item = visibleItemsWidget.selectedItems()[0]
            index = visibleItemsWidget.indexOfTopLevelItem(item)
            visibleItemsWidget.takeTopLevelItem(index)
            visibleItemsWidget.insertTopLevelItem(index - 1, item)
            visibleItemsWidget.setCurrentItem(item)
            updateUpDownArrowsEnable()

        upArrow.clicked.connect(upArrowClicked)

        def downArrowClicked():
            item = visibleItemsWidget.selectedItems()[0]
            index = visibleItemsWidget.indexOfTopLevelItem(item)
            visibleItemsWidget.takeTopLevelItem(index)
            visibleItemsWidget.insertTopLevelItem(index + 1, item)
            visibleItemsWidget.setCurrentItem(item)
            updateUpDownArrowsEnable()

        downArrow.clicked.connect(downArrowClicked)

        def leftArrowClicked():
            item = visibleItemsWidget.selectedItems()[0]
            index = visibleItemsWidget.indexOfTopLevelItem(item)
            visibleItemsWidget.takeTopLevelItem(index)
            availableItemsWidget.addTopLevelItem(item)
            updateUpDownArrowsEnable()

        leftArrow.clicked.connect(leftArrowClicked)

        def rightArrowClicked():
            item = availableItemsWidget.selectedItems()[0]
            index = availableItemsWidget.indexOfTopLevelItem(item)
            availableItemsWidget.takeTopLevelItem(index)
            visibleItemsWidget.addTopLevelItem(item)
            updateUpDownArrowsEnable()

        rightArrow.clicked.connect(rightArrowClicked)

        visibleItemsPack = QtGui.QWidget()
        visibleItemsPack.setLayout(visibleItemsPackLayout)
        itemsLayout.addWidget(visibleItemsPack)

        items = QtGui.QWidget(self)
        items.setLayout(itemsLayout)

        layout.addRow(itemsLabel, items)
        return group
