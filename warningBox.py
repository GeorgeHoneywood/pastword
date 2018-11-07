from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *

def warningBox(message, detail):
    warning = QtGui.QMessageBox()
    warning.setIcon(QtGui.QMessageBox.Warning)
    warning.setWindowTitle("Warning")

    warning.setText(message)
    if detail != None:
        warning.setDetailedText("Cause of exception:\n" + str(detail))

    warning.exec_()