import logging
import socket
import time

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
        self.sock.bind(server_address)
        
        #Calling listen() puts the socket into server mode, and accept() waits for an incoming connection.
        self.sock.listen(1)
    
    def Connect(self): 
#         while True:
#             self.logger.info('Waiting for a connection')
            self.connection, client_address = self.sock.accept()
            self.logger.info('Connection address: %s' ,client_address ) 
        
    def Send(self,data):
#             i=0
#             while True:
#                 message = str(i)
#                 if message:
        try:
            self.connection.sendall(data)
            self.logger.info('Send command')
        except socket.error as err:
            if err.errno :
                self.logger.info('%s' ,err )
#                 break                
#                     i+=1
#                 time.sleep(3)
    def MakeByteArray(self, data):
        bytes = bytearray()
        for itm in data:
            bytes.append(itm)
        return bytes
        
              
    def Close(self):
        self.connection.close()

        
        