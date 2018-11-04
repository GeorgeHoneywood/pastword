import sys, os, sqlite3

from shutil import copyfile

from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from findDataFile import findDataFile #!!!!!!!!work out how to do!!!!!!!!!!!!

from passwordGenerator import passwordGenerator

Ui_MainWindow, QtBaseClass = uic.loadUiType(findDataFile("pastword.ui"))

dbName = ""

class editEntryDialog(QtGui.QDialog):
    def __init__(self, currentWindow):
        QtGui.QDialog.__init__(self)
        uic.loadUi(findDataFile("editEntry.ui"), self)

        self.pbCancel.clicked.connect(self.close)
        self.pbAccept.clicked.connect(currentWindow.acceptEdit)

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
        
    def addEntry(self): #effectively the same as edit entry, but dont need to load values into popup
        self.editPopup.exec_()

    def removeEntry(self):
        indexes = self.loginTable.selectionModel().selectedRows()
        for row in sorted(indexes, reverse=True):
            self.loginTable.removeRow(row.row())

    def editEntry(self):
        indexes = self.loginTable.selectionModel().selectedRows()
        index = indexes[0].row()

        try:
            self.editPopup.txtSite.setText(self.loginTable.item(index, 1).text())
            self.editPopup.txtUsername.setText(self.loginTable.item(index, 2).text())
            self.editPopup.txtEmail.setText(self.loginTable.item(index, 3).text())
            self.editPopup.txtPassword.setText(self.loginTable.item(index, 4).text())
            self.editPopup.txtNotes.setText(self.loginTable.item(index, 5).text())
            
        except AttributeError:
            print("Ensure all fields are filled out")
            self.editPopup.txtSite.setText("")
            self.editPopup.txtUsername.setText("")
            self.editPopup.txtEmail.setText("")
            self.editPopup.txtPassword.setText("")
            self.editPopup.txtNotes.setText("")

        self.editPopup.exec_()
    
    def acceptEdit(self):
        dbConn = sqlite3.connect(dbName)
        dbCursor = dbConn.cursor()

        # dbCursor.execute("DROP TABLE IF EXISTS logins")
        # dbConn.commit()
        
        indexList = self.loginTable.selectionModel().selectedRows()
        
        if indexList == []:
            loginData = (None, self.editPopup.txtSite.text(), self.editPopup.txtUsername.text(), self.editPopup.txtEmail.text(), self.editPopup.txtPassword.text(), self.editPopup.txtNotes.text())
            dbCursor.execute("INSERT INTO logins VALUES (?, ?, ?, ?, ?, ?)", loginData)
            
        else:
            index = indexList[0].row()
            loginData = (self.editPopup.txtSite.text(), self.editPopup.txtUsername.text(), self.editPopup.txtEmail.text(), self.editPopup.txtPassword.text(), self.editPopup.txtNotes.text(), index + 1)
            dbCursor.execute("UPDATE logins SET site = ?, username = ?, email = ?, password = ?, notes = ? WHERE login_id = ?", loginData)
        
        dbConn.commit()
        dbConn.close()

        self.updateTable()
        self.editPopup.close()

    def passwordGenerator(self):
        self.pwGenPopup.exec_()

    def openFile(self):
        global dbName
        dbName = QtGui.QFileDialog.getOpenFileName(self, 'Open database')

        dirName = os.path.dirname(dbName)
        baseName = os.path.basename(dbName)
        copyfile(dbName, dirName + "/." + baseName)

        dbName = dirName + "/." + baseName

        dbConn = sqlite3.connect(dbName)
        dbCursor = dbConn.cursor()
        dbCursor.execute("CREATE TABLE IF NOT EXISTS logins (login_id INTEGER PRIMARY KEY, site TEXT, username TEXT, email TEXT, password TEXT, notes TEXT)")
        dbConn.commit()
        dbConn.close()

        self.updateTable()
        
    def saveFile(self, saveType): #savetype ignored for now
        baseName = os.path.basename(dbName)
        copyfile(dbName, baseName[1:]) #only get chars after 1, to overwrite original
        #os.remove(dbName) #can't do this because it means users can't change edit any more

    def updateTable(self):
        dbConn = sqlite3.connect(dbName)
        dbCursor = dbConn.cursor()

        dbCursor.execute("SELECT * FROM logins")
        data = dbCursor.fetchall()

        dbConn.close()

        for rowNumber, rowData in enumerate(data):
            self.loginTable.insertRow(self.loginTable.rowCount())
            for colNumber, cellData in enumerate(rowData):
                self.loginTable.setItem(rowNumber, colNumber, QtGui.QTableWidgetItem(str(cellData)))

        header = self.loginTable.horizontalHeader()
        header.setResizeMode(0, QtGui.QHeaderView.ResizeToContents)

def main():
    app = QtGui.QApplication(sys.argv)
    #app.setApplicationName("your title") #doesn't work
    window = mainWindow()
    window.show()
    try:
        sys.exit(app.exec_())
    except SystemExit:
        print("Exiting program")

if __name__ == "__main__":
    main()