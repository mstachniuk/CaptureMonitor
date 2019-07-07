import logging
import socket
import time
import pickle
import threading
import Queue
import EventExecutor
import ConfigParser

Event_type = {
    "mouse move": 1,
    "key down": 2,
    "key up": 3,
    "key sys down": 4,
    "key sys up": 5,
    "mouse left down": 6,
    "mouse left up": 7,
    "mouse right down": 8,
    "mouse right up": 9,
    "mouse wheel": 10,
}


class TCPClient(object):

    def __init__(self):
        self.logger = logging.getLogger('TCPClient')
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        s_handler = logging.StreamHandler()
        s_handler.setLevel(logging.INFO)
        s_handler.setFormatter(formatter)
        self.logger.addHandler(s_handler)
        self.logger.debug('creating an instance of TCPClient')

        config = ConfigParser.RawConfigParser()
        config.read('config.ini')

        self.TCP_IP = config.get('server', 'TCP_IP')
        self.TCP_PORT = config.getint('server', 'TCP_PORT')
        self.BUFFER_SIZE = config.getint('server', 'BUFFER_SIZE')

        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.event_thread = threading.Event()
        time_out_event = 2
        self.queue = Queue.Queue()
        time_out_empty = 0.25
        self.stop_reading = False
        tcp_thread = threading.Thread(name='blocking',
                                      target=self.execute_tcp_command,
                                      args=(self.event_thread,
                                            time_out_event,
                                            self.queue,
                                            time_out_empty,
                                            self.stop_reading))
        tcp_thread.start()

    def connect_to_server(self):
        # connect the socket to the port where the server is listening
        server_address = (self.TCP_IP, self.TCP_PORT)
        self.logger.info('connecting to %s', server_address)

        try:
            self.sock.connect(server_address)
        except socket.error as err:
            if err.errno:
                self.logger.error('%s', err)
                self.stop_reading = True

    def receive_command(self):
        while True:
            try:
                data = self.sock.recv(self.BUFFER_SIZE)
                if data:
                    data_unpacked = pickle.loads(data)
                    self.queue.put(data_unpacked)
                    self.event_thread.set()
                    self.logger.info('%s', data_unpacked)
                    ack_format = format(data_unpacked[5], '.5f')
                    # ack is a delay time with limited number of significant digits
                    self.logger.debug('ack send : %s', ack_format)
                    self.sock.sendall(ack_format)
            except socket.error as err:
                if err.errno:
                    self.logger.error('%s', err)
                    self.stop_reading = True
                    self.sock.close()
                    break

    def execute_tcp_command(self, event_thread, time_out_event, queue, time_out_empty, stop_reading):
        executor = EventExecutor.EventExecutor()
        while True:
            event_thread.wait(time_out_event)
            if stop_reading:
                event_thread.clear()
            if event_thread.is_set():
                self.logger.info('event received: %s', event_thread.is_set())

                while True:
                    try:
                        value = queue.get(timeout=time_out_empty)
                        # If timeout, it blocks at most timeout seconds and raises the Empty exception
                        # if no item was available within that time.
                    except Queue.Empty:
                        event_thread.clear()
                        queue.task_done()
                        break
                    else:
                        time.sleep(value[5])  # first wait elapsed time then press
                        if value[2] == Event_type['mouse move']:
                            executor.do_mouse_move(value[0], value[1])

                        if (value[2] == Event_type['key down']) or (value[2] == Event_type['key sys down']):
                            if value[3] == 0:
                                executor.do_key_down(value[4])
                            else:
                                executor.do_extended_key_down(value[3])
                                executor.do_extended_key_down(value[4])
                                # ctr+C is registered as extended if ctr and c pressed or ctr and c released
                                # not registered if c  and ctr (c is first released before ctr)
                                # it's better to do  redundant auto extended Up
                                executor.do_extended_key_up(value[3])
                                executor.do_extended_key_up(value[4])
                        if (value[2] == Event_type['key up']) or (value[2] == Event_type['key sys up']):
                            if value[3] == 0:
                                executor.do_key_up(value[4])
                            else:
                                executor.do_extended_key_up(value[3])
                                executor.do_extended_key_up(value[4])

                        if value[2] == Event_type['mouse left down']:
                            executor.do_left_mouse_down(value[0], value[1])

                        if value[2] == Event_type['mouse left up']:
                            executor.do_left_mouse_up(value[0], value[1])

                        if value[2] == Event_type['mouse right down']:
                            executor.do_right_mouse_down(value[0], value[1])

                        if value[2] == Event_type['mouse right up']:
                            executor.do_right_mouse_up(value[0], value[1])

                        if value[2] == Event_type['mouse wheel']:
                            executor.do_mouse_wheel(value[0], value[1], value[4])

            else:
                self.logger.info('No data received: False')
                if self.stop_reading:
                    self.logger.debug('Reading data interrupted')
                    break


tcp_test = TCPClient()
tcp_test.connect_to_server()
tcp_test.receive_command()
