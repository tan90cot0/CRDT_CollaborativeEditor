import tkinter as tk

TOP_ROW_HEIGHT = 2
SMALL_BUTTON_HEIGHT = 1
SMALL_BUTTON_WIDTH = 1
NORMAL_BUTTON_WIDTH = 2

class FileSystemEditor():
    def __init__(self, client) -> None:
        self.root = tk.Tk()
        self.root.title(client.name)
        self.client = client
        self.curr_file = None
        self.files = []
        self.heading = None
        # self.notebooks = {}
        self.notebook = []
        self.file_index = 0
        if self.client is not None:
            Files = tk.Label(self.root, text="Files", width=10, height=TOP_ROW_HEIGHT)
            Add = tk.Button(self.root, text="+", command= lambda: self.add_name(), width=SMALL_BUTTON_WIDTH, height=SMALL_BUTTON_HEIGHT)
            Refresh = tk.Button(self.root, text="Refresh", command= lambda: self.refresh(), width=10, height=TOP_ROW_HEIGHT)
            Connect = tk.Button(self.root, text="Connect", command= lambda: self.connect(), width=10, height=TOP_ROW_HEIGHT)
            self.connect_widget = Connect
            self.disconnect_widget = None
            Files.grid(row = 0, column = 0)
            Add.grid(row = 0, column = 1)
            Refresh.grid(row = 0, column = 7)
            Connect.grid(row = 0, column = 6)
            self.client.attach_editor(self)
        
    def disconnect(self):
        # self.client.disconnect()
        print('Disconnected Clicked ... ')
        self.disconnect_widget.destroy()
        self.disconnect_widget = None
        self.client.toggle_connection()
        Connect = tk.Button(self.root, text="Connect", command= lambda: self.connect(), width=10, height=TOP_ROW_HEIGHT)
        self.connect_widget = Connect
        Connect.grid(row=0, column=6)
    
    def connect(self):
        # self.client.connect()
        print('Connected Clicked')
        self.client.toggle_connection()
        self.connect_widget.destroy()
        self.connect_widget = None
        Disconnect = tk.Button(self.root, text="Disconnect", command= lambda: self.disconnect(), width=10, height=TOP_ROW_HEIGHT)
        Disconnect.grid(row=0, column=6)
        self.disconnect_widget = Disconnect

    def refresh(self):
        for peer in self.client.get_peers():
            self.client.sync(peer)
        self.render()
    
    def add_name(self):
        file_name = tk.Entry(self.root, width=10)
        submit = tk.Button(self.root, text="submit", command=lambda: self.add_file(submit, file_name), width=10, height=TOP_ROW_HEIGHT)
        file_name.grid(row=self.file_index+1, column = 0)
        submit.grid(row=self.file_index+1, column = 1)

    def add_file(self, submit, file_name):
        name = file_name.get()
        self.curr_file = name
        if self.client is not None:
            self.client.create_file(name)

        self.file_index += 1
        # self.notebooks[name]=[]
        for cell in self.notebook:
                cell.destroy()
        self.notebook = []
        
        submit.destroy()
        delete = tk.Button(self.root, text="X", command= lambda f=name: self.delete_file(f), width=SMALL_BUTTON_WIDTH, height=SMALL_BUTTON_HEIGHT)
        delete.grid(row=self.file_index, column = 1)
        file_name.destroy()
        new_file = tk.Button(self.root, text=name, command= lambda f=name: self.open_file(f), width=10, height=SMALL_BUTTON_HEIGHT)
        new_file.grid(row=self.file_index, column = 0)
        self.files.append((new_file, delete))
 
        self.add_cell()

    def delete_file(self, filename):
        self.client.remove_file(filename)
        if self.curr_file==filename:
            self.curr_file=None
        self.render()


    def open_file(self, filename):
        self.curr_file = filename
        self.render()

    def add_cell(self, after=None):
        cell = self.create_cell_frame()
        # Figure out if where to insert or append the cell based on which cell the add
        # button was clicked
        if after in self.notebook:
            index = self.notebook.index(after) + 1
        else:
            index = len(self.notebook)

        if index >= len(self.notebook):
            self.notebook.append(cell)
            if self.client is not None:
                self.client.create_cell(self.curr_file)
        else:
            self.notebook.insert(index, cell)
            if self.client is not None:
                self.client.create_cell(self.curr_file, index)
        self.render()

    def create_cell_frame(self, after=None, initial_text='', depth=0):
        # Create the subframe to hold the cell widgets
        cell = tk.Frame(self.root)

        # Button to remove the cell
        remove = tk.Button(cell, text="X", command=lambda: self.remove_cell(cell), width=SMALL_BUTTON_WIDTH, height=SMALL_BUTTON_HEIGHT)
        remove.grid(row=5*depth+1, column=7)
        
        # Text editor widget
        text = tk.Text(cell, wrap="char", highlightbackground="gray")
        text.grid(row=5*depth+1, column=2, columnspan = 5, rowspan = 5)
        text.insert("end", initial_text)
        text.bind("<KeyRelease>", self.edit_cell_callback)
        # text.pack(side="bottom")
        
        # Button to insert a new cell
        add = tk.Button(cell, text="+", command=lambda: self.add_cell(cell), width=SMALL_BUTTON_WIDTH, height=SMALL_BUTTON_HEIGHT)
        add.grid(row=6*depth+6, column=7)
        return cell

    def edit_cell_callback(self, event):
        cell = event.widget.master
        if self.client is not None:
            # If a notebook client is attached, send the new text to the correct notebook cell
            self.client.update_cell(self.curr_file, self.notebook.index(cell), event.widget.get("1.0", "end-1c"))

    def remove_cell(self, cell):
        if self.client is not None:
            self.client.remove_cell(self.curr_file, self.notebook.index(cell))
        self.notebook.remove(cell)
        cell.destroy()
        self.render()

    # def sync(self, peer):
    #     self.client.sync(peer)
    #     self.render()

    def render(self):
        """
        Refresh the UI to reflect the current state of the notebook.
        """
        if self.client is not None:
            # Delete the current cells
            for cell in self.notebook:
                cell.destroy()

            for (file, delete) in self.files:
                file.destroy()
                delete.destroy()
            
            if self.heading is not None:
                self.heading.destroy()

            self.notebook = []
            self.files = []
            self.file_index = 0

            # Recreate all the cells with the client's current state
            file_data = self.client.get_file_data()

            for filename in file_data:
                # print(filename)
                self.file_index+=1
                new_file = tk.Button(self.root, text=str(filename), command= lambda f=filename: self.open_file(f), width=10, height=SMALL_BUTTON_HEIGHT)
                new_file.grid(row=self.file_index, column = 0)
                delete = tk.Button(self.root, text="X", command= lambda f=filename: self.delete_file(f), width=SMALL_BUTTON_WIDTH, height=SMALL_BUTTON_HEIGHT)
                delete.grid(row=self.file_index, column = 1)
                self.files.append((new_file, delete))
            
            # for file in self.files:
            #     print(file['text'])

            if self.curr_file is not None:
                cell_data = self.client.get_cell_data(self.curr_file)
            elif self.files != []:
                self.curr_file=self.files[0][0]['text']
                cell_data = self.client.get_cell_data(self.curr_file)
            else:
                cell_data = None
            
            # print(self.curr_file)
            # print(cell_data)
            if cell_data is not None:
                file = tk.Label(self.root, text=self.curr_file, width=10, height=TOP_ROW_HEIGHT)
                file.grid(row= 0, column = 2)
                self.heading = file
                index = 0
                for text in cell_data:
                    cell = self.create_cell_frame(initial_text=text, depth=index)
                    cell.grid(row=6*index+1, column=2, rowspan=5, columnspan=5)
                    # cell.pack(side="top", fill="both", expand=True)
                    self.notebook.append(cell)
                    index+=1
        else:
            for cell in self.notebook:
                cell.pack_forget()
            for cell in self.notebook:
                cell.pack(side="top", fill="both", expand=True)

    def start(self):
        """
        Start the UI. Note that this method blocks until the UI is closed.
        """
        # self.add_cell()
        self.root.mainloop()

    


# class NotebookEditor():
#     """
#     NotebookEditor defines the UI for a simple notebook editor using tkinter. It
#     optionally takes a DistributedNotebook object as input to synchronize with.
#     """
#     def __init__(self, client=None):
#         self.root = tk.Tk()
#         self.root.title(client.name if client is not None else "Untitled Notebook")
#         self.client = client
#         self.cells = []
#         self.files = []
#         if self.client is not None:
#             # for peer in self.client.get_peers():
#                 # tk.Button(self.root, text="sync with {}".format(peer), command=lambda p=peer: self.sync(p)).pack(side="top")
#             Files = tk.Label(self.root, text="Files")
#             Add = tk.Button(self.root, text="+", command= lambda: self.add_name())
#             Refresh = tk.Button(self.root, text="Refresh")
#             Files.grid(row = 0, column = 0)
#             Add.grid(row = 0, column = 1)
#             Refresh.grid(row = 0, column = 7)
#             self.client.attach_editor(self)

#     def add_file(self, submit, file_name):
#         new_file = tk.Button(self.root, text=file_name.get())
#         submit.destroy()
#         file_name.destroy()
#         new_file.grid(column = 0)

#     def add_name(self):
#         file_name = tk.Entry(self.root, width=10, height=5)
#         submit = tk.Button(self.root, text="submit", command=lambda: self.add_file(submit, file_name))
#         file_name.grid(column = 0)
#         submit.grid(column = 1)

#     def add_cell(self, after=None):
#         cell = self.create_cell_frame()

#         # Figure out if where to insert or append the cell based on which cell the add
#         # button was clicked
#         if after in self.cells:
#             index = self.cells.index(after) + 1
#         else:
#             index = len(self.cells)

#         if index >= len(self.cells):
#             self.cells.append(cell)
#             if self.client is not None:
#                 self.client.create_cell()
#         else:
#             self.cells.insert(index, cell)
#             if self.client is not None:
#                 self.client.create_cell(index)
#         self.render()

#     def create_cell_frame(self, after=None, initial_text=''):
#         # Create the subframe to hold the cell widgets
#         cell = tk.Frame(self.root)

#         # Button to remove the cell
#         remove = tk.Button(cell, text="X", command=lambda: self.remove_cell(cell))
#         remove.grid(column=7)
        
#         # Text editor widget
#         text = tk.Text(cell, wrap="char", highlightbackground="gray")
#         text.grid(column=2, columnspan = 5, rowspan = 5)
#         text.insert("end", initial_text)
#         text.bind("<KeyRelease>", self.edit_cell_callback)
#         # text.pack(side="bottom")
        
#         # Button to insert a new cell
#         add = tk.Button(cell, text="+", command=lambda: self.add_cell(cell))
#         add.grid(column=7)
#         return cell

        

#     def edit_cell_callback(self, event):
#         cell = event.widget.master
#         if self.client is not None:
#             # If a notebook client is attached, send the new text to the correct notebook cell
#             self.client.update_cell(self.cells.index(cell), event.widget.get("1.0", "end-1c"))

#     def remove_cell(self, cell):
#         if self.client is not None:
#             self.client.remove_cell(self.cells.index(cell))
#         self.cells.remove(cell)
#         cell.destroy()

#     def sync(self, peer):
#         self.client.sync(peer)
#         self.render()

#     def render(self):
#         """
#         Refresh the UI to reflect the current state of the notebook.
#         """
#         if self.client is not None:
#             # Delete the current cells
#             for cell in self.cells:
#                 cell.destroy()
#             self.cells = []

#             # Recreate all the cells with the client's current state
#             cell_data = self.client.get_cell_data()
#             for text in cell_data:
#                 cell = self.create_cell_frame(initial_text=text)
#                 cell.grid(rowspan=5, columnspan=5)
#                 # cell.pack(side="top", fill="both", expand=True)
#                 self.cells.append(cell)
#         else:
#             for cell in self.cells:
#                 cell.pack_forget()
#             for cell in self.cells:
#                 cell.pack(side="top", fill="both", expand=True)

#     def start(self):
#         """
#         Start the UI. Note that this method blocks until the UI is closed.
#         """
#         self.add_cell()
#         self.root.mainloop()
