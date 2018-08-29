import HookEvent
import CaptureScreen
import win32api
import win32con
import win32gui
import time


if __name__ == '__main__':
    
    hook = HookEvent.HookEvent()
    hook.HookMouseAndKey()

