from ExceptionAndDebug.exception import *
from Kernel.KernelStruct.kernel_struct import AGIObject


def equal(params: list) -> bool:
    if len(params) != 2:
        raise AGIException(15)
    if type(params[0]) == int:
        if type(params[1]) == int:
            if params[0] == params[1]:
                return True
            else:
                return False
        else:
            return False
    else:
        assert type(params[0]) == AGIObject
        if type(params[1]) == AGIObject:
            if params[0].concept_id == params[1].concept_id:
                return True
            else:
                return False
        else:
            return False


def greater(params: list) -> bool:
    if len(params) != 2:
        raise AGIException(15)
    if type(params[0]) != int or type(params[1]) != int:
        raise AGIException(16)
    return params[0] > params[1]


def greater_or_equal(params: list) -> bool:
    if len(params) != 2:
        raise AGIException(15)
    if type(params[0]) != int or type(params[1]) != int:
        raise AGIException(16)
    return params[0] >= params[1]


def less(params: list) -> bool:
    if len(params) != 2:
        raise AGIException(15)
    if type(params[0]) != int or type(params[1]) != int:
        raise AGIException(16)
    return params[0] < params[1]


def less_or_equal(params: list) -> bool:
    if len(params) != 2:
        raise AGIException(15)
    if type(params[0]) != int or type(params[1]) != int:
        raise AGIException(16)
    return params[0] <= params[1]


def and_(params: list) -> bool:
    if len(params) != 2:
        raise AGIException(15)
    if type(params[0]) != bool or type(params[1]) != bool:
        raise AGIException(16)
    return params[0] and params[1]


def or_(params: list) -> bool:
    if len(params) != 2:
        raise AGIException(15)
    if type(params[0]) != bool or type(params[1]) != bool:
        raise AGIException(16)
    return params[0] or params[1]


def max_(params: list) -> bool:
    if len(params) != 2:
        raise AGIException(15)
    if type(params[0]) != int or type(params[1]) != int:
        raise AGIException(16)
    max_value = -0x80000000
    for value in params:
        if value > max_value:
            max_value = value
    return max_value


def min_(params: list) -> bool:
    if len(params) != 2:
        raise AGIException(15)
    if type(params[0]) != int or type(params[1]) != int:
        raise AGIException(16)
    min_value = 0xffffffff
    for value in params:
        if value < min_value:
            min_value = value
    return min_value


def offset(params: list) -> bool:
    if len(params) != 2:
        raise AGIException(15)
    if type(params[0]) != int or type(params[1]) != int:
        raise AGIException(16)
    return params[0] + params[1]


sc = {
    '==': 1,
    '>': 2,
    '>=': 3,
    '<': 4,
    '<=': 5,
    'and': 6,
    'or': 7,
    'max': 8,
    'min': 9,
    'offset': 10
}

system_call = {
    1: equal,  # '=='
    2: greater,  # '>'
    3: greater_or_equal,  # '>='
    4: less,  # '<'
    5: less_or_equal,  # '<='
    6: and_,  # 'and'
    7: or_,  # 'or'
    8: max_,  # 'max'
    9: min_,  # 'min'
    10: offset  # 'offset'
}

rsc = {v: k for k, v in sc.items()}
