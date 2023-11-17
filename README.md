# CRDT_CollaborativeEditor
A CRDT-based collaborative Jupyter notebook styled editor that facilitates seamless real-time document collaboration, ensuring conflict-free concurrent edits, offline editing capabilities, and efficient conflict resolution.

# Instructions to run:
1. Change directory to this folder(The folder this file is in)
2. Run pip install -r requirements.txt to install the required libraries
3. Open another terminal in the same directory.
4. In one terminal type: python main.py --name alice --listen 55101 --peers bob:55102
5. In the other, type: python main.py --name bob --listen 55102 --peers alice:55101
6. In case you want to try with 3 or more users: Use the following example template: python main.py --name clara --listen 55103 --peers alice:55101 bob:55102

# Features of the Editor
1. You can edit the name of the file (Sequence of cells)
2. You can edit the contents of a cell (Sequence of characters)
3. You can add and delete cells
4. The Connect and Disconnect buttons toggle the connection.
5. The Refresh button updates the document to the latest state.
6. You can edit offline (disconnecting) and then merge by connecting again.