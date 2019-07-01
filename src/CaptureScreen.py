import logging
import win32gui
import win32ui
import win32con
import win32api
import datetime
import re
import os
from PIL import Image,ImageDraw

module_logger = logging.getLogger('application.CaptureScreen')
 
class CaptureScreen(object):
    
    def __init__(self):
        self.logger = logging.getLogger('application.CaptureScreen')
        self.logger.debug('creating an instance of CaptureScreen')
        self.width = 0
        self.height = 0
        self.srcUpLeftX = 0
        self.srcUpLeftY = 0
        self.fileName = ""
        #radius of the circle for the mouse position
        self.radius =  10

    def getCurentTimeDateToString(self):
        sString = str(datetime.datetime.now())
        sString = re.sub(":","",sString)
        return sString
    
    def setCaptureParams(self,width,height,widthOffset,hightOffset):
        
        self.fileName = self.getCurentTimeDateToString()+".png"
        self.width = width
        self.height = height
        self.widthOffset = widthOffset
        self.hightOffset = hightOffset
        self.logger.debug('Setting Capture Params %s %s and offset %s %s ' ,self.width,self.height,self.widthOffset,self.hightOffset )
             
    def setCursorDraw(self,xPoz,yPoz):
        # x position on the screenShoot ex:(x=80) = global mouse cursor pos(2000) - offset from the previous monitor(1920) from the left side.
        self.xDraw = xPoz - self.widthOffset
        self.yDraw = yPoz - self.hightOffset
        
    
    # this function gets only visible monitors (not  virtual)  
    def enumVisibleMonitors(self):
        i = 0
        try:
            i = win32api.GetSystemMetrics(win32con.SM_CMONITORS);
        except:
            self.logger.error('Error while try get visible Monitors' )
        return i

    # this function gets displayDeviceName   
    def enumDisplayDevices(self):
        i = 0
        while True:
            try:
                device = win32api.EnumDisplayDevices(None,i);
                self.logger.debug('Count [%d] Device: %s DeviceName(%s) ' ,i,device.DeviceString,device.DeviceName )
                i +=1;
            except:
                break;
            return i
    
    def grabAHandle(self):
        self.hdesktop = win32gui.GetDesktopWindow()
        return True
     
    def createContext(self): 
        #A device context is a structure that defines a set of graphic objects and their associated attributes
        self.desktop_dc = win32gui.GetWindowDC(self.hdesktop)
        # return value is a handle to a device context for the specified window.
        self.img_dc = win32ui.CreateDCFromHandle(self.desktop_dc)
        
    def createMemory(self):
        # CreateCompatibleDC function creates a memory device context (DC) compatible with the specified device.
        # return value is the handle to a memory DC.
        self.mem_dc = self.img_dc.CreateCompatibleDC()
     
    def createBitmap(self):
        self.screenshot = win32ui.CreateBitmap()
        self.screenshot.CreateCompatibleBitmap(self.img_dc, self.width, self.height)
        #self.screenshot.CreateCompatibleBitmap(self.img_dc, 640,480)
        self.mem_dc.SelectObject(self.screenshot)
     
     
    def copyScreenToMemory(self,):
        self.mem_dc.BitBlt(
                        (0, 0),
                        (self.width,self.height),
                        self.img_dc,
                        (self.widthOffset,
                        self.hightOffset),
                        win32con.SRCCOPY)
        
        #self.mem_dc.StretchBlt( (0, 0), (640,480), self.img_dc, (self.widthOffset, self.hightOffset), (self.width,self.height), win32con.SRCCOPY)

        self.bmpinfo = self.screenshot.GetInfo()
        self.bmpInt = self.screenshot.GetBitmapBits(True)

        self.image = Image.frombuffer(
                                    'RGB',
                                    (self.bmpinfo['bmWidth'], self.bmpinfo['bmHeight']),
                                    self.bmpInt, 'raw', 'BGRX', 0, 1)
        # convert BGRX to RGBA
        self.rgbaImage = self.image.convert('RGBA')
        
        #create new Image  RGBA
#         self.ellipseImage = Image.new('RGBA', self.image.size, (255,255,255,0))
        
        #draw ellipse there  
        d = ImageDraw.Draw(self.rgbaImage)
        d.ellipse((self.xDraw-self.radius, self.yDraw-self.radius, self.xDraw+self.radius, self.yDraw+self.radius), fill=(255,0,0,128))
        
        
        #blend alpha screenshot with cursor point
#         self.out = Image.alpha_composite(self.rgbaImage, self.ellipseImage)

        return True
    
    def saveBitmapToFile(self,):
        self.path = os.getcwd()
        #self.screenshot.SaveBitmapFile(self.mem_dc, "D:\\Capture\\"+ str(self.fileName))
        self.rgbaImage.save(str(self.fileName),'PNG')
   
    
    def freeObjects(self):
        self.mem_dc.DeleteDC()
        win32gui.DeleteObject(self.screenshot.GetHandle())
        self.image.close()
        self.rgbaImage.close()
#         self.ellipseImage.close()
        
