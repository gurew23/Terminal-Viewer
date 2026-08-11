import pickle
import hashlib
import struct
import time
import sys
import zstandard as zstd
import os
from functools import lru_cache
import ctypes
_char = "▄"
pixel_cache_size = 8192
frame_cache_size = 2048
if sys.platform == "win32":
     if (sys.getwindowsversion().major >= 10 and sys.getwindowsversion().build >= 10586):
        h=ctypes.windll.kernel32.GetStdHandle(-11)
        m=ctypes.c_uint()
        ctypes.windll.kernel32.GetConsoleMode(h,ctypes.byref(m))
        if (m.value & 0x0004) == 0:
            print("Warning: the terminal no enable Visual Terminal, cannot load. Please enable Visual Terminal before use.")
    else:
        print("Waring: Your system does not support this module. Please upgrade your system to Windows 10 1511 or later to use this module.")
def myprint(text:str):
    sys.stdout.write(text)
    sys.stdout.flush()
@lru_cache(maxsize=pixel_cache_size)
def transform(ur:int,ug:int,ub:int,lr:int,lg:int,lb:int,char:str = _char) -> str:
    return "\033[38;2;{0};{1};{2};48;2;{3};{4};{5}m{6}".format(lr,lg,lb,ur,ug,ub,char)
def save(lst:tuple[tuple[tuple[int,int,int,int,int,int]]] | tuple[tuple[tuple[tuple[int,int,int,int,int,int]]]],path:str,level:int = 3):
    byte = zstd.compress(pickle.dumps(lst,5),level)
    len_byte = struct.pack("<I",len(byte))
    hash_byte = hashlib.sha512(len_byte + byte).digest()
    try:
        with open(path,"wb") as f:
            f.write(len_byte + byte + hash_byte)
    except Exception as e:
        raise e
def load(path:str) -> tuple[tuple[tuple[int,int,int,int,int,int]]] | tuple[tuple[tuple[tuple[int,int,int,int,int,int]]]]:
    try:
        with open(path,'rb') as f:
            head = f.read(4)
            if len(head) < 4:
                raise ValueError("File is empty or too small to be a valid file")
            len_byte = struct.unpack("<I",head)[0]
            byte = f.read(len_byte)
            if len(byte) < len_byte:
                raise ValueError("File is too small to be a valid file")
            if hashlib.sha512(head + byte).digest() == f.read():
                return pickle.loads(zstd.decompress(byte))
            else:
                raise Exception("Verification failed.")
    except Exception as e:
        raise ValueError(f"Err:{e}")
@lru_cache(maxsize=frame_cache_size)
def parse(lst:tuple[tuple[tuple[int,int,int,int,int,int]]],char:str = _char) -> str:
    code = ''
    try:
        for i in lst:
            for l in i:
                code += transform(*l,char)
            code += "\033[0m\n"
        return code.removesuffix("\n")
    except Exception as e:
        raise ValueError(f"Invalid data, Err:{e}")
def play_video(lst:tuple[tuple[tuple[tuple[int,int,int,int,int,int]]]],char:str = _char,fps:int = 30):
    try:
        s_time = 1 / fps
        myprint('\033[?1049h\033[?25l')
        for i in lst:
            myprint(parse(i,char))
            time.sleep(s_time)
            myprint("\033[H")
        myprint('\033[?1049l\033[?25h')
    except KeyboardInterrupt:
        return
    except Exception as e:
        raise ValueError(f"Invalid data, Err{e}")
    finally:
        myprint('\033[?1049l\033[?25h')
def show_photo(lst:tuple[tuple[tuple[int,int,int,int,int,int]]],char:str = _char):
    try:
        myprint(parse(lst,char))
    except Exception as e:
        raise ValueError(f"Invalid data, Err:{e}")
