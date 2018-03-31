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
                obj = self.parent.get_names(name)
                return obj
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
        self.value = None

    def set_name(self, value: str) -> None:
        self.name = value

    def set_type(self, value) -> None:
        self.type = value

    def set_value(self, value):
        self.value = value

    def code_gen(self):
        pass


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


# составное выражение, им является базовый узел, и тело функций
class CompoundExpression(BaseAST):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.order_operations = []

    def set_child(self, obj: BaseAST) -> None:
        obj.set_parent(self)
        self.order_operations.append(obj)

    def code_gen(self):
        pass


# функция
class FunctionDefAST(CompoundExpression):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.name = ""
        self.args = []
        self.type = -1
        self.body = None

    def set_name(self, value):
        self.name = value

    def set_body(self, obj):
        self.body = obj

    def set_type(self, t):
        self.type = t

    def add_arg(self, arg):
        self.args.append(arg)
        self.add_name(arg.name, arg)

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


# условие if {...} else {...}
class ExprIfAST(CompoundExpression):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.expression = None
        self.body = None
        self.else_body = None

    def set_expression(self, expr):
        self.expression = expr

    def set_body(self, obj):
        self.body = obj

    def set_else(self, expr):
        self.else_body = expr


# цикл while ... {...}
class ExprWhileAST(CompoundExpression):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.expression = None
        self.body = None

    def set_expression(self, expr):
        self.expression = expr

    def set_body(self, obj):
        self.body = obj


# цикл do {...} while ...
class ExprDoWhileAST(CompoundExpression):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.expression = None
        self.body = None

    def set_expression(self, expr):
        self.expression = expr

    def set_body(self, obj):
        self.body = obj


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
