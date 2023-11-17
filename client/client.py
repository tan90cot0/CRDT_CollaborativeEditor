import time
import random
import pickle
import socket
import threading

from notebook.file_system import DistributedFileSystem

RECV_BUFFER = 1024

class FileSystemClient():
    """
    FileSystemClient handles syncing with remote peers to implement asynchronous
    collaboration.
    """

    def __init__(self, port, peers, name="alice", hostname="localhost"):
        self.port = int(port)
        self.peers = {}
        self.peers_last_sync = {}
        for peer in peers:
            peer_parts = peer.split(":")
            if len(peer_parts) == 2:
                self.peers[peer_parts[0]] = ("localhost", int(peer_parts[1]))
                self.peers_last_sync[peer_parts[0]] = time.time()
            elif len(peer_parts) == 3:
                self.peers_last_sync[peer_parts[0]] = time.time()
                self.peers[peer_parts[0]] = (peer_parts[1], int(peer_parts[2]))
            else:
                raise ValueError("Invalid peer format: {}".format(peer))
        self.name = name
        self.hostname = hostname
        # self.notebook = DistributedNotebook(id=name+":"+str(port))
        self.fileSystem = DistributedFileSystem(id=name+":"+str(port))
        # The client listens and responds to sync messages on another thread.
        # Therefore, notebook accesses are critical sections and must be protected by a
        # lock to prevent concurrent access.
        self.lock = threading.Lock()
        self.editor = None
        self.connected = False

    def toggle_connection(self):
        with self.lock:
            self.connected = not self.connected
        print(f"State of {self.name} changed to {self.connected}")
        if self.connected:
            listen = threading.Thread(target=self.listen, args=(self.port,))
            listen.start()
            

    def attach_editor(self, editor):
        """
        Attaches a NotebookEditor to the client to enable editor updates from listen().
        """
        self.editor = editor

    def get_peers(self):
        """
        Returns the list of peer names.
        """
        return list(self.peers.keys())
        
    def auto_sync(self):
        
        last_synced_time = time.time()
        random_sync_interval = 10 + 5 *random.random() 
        random_sync_interval = 0.5+ random.random() 
        while True:
            if time.time() - last_synced_time < random_sync_interval or not self.connected:
                continue
            for peer in self.get_peers():
                self.sync(peer)
            last_synced_time = time.time()
            random_sync_interval = 0.5 + random.random() 

    def host(self):
        """
        Starts a listener thread to receive sync messages from remote peers.
        """
        listen = threading.Thread(target=self.listen, args=(self.port,))
        listen.start()
        
        sync = threading.Thread(target=self.auto_sync)
        sync.start()

    def send_bytes(self, sock, data):
        """
        Send data over a socket.
        """
        size = len(data).to_bytes(4, byteorder='big')
        sock.sendall(size)
        sock.sendall(data)

    def recv_bytes(self, sock):
        """
        Receive data from a socket.
        """
        size = sock.recv(4)
        size = int.from_bytes(size, byteorder='big')
        data = b''
        while len(data) < size:
            buffer = sock.recv(size - len(data))
            if not buffer:
                raise EOFError("Connection closed")
            data += buffer
        return data

    def listen(self, port):
        """
        Listens for sync messages from remote peers.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.hostname, port))
            s.listen()
            print("Listening on port {}".format(port))
            while True:
                with self.lock:
                    if not self.connected:
                        break
                conn, addr = s.accept()
                print(addr)
                with conn:
                    while True:
                        with self.lock:
                            if not self.connected:
                                break
                        data = self.recv_bytes(conn)
                        if not data:
                            break
                        peer_name = pickle.loads(data)
                        print(f"Recieving Data from {peer_name}")
                        self.send_bytes(conn, pickle.dumps('ack'))
                        
                        data = self.recv_bytes(conn)
                        if not data:
                            break
                        remote = pickle.loads(data)

                        with self.lock:
                            self.fileSystem.merge(remote)
                            self.send_bytes(conn, pickle.dumps(self.fileSystem))
                        self.editor.render()
        print('Disconnected Closing Socket ...')

    def sync(self, peer):
        """
        Sends a sync message to a remote peer.
        """
        if not self.connected:
            print(f"{self.name} is Disconnected, Cannot Sync !")
            return

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect(self.peers[peer])

                with self.lock:
                    self.send_bytes(s, pickle.dumps(self.name))
                    data = self.recv_bytes(s)
                    assert pickle.loads(data) == 'ack' 
                    self.send_bytes(s, pickle.dumps(self.fileSystem))

                data = self.recv_bytes(s)
                remote = pickle.loads(data)
                
                with self.lock:
                    self.fileSystem.merge(remote)
                self.editor.render()
            except ConnectionRefusedError:
                print(f"{peer} refused connection from {self.name}")

    def create_file(self, filename=None):
        """
        Creates a new file with the given name. Appends it to the end of the fileSystem.
        """
        with self.lock:
            self.fileSystem.create_file(filename)
        
    def remove_file(self, filename=None):
        """
        Deletes the file with the given filename from the filesystem.
        """
        with self.lock:
            self.fileSystem.remove_file(filename)

    def create_cell(self, filename=None, index=None):
        """
        Creates a new cell at the given index of the file. If the index is not specified, 
        the cell is appended to the end of the file.
        """
        with self.lock:
            self.fileSystem.create_filecell(filename, index)

    def update_cell(self, filename, index, text):
        """
        Updates the cell text at given index with new text in the given file.
        """
        with self.lock:
            self.fileSystem.update_filecell(filename, index, text)

    def remove_cell(self, filename, index):
        """
        Removes the cell at the given index from the given file.
        """
        with self.lock:
            self.fileSystem.remove_filecell(filename, index)

    def get_file_data(self):
        """
        Returns all the file names from the whole File system.
        """
        with self.lock:
            return self.fileSystem.get_filename_data()

    def get_cell_data(self, filename):
        """
        Returns all the cell data from the given file.
        """
        with self.lock:
            return self.fileSystem.get_filecell_data(filename)
