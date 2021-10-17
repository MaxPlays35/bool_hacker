import ctypes
import pprint
import random
import sys
from typing import Callable, List, Tuple
from itertools import product
from copy import copy
from string import ascii_uppercase
from time import time

random.seed(time())

TABLE_COLUMN_SEPARATOR = '┃'
TABLE_CORNER_SEPARATOR = '╋'
TABLE_ROW_SEPARATOR = '━'
TOKEN_AND = '*'
TOKEN_OR = '+'
TOKEN_NOT = '¬'
TOKEN_LEFT_BRACKET = '('
TOKEN_RIGHT_BRACKET = ')'
TOKEN_TRUE = '1'
TOKEN_FALSE = '0'
TOKEN_SHEFFER = '↑'

#
# Colors
# imported from https://github.com/Radolyn/RadLibrary/tree/master/RadLibrary/Colors
#

#
# Font decorations
#
BOLD = '\x1b[1m'
UNDERLINE = '\x1b[4m'

#
# Text color
#
GREEN = '\x1b[32m'
LIGHT_BLUE = '\x1b[36m'
LIGHT_YELLOW = '\x1b[93m'
LIGHT_RED = '\x1b[91m'
RED = "\x1b[31m"

#
# Mixes
#
STEP_DEC = BOLD + LIGHT_YELLOW
RESULT_DEC = UNDERLINE + GREEN
HEADER = STEP_DEC

#
# Color and font reset
#
RESET_COLOR = '\x1b[39m'
RESET_FONT = '\x1b[0m'
RESET = RESET_COLOR + RESET_FONT

if sys.platform == "win32":
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)


def timeit(function):
    def wrapper(*args, **kwargs):
        from datetime import datetime
        start = datetime.now()
        function(*args, **kwargs)
        end = datetime.now()

        duration = end - start
        print(f'\nВзлом завершен за {RED}{duration.total_seconds()}{RESET} секунд')

    return wrapper


def unpack(*unpackable: tuple):
    return unpackable


def generate_args(count: int):
    return list(product(*[[False, True]] * count))


def multiply(exp1, exp2):
    result = []

    for left in exp1:
        for right in exp2:
            temp = left
            if right not in temp:
                temp += right
            if temp not in result:
                result.append(temp)

    return result


def humanify(args, implicants):
    exps = []
    for implicant in implicants:
        exp = []
        for char in range(len(implicant)):
            if implicant[char] == "*":
                continue
            if implicant[char] == 0:
                exp.append(TOKEN_NOT + args[char])
            if implicant[char] == 1:
                exp.append(args[char])
        exps.append(exp)
    return exps


def petric(exps, implicants_table):
    vars = {ascii_uppercase[i]: var for (i, var) in enumerate(exps)}

    res = []
    zeros = []

    for i in range(len(implicants_table[0])):
        exp = []
        for j in range(len(implicants_table)):
            if implicants_table[j][i]:
                exp.append(ascii_uppercase[j])

        if len(exp) == 0:
            zeros.append(i)
        else:
            res.append(exp)

    while len(res) > 1:
        res[0] = multiply(res[0], res[1])
        del res[1]

    shorten = min(res[0], key=len)
    final = [vars[letter] for letter in shorten]
    return final


def sum_implicants(countargs: int,
                   implicants: dict):
    implicants_new = set()
    for row_1 in implicants:
        stuck_together = 0
        for row_2 in implicants:
            final = []
            difference = 0
            if row_1 == row_2:
                continue
            for i in range(countargs):
                if row_1[i] != row_2[i]:
                    final.append("*")
                    difference += 1
                else:
                    final.append(row_1[i])
            if difference > 1:
                continue
            stuck_together += 1
            implicants_new.add(tuple(final))
        if stuck_together == 0:
            implicants_new.add(row_1)
    return implicants_new


def stringify(expression):
    return RESULT_DEC + '(' + f') {TOKEN_OR} ('.join([f' {TOKEN_AND} '.join(exp) for exp in expression]).strip() + ')' \
           + RESET


def sdnf2(args: Tuple[str], table: List[List[bool]]):
    good = []
    only_true = []
    for (row, result) in table:
        if result:
            only_true.append(row)
    implicants = set()
    for row_1 in only_true:
        for row_2 in only_true:
            final = []
            difference = 0
            for i in range(len(args)):
                if row_1[i] != row_2[i]:
                    final.append("*")
                    difference += 1
                else:
                    final.append(row_1[i])
            if difference == 1:
                implicants.add(tuple(final))

    countargs = len(args)
    implicants_new = sum_implicants(countargs, implicants)
    while implicants != implicants_new:
        implicants = implicants_new
        implicants_new = sum_implicants(countargs, implicants)

    implicants = tuple(implicants)
    implicants_table = [[] for _ in range(len(implicants))]
    for i in range(len(implicants_table)):
        for j in range(len(only_true)):
            suitable = True
            for char in range(len(implicants[i])):
                if implicants[i][char] == "*":
                    continue
                if implicants[i][char] != only_true[j][char]:
                    suitable = False
                    break
            implicants_table[i].append(suitable)

    exps = humanify(args, implicants)
    return petric(exps, implicants_table)


def ege(logic: Callable, sdnf: str, args: Tuple[str], table: List[List[bool]]):
    if 1 < len(args) <= 4:
        positive = 0
        for (row, result) in table:
            positive += int(result)
        negative = len(table) - positive
        is_neg = negative > positive
        selected = {arg: [] for arg in args}
        s = f'Логическая функция F задаётся выражением {stringify(sdnf) + LIGHT_BLUE}. Ниже приведён фрагмент таблицы ' \
            f'истинности функции F, содержащий все наборы аргументов, при которых функция F {"отрицательна" if is_neg else "положительна"}. Определите, ' \
            f'какому столбцу таблицы истинности функции F соответствует каждая из переменных {", ".join(args)}. Все ' \
            f'строки в представленном фрагменте разные. '

        for (values, result) in table:
            if result == (not is_neg):
                for i in range(len(args)):
                    selected[args[i]].append(values[i])
        args_shuffled = list(copy(args))
        random.shuffle(args_shuffled)

        print(LIGHT_BLUE)
        print(s)
        print(RESET)
        print("", TABLE_COLUMN_SEPARATOR.join(["_" for i in range(len(args))]), "F", "", sep=TABLE_COLUMN_SEPARATOR)
        idx = 0
        idx_1 = random.choice(list(selected.keys()))
        idx_2 = random.randint(0, len(selected[idx_1]) - 1)
        selected[idx_1][idx_2] = "*"

        for row in range(len(list(selected.values())[0])):
            for col in args_shuffled:
                if selected[col][idx] != "*":
                    print("", int(selected[col][idx]), sep=TABLE_COLUMN_SEPARATOR, end="")
                else:
                    print("", selected[col][idx], sep=TABLE_COLUMN_SEPARATOR, end="")
            idx += 1
            print("", int(not is_neg), "", sep=TABLE_COLUMN_SEPARATOR)

        print()
        print(STEP_DEC, end='')
        print("Ответ: ", end='')
        print(RESULT_DEC, end='')
        print(','.join(args_shuffled), end='')
        print(STEP_DEC)
        print(RESET)
        return None

    print(LIGHT_RED, end="")
    print("Для этой функции нельзя составить задание КЕГЭ", end="")
    print(RESET)


def sheffer(sdnf):
    sheffed = [item.copy() for item in sdnf]

    for i in range(len(sheffed)):
        item = sheffed[i]
        for j in range(len(item)):
            if item[j][0] == TOKEN_NOT:
                s = item[j].replace(TOKEN_NOT, "")
                item[j] = f"({s} {TOKEN_SHEFFER} {s})"

    temp = []
    for exp_idx in range(len(sdnf)):
        while len(sheffed[exp_idx]) > 1:
            sheffed[exp_idx][
                0] = f'(({sheffed[exp_idx][0]} {TOKEN_SHEFFER} {sheffed[exp_idx][1]}) {TOKEN_SHEFFER} ({sheffed[exp_idx][0]}' \
                     f' {TOKEN_SHEFFER} {sheffed[exp_idx][1]}))'
            del sheffed[exp_idx][1]
        temp.extend(sheffed[exp_idx])

    while len(temp) > 1:
        temp[0] = f'(({temp[0]} {TOKEN_SHEFFER} {temp[0]}) {TOKEN_SHEFFER} ({temp[1]} {TOKEN_SHEFFER} {temp[1]}))'
        del temp[1]

    print(STEP_DEC)
    print("Sheffer: ", end='')
    print(RESULT_DEC, end='')
    print(temp[0])
    print(RESET)


def print_sdnf(expression):
    return stringify(expression)


def regerate_table(nonfictive_vars, sdnf_2, regerated_table):
    generated_args = generate_args(len(nonfictive_vars))
    expression = stringify(sdnf_2).replace(TOKEN_NOT, "not").replace(TOKEN_AND, "and").replace(TOKEN_OR, "or")
    f = eval(f'''lambda {", ".join(nonfictive_vars)}: {expression}''')

    for item in generated_args:
        res = [*item, f(*item)]
        regerated_table.append(res)


@timeit
def hack(logic: Callable):
    gen_args = generate_args(logic.__code__.co_argcount)
    args = logic.__code__.co_varnames
    print(TABLE_ROW_SEPARATOR * ((sum(map(len, args))) + len(args) + 3))
    print("", *logic.__code__.co_varnames, "F", "", sep=TABLE_COLUMN_SEPARATOR)
    print(TABLE_ROW_SEPARATOR * ((sum(map(len, args))) + len(args) + 3))
    truth_table = []
    for row in gen_args:
        result = logic(*row)
        truth_table.append([row, result])
        idx = 0
        for col in row:
            centered = str(int(col)).center(len(args[idx]))
            print("", centered, sep=TABLE_COLUMN_SEPARATOR, end="")
            idx += 1
        print("", int(result), "", sep=TABLE_COLUMN_SEPARATOR)
    print(TABLE_ROW_SEPARATOR * ((sum(map(len, args))) + len(args) + 3))

    sdnf = []
    for (values, result) in truth_table:
        if result:
            temp = []
            idx = 0
            for value in values:
                if not value:
                    temp.append(TOKEN_NOT + args[idx])
                else:
                    temp.append(args[idx])
                idx += 1
            sdnf.append(temp)

    sdnf_2 = sdnf2(args, truth_table)
    nonfictive_vars = set()
    for i in sdnf_2:
        for j in i:
            nonfictive_vars.add(j.replace(TOKEN_NOT, ''))
    if len(sdnf) == 0:
        print(STEP_DEC, end='')
        print("SDNF:", 0)
        print(STEP_DEC, end='')
        print("SDNF2:", 0)
        print(STEP_DEC)
    elif len(sdnf) == 2 ** len(args):
        print(STEP_DEC, end='')
        print("SDNF:", 1)
        print(STEP_DEC, end='')
        print("SDNF2:", 1)
        print(STEP_DEC)
    else:
        print(STEP_DEC, end='')
        print("SDNF:", stringify(sdnf))
        print(STEP_DEC, end='')
        print("SDNF2:", stringify(sdnf_2))
        print(STEP_DEC)
        sheffer(sdnf_2)
        print(STEP_DEC, end='')
        print("Nonfictive vars: ", end='')
        print(RESULT_DEC, end='')
        print(','.join(nonfictive_vars), end='')
        print(STEP_DEC)
        print(RESET)
        if len(nonfictive_vars) == len(args):
            ege(logic, sdnf_2, args, truth_table)
        else:
            regerated_table = []
            regerate_table(nonfictive_vars, sdnf_2, regerated_table)
        print(RESET)
