import sys, os, sqlite3

from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtGui import *
from PyQt4.QtCore import *

qtCreatorFile1 = "pastword.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile1)
 

class editEntryDialog(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        uic.loadUi("editEntry.ui", self)

        #self.setupUi(self)
        #self.loadEntry()

    # def loadEntry(self):
    #     indexes = mainWindow.loginTable.selectionModel().selectedRows()
    #     print(indexes)

class mainWindow(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.actionOpen.triggered.connect(self.openFile)
        self.actionSave.triggered.connect(self.saveFile)
        self.actionAdd_entry.triggered.connect(self.addEntry)
        self.actionRemove_entry.triggered.connect(self.removeEntry)
        self.actionEdit_entry.triggered.connect(self.editEntry)
    
    def addEntry(self):
        #print("dab")
        rowPosition = self.loginTable.rowCount()
        self.loginTable.insertRow(rowPosition)
    
    def removeEntry(self):
        indexes = self.loginTable.selectionModel().selectedRows()
        for row in sorted(indexes, reverse=True):
            print(row.row())
            self.loginTable.removeRow(row.row())

    def editEntry(self):
        self.editPopup = editEntryDialog()

        indexes = self.loginTable.selectionModel().selectedRows()
        index = indexes[0].row()

        self.editPopup.txtSite.setText(self.loginTable.item(index, 0).text())
        self.editPopup.txtUsername.setText(self.loginTable.item(index, 1).text())
        self.editPopup.txtEmail.setText(self.loginTable.item(index, 2).text())
        self.editPopup.txtPassword.setText(self.loginTable.item(index, 3).text())
        self.editPopup.txtNotes.setText(self.loginTable.item(index, 4).text())

        self.editPopup.exec_()

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
                self.loginTable.setItem(row, col, QTableWidgetItem(data[row][col]))

    def saveFile(self):
        data = []

        for row in range(self.loginTable.rowCount()):
            data.append([])
            for col in range(self.loginTable.columnCount()):
                try:
                    data[row].append(self.loginTable.item(row, col).text())
                except AttributeError:
                    print("value empty")
             
        dbFile = "logins.db"

        dbConn = sqlite3.connect(dbFile)
        dbCursor = dbConn.cursor()

        dbCursor.execute("DROP TABLE logins")
        dbConn.commit()

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
    window = mainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()