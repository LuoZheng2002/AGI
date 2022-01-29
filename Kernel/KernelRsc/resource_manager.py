from ExceptionAndDebug.exception import *
from copy import deepcopy



class Register:
    next_id = 0

    def __init__(self, proc_id, reg_id, scope_info: list, first_child_index: tuple):
        self.proc_id = proc_id
        self.local_id = reg_id
        self.scope_info = deepcopy(scope_info)  # scope_info: [iter_id1, iter_id2]
        if len(scope_info) == 0:
            self.value = None
        elif first_child_index != ():
            self.value = {first_child_index: None}
        else:
            self.value = dict()
            # format:{(iter_value1, iter_value2): AGIObject,
            #         (iter_value1, iter_value2): AGIObject}
        self.id = Register.next_id
        Register.next_id += 1

    def set_value(self, child_index: tuple, value):
        if child_index == ():
            if self.value is not None:
                raise AGIException(2)
            self.value = deepcopy(value)
        else:
            if child_index not in self.value:
                raise AGIException(2)
            self.value[child_index] = deepcopy(value)

    '''
    def get_value(self, child_index: None or list) -> AGIObject or int:
        if child_index is None or child_index == []:
            return self.value
        else:
            for child_value in self.value:
                if child_value[0] == child_index:
                    return child_value[1]
            raise AGIException(3)
    '''


class Iterator:
    next_id = 0

    def __init__(self, proc_id, iter_id, start_value):
        self.proc_id = proc_id
        self.local_id = iter_id
        self.value = start_value
        self.id = Iterator.next_id
        Iterator.next_id += 1


class ResourceManager:
    def __init__(self):
        self.registers = dict()
        self.iterators = dict()

    def start_process(self, proc_id):
        assert proc_id not in self.registers
        assert proc_id not in self.iterators
        self.registers.update({proc_id: []})
        self.iterators.update({proc_id: []})
        '''
        print('Process started')
        print(proc_id)
        print(self.registers)
        print(self.iterators)
        '''

    def has_reg(self, proc_id, reg_id, child_index: tuple):
        if proc_id not in self.registers:
            return False
        for register in self.registers[proc_id]:
            if register.local_id == reg_id \
                    and (child_index == () or child_index in register.value):
                return True
        return False

    def create_reg(self, proc_id, reg_id, scope_info: list, child_index: tuple):  # the reg_id should be local id
        assert proc_id in self.registers
        for register in self.registers[proc_id]:
            if register.local_id == reg_id:  # if this is true, means that register has children
                if register.scope_info != scope_info:
                    raise AGIException(24)
                if child_index in register.value:
                    raise AGIException(25)
                register.value.update({child_index: None})
                return
        # if none of the registers match in the parent level:
        self.registers[proc_id].append(Register(proc_id, reg_id, scope_info, child_index))

    def create_iterator(self, proc_id, iter_id, start_value):
        assert proc_id in self.iterators
        self.iterators[proc_id].append(Iterator(proc_id, iter_id, start_value))

    def update_iterator(self, proc_id, iter_id):
        for iterator in self.iterators[proc_id]:
            if iterator.local_id == iter_id:
                iterator.value += 1
                return
        assert False

    def destroy_iterator(self, proc_id, iter_id):
        for i, iterator in enumerate(self.iterators[proc_id]):
            if iterator.local_id == iter_id:
                self.iterators[proc_id].pop(i)
                return
        assert False

    def get_iterator_value(self, proc_id, iter_id):
        for iterator in self.iterators[proc_id]:
            if iterator.local_id == iter_id:
                return iterator.value
        raise AGIException(14)

    def set_reg_value(self, proc_id, reg_id, child_index: tuple, value):
        for register in self.registers[proc_id]:
            if register.local_id == reg_id:
                register.set_value(child_index, value)

        """
        def set_reg(self, proc_id, reg_id, child_index: None or list, value: AGIObject or int):
            for register in self.registers:
                if register.proc_id == proc_id and register.local_id == reg_id:
                    register.set_value(child_index, value)
        """

    def get_reg_value(self, proc_id, reg_id, child_index: tuple):
        for register in self.registers[proc_id]:
            if register.local_id == reg_id:
                if child_index == ():
                    if register.value is None:
                        raise AGIException('reg\'s value is none')
                    return register.value
                else:
                    if child_index not in register.value:
                        raise AGIException('child_index is not in register.value')
                    if register.value[child_index] is None:
                        raise AGIException('reg\'s value is none')
                    return register.value[child_index]
        raise AGIException(5)

    def get_reg(self, proc_id, reg_id) -> Register:
        for register in self.registers[proc_id]:
            if register.local_id == reg_id:
                return register
        raise AGIException(5)

    def free_resource(self, proc_id):
        """
        print('before freeing resource')
        print(self.registers)
        print(self.iterators)
        """
        self.registers.pop(proc_id)
        self.iterators.pop(proc_id)
        '''
        print('resource freed!')
        print(proc_id)
        print(self.registers)
        print(self.iterators)
        '''