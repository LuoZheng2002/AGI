from Kernel.KernelStruct.bytecode_format import r
from ExceptionAndDebug.exception import *
from Kernel.KernelStruct.system_functions import sc, rsc
from Kernel.KernelStruct.system_types import st_text


def expr_to_text(expr) -> str:
    text = ''
    if len(expr) == 1:
        text += str(expr[0])
    else:
        head = expr[0]
        if head == r['input']:
            assert len(expr) == 2
            text += 'input'
            text += str(expr[1])
        elif head == r['reg']:
            assert len(expr) == 3
            text += 'reg'
            text += str(expr[1])
            text += '<'
            for i, j in enumerate(expr[2]):
                text += expr_to_text(j)
                if i != len(expr[2]) - 1:
                    text += ', '
            text += '>'
        elif head == r['iterator']:
            assert len(expr) == 2
            if expr[1] <= 17:
                text += chr(105 + expr[1])
            else:
                text += '<iterator_id=' + str(expr[1]) + '>'
        elif head == r['system_call']:
            assert len(expr) == 3
            params = []
            for i in expr[2]:
                params.append(expr_to_text(i))
            command = expr[1]
            middle_commands = [sc['=='], sc['>'], sc['>='], sc['<'], sc['<='],
                               sc['and'], sc['or']]
            if command in middle_commands:
                assert len(params) == 2
                text += params[0]
                text += ' '
                text += rsc[expr[1]]
                text += ' '
                text += params[1]
            elif command == sc['offset']:
                assert len(params) == 2
                text += params[0]
                if params[1][0] == '-':
                    text += '-'
                    text += params[1][1:]
                else:
                    text += '+'
                    text += params[1]
            else:
                text += rsc[expr[1]]
                text += '('
                for i, j in enumerate(params):
                    text += j
                    if i != len(params) - 1:
                        text += ', '
                text += ')'
        elif head == r['call']:
            assert len(expr) == 3
            text += 'method' + str(expr[1])
            text += '('
            for i, j in enumerate(expr[2]):
                text += expr_to_text(j)
                if i != len(expr[2]) - 1:
                    text += ', '
            text += ')'
        elif head == r['system_type']:
            assert len(expr) == 2
            text += st_text[expr[1]]
            text += '()'
        elif head == r['concept_instance']:
            assert len(expr) == 2
            text += 'Concept' + str(expr[1])
            text += '()'
        elif head == r['size']:
            assert len(expr) == 2
            text += expr_to_text(expr[1])
            text += '.size'
        elif head == r['at'] or head == r['at_reverse']:
            assert len(expr) == 3
            text += expr_to_text(expr[1])
            text += '['
            if head == r['at_reverse']:
                text += '!'
            text += expr_to_text(expr[2])
            text += ']'
        elif head == r['get_member']:
            assert len(expr) == 3
            text += expr_to_text(expr[1])
            text += '.'
            text += expr_to_text(expr[2])
        else:
            raise AGIException('Unexpected type at the head of an expression.',
                               special_name='type', special_str=str(expr[1]))
    return text


def to_text(structured_code) -> str:
    indentation_ends = []
    indentation_count = 0
    text = ''
    for line_index, line in enumerate(structured_code):
        head = line[0]
        for _ in range(indentation_count):
            text += '\t'
        if head == r['assign']:
            text += expr_to_text(line[1])
            text += ' = '
            text += expr_to_text(line[2])
        elif head == r['return']:
            text += 'return '
            text += expr_to_text(line[1])
        elif head == r['for']:
            text += 'for '
            if line[1] <= 17:
                text += chr(105 + line[1])
            else:
                text += '<iterator_id=' + str(line[1]) + '>'
            text += ' in range('
            if line[2] != [0]:
                text += expr_to_text(line[2])
                text += ', '
            text += expr_to_text(line[3])
            text += '):'
            indentation_ends.append(line[4])
            indentation_count += 1
        elif head == r['while']:
            text += 'while '
            text += expr_to_text(line[1])
            text += ':'
            indentation_ends.append(line[2])
            indentation_count += 1
        elif head == r['break']:
            text += 'break'
        elif head == r['if']:
            text += 'if '
            text += expr_to_text(line[1])
            text += ':'
            indentation_ends.append(line[2])
            indentation_count += 1
        elif head == r['else_if']:
            text += 'else if '
            text += expr_to_text(line[1])
            text += ':'
            indentation_ends.append(line[2])
            indentation_count += 1
        elif head == r['else']:
            text += 'else:'
            indentation_ends.append(line[1])
            indentation_count += 1
        elif head == r['delete']:
            text += 'delete reg'
            text += str(line[1])
            text += '<'
            for i, expr in enumerate(line[2]):
                text += expr_to_text(expr)
                if i != len(line[2]) - 1:
                    text += ', '
            text += '>'
        else:
            raise AGIException('Unexpected type as head of a line')
        text += '\n'

        if len(indentation_ends) != 0 and line_index == indentation_ends[-1]:
            indentation_count -= 1
            indentation_ends.pop()
    return text
