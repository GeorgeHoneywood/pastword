from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from findDataFile import findDataFile
import resources_rc  # import icons

class passCheck(QtGui.QDialog):
    def __init__(self, mainWindow):
        QtGui.QDialog.__init__(self)
        uic.loadUi(findDataFile("passCheck.ui"), self)
        
        self.pbCheckPass.clicked.connect(mainWindow.setPass)

class newPass(QtGui.QDialog):
    def __init__(self, mainWindow):
        QtGui.QDialog.__init__(self)
        uic.loadUi(findDataFile("newPass.ui"), self)

        self.pbCheckPass.clicked.connect(mainWindow.setPass)