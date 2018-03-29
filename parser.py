from typing import Tuple, Union, List

import ast
import my_token

from rpn import get_rpn
from tokenizer import get_token


def var_parse(i: int, tokens_str, tokens_type, parent) -> Tuple[Union[ast.VarDecAST, None], int, str]:
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
    v = ast.VarDecAST()
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
        if ast.is_type(tokens_type[i]):
            v.set_type(tokens_str[i])
        else:
            error = "Ошибка объявления переменной. Некорректно указан тип."
            print(error)
            return None, i, error
        i += 1
        if tokens_type[i] == my_token.SEMI:
            # i += 1
            return v, i, ""
        else:
            error = "Ошибка. Нет точки с запятой."
            print(error)
            return None, i, error


def func_parse(i: int, tokens_str, tokens_type, parent: ast.BaseAST) \
        -> Tuple[Union[ast.FunctionDefAST, None], int, str]:
    pass


# Сделано правильно!!!
def func_call_parse(i: int, tokens_str, tokens_type, parent) -> Tuple[Union[ast.FunctionCallAST, None], int, str]:
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
            f = ast.FunctionCallAST(obj, args)
            f.set_parent(parent)
            return f, i, error
        else:
            error = "Не объявлена функция с именем " + name
            print(error)
            return None, i, error
    else:
        error = "Не корректное объявление функции"
        print(error)
        return None, i, error


# Сделано правильно!!!
def bin_op_parse(i: int, tokens_str, tokens_type, parent: ast.BaseAST) -> Tuple[Union[ast.BinaryAST, None], int, str]:
    error = ""
    root = None

    j, rpn, error = get_rpn(i, tokens_type)
    if error != "":
        print(error)
        return None, i, error

    stack = []
    for k in range(len(rpn)):
        if tokens_type[rpn[k]] == my_token.INT_NUMBER:
            hs = ast.IntNumericAST(int(tokens_str[rpn[k]]))
            stack.append(hs)
            continue
        if tokens_type[rpn[k]] == my_token.DOUBLE_NUMBER:
            hs = ast.DoubleNumericAST(float(tokens_str[rpn[k]]))
            stack.append(hs)
            continue
        if tokens_type[rpn[k]] == my_token.IDENTIFIER:
            obj = parent.get_names(tokens_str[rpn[k]])
            if obj is None:
                error = "Переменная с именем " + tokens_str[rpn[k]] + " не объявлена."
                print(error)
                return None, rpn[k], error
            else:
                if tokens_type[rpn[k] + 1] == my_token.RPAR:
                    func_call_obj, i, error = func_call_parse(rpn[k], tokens_str, tokens_type, parent)
                    if func_call_obj is None:
                        # error = "Функция с именем " + tokens_str[i] + " вызвана некорректно."
                        print(error)
                        return None, i, error
                    else:
                        stack.append(func_call_obj)
                else:
                    stack.append(obj)
        if my_token.is_operator(tokens_type[rpn[k]]):
            bin_op = ast.BinaryAST()
            bin_op.set_op(tokens_type[rpn[k]])
            rhs = stack.pop()
            lhs = stack.pop()
            rhs.set_parent(bin_op)
            lhs.set_parent(bin_op)
            bin_op.set_rhs(rhs)
            bin_op.set_lhs(lhs)
            stack.append(bin_op)
    if len(stack) == 1:
        root = stack.pop()
        root.set_parent(parent)
        return root, j, error


def base_parse(tokens_str: List[str], tokens_type):
    base = ast.CompoundExpression(None)  # базовый узел
    i = 0
    error = ""
    while i < len(tokens_type):
        base, i, error = compound_expression_parse(i, tokens_str, tokens_type, base)
        if error != "":
            print(error)
            return None, i, error
        i += 1
    return base, i, error


def func_def_parse(i: int, tokens_str: List[str], tokens_type, parent=None):
    dunc_obj = ast.FunctionDefAST(parent)
    error = ""
    while tokens_type[i] != my_token.RBRACE:
        if tokens_type[i] == my_token.DEF_FUNC:
            i += 1
            continue
        elif tokens_type[i] == my_token.IDENTIFIER:
            obj = parent.get_names(tokens_str[i])
            if obj is not None:
                error = "Переменная с именем " + tokens_str[i] + " уже объявлена."
                print(error)
                return None, i, error
            dunc_obj.set_name(tokens_str[i])
            i += 1
        elif tokens_type[i] == my_token.LPAR:
            i += 1
            while tokens_type[i] != my_token.RPAR:
                if tokens_type[i] == my_token.IDENTIFIER:
                    a = parent.get_names(tokens_str[i])
                    if a is not None:
                        error = "Переменная с именем " + tokens_str[i] + " уже объявлена во внешней области видимости."
                        print(error)
                        return None, i, error
                    a = ast.VarDecAST(dunc_obj)
                    a.set_name(tokens_str[i])
                    dunc_obj.add_arg(a)
                    i += 1
                    if ast.is_type(tokens_type[i]):
                        a.set_type(tokens_type[i])
                    else:
                        error = "Не указан тип у переменной с именем " + tokens_str[i] + "."
                        print(error)
                        return None, i, error
                    i += 1
            i += 1
            continue
        elif tokens_type[i] == my_token.ARROW:
            i += 1
            if ast.is_type(tokens_type[i]):
                dunc_obj.set_type(tokens_type[i])
                i += 1
                continue
            else:
                error = "Не указан возвращаемый тип у функции с именем " + dunc_obj.name + "."
                print(error)
                return None, i, error
        elif tokens_type[i] == my_token.LBRACE:
            i += 1
            # compound_expression = ast.CompoundExpression(dunc_obj)
            while tokens_type[i] != my_token.RBRACE:
                compound_expression, i, error = compound_expression_parse(i, tokens_str, tokens_type, dunc_obj)
                i += 1
            if error != "":
                print(error)
                return None, i, error
    return dunc_obj, i, error



# разбо составного выражения, хранит имена (область видимости)
# def compound_expression_parse(i: int, tokens_str: List[str], tokens_type, parent=None):
#     compound_expression = ast.CompoundExpression(parent)  # базовый узел
#     while tokens_type[i] != my_token.RBRACE:
#         obj, i, error = parse(i, tokens_str, tokens_type, parent=compound_expression)
#         if error != "":
#             print(error)
#             return None, i, error
#         compound_expression.set_child(obj)
#         i += 1
#     return compound_expression


def compound_expression_parse(i: int, tokens_str: List[str], tokens_type, compound_expression):
    obj, i, error = parse(i, tokens_str, tokens_type, parent=compound_expression)
    if error != "":
        print(error)
        return None, i, error
    compound_expression.set_child(obj)
    return compound_expression, i, error


def parse(i: int, tokens_str: List[str], tokens_type, parent=None):
    obj = None
    error = ""
    if tokens_type[i] == my_token.DEF_VAR:
        obj, i, error = var_parse(i, tokens_str, tokens_type, parent)
        if obj is None:
            print(error)
            return None
    elif tokens_type[i] == my_token.SEMI:
        i += 1
    elif tokens_type[i] == my_token.DEF_FUNC:
        obj, i, error = func_def_parse(i, tokens_str, tokens_type, parent)
        if error != "":
            print(error)
            return None
    elif tokens_type[i] == my_token.IDENTIFIER:
        if tokens_type[i + 1] == my_token.RPAR:
            obj, i, error = func_call_parse(i, tokens_str, tokens_type, parent)
            if obj is None:
                print(error)
                return None
        elif my_token.is_operator(tokens_type[i + 1]):
            obj, i, error = bin_op_parse(i, tokens_str, tokens_type, parent)
            if obj is None:
                print(error)
                return None
    return obj, i, error


def main():
    with open("code.txt", 'r', encoding='utf-8') as f:
        code = f.read()
    # print(code)
    tokens_str, tokens_type = get_token(code)
    print(tokens_str)
    print(tokens_type)

    root = base_parse(tokens_str, tokens_type)


if __name__ == "__main__":
    main()
