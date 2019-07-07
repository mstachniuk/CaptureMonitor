import logging
import win32api
import win32con

module_logger = logging.getLogger('application.EventExecutor')


class EventExecutor(object):

    def __init__(self):
        self.logger = logging.getLogger('application.EventExecutor')
        self.logger.debug('creating an instance of EventExecutor')

    def do_mouse_move(self, x_pos, y_pos):
        # Pass the coordinates as a tuple:
        win32api.SetCursorPos((x_pos, y_pos))
        self.logger.debug('do_mouse_move : %s %s', x_pos, y_pos)

    def do_key_down(self, key):
        win32api.keybd_event(key, 0, 0, 0)
        self.logger.debug('do_key_down : %s ', hex(key))

    def do_extended_key_down(self, key):
        win32api.keybd_event(key, 0, win32con.KEYEVENTF_EXTENDEDKEY, 0)
        self.logger.debug('do_extended_key_down : %s ', hex(key))

    def do_key_up(self, key):
        win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)
        self.logger.debug('do_key_up : %s ', hex(key))

    def do_extended_key_up(self, key):
        win32api.keybd_event(key, 0, win32con.KEYEVENTF_EXTENDEDKEY | win32con.KEYEVENTF_KEYUP, 0)
        self.logger.debug('do_extended_key_up : %s ', hex(key))

    def do_left_mouse_down(self, x_pos, y_pos):
        win32api.SetCursorPos((x_pos, y_pos))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x_pos, y_pos, 0, 0)
        self.logger.debug('do_left_mouse_down %s %s', x_pos, y_pos)

    def do_left_mouse_up(self, x_pos, y_pos):
        win32api.SetCursorPos((x_pos, y_pos))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x_pos, y_pos, 0, 0)
        self.logger.debug('do_left_mouse_up %s %s', x_pos, y_pos)

    def do_right_mouse_down(self, x_pos, y_pos):
        win32api.SetCursorPos((x_pos, y_pos))
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, x_pos, y_pos, 0, 0)
        self.logger.debug('do_right_mouse_down %s %s', x_pos, y_pos)

    def do_right_mouse_up(self, x_pos, y_pos):
        win32api.SetCursorPos((x_pos, y_pos))
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, x_pos, y_pos, 0, 0)
        self.logger.debug('do_right_mouse_up %s %s', x_pos, y_pos)

    def do_mouse_wheel(self, x_pos, y_pos, direct):
        win32api.SetCursorPos((x_pos, y_pos))
        win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, x_pos, y_pos, win32con.WHEEL_DELTA * int(direct), 0)
        self.logger.debug('do_mouse_wheel %s %s %s', x_pos, y_pos)
