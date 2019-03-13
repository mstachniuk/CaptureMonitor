import logging
import win32api
import win32gui
import win32con

module_logger = logging.getLogger('application.EventExecutor')

class EventExecutor(object):

    def __init__ (self):
        self.logger = logging.getLogger('application.EventExecutor')
        self.logger.debug('creating an instance of EventExecutor')

    def doMouseMove(self, x_pos, y_pos):
        #Pass the coordinates as a tuple:
        win32api.SetCursorPos((x_pos,y_pos))
        
    def doKeyDown(self,key):
        win32api.keybd_event(key, 0, 0, 0);
        self.logger.info('doKeyDown : %s ',hex(key))
        
    def doExtendedKeyDown(self,key):
        win32api.keybd_event(key, 0, win32con.KEYEVENTF_EXTENDEDKEY, 0);
        self.logger.info('doExtendedKeyDown : %s ',hex(key))
    
    def doKeyUp(self,key):
        win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0);
        self.logger.info('doKeyUp : %s ',hex(key))
        
    def doExtendedKeyUp(self,key):
        win32api.keybd_event(key, 0, win32con.KEYEVENTF_EXTENDEDKEY | win32con.KEYEVENTF_KEYUP, 0);
        
        self.logger.info('doExtendedKeyUp : %s ',hex(key))
    
    def doLeftMouseDonw(self, x_pos, y_pos):
        win32api.SetCursorPos((x_pos,y_pos))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x_pos,y_pos,0,0)
        
    def doLeftMouseUp(self, x_pos, y_pos):
        win32api.SetCursorPos((x_pos,y_pos))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x_pos,y_pos,0,0)
        
    def doRightMouseDonw(self, x_pos, y_pos):
        win32api.SetCursorPos((x_pos,y_pos))
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN,x_pos,y_pos,0,0)
    
    def doRightMouseUp(self, x_pos, y_pos):
        win32api.SetCursorPos((x_pos,y_pos))
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP,x_pos,y_pos,0,0)
        
    def doMouseWheel(self, x_pos, y_pos , direct):
        win32api.SetCursorPos((x_pos,y_pos))
        win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, x_pos,y_pos, win32con.WHEEL_DELTA *int(direct), 0)

