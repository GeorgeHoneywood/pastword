# Stuff I need to do in my computing coursework

Here is a small list of improvements or features that I need to add to my program. Bugs will also be listed here so I know what I have to fix:

* Censor passwords in the table, show on hold click or context menu (right click). Passwords are now censored, but have to be revealed to be seen in the edit tab. Need to find a way to read real value from db, instead of from table.
* Half done - still need to do redo - Implement undo/redo with a new column, and a stack which holds entries that have been changed. Still need to do undo for new entries. Also undo seems to now be broken :/
* Add a lock database button
* Setting menu for things like autolockout, change master password etc.
* Lock interface until file has been opened, will remove SQL errors. Need to find a good way to do this. Maybe just disable the edit part of the menu strip?
* Reveal password when held down in table.
* Link to password generator from the edit password menu, or simplified version of.
* Half done - still need to do redo - Implement undo/redo with a new column, and a stack which holds entries that have been changed. Still need to do undo for new entries. Also undo seems to now be broken :/
* If you cannot answer password correct, you get stuck in a loop.
* For some reason you see extra entries when searching. Think it is an issue with my sql query.
* Could impliment groups of passwords, using different tables for different groups, or just using a "group" field. The table would only display the selected group.
* Should probably change undo, so that entries store a reference to their parent. That would mean we know which one to show again.