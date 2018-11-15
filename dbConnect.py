import sqlite3

def dbConnect():
    dbConnMem = sqlite3.connect("file::memory:?cache=shared")
    dbCursorMem = dbConnMem.cursor()
    return dbConnMem, dbCursorMem