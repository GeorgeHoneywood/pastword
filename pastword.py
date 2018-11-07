import os
import sqlite3
import sys
from shutil import copyfile

from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import resources_rc  # import icons
from findDataFile import findDataFile
from passwordGenerator import passwordGenerator
from warningBox import warningBox
from dbConnect import dbConnect

Ui_MainWindow, QtBaseClass = uic.loadUiType(findDataFile("pastword.ui"))

dbName = "" #make file name global variable
modifiedItems = []

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

        self.setWindowState(QtCore.Qt.WindowMaximized) #maximize the window

        self.actionOpen.triggered.connect(self.openFile)
        self.actionSave.triggered.connect(lambda: self.saveFile("default"))
        self.actionSave_as.triggered.connect(lambda: self.saveFile("saveAs"))
        self.actionNewDB.triggered.connect(self.newDB)

        self.actionAdd_entry.triggered.connect(self.addEntry)
        self.actionRemove_entry.triggered.connect(self.removeEntry)
        self.actionEdit_entry.triggered.connect(self.editEntry)
        self.loginTable.doubleClicked.connect(self.editEntry)
        self.editPopup = editEntryDialog(self)

        self.actionUndo.triggered.connect(self.undo)
        #self.actionRedo.triggered.connect(self.redo) #need to impliment redo

        self.actionAbout.triggered.connect(self.about)

        self.actionPassword_Generator.triggered.connect(self.passwordGenerator)
        self.pwGenPopup = passwordGenerator(self)

        self.pbSearch.clicked.connect(self.searchDB)
        self.txtSearch.returnPressed.connect(self.searchDB)
        self.txtSearch.textChanged.connect(self.searchDB)
        self.cbAutoSearch.stateChanged.connect(self.autoSearch)

        self.loginTable.customContextMenuRequested.connect(self.contextMenuEvent) #tried to impliment context menu, doesn't work

    def newDB(self):
        global dbName
        dbName = QtGui.QFileDialog.getSaveFileName(self, 'New database')

        dirName = os.path.dirname(dbName)
        baseName = os.path.basename(dbName)
        
        dbName = dirName + "/." + baseName

        dbConn, dbCursor = dbConnect(dbName)
        dbCursor.execute("CREATE TABLE IF NOT EXISTS logins (login_id INTEGER PRIMARY KEY, site TEXT, username TEXT, email TEXT, password TEXT, notes TEXT, hidden BOOLEAN)")
        dbConn.commit()
        dbConn.close()
        
    def openFile(self):
        global dbName
        dbName = QtGui.QFileDialog.getOpenFileName(self, 'Open database')

        if dbName == '':
            warningBox("Please select a file", None)
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

    def returnItems(self, searchQ):
        dbConn, dbCursor = dbConnect(dbName)

        if searchQ == None:
            dbCursor.execute("SELECT login_id, site, username, email, password, notes FROM logins WHERE hidden = 0")
        else:
            dbCursor.execute("SELECT login_id, site, username, email, password, notes FROM logins WHERE site LIKE ? AND hidden = 0", (searchQ, ) )
        dbData = dbCursor.fetchall()
        dbConn.close()

        return dbData

    def updateTable(self, searchQ):
        dbData = self.returnItems(searchQ)

        #first delete all rows from table
        self.loginTable.setRowCount(0)

        if dbData == []:
            self.loginTable.insertRow(self.loginTable.rowCount())
            self.loginTable.setItem(0, 0, QtGui.QTableWidgetItem("No data to display! - Either open a DB or widen your search"))

        #load in all items from db, only creating if necessary 
        for rowNumber, rowData in enumerate(dbData):
            self.loginTable.insertRow(self.loginTable.rowCount())
            for colNumber, cellData in enumerate(rowData):
                self.loginTable.setItem(rowNumber, colNumber, QtGui.QTableWidgetItem(str(cellData)))

        header = self.loginTable.horizontalHeader()
        header.setResizeMode(0, QtGui.QHeaderView.ResizeToContents)

    def addEntry(self): #effectively the same as edit entry, but dont need to load values into popup
        self.clearEditPopup() #remove entries from the popup before displaying
        self.editPopup.exec_()

    def removeEntry(self):
        global modifiedItems
        dbConn, dbCursor = dbConnect(dbName)

        i = 0
        indexList = self.loginTable.selectionModel().selectedRows()
        for row in sorted(indexList): #hide the entry, don't actually delete - this allows for undo
            index = indexList[i].row()
            index = int(self.loginTable.item(index, 0).text())
            dbCursor.execute("UPDATE logins SET hidden = 1 WHERE login_id = ?", (index, ))
            modifiedItems.append(index)
            i += 1

        dbConn.commit()
        dbConn.close()
        self.updateTable(searchQ = None)

    def editEntry(self):
        indexes = self.loginTable.selectionModel().selectedRows()
        try:
            index = indexes[0].row()
        except IndexError as detail:
            warningBox("Please select an item before trying to edit it", detail)
            return None
        try:
            self.editPopup.txtSite.setText(self.loginTable.item(index, 1).text())
            self.editPopup.txtUsername.setText(self.loginTable.item(index, 2).text())
            self.editPopup.txtEmail.setText(self.loginTable.item(index, 3).text())
            self.editPopup.txtPassword.setText(self.loginTable.item(index, 4).text())
            self.editPopup.txtNotes.setText(self.loginTable.item(index, 5).text())
        except AttributeError as detail:
            warningBox("Ensure all fields are filled out", detail)
            self.clearEditPopup()

        self.editPopup.exec_()

    def clearEditPopup(self):
            self.editPopup.txtSite.setText("")
            self.editPopup.txtUsername.setText("")
            self.editPopup.txtEmail.setText("")
            self.editPopup.txtPassword.setText("")
            self.editPopup.txtNotes.setText("")
    
    def acceptEdit(self):
        dbConn, dbCursor = dbConnect(dbName)

        loginData = (None, self.editPopup.txtSite.text(), self.editPopup.txtUsername.text(), self.editPopup.txtEmail.text(), self.editPopup.txtPassword.text(), self.editPopup.txtNotes.text(), 0)
        
        indexList = self.loginTable.selectionModel().selectedRows()
        if indexList == []: #if there are not not rows selcted, add an entry
             #None so that it auto allocates an ID, 0 so that it is not marked as hidden
            dbCursor.execute("INSERT INTO logins VALUES (?, ?, ?, ?, ?, ?, ?)", loginData)
            
        else: #if the user has selected a row
            indexTable = indexList[0].row()
            indexDB = int(self.loginTable.item(indexTable, 0).text())
            dbCursor.execute("UPDATE logins SET hidden = 1 WHERE login_id = ?", (indexDB, )) #hide the old entry
            modifiedItems.append(indexDB) #add this entry to the undo list
            dbCursor.execute("INSERT INTO logins VALUES (?, ?, ?, ?, ?, ?, ?)", loginData)
            #dbCursor.execute("UPDATE logins SET site = ?, username = ?, email = ?, password = ?, notes = ? WHERE login_id = ?", loginData)
        
        dbConn.commit()
        dbConn.close()

        self.updateTable(searchQ = None)
        self.editPopup.close()

    def passwordGenerator(self):
        self.pwGenPopup.exec_()

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
    
    def contextMenuEvent(self, event):
        contextMenu = QtGui.QMenu("DB Entry")
        edit = contextMenu.addAction("Edit entry")

        edit.triggered.connect(self.editEntry)
        
        contextMenu.exec_(event.screenPos())

    def undo(self):
        dbConn, dbCursor = dbConnect(dbName)

        if len(modifiedItems) == 0:
            warningBox("No more actions to undo", None)
            return None

        index = modifiedItems[len(modifiedItems) - 1] #return last item in list
        dbCursor.execute("UPDATE logins SET hidden = 0 WHERE login_id = ?", (index, ))
        modifiedItems.pop()

        dbConn.commit()
        dbConn.close()
        self.updateTable(searchQ = None)

    def about(self):
        aboutBox = QtGui.QMessageBox()
        aboutBox.setIcon(QtGui.QMessageBox.Information)
        aboutBox.setWindowTitle("About Pastword")

        aboutBox.setText("Pastword is a basic password manager, which I have written for my A-Level Computer Science coursework. This program has written in Python3, using PyQt4 for the interface, and SQLite for storage of the database.")
        aboutBox.setInformativeText("This program was written in 2018 by George Honeywood.")

        aboutBox.exec_()

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