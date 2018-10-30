import os, sys
def findDataFile(filename): #checks to see whether program is frozen or not, so we know where to load files from
    if getattr(sys, 'frozen', False):
        # The application is frozen
        datadir = os.path.dirname(sys.executable)
    else:
        # The application is not frozen
        # Change this bit to match where you store your data files:
        datadir = "resources"

    return os.path.join(datadir, filename)