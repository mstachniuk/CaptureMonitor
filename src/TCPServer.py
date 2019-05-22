import logging
import socket
from _socket import SOL_SOCKET, SO_REUSEADDR
import threading
import ConfigParser

module_logger = logging.getLogger('application.TCPServer')


class TCPServer(object):
    
    def __init__(self):
        self.logger = logging.getLogger('application.TCPServer')
        self.logger.debug('creating an instance of TCPServer')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        config = ConfigParser.RawConfigParser()
        config.read('config.ini')
        self.TCP_IP = config.get('server', 'TCP_IP')
        self.TCP_PORT = config.getint('server', 'TCP_PORT')
        self.BUFFER_SIZE = config.getint('server', 'BUFFER_SIZE')
        
        server_address = (self.TCP_IP, self.TCP_PORT)
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
            
            self.connection.settimeout(3)
            
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
            
    def SetTimeout(self,):
#         self.timeout_event = timeout_event
        self.timeout_event.set()
      
    def WaitForReceived(self,ackFormat):
        self.timeout_event = threading.Event()
        time_value =  3
        t = threading.Timer(time_value, self.SetTimeout, [])
        self.logger.info('Start timeout : %s seconds' ,time_value )
        t.start()
        while True:
            try:
                self.logger.info('Waiting for ACK: %s' ,ackFormat )
                data = self.connection.recv(self.BUFFER_SIZE)
                # global timeout connection is 3 seconds.
                ackReceived = data.decode('UTF-8')
                self.logger.info('Received and decoding ACK: %s' ,ackReceived )

                
            except socket.error as err:
                if err.errno :
                    self.logger.info('Error received data: %s' ,err )
                    return False
                    break
            if ackReceived == ackFormat:
                self.logger.info('Ack is correct  %s ',ackFormat)
                return True
                break
            if self.timeout_event.is_set():
                self.logger.info('No ack received %s' ,time_value )
                return False
                break
                
    
    def Close(self):
        self.connection.close()