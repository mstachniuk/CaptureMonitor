import logging
import socket
import sys
import time
import win32api
import win32gui
import win32con

module_logger = logging.getLogger('application.TCPClient')

TCP_IP = 'localhost'
TCP_PORT = 5005
BUFFER_SIZE = 1024

class TCPClient(object):
    
    def __init__(self):
        self.logger = logging.getLogger('application.TCPClient')
        self.logger.debug('creating an instance of TCPClient')

        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def ConnectToServer(self):
        # Connect the socket to the port where the server is listening
        server_address = (TCP_IP, TCP_PORT)
        #self.logger.info('connecting to %s port %s' ,server_address ) 
        #print >>sys.stderr, 'connecting to %s port %s' % server_address
        self.sock.connect(server_address)

    def ReciveCommand(self):
        while True:
            try:
                data = self.sock.recv(BUFFER_SIZE)
                if data:
                    print "recived command: %s"  %data
#                   self.logger.info('Recived data: %s' ,data )
                    self.doMouseMove(int(data))
            except socket.error as err:
                if err.errno :
                    self.logger.info('%s' ,err )
                    break
        self.sock.close()
            
    def doMouseMove(self, x_pos):
        #Pass the coordinates as a tuple:
        win32api.SetCursorPos((x_pos,0))
        
    def doExtendedKeyDown(self,key):
        win32api.keybd_event(key, 0, win32con.KEYEVENTF_EXTENDEDKEY, 0);
    
    def doExtendedKeyUp(self,key):
        win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0);
        
    def unHookMouseAndKey(self):
        self.hm.UnhookMouse()
        self.hm.UnHookKeyboard()

tcptest = TCPClient()
tcptest.ConnectToServer()
tcptest.ReciveCommand()
