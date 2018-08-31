import win32gui
import win32ui
import win32con
import win32api
import datetime
import re

 
class CaptureScreen():

    def getCurentTimeDateToString(self):
        sString = str(datetime.datetime.now())
        sString = re.sub(":","",sString)
        return sString
         
    # this function gets only visible monitors (not  virtual)  
    def enumVisibleMonitors(self):
        i = 0
        try:
            i = win32api.GetSystemMetrics(win32con.SM_CMONITORS);
        except:
            print "error while try get visible Monitors. "
        return i

    # this function gets displayDeviceName    
    def enumDisplayDevices(self):
        i = 0
        while True:
            try:
                device = win32api.EnumDisplayDevices(None,i);
                print("[%d] %s (%s)"%(i,device.DeviceString,device.DeviceName));
                i +=1;
            except:
                break;
            return i
    
    def grabAHandle(self):
        self.hdesktop = win32gui.GetDesktopWindow()
      
    def determineSizeMonitors(self):
        self.width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
        #SM_CXVIRTUALSCREEN in X
        #The width of the virtual screen, in pixels. 
        #The virtual screen is the bounding rectangle of all display monitors.
        #The SM_XVIRTUALSCREEN metric is the coordinates for the left side of the virtual screen.
        self.height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
        #SM_CYVIRTUALSCREEN
        #The height of the virtual screen, in pixels. 
        self.left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
        #SM_XVIRTUALSCREEN
        #The coordinates for the left side of the virtual screen.
        self.top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
        #SM_YVIRTUALSCREEN
        #The coordinates for the top of the virtual screen.
     
    def createContext(self): 
        #A device context is a structure that defines a set of graphic objects and their associated attributes
        self.desktop_dc = win32gui.GetWindowDC(self.hdesktop)
        # return value is a handle to a device context for the specified window.
        self.img_dc = win32ui.CreateDCFromHandle(self.desktop_dc)
        
    def createMemory(self):
        # CreateCompatibleDC function creates a memory device context (DC) compatible with the specified device.
        # return value is the handle to a memory DC.
        self.mem_dc = self.img_dc.CreateCompatibleDC()
     
    def createBitmap(self,width,height):
        self.screenshot = win32ui.CreateBitmap()
        self.screenshot.CreateCompatibleBitmap(self.img_dc, width, height)
        #/self.screenshot.CreateCompatibleBitmap(self.img_dc, 500, 500)
        self.mem_dc.SelectObject(self.screenshot)
     
     
    def copyScreenToMemory(self,width, height, srcUpLeftX,srcUpLeftY):
        self.mem_dc.BitBlt((0, 0), (width,height), self.img_dc, (srcUpLeftX, srcUpLeftY),win32con.SRCCOPY)
        print "start X pixel:" + str (srcUpLeftX)
        print "start Y pixel:" + str (srcUpLeftY)
        print "width:" + str (width)
        print "height:" + str (height)
        #self.mem_dc.StretchBlt((0, 0), (self.width, self.height), self.img_dc, (0, 0), (self.width, self.height), win32con.SRCCOPY)

        #bmpinfo = self.screenshot.GetInfo()
        #bmpInt = self.screenshot.GetBitmapBits(False) 
        #print bmpInt
        #self.mem_dc.BitBlt((0, 0), (500, 500), self.img_dc, (250, 250),win32con.SRCCOPY)
     
    def saveBitmapToFile(self):
        self.screenshot.SaveBitmapFile(self.mem_dc, self.getCurentTimeDateToString()+".jpg")

    
    def freeObjects(self):
        self.mem_dc.DeleteDC()
        win32gui.DeleteObject(self.screenshot.GetHandle())

    
