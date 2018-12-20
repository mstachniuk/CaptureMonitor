import logging
import win32api
import win32gui
import win32con
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
        self.isRecord = False
        self.isPlay = False

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

    def createEventList(self,eventMessageName,keyTupe):
        if(self.isRecord == True):
            elapsedTime = time.time() - self.startTime
            #elapsedTime = 300
            self.startTime = time.time()
            self.identyfyMonitorParams()
            (x,y) = self.getCursorPosition()
            self.logger.info('Mouse event: %s position %s %s ' ,eventMessageName,x,y)
            argList = [x,y,eventMessageName,keyTupe,elapsedTime]
            self.eventList.append(argList)
            for x in self.eventList:
                print(x)
        return False

    def doCaptureScreen(self,eventMessageName,keyTupe):
        #if(self.isRecord == True):
        self.createEventList(eventMessageName,keyTupe)

        captureScreen = CaptureScreen.CaptureScreen()
        captureScreen.setCaptureParams(self.width,self.height,self.widthOffset,self.hightOffset)
        captureScreen.grabAHandle()
        captureScreen.createContext()
        captureScreen.createMemory()
        captureScreen.createBitmap()
        captureScreen.copyScreenToMemory()
        captureScreen.saveBitmapToFile()
        captureScreen.freeObjects()
#            return True
        return False


    def left_down(self,event):
        self.logger.info('Mouse event : %s ',event.MessageName)
        if(self.isRecord == True):
            thread.start_new_thread(self.doCaptureScreen, (event.MessageName,
                                                           ('0x01',),
                                                           ))
        return True

    def right_down(self,event):
        self.logger.info('Mouse event : %s ',event.MessageName)
        if(self.isRecord == True):
            thread.start_new_thread(self.doCaptureScreen, (event.MessageName,
                                                           ('0x02',),
                                                           ))
        return True

    def middle_down(self,event):
        self.logger.info('Mouse event : %s ',event.MessageName)
        if(self.isRecord == True):
            thread.start_new_thread(self.doCaptureScreen, (event.MessageName,
                                                           ('0x04',),
                                                           ))
        return True

    def wheel(self,event):
        self.logger.info('Mouse event : %s ',event.MessageName)
        if(self.isRecord == True):
        #thread.start_new_thread(self.doCaptureScreen, (event.MessageName,))
            thread.start_new_thread(self.createEventList, (event.MessageName,
                                                           (str(event.Wheel),),
                                                           ))
        return True

    def onKeyboardEvent(self,event):
        #print chr(event.Ascii)WM_KEYUPWM_KEYUPWM_KEYUPWM_KEYUP
        if GetKeyState(HookConstants.VKeyToID('VK_MENU')) and event.KeyID == int("0x56", 16) :
            if(self.isRecord == True):
                if(event.MessageName == 'key sys down'):
                    # key sys down when ALT+V pressed. Key down if single key
                    self.isRecord = False
                    self.logger.info('Capture : STOP Recording ')
            else:
                if(self.isPlay == False):
                    if(event.MessageName == 'key sys down'):
                        # key sys down when ALT+V pressed. Key down if single key
                        self.isRecord = True
                        self.logger.info('Capture : START Recording ')
                        self.startTime = time.time()
                else:
                    self.logger.info('If you want record event, please first stop playback ')

        elif GetKeyState(HookConstants.VKeyToID('VK_MENU')) and event.KeyID == int("0x42", 16) :
            if(self.isPlay == True):
                if(event.MessageName == 'key sys down'):
                    # key sys down when ALT+V pressed. Key down if single key
                    self.isPlay = False
                    self.logger.info('Playback : STOP playback ')
            else:
                if(self.isRecord == False):
                    if(event.MessageName == 'key sys down'):
                        # key sys down when ALT+V pressed. Key down if single key
                        self.isPlay = True
                        self.logger.info('Playback : PLAY playback ')
                        thread.start_new_thread(self.playEventList, ())
                else:
                    self.logger.info('If you want play event, please first stop recording ')

        elif GetKeyState(HookConstants.VKeyToID('VK_LSHIFT')) and event.KeyID == HookConstants.VKeyToID('VK_SNAPSHOT'):
            #print "Shitf+Print screen"
            self.logger.info('KeyboardEvent : Shitf+Print screen ')
            if(self.isRecord == True):
                thread.start_new_thread(self.doCaptureScreen, (event.MessageName,
                                                               ('0xa0',hex(event.KeyID),),
                                                               ))

        elif GetKeyState(HookConstants.VKeyToID('VK_CONTROL')) and event.KeyID == int("0x43", 16) :
            #print "ctrl+C"
            self.logger.info('KeyboardEvent : ctrl+C ')
            if(self.isRecord == True):
                thread.start_new_thread(self.doCaptureScreen, (event.MessageName,
                                                               ('0xa2',hex(event.KeyID),),
                                                               ))

        elif GetKeyState(HookConstants.VKeyToID('VK_CONTROL')) and event.KeyID == int("0x56", 16) :
            #print "ctrl+V"
            self.logger.info('KeyboardEvent : ctrl+V ')
            if(self.isRecord == True):
                thread.start_new_thread(self.doCaptureScreen, (event.MessageName,
                                                               ('0xa2',hex(event.KeyID),),
                                                               ))

        elif GetKeyState(HookConstants.VKeyToID('VK_CONTROL')) and event.KeyID == int("0x53", 16) :
            #print "ctrl+S"
            self.logger.info('KeyboardEvent : ctrl+S ')
            if(self.isRecord == True):
                thread.start_new_thread(self.doCaptureScreen, (event.MessageName,
                                                               ('0xa2',hex(event.KeyID),),
                                                               ))

        elif GetKeyState(HookConstants.VKeyToID('VK_CONTROL')) and event.KeyID == int("0x41", 16) :
            #print "ctrl+A"
            self.logger.info('KeyboardEvent : ctrl+A ')
            if(self.isRecord == True):
                thread.start_new_thread(self.doCaptureScreen, (event.MessageName,
                                                               ('0xa2',hex(event.KeyID),),
                                                               ))

        elif (event.KeyID == int("0xa4", 16) or
              event.KeyID == int("0x56", 16) or
              event.KeyID == int("0x42", 16)
              #event.KeyID == int("0x4e", 16)
              ):
                self.logger.info('DISALLOWED : %s ',hex(event.KeyID))
        # Keys
        else:
                self.logger.info('KeyboardEvent : %s %s ',event.MessageName, hex(event.KeyID))
                if(self.isRecord == True):
                    if(event.MessageName == 'key down'):
                        thread.start_new_thread(self.doCaptureScreen, (event.MessageName,
                                                                   (hex(event.KeyID),),
                                                                   ))
                    else:
                        thread.start_new_thread(self.createEventList, (event.MessageName,
                                                                   (hex(event.KeyID),),
                                                                   ))
        return True

    # hook mouse
    def hookMouseAndKey(self):
        self.hm.SubscribeMouseLeftDown(self.left_down)
        self.hm.SubscribeMouseRightDown(self.right_down)
        self.hm.SubscribeMouseMiddleDown(self.middle_down)
        self.hm.SubscribeMouseLeftUp(self.left_down)
        self.hm.SubscribeMouseRightUp(self.right_down)
        self.hm.SubscribeMouseMiddleUp(self.middle_down)
        self.hm.SubscribeMouseWheel(self.wheel)
        self.hm.HookMouse()

        #hook keyboard
        self.hm.KeyDown = self.onKeyboardEvent # watch for all keyboard events
        self.hm.KeyUp = self.onKeyboardEvent
        self.hm.HookKeyboard()

        try:
            pythoncom.PumpMessages()
        except KeyboardInterrupt:
            pass

    def createKeyEvent(self,key):
            win32api.keybd_event(int(key, 16), 0,0,0)
            time.sleep(.05)
            win32api.keybd_event(int(key, 16),0 ,win32con.KEYEVENTF_KEYUP ,0)

    def playEventList(self):
        while self.isPlay:
            for itm in self.eventList:
                print itm[4]
                time.sleep(itm[4]) #first wait elapsed time then press
                #self.createKeyEvent(x[3])
                if itm[2] == 'key down':
                    if len(itm[3]) > 1:
                        win32api.keybd_event(int(itm[3][0], 16), 0, win32con.KEYEVENTF_EXTENDEDKEY, 0);
                        win32api.keybd_event(int(itm[3][1], 16), 0, win32con.KEYEVENTF_EXTENDEDKEY, 0);
                    else:
                        win32api.keybd_event(int(itm[3][0], 16), 0,0,0)
                if itm[2] == 'key up':
                    if len(itm[3]) > 1:
                        win32api.keybd_event(int(itm[3][0], 16), 0, win32con.KEYEVENTF_KEYUP, 0);
                        win32api.keybd_event(int(itm[3][1], 16), 0, win32con.KEYEVENTF_KEYUP, 0);
                    else:
                        win32api.keybd_event(int(itm[3][0], 16), 0,win32con.KEYEVENTF_KEYUP,0)
                if itm[2] == 'mouse left down':
                        win32api.SetCursorPos((itm[0],itm[1]))
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,itm[0],itm[1],0,0)
                if itm[2] == 'mouse left up':
                        win32api.SetCursorPos((itm[0],itm[1]))
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,itm[0],itm[1],0,0)
                if itm[2] == 'mouse right down':
                        win32api.SetCursorPos((itm[0],itm[1]))
                        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN,itm[0],itm[1],0,0)
                if itm[2] == 'mouse right up':
                        win32api.SetCursorPos((itm[0],itm[1]))
                        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP,itm[0],itm[1],0,0)
                if itm[2] == 'mouse wheel':
                        win32api.SetCursorPos((itm[0],itm[1]))
                        win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, itm[0],itm[1], int(itm[3][0]), 0)
                if(self.isPlay == False):
                    break


    def unHookMouseAndKey(self):
        self.hm.UnhookMouse()
        self.hm.UnHookKeyboard()
