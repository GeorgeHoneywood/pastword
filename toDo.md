# Stuff I need to do in my computing coursework

Here is a small list of improvements or features that I need to add to my program. Bugs will also be listed here so I know what I have to fix:

* Censor passwords in the table, show on hold click or context menu (right click). Passwords are now censored, but have to be revealed to be seen in the edit tab. Need to find a way to read real value from db, instead of from table.
* Half done - still need to do redo - Implement undo/redo with a new column, and a stack which holds entries that have been changed. Still need to do undo for new entries. Also undo seems to now be broken :/
* Query the user for the password, using the form, during save, new or open, then don't pester when saving.
* Should probably encrypt whole file rather line by line.
* Add a lock databse button
* Setting menu for things like autolockout, change master password etc.
* Lock interface until file has been opened, will remove SQL errors. Need to find a good way to do this. Maybe just disable the edit part of the menu strip?