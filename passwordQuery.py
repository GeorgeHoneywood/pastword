from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from findDataFile import findDataFile
import resources_rc  # import icons

class passCheck(QtGui.QDialog):
    def __init__(self, mainWindow):
        QtGui.QDialog.__init__(self)
        uic.loadUi(findDataFile("passCheck.ui"), self)
        
        self.pbCheckPass.clicked.connect(lambda: mainWindow.setPass(self, "check"))

class newPass(QtGui.QDialog):
    def __init__(self, mainWindow):
        QtGui.QDialog.__init__(self)
        uic.loadUi(findDataFile("newPass.ui"), self)

        self.pbNewPass.clicked.connect(lambda: mainWindow.setPass(self, "new"))
        self.txtNewPass1.textChanged.connect(self.checkSame)
        self.txtNewPass2.textChanged.connect(self.checkSame)

        self.pbNewPass.setEnabled(False)

    def checkSame(self):
        if len(self.txtNewPass1.text()) <= 8:
            self.txtNewPass1.setStyleSheet("color: yellow;")
            return None
        else:
            self.txtNewPass1.setStyleSheet("color: blue;")

        if self.txtNewPass1.text() == self.txtNewPass2.text():
            self.txtNewPass2.setStyleSheet("color: green;")
            self.pbNewPass.setEnabled(True)

        else:
            self.txtNewPass2.setStyleSheet("color: red;")
            self.pbNewPass.setEnabled(False)