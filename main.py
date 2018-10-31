import sys, os, sqlite3, string
from random import choice

from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from findDataFile import findDataFile #!!!!!!!!work out how to do!!!!!!!!!!!!

import passwordGenerator

Ui_MainWindow, QtBaseClass = uic.loadUiType(findDataFile("pastword.ui"))

class editEntryDialog(QtGui.QDialog):
    def __init__(self, currentWindow):
        QtGui.QDialog.__init__(self)
        uic.loadUi(findDataFile("editEntry.ui"), self)

        self.pbCancel.clicked.connect(self.close)
        self.pbAccept.clicked.connect(currentWindow.acceptEdit)

# class passwordGenerator(QtGui.QDialog):
#     def __init__(self, currentWindow):
#         QtGui.QDialog.__init__(self)
#         uic.loadUi(findDataFile("passwordGenerator.ui"), self)

#         self.pbGenerate.clicked.connect(self.generatePassword)
#         self.sliderPasswordLength.valueChanged.connect(self.generatePassword)
#         self.radioIncludeLowerCase.toggled.connect(self.generatePassword)
#         self.radioIncludeUpperCase.toggled.connect(self.generatePassword)
#         self.radioIncludeNumbers.toggled.connect(self.generatePassword)
#         self.radioIncludePunctuation.toggled.connect(self.generatePassword)

#         self.pbCopy2Clipboard.clicked.connect(self.copy2Clipboard)
#         self.txtGeneratedPassword.setFont(QtGui.QFont("Monospace"))

#         self.generatePassword()

#     def generatePassword(self):
#         charsToUse = ""
#         if self.radioIncludeLowerCase.isChecked():
#             charsToUse += string.ascii_lowercase
#         if self.radioIncludeUpperCase.isChecked():
#             charsToUse += string.ascii_uppercase
#         if self.radioIncludeNumbers.isChecked():
#             charsToUse += string.digits 
#         if self.radioIncludePunctuation.isChecked():
#             charsToUse += string.punctuation
#         if charsToUse == "":
#             self.txtGeneratedPassword.clear()
#             self.txtGeneratedPassword.appendPlainText("Select at least one character set")
#             return None

#         length = self.sliderPasswordLength.value()

#         password = "".join(choice(charsToUse) for chars in range(length))

#         self.txtGeneratedPassword.clear()
#         self.txtGeneratedPassword.appendPlainText(password)

#     def copy2Clipboard(self):
#         QtGui.QApplication.clipboard().clear()
#         QtGui.QApplication.clipboard().setText(self.txtGeneratedPassword.toPlainText())

class mainWindow(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.actionOpen.triggered.connect(self.openFile)
        self.actionSave.triggered.connect(lambda: self.saveFile("default"))
        self.actionSave_as.triggered.connect(lambda: self.saveFile("saveAs"))
        self.actionAdd_entry.triggered.connect(self.addEntry)
        self.actionRemove_entry.triggered.connect(self.removeEntry)

        self.actionEdit_entry.triggered.connect(self.editEntry)
        self.loginTable.doubleClicked.connect(self.editEntry)
        self.editPopup = editEntryDialog(self)

        self.actionPassword_Generator.triggered.connect(self.passwordGenerator)
        self.pwGenPopup = passwordGenerator(self)
        
    def addEntry(self):
        #print("dab")
        rowPosition = self.loginTable.rowCount()
        self.loginTable.insertRow(rowPosition)
    
    def removeEntry(self):
        indexes = self.loginTable.selectionModel().selectedRows()
        for row in sorted(indexes, reverse=True):
            #print(row.row())
            self.loginTable.removeRow(row.row())

    def editEntry(self):
        indexes = self.loginTable.selectionModel().selectedRows()
        index = indexes[0].row()

        try:
            self.editPopup.txtSite.setText(self.loginTable.item(index, 0).text())
            self.editPopup.txtUsername.setText(self.loginTable.item(index, 1).text())
            self.editPopup.txtEmail.setText(self.loginTable.item(index, 2).text())
            self.editPopup.txtPassword.setText(self.loginTable.item(index, 3).text())
            self.editPopup.txtNotes.setText(self.loginTable.item(index, 4).text())
            
        except AttributeError:
            print("Ensure all fields are filled out")
            self.editPopup.txtSite.setText("")
            self.editPopup.txtUsername.setText("")
            self.editPopup.txtEmail.setText("")
            self.editPopup.txtPassword.setText("")
            self.editPopup.txtNotes.setText("")

        self.editPopup.exec_()
    
    def acceptEdit(self):
        indexes = self.loginTable.selectionModel().selectedRows()
        index = indexes[0].row()

        #print(self.editPopup.txtSite.text())

        self.loginTable.setItem(index, 0, QtGui.QTableWidgetItem(self.editPopup.txtSite.text()))
        self.loginTable.setItem(index, 1, QtGui.QTableWidgetItem(self.editPopup.txtUsername.text()))
        self.loginTable.setItem(index, 2, QtGui.QTableWidgetItem(self.editPopup.txtEmail.text()))
        self.loginTable.setItem(index, 3, QtGui.QTableWidgetItem(self.editPopup.txtPassword.text()))
        self.loginTable.setItem(index, 4, QtGui.QTableWidgetItem(self.editPopup.txtNotes.text()))

        self.editPopup.close()

    def passwordGenerator(self):
        self.pwGenPopup.exec_()

    def openFile(self):
        dbName = QtGui.QFileDialog.getOpenFileName(self, 'Open database')
        
        dbConn = sqlite3.connect(dbName)
        dbCursor = dbConn.cursor()

        dbCursor.execute("SELECT * FROM logins")
        data = dbCursor.fetchall()
        #print(data)

        for row in range(len(data)):
            self.addEntry()
            #print(len(data[row]))
            for col in range(len(data[row])):
                #print(data[row][col])
                self.loginTable.setItem(row, col, QtGui.QTableWidgetItem(data[row][col]))

    def saveFile(self, saveType):
        if saveType == "saveAs":
            dbFile = QtGui.QFileDialog.getSaveFileName() + ".db"
        else:
            dbFile = "logins.db"

        data = []

        for row in range(self.loginTable.rowCount()):
            data.append([])
            for col in range(self.loginTable.columnCount()):
                try:
                    data[row].append(self.loginTable.item(row, col).text())
                except AttributeError:
                    print("value empty")

        dbConn = sqlite3.connect(dbFile)
        dbCursor = dbConn.cursor()

        if saveType == "default":
            dbCursor.execute("DROP TABLE logins")
            dbConn.commit()

        print("creating table")
        dbCursor.execute("CREATE TABLE logins (site TEXT NOT NULL, username TEXT, email TEXT, password TEXT, notes TEXT)")
        dbConn.commit()

        for item in range(len(data)):
            #print(item)
            dataTuple = tuple(data[item])

            #print(dataTuple)
            dbCursor.execute("INSERT INTO logins VALUES (?,?,?,?,?)", dataTuple)
            dbConn.commit()

        dbConn.close()

def main():
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("your title") #doesn't work
    window = mainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()