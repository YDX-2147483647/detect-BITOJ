"""
*_code: &_code.format()
"""

tab = " " * 4

error_dict = {"FPE": 0, "TLE": 1, "RE": 2, "WA": 3}

base_code_head = '''#include <stdio.h>
#include <stdlib.h>
int main(){
'''
base_code_tail = f"{tab}return 0;\n}}\n"


def input_code(num, input_format_string=""):
    """Generate the C code that can read zero or more input, using scanf().

    :param num: the number of arguments.
    :param input_format_string: the C-style format string (eg. "%d%c"); if not given, the function will use "%d%d...".
    :return: the C code. (string)
    """
    if num:
        # declaration
        ans = [tab, "int "]
        for i in range(num - 1):
            ans.extend(["x", str(i), ", "])
        ans.extend(["x", str(num - 1), ";\n"])

        # definition
        if not input_format_string:
            ans.extend([tab, 'scanf("', "%d" * num, '"'])
        else:
            ans.extend([tab, 'scanf("', input_format_string, '"'])
        ans.extend([f", &x{str(i)}" for i in range(num)])
        ans.extend(");\n")
        ans.extend("\n")

        return "".join(ans)
    else:
        return ""


def test_code(condition):
    """Generate the code that can detect whether the condition is true or not.

    :param condition: a string. (eg. "x0 < 3")
    :return: a C code which raises TLE when the condition is true, and FPE when false.
    """
    ans = [tab, "if(", condition, ")\n"]
    ans.extend([tab, tab, "while(1);", "\n"])  # TLE
    ans.extend([tab, "else{\n"])
    ans.extend([tab, tab, "int tmp = 0;\n"])
    ans.extend([tab, tab, 'printf("%d", 1/tmp);\n'])  # FPE
    ans.extend([tab, "}\n"])
    ans.extend("\n")
    return "".join(ans)


def quadruple_test_code(conditions):
    """A function similar to test_code(), but can test 3 conditions (4 if including all wrong) each time.

    :param conditions: the list of conditions. (eg. ["x0<2", "x0==2", "x0>2"])
    :return: a C code which raises errors according to error_dict.
    """
    ans = [f'if({conditions[0]}){{',  # FPE
           f'{tab}int tmp = 0;',
           f'{tab}printf("%d", 1/tmp);',
           f'}}',
           f'else if({conditions[1]})',  # TLE
           f'{tab}while(1);',
           f'else if({conditions[2]})',  # RE
           f'{tab}abort();',
           f'else',  # WA
           f'{tab};']
    return tab + f'\n{tab}'.join(ans) + '\n'


def get_binary_digit(n, i, digit):
    """Generate a code that can raise errors on purpose to show whether the specific digit of the input is not zero.

    :param n: the number of arguments.
    :param i: the index of the one you are interested in. (0 ~ n-1)
    :param digit: the index of the digit (eg. the right-most digit's index is 0), including the sign digit.
    :return: the C code.
    """
    return "".join([base_code_head, input_code(n), test_code(f"((unsigned)x{i}>>{digit}) % 2"), base_code_tail])


def get_2_binary_digit(n, i, digit, input_format_string=""):
    """Generate a code that can raise errors on purpose to show whether the specific digit of the input is not zero.

    :param n: the number of arguments.
    :param i: the index of the one you are interested in. (0 ~ n-1)
    :param digit: the index of the lower digit of the two(eg. the right-most digit's index is 0),
    including the sign digit.
    :param input_format_string: the C-style format string (eg. "%d%c"); if not given, the function will use "%d%d...".
    :return: the C code.
    """
    ans = [base_code_head, input_code(n, input_format_string)]
    ans.extend(quadruple_test_code([f"((unsigned)x{i}>>{digit}) % 4 == {j}" for j in range(4)]))
    ans.extend(base_code_tail)
    return "".join(ans)


# TODO: get_char()
def get_char(n, i, digit, char_set="0123456789 \n"):
    """Generate a code that can raise errors on purpose due to the char.

    :param n: string length.
    :param i: the index of the char that you are interested in. (0 ~ n-1)
    :param digit: the digit of the index in char_set.
    :param char_set: an assumed set of chars. (only numbers, " ", "\n" if not given)
    :return: the C code.
    """
    ans = [base_code_head, input_code(n, "%c%c%c")]
    ans.extend(quadruple_test_code([f"((unsigned)x{i}>>{digit}) % 4 == {j}" for j in range(4)]))
    ans.extend(base_code_tail)
    return "".join(ans)


if __name__ == "__main__":
    print("这是一个示例：")
    print(get_binary_digit(3, 1, 0))

    print("又一个示例：")
    print(get_2_binary_digit(3, 1, 0))
