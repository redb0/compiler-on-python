import llvm
import llvm.core

import my_token
from code_generator import get_type


# базовый класс
class BaseAST:
    def __init__(self, parent=None):
        self.parent = parent
        self.names = {}

    def code_gen(self, module):
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

    def code_gen(self, module):
        # TODO: не понял как сделать локальную переменную
        t = get_type(self.type)
        gv = module.add_global_variable(t, self.name)
        return gv


class VarDefAST(BaseAST):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.var_dec = None
        self.value = None

    def set_declaration(self, obj: VarDecAST) -> None:
        self.var_dec = obj

    def set_value(self, value) -> None:
        self.value = value


class IntNumericAST(BaseAST):
    """Целое число"""
    def __init__(self, value: int, parent=None):
        super().__init__(parent)
        self.value = value

    def code_gen(self, module):
        # тип - 32-bit целое число
        int_type = llvm.core.Type.int()
        const = llvm.core.Constant.int(int_type, self.value)
        return const


class DoubleNumericAST(BaseAST):
    """Число с плавающей запятой"""
    def __init__(self, value: float, parent=None):
        super().__init__(parent)
        self.value = value

    def code_gen(self, module):
        # тип - 64-bit число с плавающей запятой
        double_type = llvm.core.Type.double()
        const = llvm.core.Constant.int(double_type, self.value)
        return const


# составное выражение, им является базовый узел, и тело функций
class CompoundExpression(BaseAST):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.order_operations = []

    def set_child(self, obj: BaseAST) -> None:
        obj.set_parent(self)
        self.order_operations.append(obj)

    def get_var_def(self, name: str):
        for i in range(len(self.order_operations) - 1, 0, -1):
            # if self.order_operations[i].__class__ == VarDefAST:
            #     if self.order_operations[i].var_dec.name == name:
            #         return self.order_operations[i]
            if self.order_operations[i].__class__ == BinaryAST:
                if (self.order_operations[i].operator == 12) and (self.order_operations[i].lhs.__class__ == VarDecAST):
                    if self.order_operations[i].lhs.name == name:
                        return self.order_operations[i]
        return None

    def code_gen(self, module):
        pass


# функция
class FunctionDefAST(CompoundExpression):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.name = ""
        self.args = []
        self.return_values = []
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

    def add_return_value(self, obj):
        self.return_values.append(obj)

    def code_gen(self, module):
        # получаем возвращаемый функцией тип
        ret_type = get_type(self.type)

        # составляем список типов аргуметнов
        args_type = []
        for arg in self.args:
            t = get_type(arg.type)
            args_type.append(t)

        # составляем сигнатуру функции
        ty_func = llvm.core.Type.function(ret_type, args_type)

        # добавляем функцию к модулю
        func = module.add_function(ty_func, self.name)

        # называем аргументы функции
        for i in range(len(self.args)):
            func.args[i].name = self.args[i].name

        # Задаем базовый блок функции ("basic block") -
        # набор инструций, заканчивающийся return
        # По соглашению первый блок называется «запись».
        bb = func.append_basic_block("entry")

        # Добавление инструкций в блок
        builder = llvm.core.Builder.new(bb)

        # Созднание инструкций в базовом блоке.
        # команда возврата значения - ret
        # TODO: надо обойти ASTтела функции и сгенерить его.
        tmp = builder.add(f_sum.args[0], f_sum.args[1], "tmp")
        builder.ret(tmp)

        print(module)


# class Body(BaseAST):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.expr = []
#
#     def set_parent(self, value):
#         self.parent = value
#
#     def add_expr(self, expr):
#         self.expr.append(expr)
#
#     def code_gen(self, module):
#         pass


# вызов функции
class FunctionCallAST(BaseAST):
    def __init__(self, func, args, parent=None):
        super().__init__(parent)
        self.func_callee = func
        self.args = args

    def set_parent(self, value):
        self.parent = value

    def code_gen(self, module):
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

    def code_gen(self, module):
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

    def code_gen(self, module):
        pass


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

    def code_gen(self, module):
        pass


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

    def code_gen(self, module):
        pass


def is_type(token):
    """
    Функция проверки на допустимый тип.
    :param token: токен, представлен в виде целого числа.
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
