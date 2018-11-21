# Stuff I need to do in my computing coursework

Here is a small list of improvements or features that I need to add to my program. Bugs will also be listed here so I know what I have to fix:

* DONE - Check to see what is in the database after edit is made, as it seem to alter the entry one too low.
* DONE - Add checking to ensure that the user has selected a box when they click edit entry, maybe with try/execpt.
* DONE - Add a search function, with a bar which can be entered into (QLineEdit), then click a button or press enter to commence the search. This should probably be handed by an optional parameter passed into the "updateTable" routine, like a "WHERE" SQL statement.
* ?DONE? - Check to see if file has been opened or not, otherwise, don't allow user to edit entries.
* DONE - Add icons to program, using '```pyrcc4 -py3 -o ../resources_rc.py resources.qrc```' -- kinda works, but not all icons show, especially on linux.
* Half done - Censor passwords in the table, show on hold click or context menu (right click). Passwords are now censored, but have to be revealed to be seen in the edit tab. Need to find a way to read real value from db, instead of from table.
* Half done - still need to do redo - Implement undo/redo with a new column, and a stack which holds entries that have been changed. Still need to do undo for new entries.
* DONE - Actually encrypt the file on disk. Kinda done, doesn't really work and has broken the program (mostly search)
* DONE - Build up list for row, then create list of rows
* Still thinking about it, should database be stored in memory, changes made to disk file, then loaded back into memory, or should just load whole thing into memory, make changes to it, then save to disk encrypted. Would make program faster as would only have to encrypt and decypt when loading or saving.
* Query the user for the password, using the form.
* Maybe execpt is causing errors in decryption? Need to test this.