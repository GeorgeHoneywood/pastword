# Stuff I need to do in my computing coursework

Here is a small list of improvements or features that I need to add to my program. Bugs will also be listed here so I know what I have to fix:

* DONE - Check to see what is in the database after edit is made, as it seem to alter the entry one too low.
* DONE - Add checking to ensure that the user has selected a box when they click edit entry, maybe with try/execpt.
* DONE - Add a search function, with a bar which can be entered into (QLineEdit), then click a button or press enter to commence the search. This should probably be handed by an optional parameter passed into the "updateTable" routine, like a "WHERE" SQL statement.
* ?DONE? - Check to see if file has been opened or not, otherwise, don't allow user to edit entries.
* Add icons to program, using '```pyrcc4 -py3 -o ../resources_rc.py resources.qrc```' -- kinda works, but not all icons show, especially on linux.
* Censor passwords in the table, show on hold click or context menu (right click)
* Implement undo/redo with a new column, and a stack which holds entries that have been changed.