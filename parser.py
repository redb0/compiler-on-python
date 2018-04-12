from typing import Tuple, Union, List

import llvm
import llvm.core

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
            v.set_type(tokens_type[i])
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


def var_def_parse(i: int, tokens_str, tokens_type, parent: ast.CompoundExpression) -> Tuple[Union[ast.VarDefAST, None], int, str]:
    error = ""
    var_def = None
    if (tokens_type[i] == my_token.IDENTIFIER) and (tokens_type[i + 1] == my_token.ASSIGN):
        obj = parent.get_names(tokens_str[i])
        if obj is None:
            error = "Переменная с именем " + tokens_str[i] + " не объявлена."
            print(error)
            return None, i, error
        var_def = ast.VarDefAST(parent)
        var_def.set_declaration(obj)
        i += 2
        if (tokens_type[i] == my_token.IDENTIFIER) or my_token.is_number(tokens_type[i]):
            if my_token.is_operator(tokens_type[i + 1]):
                obj, i, error = bin_op_parse(i, tokens_str, tokens_type, parent)
                if obj is None:
                    print(error)
                    return None, i, error
                var_def.set_value(obj)
            # elif tokens_type[i + 1] == my_token.SEMI:
            elif tokens_type[i + 1] == my_token.LPAR:
                j = i + 1
                while tokens_type[j] != my_token.RPAR:
                    j += 1
                if tokens_type[j] == my_token.RPAR:
                    j += 1
                if my_token.is_operator(tokens_type[j + 1]):
                    obj, i, error = bin_op_parse(i, tokens_str, tokens_type, parent)
                    if obj is None:
                        print(error)
                        return None, i, error
                    var_def.set_value(obj)
            else:
                if (tokens_type[i] == my_token.INT_NUMBER) and (var_def.var_dec.type == 'int'):
                    var_def.set_value(int(tokens_str[i]))
                elif (tokens_type[i] == my_token.DOUBLE_NUMBER) and (var_def.var_dec.type == 'double'):
                    var_def.set_value(float(tokens_str[i]))
                elif tokens_type[i] == my_token.IDENTIFIER:
                    obj = parent.get_var_def(tokens_str[i])
                    if obj is not None:
                        error = "Переменная с именем " + tokens_str[i] + " не инициализирована."
                        print(error)
                        return None, i, error
                    var_def.set_value(obj)
    return var_def, i, error


def func_parse(i: int, tokens_str, tokens_type, parent: ast.BaseAST) \
        -> Tuple[Union[ast.FunctionDefAST, None], int, str]:
    pass


def func_call_parse(i: int, tokens_str, tokens_type, parent) -> Tuple[Union[ast.FunctionCallAST, None], int, str]:
    error = ""
    name = ""
    args = []
    if tokens_type[i] == my_token.IDENTIFIER:
        name = tokens_str[i]
    i += 1
    if tokens_type[i] == my_token.LPAR:
        i += 1
        while tokens_type[i] != my_token.RPAR:
            if my_token.is_number(tokens_type[i]):
                if tokens_type[i] == my_token.INT_NUMBER:
                    numb = ast.IntNumericAST(int(tokens_str[i]))
                    args.append(numb)
                elif tokens_type[i] == my_token.DOUBLE_NUMBER:
                    numb = ast.DoubleNumericAST(float(tokens_str[i]))
                    args.append(numb)
            elif tokens_type[i] == my_token.IDENTIFIER:
                obj = parent.get_names(tokens_str[i])
                if obj is None:
                    error = "Переменная с имененем " + tokens_str[i] + " не объявлена."
                    print(error)
                    return None, i, error
                args.append(tokens_str[i])
            i += 1

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
                if tokens_type[rpn[k] + 1] == my_token.LPAR:
                    func_call_obj, i, error = func_call_parse(rpn[k], tokens_str, tokens_type, parent)
                    if func_call_obj is None:
                        # error = "Функция с именем " + tokens_str[i] + " вызвана некорректно."
                        print(error)
                        return None, i, error
                    else:
                        stack.append(func_call_obj)
                else:
                    var_def_obj = ast.VarDefAST(parent)
                    var_def_obj.set_declaration(obj)
                    stack.append(var_def_obj)
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
            parent.add_name(tokens_str[i], dunc_obj)
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
        # elif tokens_type[i] == my_token.RETURN:
        #     i += 1
        #     obj, i, error = expr_parse(i, tokens_str, tokens_type, parent)
        #     if obj is None:
        #         print(error)
        #         return None
        #     if parent.__class__ == ast.FunctionDefAST:
        #         parent.add_return_value(obj)
        #     else:
        #         error = "Недопустимая конструкция: return в " + parent.__class__.__name__
        #         print(error)
        #         return None
    return dunc_obj, i, error


def compound_expression_parse(i: int, tokens_str: List[str], tokens_type, compound_expression):
    obj, i, error = parse(i, tokens_str, tokens_type, parent=compound_expression)
    if error != "":
        print(error)
        return None, i, error
    compound_expression.set_child(obj)
    return compound_expression, i, error


def expr_parse(i: int, tokens_str: List[str], tokens_type, parent=None):
    if (tokens_type[i] == my_token.IDENTIFIER) or my_token.is_number(tokens_type[i]):
        if my_token.is_operator(tokens_type[i + 1]):
            obj, i, error = bin_op_parse(i, tokens_str, tokens_type, parent)
            if obj is None:
                print(error)
                return None, i, error
            return obj, i, ""
        if tokens_type[i] == my_token.IDENTIFIER:
            # if my_token.is_operator(tokens_type[i + 1]):
            #     obj, i, error = bin_op_parse(i, tokens_str, tokens_type, parent)
            #     if obj is not None:
            #         print(error)
            #         return None, i, error
            #     return obj, i, ""
            if tokens_type[i + 1] == my_token.RPAR:
                j = i + 1
                while tokens_type[j] != my_token.LPAR:
                    j += 1
                if tokens_type[j] == my_token.LPAR:
                    j += 1
                if my_token.is_operator(tokens_type[j]):
                    obj, i, error = bin_op_parse(i, tokens_str, tokens_type, parent)
                    if obj is None:
                        print(error)
                        return None, i, error
                    return obj, i, ""
                else:
                    obj, i, error = func_call_parse(i, tokens_str, tokens_type, parent)
                    if obj is None:
                        print(error)
                        return None, i, error
                    return obj, i, ""
            else:
                var_def_obj = parent.get_var_def(tokens_str[i])
                if var_def_obj is None:
                    error = "Переменная с именем " + tokens_str[i] + " не инициализирована."
                    print(error)
                    return None, i, error
                # var_def_obj = ast.VarDefAST(parent)
                # var_def_obj.set_declaration(obj)
                return var_def_obj, i, ""
        elif tokens_type[i] == my_token.INT_NUMBER:
            obj = ast.IntNumericAST(int(tokens_str[i]))
            return obj, i, ""
        elif tokens_type[i] == my_token.DOUBLE_NUMBER:
            obj = ast.DoubleNumericAST(float(tokens_str[i]))
            return obj, i, ""


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
    elif tokens_type[i] == my_token.IF:
        obj, i, error = expr_if_parse(i, tokens_str, tokens_type, parent)
    elif tokens_type[i] == my_token.DO:
        # вызов разбора do while
        obj, i, error = expr_do_while_parse(i, tokens_str, tokens_type, parent)
    elif tokens_type[i] == my_token.WHILE:
        # вызок разбора while
        obj, i, error = expr_while_parse(i, tokens_str, tokens_type, parent)
    elif tokens_type[i] == my_token.RETURN:
        i += 1
        obj, i, error = expr_parse(i, tokens_str, tokens_type, parent)
        if obj is None:
            print(error)
            return None
        if parent.__class__ == ast.FunctionDefAST:
            parent.add_return_value(obj)
            i += 1
        else:
            error = "Недопустимая конструкция: return в " + parent.__class__.__name__
            print(error)
            return None
    return obj, i, error


def expr_if_parse(i: int, tokens_str: List[str], tokens_type, parent=None):
    error = ""
    if tokens_type[i] == my_token.IF:
        if_ast = ast.ExprIfAST(parent=parent)
        i += 1
        if (tokens_type[i] == my_token.IDENTIFIER) or \
                (tokens_type[i] == my_token.INT_NUMBER) or (tokens_type[i] == my_token.DOUBLE_NUMBER) \
                or (tokens_type[i] == my_token.BOOL):
            obj, i, error = expr_parse(i, tokens_str, tokens_type, parent)
            if_ast.set_expression(obj)
        else:
            error = "Ожидается выражение"
            print(error)
            return None, i, error
        if tokens_type[i] == my_token.LBRACE:
            i += 1
            # разбор тела
            if_body = ast.CompoundExpression(parent=if_ast)
            while tokens_type[i] != my_token.RBRACE:
                if_body, i, error = compound_expression_parse(i, tokens_str, tokens_type, if_body)
                i += 1
            if error != "":
                print(error)
                return None, i, error
            if_ast.set_body(if_body)
            if tokens_type[i] == my_token.RBRACE:
                i += 1
                if tokens_type[i] == my_token.ELSE:
                    i += 1
                    if tokens_type[i] == my_token.LBRACE:
                        i += 1
                        else_body = ast.CompoundExpression(parent=if_ast)
                        while tokens_type[i] != my_token.RBRACE:
                            else_body, i, error = compound_expression_parse(i, tokens_str, tokens_type, else_body)
                            i += 1
                        if error != "":
                            print(error)
                            return None, i, error
                        if_ast.set_else(else_body)
                    else:
                        error = "Ожидается открывающая фигурная скобка"
                        print(error)
                        return None, i, error
                else:
                    i -= 1
        return if_ast, i, error


def expr_while_parse(i: int, tokens_str: List[str], tokens_type, parent=None):
    while_expr = None
    error = ""
    while tokens_type[i] != my_token.RBRACE:
        if tokens_type[i] == my_token.WHILE:
            while_expr = ast.ExprWhileAST(parent)
            i += 1
            continue
        elif (tokens_type[i] == my_token.IDENTIFIER) or \
             (tokens_type[i] == my_token.INT_NUMBER) or (tokens_type[i] == my_token.DOUBLE_NUMBER):
            # выражение TODO: разбор условия
            expr = ast.BinaryAST(while_expr)
            expr, i, error = bin_op_parse(i, tokens_str, tokens_type, expr)
            # expr = ast.CompoundExpression(while_expr)
            # expr, i, error = compound_expression_parse(i, tokens_str, tokens_type, expr)
            if error != "":
                print(error)
                return None, i, error
            while_expr.set_expression(expr)

        elif tokens_type[i] == my_token.LBRACE:
            i += 1
            # разбор тела
            compound_expression = ast.CompoundExpression(parent=while_expr)
            while tokens_type[i] != my_token.RBRACE:
                compound_expression, i, error = compound_expression_parse(i, tokens_str,
                                                                          tokens_type, compound_expression)
                i += 1
            if error != "":
                print(error)
                return None, i, error
            while_expr.set_body(compound_expression)
    return while_expr, i, error


def expr_do_while_parse(i: int, tokens_str: List[str], tokens_type, parent=None):
    error = ""
    expr_do = None
    while tokens_type[i] != my_token.WHILE:
        if tokens_type[i] == my_token.DO:
            expr_do = ast.ExprDoWhileAST(parent)
            i += 1
            continue
        # elif tokens_type[i] == my_token.RBRACE:
        #     i += 1
        #     continue
        elif tokens_type[i] == my_token.LBRACE:
            i += 1
            # разбор тела цыкла
            compound_expression = ast.CompoundExpression(parent=expr_do)
            while tokens_type[i] != my_token.RBRACE:
                compound_expression, i, error = compound_expression_parse(i, tokens_str,
                                                                          tokens_type, compound_expression)
                i += 1
            i += 1
            if error != "":
                print(error)
                return None, i, error
            expr_do.set_body(compound_expression)

    if tokens_type[i] == my_token.WHILE:
        i += 1
        # разбор условия (выражение) TODO: разбор условия
        # expr = ast.CompoundExpression(expr_do)
        expr = ast.BinaryAST(expr_do)
        expr, i, error = bin_op_parse(i, tokens_str, tokens_type, expr)
        # expr, i, error = compound_expression_parse(i, tokens_str, tokens_type, expr)
        if error != "":
            print(error)
            return None, i, error
        expr_do.set_expression(expr)

    return expr_do, i, error


def main():
    with open("code1.txt", 'r', encoding='utf-8') as f:
        code = f.read()
    # print(code)
    tokens_str, tokens_type = get_token(code)
    print(tokens_str)
    print(tokens_type)

    root, i, error = base_parse(tokens_str, tokens_type)
    print(root)
    print(error)
    module = llvm.core.Module.new('my_module')
    root.code_gen(module)
    print(module)


if __name__ == "__main__":
    main()
