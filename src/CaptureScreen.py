import logging
import win32gui
import win32ui
import win32con
import win32api
import datetime
import re
from PIL import Image, ImageDraw

module_logger = logging.getLogger('application.CaptureScreen')


def get_current_time_date_to_string():
    s_string = str(datetime.datetime.now())
    s_string = re.sub(":", "", s_string)
    return s_string


class CaptureScreen(object):

    def __init__(self):
        self.logger = logging.getLogger('application.CaptureScreen')
        self.logger.debug('creating an instance of CaptureScreen')
        self.width = 0
        self.height = 0
        self.src_up_left_x = 0
        self.src_up_left_y = 0
        self.file_name = ""
        self.width_offset = 0
        self.height_offset = 0
        self.x_draw = 0
        self.y_draw = 0
        self.h_desktop = None
        self.desktop_dc = None
        self.img_dc = None
        self.mem_dc = None
        self.screen = None
        self.rgba_image = None
        self.image = None
        self.ellipse_image = None
        self.out = None
        # radius of the circle for the mouse position
        self.radius = 10

    def set_capture_params(self, width, height, width_offset, height_offset):

        self.file_name = get_current_time_date_to_string() + ".png"
        self.width = width
        self.height = height
        self.width_offset = width_offset
        self.height_offset = height_offset
        self.logger.debug('Setting Capture Params %s %s and offset %s %s ',
                          self.width,
                          self.height,
                          self.width_offset,
                          self.height_offset)

    def set_cursor_draw(self, x_poz, y_poz):
        # x position on the screenShoot
        # ex:(x=80) = global mouse cursor pos(2000) - offset from the previous monitor(1920) from the left side.
        self.x_draw = x_poz - self.width_offset
        self.y_draw = y_poz - self.height_offset

    # this function gets only visible monitors (not  virtual)
    def get_visible_monitors(self, ):
        i = 0
        try:
            i = win32api.GetSystemMetrics(win32con.SM_CMONITORS)
        except Exception as ex:
            self.logger.DEBUG('eception: %s', ex.message)
        return i

    # this function gets displayDeviceName   
    def enum_display_devices(self):
        i = 0
        while True:
            try:
                device = win32api.EnumDisplayDevices(None, i)
                self.logger.DEBUG('Count [%d] Device: %s DeviceName(%s) ', i, device.DeviceString, device.DeviceName)
                i += 1
            except Exception as ex:
                self.logger.info('exception: %s', ex.message)
                break
            return i

    def grab_handle(self):
        self.h_desktop = win32gui.GetDesktopWindow()
        return True

    def create_context(self):
        # A device context is a structure that defines a set of graphic objects and their associated attributes
        self.desktop_dc = win32gui.GetWindowDC(self.h_desktop)
        # return value is a handle to a device context for the specified window.
        self.img_dc = win32ui.CreateDCFromHandle(self.desktop_dc)

    def create_memory(self):
        # CreateCompatibleDC function creates a memory device context (DC) compatible with the specified device.
        # return value is the handle to a memory DC.
        self.mem_dc = self.img_dc.CreateCompatibleDC()

    def create_bitmap(self):
        self.screen = win32ui.CreateBitmap()
        self.screen.CreateCompatibleBitmap(self.img_dc, self.width, self.height)
        # self.screen.CreateCompatibleBitmap(self.img_dc, 640,480)
        self.mem_dc.SelectObject(self.screen)

    def copy_screen_to_memory(self, ):
        self.mem_dc.BitBlt(
            (0, 0),
            (self.width, self.height),
            self.img_dc,
            (self.width_offset,
             self.height_offset),
            win32con.SRCCOPY)

        # self.mem_dc.StretchBlt( (0, 0), (640,480), self.img_dc, (self.widthOffset, self.hightOffset),
        # (self.width,self.height), win32con.SRCCOPY)

        bmp_info = self.screen.GetInfo()
        bmp_int = self.screen.GetBitmapBits(True)

        self.image = Image.frombuffer(
            'RGB',
            (bmp_info['bmWidth'], bmp_info['bmHeight']),
            bmp_int, 'raw', 'BGRX', 0, 1)
        # convert BGRX to RGBA
        self.rgba_image = self.image.convert('RGBA')

        # create new Image  RGBA
        self.ellipse_image = Image.new('RGBA', self.image.size, (255, 255, 255, 0))

        # draw ellipse there
        d = ImageDraw.Draw(self.ellipse_image)
        d.ellipse((self.x_draw - self.radius,
                   self.y_draw - self.radius,
                   self.x_draw + self.radius,
                   self.y_draw + self.radius),
                  fill=(255, 0, 0, 128))

        # blend alpha screen shot with cursor point
        self.out = Image.alpha_composite(self.rgba_image, self.ellipse_image)

        return True

    def save_bitmap_to_file(self, ):
        # self.path = os.getcwd()
        # self.screen.SaveBitmapFile(self.mem_dc, "D:\\Capture\\"+ str(self.fileName))
        self.out.save(str(self.file_name), 'PNG')

    def free_objects(self):
        self.mem_dc.DeleteDC()
        win32gui.DeleteObject(self.screen.GetHandle())
        self.image.close()
        self.rgba_image.close()
        self.ellipse_image.close()
