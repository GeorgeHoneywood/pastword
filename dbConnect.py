import sqlite3

def dbConnect():
    dbConnMem = sqlite3.connect(":memory:")
    dbCursorMem = dbConnMem.cursor()
    return dbConnMem, dbCursorMem