import sqlite3

def dbConnect(dbName):
    dbConn = sqlite3.connect(dbName)
    dbCursor = dbConn.cursor()
    return dbConn, dbCursor