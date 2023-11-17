import uuid

from crdt.sequence import Sequence
from notebook.notebook import DistributedNotebook

class DistributedFileSystem(Sequence):
    """
    DistributedFileSystem is a Folder of files designed for asynchronous collaboration. It
    consists of CRDT data structures which enable consistent merges between replicas.
    """
    def __init__(self, id=..., ):
        super().__init__(id)
        self.file_ids = {}
        self.filecell_ids = {}
        self.curr_file_id = 0
        self.curr_filecell_id = 0

    def create_file(self, filename=None):
        """
        Creates a new file at the given index. If the index is not specified, the file
        is appended to the end of the notebook.
        """
        file = DistributedNotebook(id=self.id)
        self.file_ids[filename] = self.curr_file_id
        file.create_cell(self.curr_file_id)
        self.curr_file_id += 1
        file.update_cell(0,filename)
        self.append(file)
        # if index is None:
        #     self.append(file)
        # else:
        #     self.insert(index, file)

    def create_filecell(self, filename=None, index=None):
        """
        Creates a new cell in the given file at the given index.
        """
        self.filecell_ids[filename + "#" + str(index)] = self.curr_filecell_id
        
        for file in self.get():
            if file.get_cell_data()[0] == filename:
                if index is not None:
                    file.create_cell(self.curr_filecell_id, index+1)
                else:
                    file.create_cell(self.curr_filecell_id)
        self.curr_filecell_id += 1

    def update_filecell(self, filename, index, text):
        """
        Updates the cell in a particular file at a particular index.
        """
        for file in self.get():
            if file.get_cell_data()[0] == filename:
                file.update_cell(index+1, text)
        # new_file = notebook.get_cell_data()
        # for i in range(len(new_file)):
        #     self.get()[index].update_cell(i,new_file[i])
        # for j in range(len(new_file),len(self.get()[index].get())):
        #     self.get()[index].remove_cell(j)
    
    def remove_filecell(self, filename, index):
        """
        Updates the cell in a particular file at a particular index.
        """
        for file in self.get():
            if file.get_cell_data()[0] == filename:
                file.remove_cell(index+1)

    def remove_file(self, filename):
        """
        Removes the cell at the given index.
        """
        index = 0
        for file in self.get():
            if file.get_cell_data()[0] == filename:
                self.remove(index)
            index+=1

    def get_filecell_data(self, filename):
        """
        Returns all the cell data of the given file.
        """
        # return [note]
        for file in self.get():
            if file.get_cell_data()[0] == filename:
                return file.get_cell_data()[1:], file.get_cell_ids()[1:]
    
    def get_filename_data(self):
        """
        Returns all the filenames of the entire File system.
        """
        # return [note]
        return [file.get_cell_data()[0] for file in self.get()]
