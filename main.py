import sys, os, sqlite3

from shutil import copyfile

from PyQt4 import QtCore, QtGui, uic
#from PyQt4 import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from findDataFile import findDataFile

from passwordGenerator import passwordGenerator
import resources_rc #import icons

Ui_MainWindow, QtBaseClass = uic.loadUiType(findDataFile("pastword.ui"))

dbName = "" #make file name global variable

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
        self.actionNewDB.triggered.connect(self.newDB)

        self.actionEdit_entry.triggered.connect(self.editEntry)
        self.loginTable.doubleClicked.connect(self.editEntry)
        self.editPopup = editEntryDialog(self)

        self.actionPassword_Generator.triggered.connect(self.passwordGenerator)
        self.pwGenPopup = passwordGenerator(self)

        self.pbSearch.clicked.connect(self.searchDB)
        self.txtSearch.returnPressed.connect(self.searchDB)
        self.txtSearch.textChanged.connect(self.searchDB)
        self.cbAutoSearch.stateChanged.connect(self.autoSearch)

        self.loginTable.customContextMenuRequested.connect(self.contextMenuEvent) #tried to impliment context menu, doesn't work
        
    def addEntry(self): #effectively the same as edit entry, but dont need to load values into popup
        self.clearEditPopup() #remove entries from the popup before displaying
        self.editPopup.exec_()

    def removeEntry(self):
        dbConn, dbCursor = self.dbConnect()

        i = 0
        indexList = self.loginTable.selectionModel().selectedRows()
        for row in sorted(indexList):
            index = indexList[i].row()
            index = int(self.loginTable.item(index, 0).text())
            dbCursor.execute("DELETE FROM logins WHERE login_id = ?", (index, )) #make sure it is tuple rather than int
            i += 1
            # self.loginTable.removeRow(row.row())

        dbConn.commit()
        dbConn.close()
        self.updateTable(searchQ = None)

    def editEntry(self):
        indexes = self.loginTable.selectionModel().selectedRows()
        try:
            index = indexes[0].row()
        except IndexError as detail:
            self.warningBox("Please select an item before trying to edit it", detail)
            return None

        try:
            self.editPopup.txtSite.setText(self.loginTable.item(index, 1).text())
            self.editPopup.txtUsername.setText(self.loginTable.item(index, 2).text())
            self.editPopup.txtEmail.setText(self.loginTable.item(index, 3).text())
            self.editPopup.txtPassword.setText(self.loginTable.item(index, 4).text())
            self.editPopup.txtNotes.setText(self.loginTable.item(index, 5).text())
        except AttributeError as detail:
            self.warningBox("Ensure all fields are filled out", detail)
            self.clearEditPopup()

        self.editPopup.exec_()

    def clearEditPopup(self):
            self.editPopup.txtSite.setText("")
            self.editPopup.txtUsername.setText("")
            self.editPopup.txtEmail.setText("")
            self.editPopup.txtPassword.setText("")
            self.editPopup.txtNotes.setText("")
    
    def acceptEdit(self):
        dbConn, dbCursor = self.dbConnect()

        # dbCursor.execute("DROP TABLE IF EXISTS logins")
        # dbConn.commit()
        
        indexList = self.loginTable.selectionModel().selectedRows()
        if indexList == []: #if there are not not rows selcted
            loginData = (None, self.editPopup.txtSite.text(), self.editPopup.txtUsername.text(), self.editPopup.txtEmail.text(), self.editPopup.txtPassword.text(), self.editPopup.txtNotes.text(), 0)
            dbCursor.execute("INSERT INTO logins VALUES (?, ?, ?, ?, ?, ?, ?)", loginData)
            
        else: #if the user has selected rows
            indexTable = indexList[0].row()
            indexDB = int(self.loginTable.item(indexTable, 0).text())
            loginData = (self.editPopup.txtSite.text(), self.editPopup.txtUsername.text(), self.editPopup.txtEmail.text(), self.editPopup.txtPassword.text(), self.editPopup.txtNotes.text(), indexDB)
            dbCursor.execute("UPDATE logins SET site = ?, username = ?, email = ?, password = ?, notes = ? WHERE login_id = ?", loginData)
        
        dbConn.commit()
        dbConn.close()

        self.updateTable(searchQ = None)
        self.editPopup.close()

    def passwordGenerator(self):
        self.pwGenPopup.exec_()

    def openFile(self):
        global dbName
        dbName = QtGui.QFileDialog.getOpenFileName(self, 'Open database')

        if dbName == '':
            self.warningBox("Please select a file", None)
            return None

        dirName = os.path.dirname(dbName)
        baseName = os.path.basename(dbName)
        copyfile(dbName, dirName + "/." + baseName)

        dbName = dirName + "/." + baseName

        self.updateTable(searchQ = None)
        
    def saveFile(self, saveType): #savetype ignored for now
        dirName = os.path.dirname(dbName)
        baseName = os.path.basename(dbName)
        copyfile(dbName, dirName + "/" + baseName[1:]) #only get chars after 1, to overwrite original

    def updateTable(self, searchQ):
        data = self.returnItems(searchQ)

        #first delete all rows from table
        self.loginTable.setRowCount(0)

        if data == []:
            self.loginTable.insertRow(self.loginTable.rowCount())
            self.loginTable.setItem(0, 0, QtGui.QTableWidgetItem("No data to display! - Either open a DB or widen your search"))

        #load in all items from db, only creating if necessary 
        for rowNumber, rowData in enumerate(data):
            self.loginTable.insertRow(self.loginTable.rowCount())
            for colNumber, cellData in enumerate(rowData):
                self.loginTable.setItem(rowNumber, colNumber, QtGui.QTableWidgetItem(str(cellData)))

        header = self.loginTable.horizontalHeader()
        header.setResizeMode(0, QtGui.QHeaderView.ResizeToContents)

    def dbConnect(self):
        dbConn = sqlite3.connect(dbName)
        dbCursor = dbConn.cursor()
        return dbConn, dbCursor

    def searchDB(self):
        searchQ = self.txtSearch.text()
        if searchQ == '': #if nothing in text box, return none for query
            searchQ = None
        else:
            searchQ = "%" + searchQ + "%" 
        self.updateTable(searchQ)

    def autoSearch(self, state):
        if state == QtCore.Qt.Checked:
            self.txtSearch.textChanged.connect(self.searchDB)
        else:
            self.txtSearch.textChanged.disconnect(self.searchDB)

    def newDB(self):
        global dbName
        dbName = QtGui.QFileDialog.getSaveFileName(self, 'New database')

        dirName = os.path.dirname(dbName)
        baseName = os.path.basename(dbName)
        
        dbName = dirName + "/." + baseName

        dbConn, dbCursor = self.dbConnect()
        dbCursor.execute("CREATE TABLE IF NOT EXISTS logins (login_id INTEGER PRIMARY KEY, site TEXT, username TEXT, email TEXT, password TEXT, notes TEXT, modified BOOLEAN)")
        dbConn.commit()
        dbConn.close()
    
    def contextMenuEvent(self, event):
        contextMenu = QtGui.QMenu("DB Entry")
        edit = contextMenu.addAction("Edit entry")

        edit.triggered.connect(self.editEntry)
        
        contextMenu.exec_(event.screenPos())

    def warningBox(self, message, detail):
        warning = QtGui.QMessageBox()
        warning.setIcon(QtGui.QMessageBox.Warning)
        warning.setWindowTitle("Warning")

        warning.setText("Warning - " + message)
        if detail != None:
            warning.setDetailedText("Cause of exception:\n" + str(detail))

        warning.exec_()

    # def undoRedo(self):
    #     dbConn, dbCursor = self.dbConnect()
    #     return table

    def returnItems(self, searchQ):
        dbConn, dbCursor = self.dbConnect()

        if searchQ == None:
            dbCursor.execute("SELECT login_id, site, username, email, password, notes FROM logins")
        else:
            dbCursor.execute("SELECT login_id, site, username, email, password, notes FROM logins WHERE site LIKE ?", (searchQ, ) )
        data = dbCursor.fetchall()
        dbConn.close()

        return data

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
    if dbName != "":
        os.remove(dbName) #remove temporary .file after exit of program