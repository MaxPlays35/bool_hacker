import pprint
import random
from typing import Callable, List, Tuple
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

    implicants_table = {key: [] for key in implicants}
    for row in only_true:
        for implicant in implicants:
            suitable = True
            for i in range(len(args)):
                if implicant[i] == "*":
                    continue
                if implicant[i] != row[i]:
                    suitable = False
                    break
            implicants_table[implicant].append(suitable)

    # Header
    print("-" * 100)
    print(" " * len(only_true[0]), end=TABLE_COLUMN_SEPARATOR)
    for key in implicants_table.keys():
        for char in key:
            print(int(char) if char != "*" else char, end="")
        print("", end=TABLE_COLUMN_SEPARATOR)
    print()
    values = list(implicants_table.values())
    # for idx in range(len(implicants_table.values())):
    #     for row in range(len(values[idx])):
    #         for char in only_true[idx]:
    #             print(int(char), end="")
    #         print("", end=TABLE_COLUMN_SEPARATOR)
    #     print()
    for idx in range(len(only_true)):
        for char in only_true[idx]:
            print(int(char), end="")
        print("", end=TABLE_COLUMN_SEPARATOR)
        for value in values[idx]:
            print(str(int(value)).center(len(args)), end=TABLE_COLUMN_SEPARATOR)
        print()
    print("-" * 100)

    #NEW TABLE
    print("Simplified")
    essential_implicants = set()
    converted_implicants = tuple(implicants)
    for key in implicants_table.keys():
        if implicants_table[key].count(True) == 1:
            essential_implicants.add(converted_implicants[implicants_table[key].index(True)])
    print(essential_implicants)




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
    sdnf2(args, truth_table)
    print("SDNF2:", "not implemented")
    ege(logic, sdnf, args, truth_table)
