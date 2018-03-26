from typing import Tuple, Union

# from llvm import Value

import my_token


# базовый класс
class BaseAST:
    def __init__(self, parent=None):
        self.parent = parent
        self.names = {}

    def code_gen(self):
        pass

    def get_names(self, name: str):
        try:
            obj = self.names[name]
            return obj
        except KeyError:
            if self.parent is not None:
                self.parent.get_names(name)
            else:
                return None

    def add_name(self, name: str, obj) -> None:
        self.names[name] = obj

    def set_parent(self, value):
        self.parent = value


# Определение переменной "var x int"
class VarDecAST(BaseAST):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.name = ""
        self.type = None

    def set_name(self, value: str) -> None:
        self.name = value

    def set_type(self, value) -> None:
        self.type = value

    def code_gen(self):
        pass


# присвоение значения переменной
# class VarDefAST(BaseAST):
#     def __init__(self, declaration, parent=None):
#         super().__init__(parent)
#         self.var_dec = declaration
#
#     def code_gen(self):
#         pass

class IntNumericAST(BaseAST):
    def __init__(self, value: int, parent=None):
        super().__init__(parent)
        self.value = value

    def code_gen(self):
        pass


class DoubleNumericAST(BaseAST):
    def __init__(self, value: float, parent=None):
        super().__init__(parent)
        self.value = value

    def code_gen(self):
        pass


# функция
class FunctionDefAST(BaseAST):
    def __init__(self, name: str, args, t: int, body, parent=None):
        super().__init__(parent)
        self.name = name
        self.args = args
        self.type = t
        self.body = body

    def code_gen(self):
        pass


class Body(BaseAST):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.expr = []

    def set_parent(self, value):
        self.parent = value

    def add_expr(self, expr):
        self.expr.append(expr)

    def code_gen(self):
        pass


class CompoundExpression(BaseAST):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.index = 0

    def set_index(self, value):
        self.index = value

    def code_gen(self):
        pass


# вызов функции
class FunctionCallAST(BaseAST):
    def __init__(self, func, args, parent=None):
        super().__init__(parent)
        self.func_callee = func
        self.args = args

    def set_parent(self, value):
        self.parent = value

    def code_gen(self):
        pass


class BinaryAST(BaseAST):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.operator = -1
        self.lhs = None
        self.rhs = None

    def set_lhs(self, value: BaseAST) -> None:
        self.lhs = value

    def set_rhs(self, value: BaseAST) -> None:
        self.rhs = value

    def set_op(self, value: int) -> None:
        self.operator = value

    def is_valid(self) -> bool:
        if (self.operator >= 0) and (self.lhs is not None) and (self.rhs is not None):
            return True
        else:
            return False

    def code_gen(self):
        pass


def generate_ast(tokens_str, tokens_type):
    i = 0
    error = ""
    while i < len(tokens_type):
        if tokens_type[i] == my_token.DEF_FUNC:
            name_func = ""
            func_type = 0
            i += 1
            while tokens_type[i] != my_token.RBRACE:
                if (tokens_type[i] == my_token.IDENTIFIER) and (tokens_type[i-1] == my_token.DEF_FUNC):
                    name_func = tokens_str[i]
                    i += 1
                    continue
                if tokens_type[i] == my_token.RPAR:
                    i += 1
                    args = []
                    while tokens_type[i] != my_token.LPAR:
                        if tokens_type[i] == my_token.IDENTIFIER:
                            if is_type(tokens_type[i + 1]):
                                a = VarDecAST(tokens_type[i], tokens_type[i+1])
                                args.append(a)
                                i += 2
                            else:
                                error = "Ошибка объявления функции " + name_func
                                print(error)
                                return None, error
                    i += 1
                if tokens_type[i] == my_token.ARROW:
                    i += 1
                    if is_type(tokens_type[i]):
                        func_type = tokens_type[i]
                    else:
                        error = "Ошибка объявления функции " + name_func + ". Не указан возвращаемый тип."
                        print(error)
                        return None, error
                if tokens_type[i] == my_token.LBRACE:
                    i += 1
                    while tokens_type[i] != my_token.RBRACE:
                        pass
#                     TODO: дописать!!!!


def compound_expression_parse(i, tokens_str, tokens_type, parent):
    j = 0
    while tokens_type[i] != my_token.RBRACE:
        exp = CompoundExpression()
        exp.set_index(j)
        exp.set_parent(parent)
        if tokens_type[i] == my_token.SEMI:
            j += 1
            v, i, err = var_parse(i, tokens_str, tokens_type, exp)
            if err != "":
                pass

#         TODO: дописать!!!


def is_type(token):
    """
    Функция проверки на допустимый тип.
    :param token: точен, представлен в виде целого числа.
    :return: True - если допустимый тип, False - в противном случае.
    """
    t = [my_token.INT, my_token.DOUBLE, my_token.BOOL]
    if token in t:
        return True
    else:
        return False


def main():
    pass

if __name__ == "__main__":
    main()

