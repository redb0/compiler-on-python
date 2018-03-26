from typing import Tuple, Union

import my_token
from ast import VarDecAST, is_type, FunctionDefAST, Body, FunctionCallAST, BaseAST, BinaryAST


# Сделано правильно!!!
def var_parse(i: int, tokens_str, tokens_type, parent) -> Tuple[Union[VarDecAST, None], int, str]:
    """
    Функция парсинга объявления переменной.
    Переменная объявляется следующим образом:
        var имя_переменной тип_переменной;
    Пример:
        var x int;
    :param i: 
    :param tokens_str: 
    :param tokens_type: 
    :param parent: 
    :return: 
    """
    v = VarDecAST()
    v.set_parent(parent)
    if tokens_type[i] == my_token.DEF_VAR:
        i += 1
        if tokens_type[i] == my_token.IDENTIFIER:
            obj = parent.get_names(tokens_str[i])
            if obj is not None:
                error = "Переменная с именем " + tokens_str[i] + " существует."
                print(error)
                return None, i, error
            else:
                parent.add_name(tokens_str[i], v)
                v.set_name(tokens_str[i])
        else:
            error = "Ошибка объявления переменной. Не указано имя."
            print(error)
            return None, i, error
        i += 1
        if is_type(tokens_type[i]):
            v.set_type(tokens_str[i])
        else:
            error = "Ошибка объявления переменной. Некорректно указан тип."
            print(error)
            return None, i, error
        i += 1
        if tokens_type[i] == my_token.SEMI:
            return v, i, ""
        else:
            error = "Ошибка. Нет точки с запятой."
            print(error)
            return None, i, error


def func_parse(i: int, tokens_str, tokens_type, parent) -> Tuple[Union[FunctionDefAST, None], int, str]:
    i += 1
    j = i
    error = ""
    name = ""
    func_t = -1
    args = []
    if tokens_type[i] == my_token.IDENTIFIER:
        name = tokens_str[i]
        i += 1
    if tokens_type[i] == my_token.LPAR:
        i += 1
        while tokens_type[i] != my_token.RPAR:
            a = VarDecAST()
            if tokens_type[i] == my_token.IDENTIFIER:
                a.set_name(tokens_str[i])
            i += 1
            if is_type(tokens_type[i]):
                a.set_type(tokens_str[i])
            i += 1
            args.append(a)
        i += 1
    if tokens_type[i] == my_token.ARROW:
        i += 1
        if is_type(tokens_type[i]):
            func_t = tokens_type[i]
        i += 1
    if tokens_type[i] == my_token.LBRACE:
        i += 1
        k = 0
        body = Body()
        while tokens_type[i] != my_token.RBRACE:



    if (name != "") and (func_t != -1):
        pass

    while tokens_type[i] != my_token.RBRACE:


    return


def compound_expression_parse(i: int, tokens_str, tokens_type, parent: BaseAST) -> Tuple[Union[VarDecAST, None], int, str]:
    pass


def expression_parse(i: int, tokens_str, tokens_type, parent: BaseAST) -> Tuple[Union[VarDecAST, None], int, str]:
    while tokens_type[i] != my_token.SEMI:
        if tokens_type[i] == my_token.DEF_VAR:
            v, i, error = var_parse(i, tokens_str, tokens_type, parent)
            if (v is not None) and (error != ""):
                print(error)
                return None, i, error
        if tokens_type[i] == my_token.IDENTIFIER:
            if tokens_type[i+1] == my_token.LPAR:
                f, i, error = func_call_parse(i, tokens_str, tokens_type, parent)
                if (f is not None) and (error != ""):
                    return None, i, error
            elif my_token.is_operator(tokens_type[i+1]):
                # TODO: здесь парсинг бинарных выражений
                pass
        # TODO: еще может быть условие или цикл.


# Сделано правильно!!!
def func_call_parse(i: int, tokens_str, tokens_type, parent: BaseAST) -> Tuple[Union[VarDecAST, None], int, str]:
    error = ""
    name = ""
    args = []
    if tokens_type[i] == my_token.IDENTIFIER:
        name = tokens_str[i]
    i += 1
    if tokens_type[i] == my_token.RPAR:
        i += 1
        while tokens_type[i] != my_token.LPAR:
            if tokens_type[i] == my_token.NUMBER:
                args.append(tokens_str[i])

    if name != "":
        obj = parent.get_names(name)
        if obj is not None:
            f = FunctionCallAST(obj, args)
            f.set_parent(parent)
        else:
            error = "Не объявлена функция с именем " + name
            print(error)
            return None, i, error
    else:
        error = "Не корректное объявление функции"
        print(error)
        return None, i, error


def bin_op_parse(i: int, tokens_str, tokens_type, parent: BaseAST) -> Tuple[Union[BinaryAST, None], int, str]:
    error = ""
    bin_op = BinaryAST(parent)
    if tokens_type[i] == my_token.IDENTIFIER:
        lhs = parent.get_names(tokens_str[i])
        if lhs is None:
            error = "Переменная с именем " + tokens_str[i] + " не объявлена."
            print(error)
            return None, i, error
        else:
            bin_op.set_lhs(lhs)
        i += 1
        if my_token.is_operator(tokens_type[i]):
            bin_op.set_op(tokens_type[i])
        else:
            error = "Некорректное выражение."
            print(error)
            return None, i, error
        i += 1
        if tokens_type[i] == my_token.IDENTIFIER:
            # TODO: а тут может быть несколько вариантов: либо число, либо переменная либо вызов функции.
            pass