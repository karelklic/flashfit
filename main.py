#!/usr/bin/python

import sys
import PyQt4
import gui_mainwindow

application = PyQt4.QtGui.QApplication(sys.argv)
PyQt4.QtCore.QCoreApplication.setOrganizationName("flashfit")
PyQt4.QtCore.QCoreApplication.setOrganizationDomain("")
PyQt4.QtCore.QCoreApplication.setApplicationName("flashfit");
window = gui_mainwindow.MainWindow()
window.show()
application.lastWindowClosed.connect(application.quit)
application.exec_()
