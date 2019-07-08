import logging
import win32api
import win32gui
import pythoncom
import pyHook
from pyHook import GetKeyState, HookConstants
import CaptureScreen
import EventExecutor
import threading
import time
import string
import TCPServer
import XmlCreator
import pickle
import Queue
import os

module_logger = logging.getLogger('application.HookEvent')

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


def get_cursor_position():
    flags, handle, (x, y) = win32gui.GetCursorInfo()
    coordinates = (x, y)
    return coordinates


def on_mouse_event(event):
    print 'MessageName:', event.MessageName
    print 'Message:', event.Message
    print 'Time:', event.Time
    print 'Window:', event.Window
    print 'WindowName:', event.WindowName
    print 'Position:', event.Position
    print 'Wheel:', event.Wheel
    print 'Injected:', event.Injected
    print '---'
    return True

    # hook mouse


class HookEvent(object):

    def __init__(self):
        self.logger = logging.getLogger('application.HookEvent')
        self.logger.debug('creating an instance of HookEvent')
        self.hm = pyHook.HookManager()
        self.event_list = []
        self.is_record = False
        self.is_play = False
        self.is_connected = False
        self.start_time = time.time()

        self.width = 0
        self.height = 0
        self.width_offset = 0
        self.height_offset = 0

        self.enum = CaptureScreen.CaptureScreen()
        self.logger.debug('Number of display devices: %s ', str(self.enum.enum_display_devices()))
        self.logger.debug('Number of physical monitors: %s ', str(self.enum.get_visible_monitors()))

        self.event_thread = threading.Event()
        time_out_event = 2
        self.queue = Queue.Queue()
        time_out_empty = 0.25
        tcp_thread = threading.Thread(name='blocking',
                                      target=self.send_tcp_command,
                                      args=(self.event_thread, time_out_event, self.queue, time_out_empty))
        tcp_thread.start()
        self.server = None

        self.xml_data = XmlCreator

    def identify_monitor_params(self):
        monitor_info = win32api.GetMonitorInfo(win32api.MonitorFromPoint(win32api.GetCursorPos()))
        self.logger.debug('Monitor info,: %s ', str(monitor_info))

        self.width_offset = monitor_info.get('Monitor')[0]
        all_width = monitor_info.get('Monitor')[2]
        self.width = all_width - self.width_offset

        self.logger.debug('Monitor detection, width: %s ', str(self.width))

        self.height_offset = monitor_info.get('Monitor')[1]
        all_height = monitor_info.get('Monitor')[3]
        self.height = all_height - self.height_offset

        self.logger.debug('Monitor detection, height: %s ', str(self.height))

    def create_event_list(self, event_message_name, key1, key2):
        if self.is_record:
            elapsed_time = time.time() - self.start_time

            self.start_time = time.time()
            self.identify_monitor_params()

            (x, y) = get_cursor_position()
            self.logger.debug('Mouse event: %s position %s %s ', event_message_name, x, y)

            arg_list = [x, y, event_message_name, key1, key2, elapsed_time]
            self.event_list.append(arg_list)

            self.logger.info('Event %s %s %s ', event_message_name, hex(key1), hex(key2))

        return True

    def send_tcp_command(self, event_thread, time_out_event, queue, time_out_empty):

        while True:
            if not self.is_connected:
                self.server = TCPServer.TCPServer()
                self.is_connected = self.server.connect()

            event_thread.wait(time_out_event)
            if event_thread.is_set():
                self.logger.debug('New data on the list - ready to be sent: %s', event_thread.is_set())

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
                        if self.is_connected:
                            data = pickle.dumps(value)
                            self.logger.debug('send_data TCP')
                            self.is_connected = self.server.send_data(data)
                            self.logger.debug('Value: %s', value)

                            ack_format = format(value[5], '.5f')
                            is_ack = self.server.wait_for_received(ack_format)
                            if not is_ack:
                                self.logger.error('Timeout ACK')
                            if is_ack:
                                self.logger.debug('Next data')
                        else:
                            break
            else:
                self.logger.debug('Waiting for event to send %s:', event_thread.is_set())

    def do_capture_screen(self):
        capture_screen = CaptureScreen.CaptureScreen()
        capture_screen.set_capture_params(self.width, self.height, self.width_offset, self.height_offset)
        (x, y) = get_cursor_position()
        capture_screen.set_cursor_draw(x, y)
        capture_screen.grab_handle()
        capture_screen.create_context()
        capture_screen.create_memory()
        capture_screen.create_bitmap()
        capture_screen.copy_screen_to_memory()
        capture_screen.save_bitmap_to_file()
        capture_screen.free_objects()

        return False

    def move(self, event):
        self.logger.debug('Mouse event : %s ', event.MessageName)
        if self.is_record:
            self.create_event_list(Event_type[event.MessageName],
                                   0,
                                   0)
        return True

    def left_down(self, event):
        self.logger.debug('Mouse event : %s ', event.MessageName)
        if self.is_record:
            self.create_event_list(Event_type[event.MessageName],
                                   0,
                                   1)
            t = threading.Thread(target=self.do_capture_screen)
            t.start()

        return True

    def right_down(self, event):
        self.logger.debug('Mouse event : %s ', event.MessageName)
        if self.is_record:
            self.create_event_list(Event_type[event.MessageName],
                                   0,
                                   2)
            t = threading.Thread(target=self.do_capture_screen)
            t.start()

        return True

    def middle_down(self, event):
        self.logger.debug('Mouse event : %s ', event.MessageName)
        if self.is_record:
            self.create_event_list(Event_type[event.MessageName],
                                   0,
                                   4)
            t = threading.Thread(target=self.do_capture_screen)
            t.start()

        return True

    def wheel(self, event):
        self.logger.debug('Mouse event : %s ', event.MessageName)
        if self.is_record:
            self.create_event_list(Event_type[event.MessageName],
                                   0,
                                   event.Wheel)

        return True

    def on_keyboard_event(self, event):
        #         if GetKeyState(HookConstants.VKeyToID('VK_MENU')) and event.KeyID == int("0x4D", 16) :
        #             if(event.MessageName == 'key sys down'):
        #                 tcpThread = threading.Thread(name='blocking',
        #                                              target=self.send_tcp_command,
        #                                              args=(self.eventThread,timeOut,self.queue))
        #                 tcpThread.start()

        # "ALT+V record event "    
        if GetKeyState(HookConstants.VKeyToID('VK_MENU')) and event.KeyID == int("0x56", 16):
            if self.is_record:
                if event.MessageName == 'key sys down':
                    # key sys down when ALT+V pressed. Key down if single key
                    # add the last up ALT , before stop recording
                    self.create_event_list(Event_type["key sys up"],
                                           0,
                                           164)

                    self.is_record = False
                    self.logger.info('Capture : STOP Recording ')
            else:
                if not self.is_play:
                    if event.MessageName == 'key sys down':
                        # key sys down when ALT+V pressed. Key down if single key
                        self.is_record = True
                        self.logger.info('Capture : START Recording ')
                        self.start_time = time.time()
                else:
                    self.logger.info('If you want record event, please first stop playback ')

        # "ALT+B play list"
        elif GetKeyState(HookConstants.VKeyToID('VK_MENU')) and event.KeyID == int("0x42", 16):
            if self.is_play:
                if event.MessageName == 'key sys down':
                    # key sys down when ALT+V pressed. Key down if single key
                    self.is_play = False
                    self.logger.info('Playback : STOP playback ')
            else:
                if not self.is_record:
                    if event.MessageName == 'key sys down':
                        # key sys down when ALT+V pressed. Key down if single key
                        self.is_play = True
                        self.logger.info('Playback : PLAY playback ')
                        t = threading.Thread(target=self.play_event_list)
                        t.start()
                else:
                    self.logger.info('If you want play event, please first stop recording ')
        # ALT+S Save current list.
        elif GetKeyState(HookConstants.VKeyToID('VK_MENU')) and event.KeyID == int("0x53", 16):
            if not self.is_record and not self.is_play:
                if event.MessageName == 'key sys down':
                    self.save_event_list()
                    self.logger.info('Saving List')
            else:
                self.logger.info('If you want save list, please first stop playback and capture ')
        # ALT+L Load merged xml files
        elif GetKeyState(HookConstants.VKeyToID('VK_MENU')) and event.KeyID == int("0x4C", 16):
            if not self.is_record and not self.is_play:
                if event.MessageName == 'key sys down':
                    path = str(os.getcwd())
                    self.event_list = self.xml_data.merge_files(path, "command", "param")
                    self.logger.info('Merge xml files into the command list')
                    # for element in self.event_list:
                    #     print element
        # "ALT+N clear recording list"
        elif GetKeyState(HookConstants.VKeyToID('VK_MENU')) and event.KeyID == int("0x4e", 16):
            if not self.is_record and not self.is_play:
                if event.MessageName == 'key sys down':
                    del self.event_list[:]
                    self.logger.info('Event List : clear ')
            else:
                self.logger.info('If you want clear list, please first stop playback and capture ')

        elif GetKeyState(HookConstants.VKeyToID('VK_LSHIFT')) and event.KeyID == HookConstants.VKeyToID('VK_SNAPSHOT'):
            # print "Shift+Print screen"
            self.logger.info('KeyboardEvent : Shift+Print screen ')
            if self.is_record:
                print event.MessageName
                self.create_event_list(Event_type[event.MessageName],
                                       160,
                                       event.KeyID)

        # "CTRL+key"
        elif GetKeyState(HookConstants.VKeyToID('VK_CONTROL')):
            # if button ctr is DOWN only !!
            # self.logger.info('KeyboardEvent CTRL: %s %s ',event.MessageName, hex(event.KeyID))
            if self.is_record:
                if event.Key in string.ascii_uppercase:
                    # if ctrl pressed and The uppercase letters 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                    self.create_event_list(Event_type[event.MessageName],
                                           162,
                                           event.KeyID)
                    t = threading.Thread(target=self.do_capture_screen)
                    t.start()
                else:
                    self.create_event_list(Event_type[event.MessageName],
                                           0,
                                           event.KeyID)
                    t = threading.Thread(target=self.do_capture_screen)
                    t.start()
        # Keys
        else:
            # self.logger.info('KeyboardEvent : %s %s ',event.MessageName, hex(event.KeyID))
            if self.is_record:
                if event.MessageName == 'key down':
                    self.create_event_list(Event_type[event.MessageName],
                                           0,
                                           event.KeyID)
                    t = threading.Thread(target=self.do_capture_screen)
                    t.start()
                else:
                    self.create_event_list(Event_type[event.MessageName],
                                           0,
                                           event.KeyID)
        return True

    def hook_mouse_and_key(self):
        self.hm.SubscribeMouseMove(self.move)
        self.hm.SubscribeMouseLeftDown(self.left_down)
        self.hm.SubscribeMouseRightDown(self.right_down)
        self.hm.SubscribeMouseMiddleDown(self.middle_down)
        self.hm.SubscribeMouseLeftUp(self.left_down)
        self.hm.SubscribeMouseRightUp(self.right_down)
        self.hm.SubscribeMouseMiddleUp(self.middle_down)
        self.hm.SubscribeMouseWheel(self.wheel)
        #         self.hm.MouseAll = self.on_mouse_event
        self.hm.HookMouse()

        # hook keyboard
        self.hm.KeyDown = self.on_keyboard_event  # watch for all keyboard events
        self.hm.KeyUp = self.on_keyboard_event
        self.hm.HookKeyboard()

        try:
            pythoncom.PumpMessages()
        except KeyboardInterrupt:
            pass

    def play_event_list(self):
        executor = EventExecutor.EventExecutor()

        while self.is_play:
            for value in self.event_list:
                # self.logger.info('Play event delay : %s ',value[4])
                self.logger.debug('Wait delay time to execute next command: %s', value[5])
                time.sleep(value[5])  # first wait elapsed time then press

                if self.is_connected:
                    self.queue.put(value)
                    self.event_thread.set()
                    self.logger.debug('Set event to send: %s', self.event_thread.is_set())

                if value[2] == Event_type['mouse move']:
                    # Pass the coordinates (x,y) as a tuple:
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
                if not self.is_play:
                    break
            self.logger.info('Playback : STOPPED - Event list is finished ')
            self.is_play = False

    def save_event_list(self):
        xml = XmlCreator.XmlCreator()
        xml.create_root("root")
        for value in self.event_list:
            xml.create_child("command")
            xml.create_element("param", "posX", str(value[0]))
            xml.create_element("param", "posY", str(value[1]))
            xml.create_element("param", "message", str(value[2]))
            xml.create_element("param", "key1", str(value[3]))
            xml.create_element("param", "key2", str(value[4]))
            xml.create_element("param", "time", str(value[5]))
        xml.compose_tree()
        xml.save_xml()

    def un_hook_mouse_and_key(self):
        self.hm.UnhookMouse()
        self.hm.UnHookKeyboard()
