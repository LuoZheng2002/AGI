from ExceptionAndDebug.code_visualization import *
from Kernel.KernelFuncs.Executers.method_translator import encode_method
from temporary import method_3
try:
    '''print(method_1)
    result = encode_method(method_1)
    # print(result)
    print(decode_method(result))
    print(method_1 == decode_method(encode_method(method_1)))'''
    print(method_3)
    a = encode_method(method_3)
    bytecode = bytes()
    for integer in a:
        bytecode += integer.to_bytes(4, byteorder='little', signed=True)
    print(a)
    print(bytecode)
    file = open('Library/Knowledge/Method/Code/3.txt', 'wb')
    file.write(bytecode)
    file.close()
except AGIException as e:
    e.show()
