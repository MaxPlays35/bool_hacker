import pprint
import random
from typing import Callable, List, Tuple
from itertools import product
from copy import copy
from string import ascii_uppercase

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
                   implicants: dict):  # ещё лучше юзать сет, потому что одинаковых импликант быть не может
    # короче, советую написать по нормальному без ^ словаря,
    # и код тогда проще будет
    # в итоге получится 3 цикла
    # row_1, row_2, и для сравнения

    implicants_new = set()
    for row_1 in implicants:  # короче смотри, здесь ставишь счётчик, и если он ни с одной импликантой не сросся, то записываешь в РЕЗУЛЬТАТ, а то он у тебя так и будет до бесконечности крутиться
        stuck_together = 0
        for row_2 in implicants:  # потом тут у тебя было i + 1, len... - так не надо, потому что теряешь импилканты
            final = []  # ещё въебашь проверку на row1 == row2 :continue
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
            implicants_new.add(row_1)  # <- как минимум из-за этого = нет,
        # сейчас это заработает?
        #
    return implicants_new


def stringify(expression):
    return '(' + f') {TOKEN_OR} ('.join([f' {TOKEN_AND} '.join(exp) for exp in expression]).strip() + ')'


def sdnf2(args: Tuple[str], table: List[List[bool]]):
    good = []
    only_true = []
    # эту часть сносишь крч,
    # и делаешь чисто сет вида из (True, False, True, False..)
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
    pprint.pprint(implicants_table)

    # CODE
    # implicants_table = [[] for _ in range(len(only_true))]
    # for i in range(len(implicants_table)):
    #     for j in range(len(implicants)):
    #         suitable = True
    #         for char in range(len(implicants[j])):
    #             if implicants[j][char] == "*":
    #                 continue
    #             if implicants[j][char] != only_true[i][char]:
    #                 suitable = False
    #                 break
    #         implicants_table[i].append(suitable)
    # pprint.pprint(implicants_table)

    # offset = 0
    # for row in range(len(implicants_table)):

    # row = 0
    # while row < len(implicants_table):
    #     if implicants_table[row].count(True) == 1:
    #         idx = implicants_table[row].index(True)
    #         del implicants_table[row]
    #         offset += 1
    #         offset_new = 0
    #         for new_col in range(len(implicants_table)):
    #             if implicants_table[new_col - offset_new][idx] == 1:
    #                 del implicants_table[new_col - offset_new]
    #                 offset_new += 1
    #                 continue
    #             if implicants_table[new_col - offset_new][idx] == 0:
    #                 del implicants_table[new_col - offset_new][idx]
    #                 continue
    #     row += 1
    # pprint.pprint(implicants_table)


    exps = humanify(args, implicants)
    return petric(exps, implicants_table)
    # Header
    # print("-" * 100)
    # print(" " * len(only_true[0]), end=TABLE_COLUMN_SEPARATOR)
    # for key in implicants_table.keys():
    #     for value in key:
    #         print(int(value), end="")
    #     print("", end=TABLE_COLUMN_SEPARATOR)
    # print()
    # iterable_set = iter(implicants)
    # for idx in range(len(implicants)):
    #     implicant = next(iterable_set)
    #     for char in implicant:
    #         print(int(char) if char != "*" else char, end="")
    #     print("", end=TABLE_COLUMN_SEPARATOR)
    #     for key in implicants_table.keys():
    #         print(str(int(implicants_table[key][idx])).center(len(key)), end=TABLE_COLUMN_SEPARATOR)
    #     print()
    # print("-" * 100)
    #
    # # NEW TABLE
    # print("Simplified")
    # essential_implicants = set()
    # converted_implicants = tuple(implicants)
    # new_table = copy(implicants_table)
    # for key in implicants_table.keys():
    #     if implicants_table[key].count(True) == 1:
    #         index = implicants_table[key].index(True)
    #         essential_implicants.add(converted_implicants[index])
    #         del new_table[key]
    #         for new_key in new_table.keys():
    #
    # print(essential_implicants)

    # pprint.pprint(implicants_set)

    # pprint.pprint(set(map(tuple, implicants.values())))


def ege(logic: Callable, sdnf: str, args: Tuple[str], table: List[List[bool]]):
    if 1 < len(args) <= 4:
        positive = 0
        for (row, result) in table:
            positive += int(result)
        negative = len(table) - positive
        is_neg = negative > positive
        selected = {arg: [] for arg in args}
        s = f'Логическая функция F задаётся выражением {sdnf}. Ниже приведён фрагмент таблицы ' \
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
                0] = f'(({sheffed[exp_idx][0]} {TOKEN_SHEFFER} {sheffed[exp_idx][1]}) {TOKEN_SHEFFER} ({sheffed[exp_idx][0]} {TOKEN_SHEFFER} {sheffed[exp_idx][1]}))'
            del sheffed[exp_idx][1]
        temp.extend(sheffed[exp_idx])

    while len(temp) > 1:
        temp[0] = f'(({temp[0]} {TOKEN_SHEFFER} {temp[0]}) {TOKEN_SHEFFER} ({temp[1]} {TOKEN_SHEFFER} {temp[1]}))'
        del temp[1]

    print(temp[0])


def print_sdnf(expression):
    return stringify(expression)


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
    print("SDNF2:", print_sdnf(sdnf_2))
    sheffer(sdnf_2)
    ege(logic, sdnf_2, args, truth_table)
