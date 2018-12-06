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
        #self.startTime = time.time()
        self.recordStatus = False
        
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
        
    def createEventList(self,eventMessageName,keyCode):
        if(self.recordStatus == True):
            elapsedTime = time.time() - self.startTime    
            self.startTime = time.time()
            self.identyfyMonitorParams()
            (x,y) = self.getCursorPosition()
            self.logger.info('Mouse event: %s position %s %s ' ,eventMessageName,x,y)
            argList = [x,y,eventMessageName,(keyCode,),elapsedTime]
            self.eventList.append(argList)
            for x in self.eventList:
                print(x)
        return False    
        
    def doCaptureScreen(self,eventMessageName,keyCode):
        if(self.recordStatus == True):
            self.createEventList(eventMessageName,keyCode)
            
            captureScreen = CaptureScreen.CaptureScreen()
            captureScreen.setCaptureParams(self.width,self.height,self.widthOffset,self.hightOffset)
            captureScreen.grabAHandle()
            captureScreen.createContext()
            captureScreen.createMemory()
            captureScreen.createBitmap()
            captureScreen.copyScreenToMemory()
            captureScreen.saveBitmapToFile()
            captureScreen.freeObjects()
        return False
    

    def left_down(self,event):
        thread.start_new_thread(self.doCaptureScreen, (event.MessageName,('VK_LBUTTON')))
        return True 
    
    def right_down(self,event):
        thread.start_new_thread(self.doCaptureScreen, (event.MessageName,('VK_RBUTTON',)))
        return True    
    
    def middle_down(self,event):
        thread.start_new_thread(self.doCaptureScreen, (event.MessageName,('VK_MBUTTON',)))
        return True
         
    def wheel(self,event):
        #thread.start_new_thread(self.doCaptureScreen, (event.MessageName,))
        thread.start_new_thread(self.createEventList, (event.MessageName,(str(event.Wheel))))
        return True
    
    def onKeyboardEvent(self,event):
        #print chr(event.Ascii)WM_KEYUPWM_KEYUPWM_KEYUPWM_KEYUP
        if GetKeyState(HookConstants.VKeyToID('VK_MENU')) and event.KeyID == 68 :
            #print "ALT+D+1"
            if(self.recordStatus == True):
                self.recordStatus = False
                self.logger.info('Capture : STOP Recording ')
            else:
                self.recordStatus = True
                self.logger.info('Capture : START Recording ')
                self.startTime = time.time()
        elif GetKeyState(HookConstants.VKeyToID('VK_LSHIFT')) and event.KeyID == HookConstants.VKeyToID('VK_SNAPSHOT'):
            #print "Shitf+Print screen"
            self.logger.info('KeyboardEvent : Shitf+Print screen ')
            thread.start_new_thread(self.doCaptureScreen, (event.MessageName,('VK_LSHIFT','VK_SNAPSHOT',)))
        elif GetKeyState(HookConstants.VKeyToID('VK_CONTROL')) and event.KeyID == 67:
            #print "ctrl+C"
            self.logger.info('KeyboardEvent : ctrl+C ')
            thread.start_new_thread(self.doCaptureScreen, (event.MessageName,('VK_CONTROL','67',)))
        elif GetKeyState(HookConstants.VKeyToID('VK_CONTROL')) and event.KeyID == 86:
            #print "ctrl+V"
            self.logger.info('KeyboardEvent : ctrl+V ')
            thread.start_new_thread(self.doCaptureScreen, (event.MessageName,('VK_CONTROL','86',)))
        elif GetKeyState(HookConstants.VKeyToID('VK_CONTROL')) and event.KeyID == 83:
            #print "ctrl+S"
            self.logger.info('KeyboardEvent : ctrl+S ')
            thread.start_new_thread(self.doCaptureScreen, (event.MessageName,('VK_CONTROL','83',)))
        elif GetKeyState(HookConstants.VKeyToID('VK_CONTROL')) and event.KeyID == 65:
            #print "ctrl+A"
            self.logger.info('KeyboardEvent : ctrl+A ')
            thread.start_new_thread(self.doCaptureScreen, (event.MessageName,('VK_CONTROL','65',)))
        else:
            #print "event id " + str(event.KeyID)
            self.logger.info('KeyboardEvent : %s ',event.KeyID)
            thread.start_new_thread(self.doCaptureScreen, (event.MessageName,str(event.KeyID)))
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
        