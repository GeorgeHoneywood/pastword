import string
from random import choice

from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from findDataFile import findDataFile

class passwordGenerator(QtGui.QDialog):
    def __init__(self, currentWindow):
        QtGui.QDialog.__init__(self)
        uic.loadUi(findDataFile("passwordGenerator.ui"), self)

        self.pbGenerate.clicked.connect(self.generatePassword)
        self.sliderPasswordLength.valueChanged.connect(self.generatePassword)
        self.radioIncludeLowerCase.toggled.connect(self.generatePassword)
        self.radioIncludeUpperCase.toggled.connect(self.generatePassword)
        self.radioIncludeNumbers.toggled.connect(self.generatePassword)
        self.radioIncludePunctuation.toggled.connect(self.generatePassword)

        self.pbCopy2Clipboard.clicked.connect(self.copy2Clipboard)
        self.txtGeneratedPassword.setFont(QtGui.QFont("Monospace"))

        self.generatePassword()

    def generatePassword(self):
        charsToUse = ""
        if self.radioIncludeLowerCase.isChecked():
            charsToUse += string.ascii_lowercase
        if self.radioIncludeUpperCase.isChecked():
            charsToUse += string.ascii_uppercase
        if self.radioIncludeNumbers.isChecked():
            charsToUse += string.digits 
        if self.radioIncludePunctuation.isChecked():
            charsToUse += string.punctuation
        if charsToUse == "":
            self.txtGeneratedPassword.clear()
            self.txtGeneratedPassword.appendPlainText("Select at least one character set")
            return None

        length = self.sliderPasswordLength.value()

        password = "".join(choice(charsToUse) for chars in range(length))

        self.txtGeneratedPassword.clear()
        self.txtGeneratedPassword.appendPlainText(password)

    def copy2Clipboard(self):
        QtGui.QApplication.clipboard().clear()
        QtGui.QApplication.clipboard().setText(self.txtGeneratedPassword.toPlainText())