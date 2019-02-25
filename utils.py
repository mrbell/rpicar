import struct
import numpy as np

def int_to_bytes(the_int):
    return struct.pack('>I', the_int)

def bytes_to_int(the_bytes):
    return struct.unpack('>I', the_bytes)[0]

def array_to_bytes(the_array):
    return the_array.to_bytes()

def bytes_to_array(the_bytes, dtype='int32'):
    return np.frombuffer(the_bytes, dtype=dtype)
