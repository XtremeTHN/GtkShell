from ctypes import cdll, byref, create_string_buffer
import sys

def set_proc_name(newname):
    libc = cdll.LoadLibrary('libc.so.6')
    buff = create_string_buffer(len(newname)+1)
    buff.value = newname.encode("utf-8")
    libc.prctl(15, byref(buff), 0, 0, 0)

def get_proc_name():
    libc = cdll.LoadLibrary('libc.so.6')
    buff = create_string_buffer(128)
    # 16 == PR_GET_NAME from <linux/prctl.h>
    libc.prctl(16, byref(buff), 0, 0, 0)
    return buff.value
