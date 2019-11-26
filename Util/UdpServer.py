import socket

class UdpServer():

    def __init__(self, host="", port=10000):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((host, port))
        print port
        
    def close(self):
        self.sock.close()