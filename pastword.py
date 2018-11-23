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
from encryption import enc, dec, createCipher
from dbConnect import dbConnect
from passwordQuery import passCheck, newPass

Ui_MainWindow, QtBaseClass = uic.loadUiType(findDataFile("pastword.ui"))

dbName = "" #make file name global variable
dbOpen = False
password = ""

dbConnMem, dbCursorMem = dbConnect()

class mainWindow(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.setWindowState(QtCore.Qt.WindowMaximized) #maximize the window

        self.connectGUI()

    def connectGUI(self):
        self.actionOpen.triggered.connect(self.openFile)
        self.actionSave.triggered.connect(lambda: self.saveFile("default"))
        self.actionSave_as.triggered.connect(lambda: self.saveFile("saveAs"))
        self.actionNewDB.triggered.connect(self.newDB)
        self.actionRefresh_table.triggered.connect(lambda: self.updateTable(searchQ = None))

        self.actionAdd_entry.triggered.connect(self.addEntry)
        self.actionRemove_entry.triggered.connect(self.removeEntry)
        self.actionEdit_entry.triggered.connect(self.editEntry)
        self.loginTable.doubleClicked.connect(self.editEntry)
        self.editPopup = editEntryDialog(self)

        self.actionUndo.triggered.connect(self.undo)
        #self.actionRedo.triggered.connect(self.redo) #need to impliment redo

        self.actionAbout.triggered.connect(self.about)

        self.actionPassword_Generator.triggered.connect(self.passwordGenerator)
        self.pwGenPopup = passwordGenerator()

        self.actionClear_deleted_entries.triggered.connect(self.removeOldEntries)

        self.actionHide_passwords.changed.connect(lambda: self.updateTable(searchQ = None))

        self.pbSearch.clicked.connect(self.searchDB)
        self.txtSearch.returnPressed.connect(self.searchDB)
        self.txtSearch.textChanged.connect(self.searchDB)
        self.cbAutoSearch.stateChanged.connect(self.autoSearch)

        self.newPassPopup = newPass(self)
        self.checkPassPopup = passCheck(self)

        self.loginTable.customContextMenuRequested.connect(self.contextMenuEvent) #tried to impliment context menu, doesn't work

    def newDB(self): # if there is already data in the table, this will not erase it
        global dbName, dbOpen
        dbOpen = True

        dbName = QtGui.QFileDialog.getSaveFileName(self, "New database")

        if not dbName:
            warningBox("Please select a file", None)
            return None

        dbCursorMem.execute("CREATE TABLE IF NOT EXISTS logins (login_id INTEGER PRIMARY KEY, site TEXT, username TEXT, email TEXT, password TEXT, notes TEXT, hidden BOOLEAN)")
        dbConnMem.commit()
        dbCursorMem.execute("CREATE TABLE IF NOT EXISTS undo (undo_id INTEGER PRIMARY KEY, login_id INTEGER)")
        dbConnMem.commit()

        self.newPass()

    def openFile(self):
        global dbName, dbOpen
        dbOpen = True

        dbName = QtGui.QFileDialog.getOpenFileName(self, "Open database")

        if not dbName:
            warningBox("Please select a file", None)
            return None

        self.checkPass()

        dbFile = open(dbName, "r")
        dbLine = dbFile.readline()

        cipher = createCipher(password)
        decDB = ""

        decDB = dec(cipher, dbLine[2:-1].encode()) # remove \n chars from end of string & and old chars from being byte encoded

        dbCursorMem.executescript(decDB) #run the sql dump to rebuild tables and contents of them
        self.updateTable(searchQ = None)

    def newPass(self):
        self.newPassPopup.exec_()
    
    def checkPass(self):
        self.checkPassPopup.exec_()

    def setPass(self, dialog, kind):
        global password
        if kind == "check":
            password = dialog.txtPass.text()
        else:
            password = dialog.txtNewPass2.text()
        
        dialog.close()
    
    def saveFile(self, saveType): #savetype ignored for now
        global dbName

        if not dbName:
            dbName = "defaultSave.name"

        cipher = createCipher(password)
        
        decDB = ""
        for decLine in dbConnMem.iterdump():
                decDB += decLine + "\n"
                
        with open(dbName, "w") as dbFile:
            dbFile.write(str(enc(cipher, decDB)))

    def returnItems(self, searchQ):
        if searchQ is None:
            dbCursorMem.execute("SELECT login_id, site, username, email, password, notes FROM logins WHERE hidden = 0")
        else:
            dbCursorMem.execute("SELECT login_id, site, username, email, password, notes FROM logins WHERE site LIKE ? AND hidden = 0", (searchQ, ))
        return dbCursorMem.fetchall()

    def updateTable(self, searchQ):
        dbData = self.returnItems(searchQ)

        #first delete all rows from table
        self.loginTable.setRowCount(0)

        if not dbData: # if there are no items returned, db is empty
            self.loginTable.insertRow(self.loginTable.rowCount())
            self.loginTable.setItem(0, 0, QtGui.QTableWidgetItem("No data to display! - Either open a DB or widen your search"))

        #load in all items from db, only creating if necessary 
        for rowNumber, rowData in enumerate(dbData):
            self.loginTable.insertRow(self.loginTable.rowCount())
            for colNumber, cellData in enumerate(rowData):
                if self.actionHide_passwords.isChecked() and colNumber == 4: # hide passwords if the box is checked
                    self.loginTable.setItem(rowNumber, colNumber, QtGui.QTableWidgetItem(str("*" * len(cellData))))
                else:
                    self.loginTable.setItem(rowNumber, colNumber, QtGui.QTableWidgetItem(str(cellData)))
                    
        header = self.loginTable.horizontalHeader()
        header.setResizeMode(0, QtGui.QHeaderView.ResizeToContents)

    def addEntry(self): #effectively the same as edit entry, but dont need to load values into popup
        self.clearEditPopup() #remove entries from the popup before displaying
        self.editPopup.exec_()

    def removeEntry(self):
        indexList = [index.row() for index in self.loginTable.selectionModel().selectedRows()] #create list containing selected rows in table

        if not indexList:
            warningBox("Please select an item before trying to delete it", None)
            return None

        for row in indexList: #hide the entry, don't actually delete - this allows for undo
            dbRow = int(self.loginTable.item(row, 0).text()) #get the index of the item in the DB from the ID column
            dbCursorMem.execute("UPDATE logins SET hidden = 1 WHERE login_id = ?", (dbRow, )) #hide said item
            dbConnMem.commit()
            self.addToUndoTable(dbRow)

        self.updateTable(searchQ = None)

    def editEntry(self):
        indexes = self.loginTable.selectionModel().selectedRows()
        if not indexes:
            warningBox("Please select an item before trying to edit it", None)
            return None

        index = indexes[0].row()
        
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
        # fieldNames = ["txtSite", "txtUsername", "txtEmail", "txtPassword", "txtNotes"] #would be nice if i could do it like so

        # for fieldName in fieldNames:
        #     self.editPopup.{}.setText("").format{fieldName}

        self.editPopup.txtSite.setText("")
        self.editPopup.txtUsername.setText("")
        self.editPopup.txtEmail.setText("")
        self.editPopup.txtPassword.setText("")
        self.editPopup.txtNotes.setText("")
    
    def acceptEntry(self):
        loginData = (None, self.editPopup.txtSite.text(), self.editPopup.txtUsername.text(), self.editPopup.txtEmail.text(), self.editPopup.txtPassword.text(), self.editPopup.txtNotes.text(), 0)

        if not dbOpen:
            warningBox("Please open or create a DB before trying to edit it.", None)
            return None
        
        indexList = self.loginTable.selectionModel().selectedRows()
        if not indexList: #if there are not not rows selcted, add an entry
             #None so that it auto allocates an ID, 0 so that it is not marked as hidden
            dbCursorMem.execute("INSERT INTO logins VALUES (?, ?, ?, ?, ?, ?, ?)", loginData)
            
        else: #if the user has selected a row
            indexTable = indexList[0].row()
            indexDB = int(self.loginTable.item(indexTable, 0).text())
            dbCursorMem.execute("UPDATE logins SET hidden = 1 WHERE login_id = ?", (indexDB, )) #hide the old entry
            dbConnMem.commit()
            self.addToUndoTable(indexDB) #add this entry to the undo list

            dbCursorMem.execute("INSERT INTO logins VALUES (?, ?, ?, ?, ?, ?, ?)", loginData) #add a new entry
            dbConnMem.commit()
            self.addToUndoTable(dbCursorMem.lastrowid)
        
        dbConnMem.commit()

        self.updateTable(searchQ = None)
        self.editPopup.close()

    def passwordGenerator(self):
        self.pwGenPopup.exec_()

    def searchDB(self):
        searchQ = self.txtSearch.text()
        if not searchQ: #if nothing in text box, return none for query
            searchQ = None
        else:
            searchQ = "{}{}{}".format("%", searchQ, "%")
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
        lastItem = self.lastItemToUndo()

        if not lastItem: # if lastitem is none
            warningBox("No more actions to undo", None)
            return None

        dbCursorMem.execute("DELETE FROM undo WHERE undo_id = ?", lastItem)
        dbConnMem.commit()

        dbCursorMem.execute("SELECT hidden FROM logins WHERE login_id = ?", (lastItem))
        dbData = dbCursorMem.fetchone()
        if dbData[0] == 0: #if the item is already hidden, we know it has been edited, rather than deleted
            dbCursorMem.execute("UPDATE logins SET hidden = 1 WHERE login_id = ?", (lastItem)) #hide the edited item

            lastItem = self.lastItemToUndo()
            dbCursorMem.execute("UPDATE logins SET hidden = 0 WHERE login_id = ?", (lastItem))

        else:
            dbCursorMem.execute("UPDATE logins SET hidden = 0 WHERE login_id = ?", (lastItem))

        dbConnMem.commit()
        self.updateTable(searchQ = None)

    def lastItemToUndo(self):
        dbCursorMem.execute("SELECT login_id FROM undo WHERE undo_id = (SELECT MAX(login_id) FROM undo)")
        lastItem = dbCursorMem.fetchone()

        return lastItem

    def addToUndoTable(self, item):
        item = (None, item)
        dbCursorMem.execute("INSERT INTO undo VALUES (?, ?)", item)
        dbConnMem.commit()

    def removeOldEntries(self):
        dbCursorMem.execute("DELETE FROM logins WHERE hidden = 1") #delete all of the old entries from the table
        dbCursorMem.execute("DELETE FROM undo")
        
        dbConnMem.commit()

    def about(self):
        aboutBox = QtGui.QMessageBox()
        aboutBox.setIcon(QtGui.QMessageBox.Information)
        aboutBox.setWindowTitle("About Pastword")

        aboutBox.setText("Pastword is a basic password manager, which I have written for my A-Level Computer Science coursework. This program has written in Python3, using PyQt4 for the interface, and SQLite for storage of the database.")
        aboutBox.setInformativeText("This program was written in 2018 by George Honeywood.")

        aboutBox.exec_()

class editEntryDialog(QtGui.QDialog):
    def __init__(self, mainWindow):
        QtGui.QDialog.__init__(self)
        uic.loadUi(findDataFile("editEntry.ui"), self)

        self.pbCancel.clicked.connect(self.close)
        self.pbAccept.clicked.connect(mainWindow.acceptEntry)

def main():
    app = QtGui.QApplication(["Pastword"]) # sets the name of the application
    window = mainWindow()
    window.show()
    try:
        sys.exit(app.exec_())
    except SystemExit:
        print("Exiting program")

if __name__ == "__main__":
    main()