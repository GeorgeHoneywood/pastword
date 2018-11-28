
# -*- coding: utf-8 -*-

# A simple setup script to create an executable using PyQt4. This also
# demonstrates the method for creating a Windows executable that does not have
# an associated console.
#
# PyQt4app.py is a very simple type of PyQt4 application
#
# Run the build process by running the command 'python setup.py build'
#
# If everything works well you should find a subdirectory in the build
# subdirectory that contains the files needed to run the application

import sys
from cx_Freeze import setup, Executable

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

includefiles = ['resources/pastword.ui', 'resources/editEntry.ui', 'resources/passwordGenerator.ui', 'resources/newPass.ui', 'resources/passCheck.ui', 'resources/resources.qrc']
includepackages = ['sqlite3', 'PyQt4', 'base64', 'cryptography']

options = {
    'build_exe': {
        'includes': 'atexit',
        'include_files': includefiles,
        'packages': includepackages
    }
}

executables = [
    Executable('pastword.pyw', base=base)
]

setup(name='Pastword',
      version='1.0',
      description='Pastword password manager, written using PyQt.',
      options=options,
      executables=executables 
)


