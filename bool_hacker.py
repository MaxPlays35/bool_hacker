import pprint
import random
from typing import Callable
from itertools import product
from copy import copy

random.seed()

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


def unpack(*unpackable: tuple):
    return unpackable

def generate_args(count: int):
    return list(product(*[[False, True]] * count))

def sum_implicants(countargs: int, implicants: dict):
    implicants_new = {i: set() for i in range(countargs)}
    keys = implicants.keys()
    for key in list(keys):
        if len(implicants[key]) == 1:
            implicants_new[key].add(tuple(implicants[key][0]))
            continue
        for row_1 in range(len(implicants[key])):
            for row_2 in range(row_1+1, len(implicants[key])):
                final = []
                difference = 0
                for i in range(countargs):
                    if implicants[key][row_1][i] != implicants[key][row_2][i]:
                        final.append("*")
                        difference += 1
                    else:
                        final.append(implicants[key][row_1][i])
                if difference > 1:
                    implicants_new[key].add(tuple(implicants[key][row_1]))
                    implicants_new[key].add(tuple(implicants[key][row_2]))
                    continue
                implicants_new[key].add(tuple(final))
    return implicants_new



def sdnf2(args: tuple[str], table: [[bool], bool]):
    good = {i : [] for i in range(len(args)+1)}
    only_true = []
    keys = good.keys()
    for (row, result) in table:
        if result:
            good[row.count(True)].append(row)
            only_true.append(row)
    implicants = {i: [] for i in range(len(args))}
    for key in list(keys)[:len(keys) - 1]:
        for row_1 in good[key]:
            for row_2 in good[key + 1]:
                final = []
                difference = 0
                for i in range(len(args)):
                    if row_1[i] != row_2[i]:
                        final.append("*")
                        difference += 1
                    else:
                        final.append(row_1[i])
                if difference > 1:
                    continue
                implicants[final.index("*")].append(tuple(final))

    countargs = len(args)
    implicants_new = sum_implicants(countargs, implicants)
    while implicants != implicants_new:
        implicants = implicants_new
        implicants_new = sum_implicants(countargs, implicants)

    implicants_set = set()
    for i in map(tuple, implicants.values()):
        implicants_set.add(i[0])
    implicants_table = {key: [] for key in only_true}
    for key in implicants_table.keys():
        for implicant in implicants_set:
            suitable = True
            for i in range(len(args)):
                if implicant[i] == "*":
                    continue
                if implicant[i] != key[i]:
                    suitable = False
                    break
            implicants_table[key].append(suitable)
    #Header
    print("-"*100)
    print(" "*len(only_true[0]), end=TABLE_COLUMN_SEPARATOR)
    for key in implicants_table.keys():
        for value in key:
            print(int(value), end="")
        print("", end=TABLE_COLUMN_SEPARATOR)
    print()
    iterable_set = iter(implicants_set)
    for idx in range(len(implicants_set)):
        implicant = next(iterable_set)
        for char in implicant:
            print(int(char) if char != "*" else char, end="")
        print("", end=TABLE_COLUMN_SEPARATOR)
        for key in implicants_table.keys():
            print(str(int(implicants_table[key][idx])).center(len(key)), end=TABLE_COLUMN_SEPARATOR)
        print()
    print("-" * 100)

    # pprint.pprint(implicants_set)

    # pprint.pprint(set(map(tuple, implicants.values())))


def ege(logic: Callable, sdnf: str, args: tuple[str], table: [[bool], bool]):
    if 1 < len(args) <= 4:
        positive = 0
        for (row, result) in table:
            positive += int(result)
        negative = len(table) - positive
        is_neg = negative > positive
        selected = {arg: [] for arg in args}
        s = f'Логическая функция F задаётся выражением {"+".join(sdnf)}. Ниже приведён фрагмент таблицы ' \
            f'истинности функции F, содержащий все наборы аргументов, при которых функция F {"отрицательна" if is_neg else "положительна"}. Определите, ' \
            f'какому столбцу таблицы истинности функции F соответствует каждая из переменных {", ".join(args)}. Все ' \
            f'строки в представленном фрагменте разные. '

        for (values, result) in table:
            if result == (not is_neg):
                for i in range(len(args)):
                    selected[args[i]].append(values[i])
        args_shuffled = list(copy(args))
        random.shuffle(args_shuffled)

        print(s)
        print("", TABLE_COLUMN_SEPARATOR.join(["_" for i in range(len(args))]), "F", "", sep=TABLE_COLUMN_SEPARATOR)
        idx = 0
        for row in range(len(list(selected.values())[0])):
            for col in args_shuffled:
                print("", int(selected[col][idx]), sep=TABLE_COLUMN_SEPARATOR, end="")
            idx += 1
            print("", int(not is_neg), "", sep=TABLE_COLUMN_SEPARATOR)
        return None

    print("Для этой функции нельзя составить задание КЕГЭ")


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
            temp = TOKEN_LEFT_BRACKET
            idx = 0
            for value in values:
                if not value:
                    temp += TOKEN_NOT + args[idx]
                else:
                    temp += args[idx]
                if idx + 1 != len(args):
                    temp += TOKEN_AND
                idx += 1
            sdnf.append(temp + TOKEN_RIGHT_BRACKET)

    print("SDNF:", "+".join(sdnf))
    sdnf_2 = sdnf2(args, truth_table)
    print("SDNF2:", sdnf2(args, truth_table))
    ege(logic, sdnf_2, args, truth_table)
