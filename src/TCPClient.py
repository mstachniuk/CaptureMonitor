import logging
import socket
import time
import pickle
import threading
import Queue
import EventExecutor
import ConfigParser

Event_type = {
    "mouse move" : 1,
    "key down" : 2,
    "key up" : 3,
    "key sys down" : 4,
    "key sys up" : 5,
    "mouse left down" : 6,
    "mouse left up" : 7,
    "mouse right down" : 8,
    "mouse right up" : 9,
    "mouse wheel" : 10,
    }

class TCPClient(object):
    
    def __init__(self):
        self.logger = logging.getLogger('TCPClient')
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        shandler = logging.StreamHandler()
        shandler.setLevel(logging.DEBUG)
        shandler.setFormatter(formatter)
        self.logger.addHandler(shandler)
        self.logger.debug('creating an instance of TCPClient')
        
        config = ConfigParser.RawConfigParser()
        config.read('config.ini')
        
        self.TCP_IP = config.get('server', 'TCP_IP')
        self.TCP_PORT = config.getint('server', 'TCP_PORT')
        self.BUFFER_SIZE = config.getint('server', 'BUFFER_SIZE')

        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self.eventThread = threading.Event()
        timeOut_event= 2
        self.queue = Queue.Queue()
        timeOut_empty = 0.25
        self.stop_reading = False
        tcpThread = threading.Thread(name='blocking', 
                                     target=self.executeTCPComand,
                                    args=(self.eventThread,timeOut_event,self.queue,timeOut_empty,self.stop_reading))
        tcpThread.start()
        
        
    
    def ConnectToServer(self):
        # Connect the socket to the port where the server is listening
        server_address = (self.TCP_IP, self.TCP_PORT)
        #self.logger.info('connecting to %s port %s' ,server_address ) 
        #print >>sys.stderr, 'connecting to %s port %s' % server_address
        try:
            self.sock.connect(server_address)
        except socket.error as err:
            if err.errno :
                self.logger.info('%s' ,err )
            
            

    def ReciveCommand(self):
        while True:
            try:
                data = self.sock.recv(self.BUFFER_SIZE)
                if data:
                    dataUnpacked = pickle.loads(data)
                    self.queue.put(dataUnpacked)
                    self.eventThread.set()
                    self.logger.info('%s' ,dataUnpacked )
                    ackFormat = format(dataUnpacked[5], '.5f')
                    # ack is a delay time with limited number of significant digits
                    self.logger.info('ack send : %s' ,ackFormat )
                    self.sock.sendall(ackFormat)
            except socket.error as err:
                if err.errno :
                    self.logger.info('%s' ,err )
                    self.stop_reading = True
                    self.sock.close()
                    break
    
    def executeTCPComand(self,eventThread,timeOut_event,queue,timeOut_empty,stop_reading):
        executor = EventExecutor.EventExecutor()
        while True:
                eventThread.wait(timeOut_event)
                if(eventThread.is_set()):
                    self.logger.info('event received: %s', eventThread.is_set())
                    
                    while True:
                        try:
                            value = queue.get(timeout=timeOut_empty)
                            # If timeout, it blocks at most timeout seconds and raises the Empty exception
                            # if no item was available within that time.
                        except Queue.Empty:                               
                            eventThread.clear()
                            queue.task_done()
                            break
                        else:
                            time.sleep(value[5]) #first wait elapsed time then press
                            if value[2] == Event_type['mouse move']:
                                executor.doMouseMove(value[0],value[1])
                                
                            if (value[2] == Event_type['key down']) or (value[2] == Event_type['key sys down']) :
                                if value[3] == 0:
                                    executor.doKeyDown(value[4])
                                else:
                                    executor.doExtendedKeyDown(value[3])
                                    executor.doExtendedKeyDown(value[4])
                                    # ctr+C is registered as extended if ctr and c pressed or ctr and c released
                                    # not registered if c  and ctr (c is first released before ctr)
                                    # it's better to do  redundant auto extended Up
                                    executor.doExtendedKeyUp(value[3])
                                    executor.doExtendedKeyUp(value[4])
                            if (value[2] == Event_type['key up']) or (value[2] == Event_type['key sys up']) :
                                if value[3] == 0:
                                    executor.doKeyUp(value[4])
                                else:
                                    executor.doExtendedKeyUp(value[3])
                                    executor.doExtendedKeyUp(value[4])

                            if value[2] == Event_type['mouse left down']:
                                executor.doLeftMouseDonw(value[0], value[1])
                                
                            if value[2] == Event_type['mouse left up']:
                                executor.doLeftMouseUp(value[0], value[1])

                            if value[2] == Event_type['mouse right down']:
                                executor.doRightMouseDonw(value[0], value[1])

                            if value[2] == Event_type['mouse right up']:
                                executor.doRightMouseUp(value[0], value[1])

                            if value[2] == Event_type['mouse wheel']:
                                executor.doMouseWheel(value[0], value[1], value[4])

                else:
                    self.logger.info('No data received: False')
                    if(self.stop_reading == True):
                        self.logger.info('Reading data interrupted')
                        break

tcptest = TCPClient()
tcptest.ConnectToServer()
tcptest.ReciveCommand()
