import traceback

error_description = \
    {
        0: ['Unknown error',
            'Unknown error'],
        1: ['Method Files should be in size multiple of 4',
            'This error may occur because of:\n'
            'The method file is broken.\n'
            'The file generator is broken'],
        2: ['Child register not registered',
            'This error may occur when the method file is broken.'],
        3: ['Target child register not found.',
            'This error may occur when the target child register has not been set\n'
            'Or the child register has been deleted in advance.'],
        4: ['Unexpected type after \'assign\'',
            'Only \'reg\' is allowed to be assigned'],
        5: ['Can\'t find target value of the register',
            'None'],
        6: ['The right hand side of assign statement should start with "expr" or "constexpr"',
            'None'],
        7: ['Unexpected type at the beginning of a line',
            'Method file error.'],
        8: ['Method doesn\'t return when reaching the end of file.',
            'Method file error.'],
        9: ['lhs[0] is supposed to be an AGIObject',
            'None'],
        10: ['AGIObject appears not iterable',
             'None'],
        11: ['Target iterable does not appear in the list',
             'The list is somehow too short,'],
        12: ['Can\'t find target member when calling "get_member"',
             'None.'],
        13: ['Wrong type at the beginning of an expression',
             'None.'],
        14: ['Target iterator not found.',
             'The iterator isn\'t created or has been destroyed.'],
        15: ['Wrong param count in a system call.',
             'There might be bugs in driver.'],
        16: ['Wrong param type in a system call.',
             'Method file may be broken.'],
        17: ['Expect an array as parameter in max or min function',
             'The parameter passed in is not an array.'],
        18: ['Unrecognized system type',
             'The method file might be broken.'],
        19: ['Attempting to modify an item in an AGIList',
             'Wrong index value or broken method file.'],
        20: ['Operation on input and reg can only be "at", "at_reverse", "get_member" and "size"',
             'None'],
        21: ['When calling "at"/"size" at an AGIObject, the attribute of it should be an AGIList',
             'None'],
        22: ['When calling "at" at a member of an AGIObject, the member should be an AGIList',
             'None'],
        23: ['Temporarily for loop doesn\'t support zero loop,',
             'None'],
        24: ['Different scope info are declared in the same register.',
             'None'],
        25: ['Child register already created.',
             'None'],
        26: ['Try to create a parent register twice.',
             'None'],
        27: ['Else if statement doesn\'nt follow if statement',
             'None'],
    }


class AGIException(BaseException):
    def __init__(self, error_name,
                 current_process=None,  # proc_id
                 current_method=None,
                 current_expression=None,  # expression head, params
                 raw_expression=None,
                 current_line=None,
                 special_name=None,
                 special_str=None):
        self.error_name = error_name
        self.current_process = current_process
        self.current_method = current_method
        self.current_expression = current_expression
        self.raw_expression = raw_expression
        self.current_line = current_line
        self.special_name = special_name
        self.special_str = special_str

    def show(self):
        print('\n################################')
        print('AGI Exception Triggered!')
        print('[Description]: ' + self.error_name)
        if self.current_process is not None:
            print('[Process]:     ' + str(self.current_process))
        if self.current_process is not None:
            print('[Method]:      ' + str(self.current_method))
        if self.current_line is not None:
            print('[Current Line]:  ' + str(self.current_line))
        if self.current_expression is not None:
            print('[Expression]:  ' + str(self.current_expression))
        if self.raw_expression is not None:
            print('[Raw Expr]:    ' + str(self.raw_expression))
        if self.special_name is not None:
            print('[' + self.special_name + ']: ' + self.special_str)
        print('################################\n')
        traceback.print_exc()
