from Kernel.KernelStruct.kernel_struct import AGIObject, AGIList
from ExceptionAndDebug.exception import *
from temporary import *
import os


# get method code/info
# add method

class Method:
    def __init__(self, method_id, code, info):
        self.method_id = method_id
        self.code = code
        self.info = info


def translate_int_codes(int_codes: list) -> list:
    pass


# need to handle file io
class KnowledgeDriver:
    def __init__(self):
        self.methods = []

    def prepare_method(self, method_id):
        for method in self.methods:
            if method.method_id == method_id:
                return
        file = open('Library/Knowledge/Method/Code/' + str(method_id) + '.txt', 'rb')
        file_size = os.stat('Library/Knowledge/Method/Code/' + str(method_id) + '.txt').st_size
        if file_size % 4 != 0:
            raise AGIException('Code file should be in size multiple of 4.')
        int_count = file_size >> 2
        bytecode = file.read(file_size)
        file.close()
        # from bytes to integers
        code = []
        for i in range(int_count):
            code.append(int.from_bytes(bytecode[4 * i:4 * i + 4], byteorder='little', signed=True))

        file = open('Library/Knowledge/Method/Info/' + str(method_id) + '.txt', 'rb')
        file_size = os.stat('Library/Knowledge/Method/Info/' + str(method_id) + '.txt').st_size
        if file_size % 4 != 0:
            raise AGIException('Info file should be in size multiple of 4.')
        int_count = file_size >> 2
        bytecode = file.read(file_size)
        file.close()
        info = []
        for i in range(int_count):
            info.append(int.from_bytes(bytecode[4 * i:4 * i + 4], byteorder='little', signed=True))
        self.methods.append(Method(method_id, code, info))

    def get_method_code(self, method_id) -> list:
        self.prepare_method(method_id)
        for method in self.methods:
            if method.method_id == method_id:
                return method.code
        raise AGIException('prepare_method doesn\'t work.')

    def get_method_info(self, method_id) -> list:
        self.prepare_method(method_id)
        for method in self.methods:
            if method.method_id == method_id:
                return method.info
        raise AGIException('prepare_method doesn\'t work.')

    def get_method_input_count(self, method_id) -> int:
        # to do
        return 0

    def is_object_iterable(self, concept_id) -> bool:
        return True

    def create_concept_instance(self, concept_id) -> AGIObject:
        # concept_struct = self.get_concept_structure(concept_id)
        # concept_id = concept_struct[0]
        # concept_type = concept_struct[1]
        # concept_attributes = concept_struct[2]
        # to do
        # attributes = dict()
        # for attribute in concept_attributes:
        #     attributes.update({attribute[0]: AGIList()})  # to do
        # return AGIObject(concept_id, concept_type, attributes)
        if concept_id == 1:
            return AGIObject(1, None, {65535: AGIList()})
        else:
            return AGIObject(concept_id, 2, dict())

    def get_concept_structure(self, concept_id):
        if concept_id == 1:
            return [1, None, [[3, None, []]]]
        elif concept_id > 99:
            return [concept_id, 2, []]
