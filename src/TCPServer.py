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
        self.connection = None
        self.timeout_event = None

        server_address = (self.TCP_IP, self.TCP_PORT)
        # Then bind() is used to associate the socket with the server address
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        # this allows the ad/port to be reused immediately instead of it being stuck in the TIME_WAIT
        # for server minutes waiting for late packets to arrive.
        self.sock.bind(server_address)

        # Calling listen() puts the socket into server mode, and accept() waits for an incoming connection.
        self.sock.listen(1)

    def connect(self):
        self.logger.info('Waiting for a connection')
        self.connection, client_address = self.sock.accept()

        self.connection.settimeout(3)

        self.logger.info('Connection address: %s', client_address)
        return True

    def send_data(self, data):
        try:
            self.connection.sendall(data)
            return True
        except socket.error as err:
            if err.errno:
                self.logger.error('Error send_data(): %s', err)
                return False

    def set_timeout(self, ):
        #         self.timeout_event = timeout_event
        self.timeout_event.set()

    def wait_for_received(self, ack_format):
        global ack_received
        self.timeout_event = threading.Event()
        time_value = 3
        t = threading.Timer(time_value, self.set_timeout, [])
        self.logger.debug('Start timeout : %s seconds', time_value)
        t.start()
        while True:
            try:
                self.logger.debug('Waiting for ACK: %s', ack_format)
                data = self.connection.recv(self.BUFFER_SIZE)
                # global timeout connection is 3 seconds.
                ack_received = data.decode('UTF-8')
                self.logger.debug('Received and decoding ACK: %s', ack_received)
            except socket.error as err:
                if err.errno:
                    self.logger.error('Error received data: %s', err)
                    return False
                    # break
            if ack_received == ack_format:
                self.logger.debug('Ack is correct  %s ', ack_format)
                return True
                # break
            if self.timeout_event.is_set():
                self.logger.debug('No ack received %s', time_value)
                return False
                # break

    def close_connection(self):
        self.connection.close()
