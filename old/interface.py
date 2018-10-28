#!/usr/bin/python3

import sys
from PyQt5.QtWidgets import (QWidget, QMessageBox, QDesktopWidget, QApplication, QMainWindow, QAction, qApp, QHBoxLayout, QVBoxLayout, QPushButton)
from PyQt5.QtGui import QIcon


class PasswordManager(QMainWindow):
    
    def __init__(self):
        super().__init__()
        
        self.initUI()
        
    def initUI(self):

        exitAct = QAction(QIcon('exit.png'), 'Exit', self)        
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(qApp.quit)

        dabAct = QAction("dab",self)
        dabAct.triggered.connect(self.closeEvent)

        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAct)
        fileMenu.addAction(dabAct)

        okButton = QPushButton("OK")
        cancelButton = QPushButton("Cancel")

        wid = QtGui.QWidget(self)
        self.setCentralWidget(wid)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(okButton)
        hbox.addWidget(cancelButton)

        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox)
        
        self.setLayout(vbox)    

        #self.setGeometry(400, 400, 350, 350)
        self.setWindowTitle('PastWord Manager')
        #self.center()    
        self.show()
        
    def closeEvent(self, event):
        
        reply = QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QMessageBox.Yes | 
            QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def center(self):
        
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())    
        
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = PasswordManager()
    sys.exit(app.exec_())