import os #for generating random bytes
import sqlite3 #for iteracting with database
import sys #to exit program

from PyQt4 import QtCore, QtGui, uic #pyqt4 stuff, uicis used to convert .ui files to python code
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import resources_rc  # import icons from qt resources file
from findDataFile import findDataFile # detect whether app is frozen or not, chnage where to load files from

#import functions from my own files
from passwordGenerator import passwordGenerator
from warningBox import warningBox
from encryption import enc, dec, createCipher
from dbConnect import dbConnect
from passwordQuery import passCheck, newPass

import platform # some code to set the window icon properly on windows. if not used, program has python icon - not needed on linux
if platform.system() == "Windows":
    import ctypes
    appID = u'pastword'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appID)

Ui_MainWindow, QtBaseClass = uic.loadUiType(findDataFile("pastword.ui")) # set the main windows ui to the pastword form

dbName = "" # make file name global variable
dbOpen = False # used to find whether a db is open or not
password = "" # used to temp store the users password, so can be kdf'd
salt = "" # store salt used for encryption and decryption

dbConnMem, dbCursorMem = dbConnect() # create a connection to a database in memory

class mainWindow(QtGui.QMainWindow, Ui_MainWindow): # class for the main window of the GUI
    def __init__(self): # code to be run when initialised
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.setWindowState(QtCore.Qt.WindowMaximized) # maximize the window

        self.loginTable.setContextMenuPolicy(Qt.CustomContextMenu)
        self.loginTable.customContextMenuRequested.connect(self.contextMenu)

        self.connectGUI() # sub to connect UI elements to functions

    def connectGUI(self):
        self.actionOpen.triggered.connect(self.openFile)
        self.actionClose.triggered.connect(self.closeFile)
        self.actionSave.triggered.connect(lambda: self.saveFile("default"))
        self.actionSave_as.triggered.connect(lambda: self.saveFile("saveAs"))
        self.actionNewDB.triggered.connect(self.newDB)
        self.actionRefresh_table.triggered.connect(lambda: self.updateTable(searchQ = None))

        self.actionAdd_entry.triggered.connect(self.addEntry)
        self.actionRemove_entry.triggered.connect(self.removeEntry)
        self.actionEdit_entry.triggered.connect(self.editEntry)
        self.loginTable.doubleClicked.connect(self.editEntry)

        self.actionUndo.triggered.connect(self.undo)
        #self.actionRedo.triggered.connect(self.redo) #need to impliment redo

        self.actionAbout.triggered.connect(self.about)

        self.actionPassword_Generator.triggered.connect(self.passwordGenerator)

        self.actionClear_deleted_entries.triggered.connect(self.removeOldEntries)

        self.actionHide_passwords.changed.connect(lambda: self.updateTable(searchQ = None))

        self.pbSearch.clicked.connect(self.searchDB)
        self.txtSearch.returnPressed.connect(self.searchDB)
        self.txtSearch.textChanged.connect(self.searchDB)
        self.cbAutoSearch.stateChanged.connect(self.autoSearch)

        self.loginTable.customContextMenuRequested.connect(self.contextMenuEvent) #tried to impliment context menu, doesn't work

    def newDB(self):
        global dbName, dbOpen, salt # allows me to interact with some global variables
        self.closeFile() # ensure that the previous tables and flags are cleared

        dbOpen = True # mark as having an open database
        dbName = QtGui.QFileDialog.getSaveFileName(self, "New database", filter="Pastword Database (*.pwdb)") # filter means that it only displays files with ".pwdb" extension

        if not dbName: # ensure that the user has actually picked something
            warningBox("Please select a file", None)
            return None

        if dbName[-5:] != ".pwdb": # for some reason windows adds .pwdb to filename automatically, so we check to see if the last chars are already correct or not
            dbName += ".pwdb" # append the .pwdb ext

        self.setTitle() # set the window title to that of the opened file

        dbCursorMem.execute("CREATE TABLE IF NOT EXISTS logins (login_id INTEGER PRIMARY KEY, site TEXT, username TEXT, email TEXT, password TEXT, notes TEXT, hidden BOOLEAN)") # create the tables in the memory database
        dbCursorMem.execute("CREATE TABLE IF NOT EXISTS undo (undo_id INTEGER PRIMARY KEY, login_id INTEGER)")
        dbConnMem.commit() # commit actually makes the changes to the database

        salt = os.urandom(16) # generate a 16 byte long salt

        self.newPass() # query the user for a new password

    def openFile(self):
        global dbName, dbOpen, salt # also need to interact with these globals
        self.closeFile() # ensure that previous file was closed

        dbOpen = True # set dbOpen flag
        dbName = QtGui.QFileDialog.getOpenFileName(self, "Open database", filter="Pastword Database (*.pwdb)")

        if not dbName:
            warningBox("Please select a file", None)
            return None           

        self.setTitle()
        self.checkPass() # ask user for the password that they used to encrypt last time

        dbFile = open(dbName, "rb") # read in file as bytes
        salt = dbFile.read(16) # first 16 bytes of file are the salt
        encDB = dbFile.read() # rest of file is the encrypted db

        cipher = createCipher(password, salt) # create the cipher to use for decryption
        decDB = ""

        decDB = dec(cipher, encDB) # decrpyt the bytes from the file

        dbCursorMem.executescript(decDB) #run the sql dump to rebuild tables and contents of them
        self.updateTable(searchQ = None) # ensure that table reflects the contents of the DB

    def closeFile(self): # reset all flags used for handing a database
        global dbName, password, dbOpen
        dbName = ""
        password = ""
        dbOpen = False

        self.setTitle() # remove file name from title

        dbCursorMem.execute("DROP TABLE IF EXISTS logins") #if tables exist, remove them
        dbCursorMem.execute("DROP TABLE IF EXISTS undo")
        dbConnMem.commit()

        self.loginTable.setRowCount(0) #remove all rows in the table, as it is now empty

    def newPass(self): #create an object of the new pass class and show it modally
        self.newPassPopup = newPass(self)

        self.newPassPopup.exec_()
    
    def checkPass(self):
        self.checkPassPopup = passCheck(self)

        self.checkPassPopup.exec_()

    def setTitle(self): # set the window title to the name of the open file
        if dbName:
            self.setWindowTitle("Pastword - \"{}\"".format(dbName)) # backslashes are needed to escape quotes
        else:
            self.setWindowTitle("Pastword")

    def setPass(self, dialog, kind): # read the password from the form, and set the global var for it
        global password
        if kind == "check": # find what type of pass the use has entered
            password = dialog.txtPass.text()
        else:
            password = dialog.txtNewPass2.text()
        
        dialog.close()
    
    def saveFile(self, saveType): #savetype ignored for now
        global dbName

        if saveType == "saveAs": # if the user wants to save as, allow them to change the db name
            dbName = QtGui.QFileDialog.getSaveFileName(self, "New database", filter="Pastword Database (*.pwdb)")
            if not dbName: # ensure that the user has actually picked something
                warningBox("Please select a file", None)
                return None
            if dbName[-5:] != ".pwdb":
                dbName += ".pwdb"

            self.setTitle()

        cipher = createCipher(password, salt)
        
        decDB = ""
        for decLine in dbConnMem.iterdump(): # iterate over the sql dump of the database. this provides the sql code to create it
                decDB += decLine + "\n" # provided line by line, so add newline to format correctly
                
        with open(dbName, "wb") as dbFile:
            dbFile.write(salt) # write the salt to the first 16 bytes

            dbFile.write(enc(cipher, decDB)) # write the rest of the encrypted data

    def returnItems(self, searchQ):
        if searchQ is None: # if not a search, return all values
            dbCursorMem.execute("SELECT login_id, site, username, email, password, notes FROM logins WHERE hidden = 0")
        else:
            dbCursorMem.execute("SELECT login_id, site, username, email, password, notes FROM logins WHERE site LIKE ? OR username LIKE ? OR email LIKE ? OR notes LIKE ? AND hidden = 0", (searchQ, searchQ, searchQ, searchQ))
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
        self.editPopup = editEntryDialog(self) #have to create a new one each time, means that text is not saved between popup openings

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
        self.editPopup = editEntryDialog(self)

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
    
    def acceptEntry(self):
        loginData = (None, self.editPopup.txtSite.text(), self.editPopup.txtUsername.text(), self.editPopup.txtEmail.text(), self.editPopup.txtPassword.text(), self.editPopup.txtNotes.text(), 0)

        if not dbOpen:
            warningBox("Please open or create a DB before trying to edit it.", None)
            self.editPopup.close()
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
        self.pwGenPopup = passwordGenerator()

        self.pwGenPopup.exec_()

    def searchDB(self):
        if not dbOpen:
            warningBox("Please open or create a DB before trying to search it.", None)
            return None

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

    def contextMenu(self, position):
        menu = QtGui.QMenu()
        openURL = menu.addAction("Open URL")        
        copyPW = menu.addAction("Copy password")
        copyUN = menu.addAction("Copy username")
        edit = menu.addAction("Edit entry")
        delete = menu.addAction("Delete entry")

        action = menu.exec_(self.mapToGlobal(position))
        if action == quitAction:
            self.about()
        elif action == openURL:
            self.openURL()

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

        self.pbEditPWGen.clicked.connect(mainWindow.passwordGenerator)

def main():
    app = QtGui.QApplication(["Pastword"]) # sets the name of the application
    if platform.system() == "Windows": #if on windows set style to Cleanlooks
        app.setStyle("Cleanlooks")
    window = mainWindow()
    window.show()
    try:
        sys.exit(app.exec_())
    except SystemExit:
        print("Exiting program")

if __name__ == "__main__":
    main()