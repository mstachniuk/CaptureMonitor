import logging
import socket
from _socket import SOL_SOCKET, SO_REUSEADDR
import threading

module_logger = logging.getLogger('application.TCPServer')

TCP_IP = 'localhost'
TCP_PORT = 5005
BUFFER_SIZE = 1024

class TCPServer(object):
    
    def __init__(self):
        self.logger = logging.getLogger('application.TCPServer')
        self.logger.debug('creating an instance of TCPServer')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (TCP_IP, TCP_PORT)
        #Then bind() is used to associate the socket with the server address
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        #this allows the ad/port to be reused immediately instead of it being stuck in the TIME_WAIT 
        # for server minutes waiting for late packets to arrive.
        self.sock.bind(server_address)
        
        #Calling listen() puts the socket into server mode, and accept() waits for an incoming connection.
        self.sock.listen(1)
        
    
    def Connect(self): 
            self.logger.info('Waiting for a connection')
            self.connection, client_address = self.sock.accept()
            self.logger.info('Connection address: %s' ,client_address )
            return True
            
        
    def Send(self,data):
        try:
            self.connection.sendall(data)
            return True
        except socket.error as err:
            if err.errno :
                self.logger.info('Error Send(): %s' ,err )
                return False
            
    def SetTimeout(self,timeout_event):
        self.timeout_event = timeout_event
        self.timeout_event.set()
      
    def WaitForReceived(self):
        timeout_event = threading.Event()
        time_value =  3
        t = threading.Timer(time_value, self.SetTimeout, [timeout_event])
        t.start()
        while True:
            data = self.connection.recv(BUFFER_SIZE)
            if data == "ack":
                self.logger.info('ack recived from client ')
                return True
                break
            if timeout_event.is_set():
                return False
                break
                
    
    def Close(self):
        self.connection.close()

        
        