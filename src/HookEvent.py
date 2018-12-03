import logging
import win32api
import win32gui
import pythoncom
import pyHook
from pyHook import GetKeyState, HookConstants
import CaptureScreen
import thread
import time

module_logger = logging.getLogger('application.HookEvent')

class HookEvent(object):
    
    def __init__ (self):
        self.logger = logging.getLogger('application.HookEvent')
        self.logger.debug('creating an instance of HookEvent')
        self.hm = pyHook.HookManager()
        self.eventList = []
        #posX,posY,action,delay
        self.start_time = time.time()
        
        self.enum = CaptureScreen.CaptureScreen()
        self.logger.debug('Numer of display devices: %s ' ,str(self.enum.enumDisplayDevices()))
        self.logger.debug('Numer of physical monitors: %s ' ,str(self.enum.enumVisibleMonitors()))
            
    def getCursorPosition(self):
        self.flags, self.handle, (x,y) = win32gui.GetCursorInfo()
        return (x,y)
  
    #this function set member _width, _hight
    def identyfyMonitorParams(self):
        monitorInfo = win32api.GetMonitorInfo(win32api.MonitorFromPoint(win32api.GetCursorPos()))
        self.logger.debug('Monitor info,: %s ' ,str(monitorInfo))
        
        self.widthOffset = monitorInfo.get('Monitor')[0]
        self.all_width = monitorInfo.get('Monitor')[2]
        self.width = self.all_width-self.widthOffset
        
        self.logger.debug('Monitor detection, width: %s ' ,str(self.width))
        
        self.hightOffset = monitorInfo.get('Monitor')[1]
        self.all_hight = monitorInfo.get('Monitor')[3]
        self.height = self.all_hight-self.hightOffset
        
        self.logger.debug('Monitor detection, height: %s ' ,str(self.height))
        
    def createEventList(self,arg):
        elapsed_time = time.time() - self.start_time    
        self.start_time = time.time()
        self.identyfyMonitorParams()
        (x,y) = self.getCursorPosition()
        self.logger.info('Mouse event: %s position %s %s ' ,arg,x,y)
        argList = [x,y,arg,elapsed_time]
        self.eventList.append(argList)
        for x in self.eventList:
            print(x)    
        
    def doCaptureScreen(self,arg):
        self.createEventList(arg)
        
        captureScreen = CaptureScreen.CaptureScreen()
        captureScreen.setCaptureParams(self.width,self.height,self.widthOffset,self.hightOffset)
        captureScreen.grabAHandle()
        captureScreen.createContext()
        captureScreen.createMemory()
        captureScreen.createBitmap()
        captureScreen.copyScreenToMemory()
        captureScreen.saveBitmapToFile()
        captureScreen.freeObjects()
        time.sleep(0.001)
        
        
        return 0
    

    def left_down(self,event):
        thread.start_new_thread(self.doCaptureScreen, (event.MessageName,))
        return True 
    
    def right_down(self,event):
        thread.start_new_thread(self.doCaptureScreen, (event.MessageName,))
        return True    
    
    def middle_down(self,event):
        thread.start_new_thread(self.doCaptureScreen, (event.MessageName,))
        return True
         
    def wheel(self,event):
        #thread.start_new_thread(self.doCaptureScreen, (event.MessageName,))
        thread.start_new_thread(self.createEventList, (event.MessageName,))
        return True
    
    def onKeyboardEvent(self,event):
        #print chr(event.Ascii)WM_KEYUPWM_KEYUPWM_KEYUPWM_KEYUP
        if GetKeyState(HookConstants.VKeyToID('VK_LSHIFT')) and event.KeyID == HookConstants.VKeyToID('VK_SNAPSHOT'):
            #print "Shitf+Print screen"
            self.logger.info('KeyboardEvent : Shitf+Print screen ')
            thread.start_new_thread(self.doCaptureScreen, (event.MessageName,))
        elif GetKeyState(HookConstants.VKeyToID('VK_CONTROL')) and event.KeyID == 67:
            #print "ctrl+C"
            self.logger.info('KeyboardEvent : ctrl+C ')
            thread.start_new_thread(self.doCaptureScreen, (event.MessageName,))
        elif GetKeyState(HookConstants.VKeyToID('VK_CONTROL')) and event.KeyID == 86:
            #print "ctrl+V"
            self.logger.info('KeyboardEvent : ctrl+V ')
            thread.start_new_thread(self.doCaptureScreen, (event.MessageName,))
        elif GetKeyState(HookConstants.VKeyToID('VK_CONTROL')) and event.KeyID == 83:
            #print "ctrl+S"
            self.logger.info('KeyboardEvent : ctrl+S ')
            thread.start_new_thread(self.doCaptureScreen, (event.MessageName,))
        elif GetKeyState(HookConstants.VKeyToID('VK_CONTROL')) and event.KeyID == 65:
            #print "ctrl+A"
            self.logger.info('KeyboardEvent : ctrl+A ')
        else:
            #print "event id " + str(event.KeyID)
            self.logger.info('KeyboardEvent : %s ',event.KeyID)
            thread.start_new_thread(self.doCaptureScreen, (event.MessageName,))
            time.sleep(0.001)
        return True

    # hook mouse
    def hookMouseAndKey(self):
        self.hm.SubscribeMouseLeftDown(self.left_down)
        self.hm.SubscribeMouseRightDown(self.right_down)
        self.hm.SubscribeMouseMiddleDown(self.middle_down)
#         self.hm.SubscribeMouseLeftUp(self.left_down)
#         self.hm.SubscribeMouseRightUp(self.right_down)
#         self.hm.SubscribeMouseMiddleUp(self.middle_down)
        self.hm.SubscribeMouseWheel(self.wheel)
        self.hm.HookMouse()
        
        #hook keyboard
        self.hm.KeyDown = self.onKeyboardEvent # watch for all keyboard events
        #self.hm.KeyUp = onKeyboardEvent
        self.hm.HookKeyboard()
        
        try:
            pythoncom.PumpMessages()
        except KeyboardInterrupt:
            pass

    def unHookMouseAndKey(self):    
        self.hm.UnhookMouse()
        self.hm.UnHookKeyboard()
        