from ExceptionAndDebug.exception import *
from Kernel.KernelStruct.bytecode_format import r


class MethodList:
    def __init__(self):
        self.value = [None] * 16
        self.iterator = [0]
        self.next_unreserved = 0

    def set_temp_iter_pos(self, value):
        self.iterator.append(value)

    def retrieve_iter_pos(self):
        self.iterator.pop()

    def expand(self):
        self.value += [None] * len(self.value)

    def write(self, value):
        while self.iterator[-1] >= len(self.value):
            self.expand()
        self.value[self.iterator[-1]] = value
        self.iterator[-1] += 1
        if self.next_unreserved < self.iterator[-1]:
            self.next_unreserved = self.iterator[-1]

    def malloc(self, value):
        return_value = self.next_unreserved
        self.next_unreserved += value
        return return_value

    def shrink_to_fit(self):
        while self.value[-1] is None:
            self.value.pop()


def fill_expr(expr_code, ml: MethodList) -> int:
    expr_size = len(expr_code)
    return_value = ml.malloc(expr_size + 1)
    ml.set_temp_iter_pos(return_value)
    ml.write(expr_size)
    for i in expr_code:
        if type(i) == int:
            ml.write(i)
        elif type(i) == list:
            ml.write(fill_expr(i, ml))
        else:
            raise AGIException('Elements in an expr should be int or list.')
    ml.retrieve_iter_pos()
    return return_value


def fill_line(line_code, ml: MethodList) -> int:
    line_length = len(line_code)
    return_value = ml.malloc(line_length + 1)
    ml.set_temp_iter_pos(return_value)
    ml.write(line_length)
    for i in line_code:
        if type(i) == int:
            ml.write(i)
        elif type(i) == list:
            ml.write(fill_expr(i, ml))
        else:
            raise AGIException('Elements in a line should be int or list.')

    ml.retrieve_iter_pos()
    return return_value


def encode_method(structured_code: list) -> list:
    ml = MethodList()
    # 'A G I E' heading and 4 bytes of version info
    ml.write((69 << 24) + (73 << 16) + (71 << 8) + 65)
    ml.write(69)
    # the third int stores how many lines of codes are in the method
    line_count = len(structured_code)
    ml.write(line_count)
    ml.malloc(line_count)
    # the following several ints are the pointers to the head of the lines
    for i in range(line_count):
        ml.write(fill_line(structured_code[i], ml))
    ml.shrink_to_fit()
    return ml.value


def make_expression(int_code, pointer) -> list:
    expr_size = int_code[pointer]
    if expr_size == 1:
        return [int_code[pointer + 1]]
    else:
        head = int_code[pointer + 1]
        # print(head)
        line = [head]
        if head == r['input']:
            assert expr_size == 2
            line.append(int_code[pointer + 2])
        elif head == r['reg'] or head == r['system_call'] or head == r['call']:
            assert expr_size == 3
            line.append(int_code[pointer + 2])
            params = []
            param_pointer = int_code[pointer + 3]
            param_count = int_code[param_pointer]
            for i in range(param_count):
                params.append(make_expression(int_code, int_code[param_pointer + 1 + i]))
            line.append(params)
        elif head == r['iterator']:
            assert expr_size == 2
            line.append(int_code[pointer + 2])
        elif head == r['system_type']:
            assert expr_size == 2
            line.append(int_code[pointer + 2])
        elif head == r['concept_instance']:
            assert expr_size == 2
            line.append(int_code[pointer + 2])
        elif head == r['size']:
            assert expr_size == 2
            line.append(make_expression(int_code, int_code[pointer + 2]))
        elif head == r['at'] or head == r['at_reverse']:
            assert expr_size == 3
            line.append(make_expression(int_code, int_code[pointer + 2]))
            line.append(make_expression(int_code, int_code[pointer + 3]))
        elif head == r['get_member']:
            assert expr_size == 3
            line.append(make_expression(int_code, int_code[pointer + 2]))
            line.append(int_code[pointer + 3])
        else:
            raise AGIException('Unexpected type at head of an expression.',
                               special_name='type id', special_str=str(head))
        return line


def make_line(int_code, pointer) -> list:
    line_length = int_code[pointer]
    head = int_code[pointer + 1]
    line = [head]
    if head == r['assign']:
        assert line_length == 3
        line.append(make_expression(int_code, int_code[pointer + 2]))
        line.append(make_expression(int_code, int_code[pointer + 3]))
    elif head == r['return']:
        assert line_length == 2
        line.append(make_expression(int_code, int_code[pointer + 2]))
    elif head == r['for']:
        assert line_length == 5
        line.append(int_code[pointer + 2])
        line.append(make_expression(int_code, int_code[pointer + 3]))
        line.append(make_expression(int_code, int_code[pointer + 4]))
        line.append(int_code[pointer + 5])
    elif head == r['while']:
        assert line_length == 3
        line.append(make_expression(int_code, int_code[pointer + 2]))
        line.append(int_code[pointer + 3])
    elif head == r['break']:
        assert line_length == 1
    elif head == r['if'] or head == r['else_if']:
        assert line_length == 3
        line.append(make_expression(int_code, int_code[pointer + 2]))
        line.append(int_code[pointer + 3])
    elif head == r['else']:
        assert line_length == 2
        line.append(int_code[pointer + 2])
    elif head == r['delete']:
        assert line_length == 3
        line.append(int_code[pointer + 2])
        children = []
        children_pointer = int_code[pointer + 3]
        param_count = int_code[children_pointer]
        for i in range(param_count):
            children.append(make_expression(int_code, int_code[children_pointer + 1 + i]))
        line.append(children)
    else:
        raise AGIException('Unexpected type at head of a line.')
    # print(line)
    return line


def decode_method(int_code: list) -> list:
    if int_code[0] != (69 << 24) + (73 << 16) + (71 << 8) + 65:
        raise AGIException('Method file should start with"A G I E"')
    if int_code[1] != 69:
        raise AGIException('The method file is not of the right version.')
    structured_code = []
    line_count = int_code[2]
    for i in range(line_count):
        structured_code.append(make_line(int_code, int_code[i + 3]))
    return structured_code
