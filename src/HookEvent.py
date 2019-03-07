import logging
import win32api
import win32gui
import win32con
import pythoncom
import pyHook
from pyHook import GetKeyState, HookConstants
import CaptureScreen
import EventExecutor
import thread
import time
import string

module_logger = logging.getLogger('application.HookEvent')

Event_type = {
    "mouse move" : 0x01,
    "key down" : 0x02,
    "key up" : 0x03,
    "key sys down" : 0x04,
    "key sys up" : 0x05,
    "mouse left down" : 0x06,
    "mouse left up" : 0x07,
    "mouse right down" : 0x08,
    "mouse right up" : 0x08,
    "mouse wheel" : 0x10,
    }

class HookEvent(object):

    def __init__ (self):
        self.logger = logging.getLogger('application.HookEvent')
        self.logger.debug('creating an instance of HookEvent')
        self.hm = pyHook.HookManager()
        self.eventList = []
        self.isRecord = False
        self.isPlay = False

        self.enum = CaptureScreen.CaptureScreen()
        self.logger.debug('Numer of display devices: %s ' ,str(self.enum.enumDisplayDevices()))
        self.logger.debug('Numer of physical monitors: %s ' ,str(self.enum.enumVisibleMonitors()))

    def getCursorPosition(self):
        self.flags, self.handle, (x,y) = win32gui.GetCursorInfo()
        return (x,y)

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

    def createEventList(self,eventMessageName,key1,key2):
        if(self.isRecord == True):
            elapsedTime = time.time() - self.startTime
            
            self.startTime = time.time()
            self.identyfyMonitorParams()
            
            (x,y) = self.getCursorPosition()
            self.logger.debug('Mouse event: %s position %s %s ' ,eventMessageName,x,y)
            
            argList = [x,y,eventMessageName,key1,key2,elapsedTime]
            self.eventList.append(argList)
            self.logger.info('Event %s ', argList )
            
        return False

    def doCaptureScreen(self):
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

    def move(self,event):
        self.logger.info('Mouse event : %s ',event.MessageName)
        if(self.isRecord == True):
            self.createEventList(Event_type[event.MessageName],
                                 None,
                                 None)
        return True
        
    def left_down(self,event):
        self.logger.info('Mouse event : %s ',event.MessageName)
        if(self.isRecord == True):
            self.createEventList(Event_type[event.MessageName],
                                 None,
                                 '0x01')
            thread.start_new_thread(self.doCaptureScreen, ())

        return True

    def right_down(self,event):
        self.logger.info('Mouse event : %s ',event.MessageName)
        if(self.isRecord == True):
            self.createEventList(Event_type[event.MessageName],
                                 None,
                                 '0x02')
            thread.start_new_thread(self.doCaptureScreen, ())

        return True

    def middle_down(self,event):
        self.logger.info('Mouse event : %s ',event.MessageName)
        if(self.isRecord == True):
            self.createEventList(Event_type[event.MessageName],
                                 None,
                                 '0x04')
            thread.start_new_thread(self.doCaptureScreen, ())
            
        return True

    def wheel(self,event):
        self.logger.info('Mouse event : %s ',event.MessageName)
        if(self.isRecord == True):
            self.createEventList(Event_type[event.MessageName],
                                 None,
                                 str(event.Wheel))

        return True

    def onKeyboardEvent(self,event):
        # "ALT+V record event "
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
        
        # "ALT+B play list"
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
                    
        # "ALT+N clear recording list"
        elif GetKeyState(HookConstants.VKeyToID('VK_MENU')) and  event.KeyID == int("0x4e", 16) :
            if(self.isRecord == False and self.isPlay == False ):
                del self.eventList[:]
                self.logger.info('Event List : clear ')
            else:
                self.logger.info('If you want clear list, please first stop playback and capture ')
                
        elif GetKeyState(HookConstants.VKeyToID('VK_LSHIFT')) and event.KeyID == HookConstants.VKeyToID('VK_SNAPSHOT'):
            #print "Shitf+Print screen"
            self.logger.info('KeyboardEvent : Shitf+Print screen ')
            if(self.isRecord == True):
                print event.MessageName
                self.createEventList(Event_type[event.MessageName],
                                     '0xa0',
                                     hex(event.KeyID))
                
        # "CTRL+key"
        elif GetKeyState(HookConstants.VKeyToID('VK_CONTROL')):

            #self.logger.info('KeyboardEvent CTRL: %s %s ',event.MessageName, hex(event.KeyID))
            if(self.isRecord == True):
                if event.Key in string.ascii_uppercase:
                    # if ctrl pressed and The uppercase letters 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                    self.createEventList(Event_type[event.MessageName],
                                     '0xa2',
                                     hex(event.KeyID))
                    thread.start_new_thread(self.doCaptureScreen, ())
                else:
                    self.createEventList(Event_type[event.MessageName],
                                     None,
                                     hex(event.KeyID))
                    thread.start_new_thread(self.doCaptureScreen, ())
                    

        # Keys
        else:
                #self.logger.info('KeyboardEvent : %s %s ',event.MessageName, hex(event.KeyID))
                if(self.isRecord == True):
                    if(event.MessageName == 'key down'):
                        self.createEventList(Event_type[event.MessageName],
                                             None,
                                             hex(event.KeyID))
                        thread.start_new_thread(self.doCaptureScreen, ())
                    else:
                        self.createEventList(Event_type[event.MessageName],
                                             None,
                                             hex(event.KeyID))
        return True
    
    def OnMouseEvent(self,event):
        print 'MessageName:',event.MessageName
        print 'Message:',event.Message
        print 'Time:',event.Time
        print 'Window:',event.Window
        print 'WindowName:',event.WindowName
        print 'Position:',event.Position
        print 'Wheel:',event.Wheel
        print 'Injected:',event.Injected
        print '---'
        return True
    
        # hook mouse
    def hookMouseAndKey(self):
#         self.hm.SubscribeMouseMove(self.move)
#         self.hm.SubscribeMouseLeftDown(self.left_down)
#         self.hm.SubscribeMouseRightDown(self.right_down)
#         self.hm.SubscribeMouseMiddleDown(self.middle_down)
#         self.hm.SubscribeMouseLeftUp(self.left_down)
#         self.hm.SubscribeMouseRightUp(self.right_down)
#         self.hm.SubscribeMouseMiddleUp(self.middle_down)
#         self.hm.SubscribeMouseWheel(self.wheel)
#         self.hm.MouseAll = self.OnMouseEvent
        self.hm.HookMouse()

        #hook keyboard
        self.hm.KeyDown = self.onKeyboardEvent # watch for all keyboard events
        self.hm.KeyUp = self.onKeyboardEvent
        self.hm.HookKeyboard()

        try:
            pythoncom.PumpMessages()
        except KeyboardInterrupt:
            pass

#     def createKeyEvent(self,key):
#             win32api.keybd_event(int(key, 16), 0,0,0)
#             time.sleep(.05)
#             win32api.keybd_event(int(key, 16),0 ,win32con.KEYEVENTF_KEYUP ,0)

    def playEventList(self):
        #[xpoz, ypoz, type, key1, key2 , delay
        executor = EventExecutor.EventExecutor()
        
        while self.isPlay:
            for itm in self.eventList:
                self.logger.info('Play event delay : %s ',itm[4])
                time.sleep(itm[5]) #first wait elapsed time then press
                if itm[2] == Event_type['mouse move']:
                    #Pass the coordinates (x,y) as a tuple:
                    #win32api.SetCursorPos((itm[0],itm[1]))
                    executor.doMouseMove(itm[0],itm[1])
                    
                if (itm[2] == Event_type['key down']) or (itm[2] == Event_type['key sys down']) :
                    if itm[3] == None:
                        executor.doExtendedKeyDown(int(itm[4], 16))
#                         win32api.keybd_event(int(itm[3][0], 16), 0, win32con.KEYEVENTF_EXTENDEDKEY, 0);
#                         win32api.keybd_event(int(itm[3][1], 16), 0, win32con.KEYEVENTF_EXTENDEDKEY, 0);
                    else:
                        executor.doExtendedKeyDown(int(itm[3], 16))
                        executor.doExtendedKeyDown(int(itm[4], 16))
#                         win32api.keybd_event(int(itm[3][0], 16), 0,0,0)
                if (itm[2] == Event_type['key up']) or (itm[2] == Event_type['key sys up']) :
                    if itm[3] == None:
                        executor.doExtendedKeyUp(int(itm[4], 16))
#                         win32api.keybd_event(int(itm[3][0], 16), 0, win32con.KEYEVENTF_KEYUP, 0);
#                         win32api.keybd_event(int(itm[3][1], 16), 0, win32con.KEYEVENTF_KEYUP, 0);
                    else:
                        executor.doExtendedKeyUp(int(itm[3], 16))
                        executor.doExtendedKeyUp(int(itm[4], 16))
#                         win32api.keybd_event(int(itm[3][0], 16), 0,win32con.KEYEVENTF_KEYUP,0)
                if itm[2] == Event_type['mouse left down']:
                    executor.doLeftMouseDonw(itm[0], itm[1])
#                         win32api.SetCursorPos((itm[0],itm[1]))
#                         win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,itm[0],itm[1],0,0)
                if itm[2] == Event_type['mouse left up']:
                    executor.doLeftMouseUp(itm[0], itm[1])
#                         win32api.SetCursorPos((itm[0],itm[1]))
#                         win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,itm[0],itm[1],0,0)
                if itm[2] == Event_type['mouse right down']:
                    executor.doRightMouseDonw(itm[0], itm[1])
#                         win32api.SetCursorPos((itm[0],itm[1]))
#                         win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN,itm[0],itm[1],0,0)
                if itm[2] == Event_type['mouse right up']:
                    executor.doRightMouseUp(itm[0], itm[1])
#                         win32api.SetCursorPos((itm[0],itm[1]))
#                         win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP,itm[0],itm[1],0,0)
                if itm[2] == Event_type['mouse wheel']:
                    executor.doMouseWheel(itm[0], itm[1], itm[4])
#                         win32api.SetCursorPos((itm[0],itm[1]))
#                         win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, itm[0],itm[1], win32con.WHEEL_DELTA *int(itm[3][0]), 0)
                if(self.isPlay == False):
                    break

        
    def unHookMouseAndKey(self):
        self.hm.UnhookMouse()
        self.hm.UnHookKeyboard()
