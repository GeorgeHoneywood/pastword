import sys
#try:
from PyQt4 import QtCore, QtGui, uic
#except ValueError:
#    print("damn")
#from openFile import openFile
import sqlite3
import os

qtCreatorFile = "pastword.ui"
 
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)
 
class MyApp(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.actionAdd_entry.triggered.connect(self.addEntry)
        self.actionRemove_entry.triggered.connect(self.removeEntry)
        self.actionOpen.triggered.connect(self.openFile)
        self.actionSave.triggered.connect(self.saveFile)
    
    def addEntry(self):
        rowPosition = self.loginTable.rowCount()
        self.loginTable.insertRow(rowPosition)
    
    def removeEntry(self):
        rowPosition = self.loginTable.rowCount() - 1 
        self.loginTable.removeRow(rowPosition)

    def openFile(self):
        dbName = QtGui.QFileDialog.getOpenFileName(self, 'Open database')
        with open(dbName, "r") as db:
            print(db.read())

    def saveFile(self):
        data = []

        for row in range(self.loginTable.rowCount()):
            data.append([])
            for col in range(self.loginTable.columnCount()):
                try:
                    data[row].append(self.loginTable.item(row, col).text())
                except AttributeError:
                    print("oh no")
             
        dbFile = "logins.db"

        if os.path.isfile(dbFile) == False:
            dbConn = sqlite3.connect(dbFile)
            dbCursor = dbConn.cursor()

            dbCursor.execute("CREATE TABLE logins (site TEXT NOT NULL, username TEXT, email TEXT, password TEXT, notes TEXT)")
            dbConn.commit()
        else:
            dbConn = sqlite3.connect(dbFile)
            dbCursor = dbConn.cursor()

        for item in range(len(data)):
            #print(item)
            dataTuple = tuple(data[item])

            #print(dataTuple)
            dbCursor.execute("INSERT INTO logins VALUES (?,?,?,?,?)", dataTuple)
            dbConn.commit()

        dbCursor.execute("SELECT * FROM logins")
        print(dbCursor.fetchall())

        dbConn.close()

        #print(data)
        # for row in range(model.rowCount()):
        #     data.append([])
        #     for column in range(model.columnCount()):
        #         index = model.index(row, column)
        #         # We suppose data are strings
        #         data[row].append(str(model.data(index).toString()))

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())