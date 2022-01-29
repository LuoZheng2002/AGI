from Kernel.KernelFuncs.Executers.method_runner import *


def main():
    while True:
        number1_str = list(input('Please input the first number: \n'))
        number2_str = list(input('Please input the second number: \n'))
        number1_list = []
        number2_list = []
        for number in number1_str:
            number1_list.append(AGIObject(100 + int(number), 2, dict()))
        for number in number2_str:
            number2_list.append(AGIObject(100 + int(number), 2, dict()))

        number1 = AGIObject(1, None, {65535: AGIList(number1_list)})
        number2 = AGIObject(1, None, {65535: AGIList(number2_list)})
        input_params = [number1, number2]
        result = run_method(1, input_params, None)
        print('the final result is:')
        str_result = ''
        for digit in result.attributes[65535].get_list():
            str_result += str(digit.concept_id - 100)
        print(str_result)


if __name__ == '__main__':
    try:
        main()
    except AGIException as e:
        e.show()
