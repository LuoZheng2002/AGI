import Kernel.KernelRsc.kernel_resource as kr
from Kernel.KernelStruct.kernel_struct import AGIList
from Kernel.KernelStruct.bytecode_format import *
from Kernel.KernelStruct.system_functions import *
from Kernel.KernelStruct.system_types import *
from Kernel.KernelFuncs.Executers.method_translator import decode_method


class ForInfo:
    def __init__(self, iter_id, start_line, end_line, start_iter_value, end_iter_value):
        self.iter_id = iter_id
        self.start_line = start_line
        self.end_line = end_line
        self.start_iter_value = start_iter_value
        self.end_iter_value = end_iter_value
        self.cur_iter_value = start_iter_value


class CodeIterator:
    def __init__(self, list_codes, proc_id):
        self.list_codes = list_codes
        self.line_count = len(list_codes)
        self.proc_id = proc_id
        self.current_line = None
        self.next_line_index = 0  # line is also counted from 0
        # for stuff
        self.scope_info = []  # contain ids of iterators
        self.for_stack = []  # contain ForInfo objects
        # while stuff
        self.while_stack = []  # contain (start_line, end_line)
        # for and while stuff
        self.for_while_stack = []  # designed for break operation, contain for/while and end_line
        # if stuffs
        self.if_stack = []  # contains the end_line of if statements
        self.if_status = None  # need to be obtained at the last if statement
        self.last_if_status = None  # True or false, only appears
        # when if statement just ended and else statement just started
        self.broken = False  # when calling break, this appears true

    def get_next_line(self):
        self.current_line = self.list_codes[self.next_line_index]
        self.next_line_index += 1

    def end_of_code(self) -> bool:
        return self.next_line_index >= self.line_count

    def enter_for_loop(self, iter_id, start_iter_value, end_iter_value, end_line):
        self.scope_info.append(iter_id)
        self.for_stack.append(ForInfo(iter_id, self.next_line_index, end_line, start_iter_value, end_iter_value))
        self.for_while_stack.append((r['for'], end_line))

    def enter_while_loop(self, start_line, end_line):
        self.while_stack.append((start_line, end_line))
        self.for_while_stack.append((r['while'], end_line))

    def send_break_message(self):
        self.broken = True

    def update_status(self):
        # flush last_if_status anyway
        self.last_if_status = None
        # when a block of if statement ends, update self.last_if_status
        if len(self.if_stack) != 0:
            if self.if_status is not None and not self.if_status:  # when if statement fails
                self.if_status = False  # True:normal,False:skip and send false to else, None:skip and send true to else
                self.last_if_status = False  # encourage else to be executed
                self.next_line_index = self.if_stack[-1] + 1  # jump to the front of else statement
                self.if_stack.pop()
            elif self.if_status is None:
                self.last_if_status = True
                self.next_line_index = self.if_stack[-1] + 1  # jump to the front of else statement
                self.if_stack.pop()
            elif self.next_line_index - 1 == self.if_stack[-1]:  # reach the end of if block
                self.last_if_status = self.if_status  # need to be assigned back to None the next time
                self.if_status = None
                self.if_stack.pop()
        # check if break is triggered
        if self.broken:
            self.broken = False
            assert len(self.for_while_stack) != 0
            for_or_while = self.for_while_stack[-1][0]
            end_line = self.for_while_stack[-1][1]
            self.next_line_index = end_line + 1
            self.for_while_stack.pop()
            if for_or_while == r['for']:
                assert len(self.for_stack) != 0
                self.for_stack.pop()
                assert len(self.scope_info) != 0
                kr.kr.rsc_mng.destroy_iterator(self.proc_id, self.scope_info[-1])
                self.scope_info.pop()
            else:
                assert for_or_while == r['while']
                assert len(self.while_stack) != 0
                self.while_stack.pop()
        # for/while loop stuff
        elif len(self.for_while_stack) != 0:
            # for loop stuff
            if self.for_while_stack[-1][0] == r['for']:
                for_info = self.for_stack[-1]
                if self.next_line_index == for_info.end_line + 1:
                    for_info.cur_iter_value += 1
                    kr.kr.rsc_mng.update_iterator(self.proc_id, for_info.iter_id)
                    if for_info.cur_iter_value == for_info.end_iter_value:
                        # end the for loop, doesn't need to change next_line_index
                        self.for_stack.pop()
                        kr.kr.rsc_mng.destroy_iterator(self.proc_id, self.scope_info[-1])
                        self.scope_info.pop()
                        self.for_while_stack.pop()
                    else:
                        # go back to start of the for loop
                        self.next_line_index = for_info.start_line
            # while loop stuff
            else:
                assert self.for_while_stack[-1][0] == r['while']
                end_line = self.while_stack[-1][1]
                if self.next_line_index == end_line + 1:
                    start_line = self.while_stack[-1][0]
                    self.next_line_index = start_line
                    self.while_stack.pop()
                    self.for_while_stack.pop()

    def send_if_info(self, status: bool or None, end_line: int):  # when else if with last_if_status == True, pass None
        self.if_stack.append(end_line)
        self.if_status = status


def get_agi_list(agi_object: AGIObject) -> AGIList:
    if len(agi_object.attributes) != 1:
        raise AGIException('Trying to get list from AGIObject but AGIObject has more than one attribute',
                           special_name='Concept id', special_str=str(agi_object.concept_id))
    for i in agi_object.attributes.values():
        if type(i) != AGIList:
            raise AGIException('Target type is not AGIList', special_name='type', special_str=str(type(i)))
        return i


def solve_expression(expr: list,
                     input_params,
                     proc_id,
                     ) -> AGIObject or AGIList:
    try:
        if type(expr) != list:
            print(expr)
            raise AGIException(0)
        assert len(expr) != 0
        # constexpr:
        if len(expr) == 1:
            return expr[0]
        else:
            # print(proc_id)
            # print(rr[expr[0]])
            # if rr[expr[0]] == 'system_call':
            #     print(rsc[expr[1]])
            # if len(rsc_mng.iterators) != 0:
            #     print('iterator_value:'+str(rsc_mng.iterators[-1].value))
            head = expr[0]
            if head == r['input']:
                # input, index_of_input
                return input_params[expr[1]]
            elif head == r['reg']:
                # reg, index_of_reg, child_info
                child_index = []
                for i in expr[2]:
                    child_index.append(solve_expression(i, input_params, proc_id))
                child_index = tuple(child_index)
                return kr.kr.rsc_mng.get_reg_value(proc_id, expr[1], child_index)
            elif head == r['iterator']:
                # iterator, index_of_iterator
                return kr.kr.rsc_mng.get_iterator_value(proc_id, expr[1])
            elif head == r['system_call']:
                # system_call, function_id, function_params
                function_id = expr[1]
                if function_id == sc['and'] or function_id == sc['or']:
                    first_result = solve_expression(expr[2][0], input_params, proc_id)
                    if function_id == sc['and'] and not first_result:
                        return False
                    elif function_id == sc['or'] and first_result:
                        return True
                function_params = []
                for i in expr[2]:
                    function_params.append(solve_expression(i, input_params, proc_id))
                result = system_call[function_id](function_params)
                assert result is not None
                return result
            elif head == r['call']:
                # call, method_id, method_params
                method_id = expr[1]
                method_params = []
                for i in expr[2]:
                    method_params.append(solve_expression(i, input_params, proc_id))
                result = run_method(method_id, method_params, proc_id)
                assert type(result) == AGIObject
                return result
            elif head == r['system_type']:
                # system_type type_id
                type_id = expr[1]
                return st[type_id]()
            elif head == r['concept_instance']:
                # concept_type, type_id
                type_id = expr[1]
                return kr.kr.kd.create_concept_instance(type_id)
            elif head == r['size']:
                # size, expr
                result = solve_expression(expr[1], input_params, proc_id)
                if type(result) == AGIObject:
                    return get_agi_list(result).size()
                else:
                    assert type(result) == AGIList
                    return result.size()
            elif head == r['at'] or head == r['at_reverse']:
                # at/at_reverse, target, index
                target = solve_expression(expr[1], input_params, proc_id)
                index = solve_expression(expr[2], input_params, proc_id)
                if type(target) == AGIObject:
                    if head == r['at']:
                        return get_agi_list(target).get_element(index)
                    else:  # head == r['at_reverse']
                        return get_agi_list(target).get_element_reverse(index)
                else:
                    if type(target) != AGIList:
                        raise AGIException('target is supposed to be AGIList or AGIObject',
                                           special_name='type of target', special_str=str(type(target)))
                    if head == r['at']:
                        return target.get_element(index)
                    else:  # head == r['at_reverse']
                        return target.get_element_reverse(index)
            elif head == r['get_member']:
                # get_member target member_name
                target = solve_expression(expr[1], input_params, proc_id)
                member_name = expr[2]
                if type(target) == AGIObject:
                    return target.attributes[member_name]
                else:
                    assert type(target) == dict
                    return target[member_name]
            else:
                raise AGIException(13)
    except AGIException as e:
        e.current_expression = rr[expr[0]]
        e.raw_expression = expr
        raise e


def run_method(method_id, input_params: list, caller_id) -> AGIObject or None:
    # process registration
    proc_id = kr.kr.proc_mng.create_process(caller_id, method_id)
    # resource manager registration
    kr.kr.rsc_mng.start_process(proc_id)
    int_code = kr.kr.kd.get_method_code(method_id)
    list_code = decode_method(int_code)

    # CodeIterator creation
    ci = CodeIterator(list_code, proc_id)

    while not ci.end_of_code():
        try:
            ci.get_next_line()
            # when debug, break here
            # if proc_id == 0:
            #     print(ci.next_line_index-1)
            # print('proc_id: ' + str(proc_id))
            # print('line: '+str(ci.next_line_index - 1))
            # print('')
            head_of_line = ci.current_line[0]
            if head_of_line == r['assign']:
                # ci.current_line[1]: lhs, ci.current_line[2]: rhs
                lhs = [None, None, None]
                head_of_lhs = ci.current_line[1][0]
                reg_id = None  # only for head_of_lhs == r['reg']
                child_index = None  # only for head_of_lhs == r['reg']
                if head_of_lhs == r['reg']:
                    reg_id = ci.current_line[1][1]
                    # get child_index
                    child_index = []
                    for expr in ci.current_line[1][2]:
                        child_index.append(solve_expression(expr, input_params, proc_id))
                    child_index = tuple(child_index)
                    # create reg
                    if not kr.kr.rsc_mng.has_reg(proc_id, reg_id, child_index):
                        kr.kr.rsc_mng.create_reg(proc_id, reg_id, ci.scope_info, child_index)
                    lhs[0] = kr.kr.rsc_mng.get_reg(proc_id, reg_id)
                elif head_of_lhs == r['at'] or head_of_lhs == r['at_reverse']:
                    # at, [expr], [expr]
                    target = solve_expression(ci.current_line[1][1], input_params, proc_id)
                    if type(target) == AGIObject:
                        lhs[0] = get_agi_list(target)
                    else:
                        assert type(target) == AGIList
                        lhs[0] = target
                    lhs[1] = head_of_lhs  # 'at' or 'at_reverse'
                    lhs[2] = solve_expression(ci.current_line[1][2], input_params, proc_id)
                elif head_of_lhs == r['get_member']:
                    # get_member, [expr], constexpr
                    target = solve_expression(ci.current_line[1][1], input_params, proc_id)
                    if type(target) == AGIObject:
                        lhs[0] = target.attributes
                    else:
                        assert type(target) == dict
                        lhs[0] = target
                    lhs[1] = head_of_lhs
                    lhs[2] = ci.current_line[1][2]
                else:
                    raise AGIException(20)
                # solve for rhs:
                rhs = solve_expression(ci.current_line[2], input_params, proc_id)
                # assign rhs to lhs:
                if lhs[1] is None:  # lhs[2] is None too, means that lhs[0] is register object
                    kr.kr.rsc_mng.set_reg_value(proc_id, reg_id, child_index, rhs)
                else:  # lhs[1] is not None, means that lhs[0] is AGIObject, AGIList or dict or int...
                    if lhs[1] == r['at']:
                        lhs[0].set_forward(lhs[2], rhs)
                    elif lhs[1] == r['at_reverse']:
                        lhs[0].set_reverse(lhs[2], rhs)
                    else:  # lhs[1] == r['get_member']
                        lhs[0][lhs[2]] = rhs
            elif head_of_line == r['return']:
                result = solve_expression(ci.current_line[1], input_params, proc_id)
                kr.kr.rsc_mng.free_resource(proc_id)
                kr.kr.proc_mng.destroy_process(proc_id)
                return result
            elif head_of_line == r['for']:
                # for, iter_id, start_value, end_value, end_line
                iter_id = ci.current_line[1]
                start_value = solve_expression(ci.current_line[2], input_params, proc_id)
                end_value = solve_expression(ci.current_line[3], input_params, proc_id)
                end_line = ci.current_line[4]
                kr.kr.rsc_mng.create_iterator(proc_id, iter_id, start_value)
                ci.enter_for_loop(iter_id, start_value, end_value, end_line)
            elif head_of_line == r['while']:
                # while statement end_line
                result = solve_expression(ci.current_line[1], input_params, proc_id)
                assert type(result) == bool
                end_line = ci.current_line[2]
                if not result:
                    ci.next_line_index = end_line + 1
                else:
                    ci.enter_while_loop(ci.next_line_index - 1, end_line)
            elif head_of_line == r['break']:
                ci.send_break_message()
            elif head_of_line == r['if']:
                result = solve_expression(ci.current_line[1], input_params, proc_id)
                assert (type(result) == bool)
                ci.send_if_info(result, ci.current_line[2])
            elif head_of_line == r['else_if']:
                if ci.last_if_status is None:
                    raise AGIException(27)
                if ci.last_if_status:
                    ci.send_if_info(None, ci.current_line[2])
                else:
                    result = solve_expression(ci.current_line[1], input_params, proc_id)
                    assert (type(result) == bool)
                    ci.send_if_info(result, ci.current_line[2])
            elif head_of_line == r['else']:
                if ci.last_if_status is None:
                    raise AGIException(27)
                if ci.last_if_status:
                    ci.send_if_info(None, ci.current_line[1])
                else:
                    ci.send_if_info(True, ci.current_line[1])
            elif head_of_line == r['delete']:
                pass  # to do
            else:
                raise AGIException(7)
        except AGIException as e:
            e.current_process = proc_id
            e.current_method = method_id
            e.current_line = ci.next_line_index - 1
            raise e
        ci.update_status()
    # rsc_mng.free_resource(proc_id)
    # proc_mng.destroy_process(proc_id)
    raise AGIException('Method exits without return.')
