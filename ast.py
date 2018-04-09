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

        self._ptr = None

    def set_name(self, value: str) -> None:
        self.name = value

    def set_type(self, value) -> None:
        self.type = value

    def set_value(self, value):
        self.value = value

    def code_gen(self, module, builder=None):
        # TODO: не понял как сделать локальную переменную
        t = get_type(self.type)
        v = builder.alloca(t, name=self.name)
        self._ptr = v
        # gv = module.add_global_variable(t, self.name)
        return v

    def get_type(self):
        return self.type


class VarDefAST(BaseAST):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.var_dec = None
        self.value = None

    def set_declaration(self, obj: VarDecAST) -> None:
        self.var_dec = obj

    def set_value(self, value) -> None:
        self.value = value

    def get_type(self):
        return self.var_dec.type

    def code_gen(self, module, builder=None):
        # tmp = builder.load(self.var_dec._ptr, self.var_dec.name)
        # return tmp

        return self.var_dec._ptr


class IntNumericAST(BaseAST):
    """Целое число"""
    def __init__(self, value: int, parent=None):
        super().__init__(parent)
        self.value = value

    def code_gen(self, module, builder=None):
        # тип - 32-bit целое число
        int_type = llvm.core.Type.int()
        const = llvm.core.Constant.int(int_type, self.value)
        return const

    def get_type(self):
        return 30


class DoubleNumericAST(BaseAST):
    """Число с плавающей запятой"""
    def __init__(self, value: float, parent=None):
        super().__init__(parent)
        self.value = value

    def code_gen(self, module, builder=None):
        # тип - 64-bit число с плавающей запятой
        double_type = llvm.core.Type.double()
        const = llvm.core.Constant.int(double_type, self.value)
        return const

    def get_type(self):
        return "double"


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
            # if self.order_operations[i].__class__ == BinaryAST:
            #     if (self.order_operations[i].operator == 12) and (self.order_operations[i].lhs.__class__ == VarDefAST):
            #         if self.order_operations[i].lhs.var_dec.name == name:
            #             return self.order_operations[i]
            if self.order_operations[i].__class__ == BinaryAST:
                if (self.order_operations[i].operator == 12) and (self.order_operations[i].lhs.__class__ == VarDefAST):
                    if self.order_operations[i].lhs.var_dec.name == name:
                        return self.order_operations[i].lhs
        return None

    def code_gen(self, module, bb=None):
        # bb = module.append_basic_block(name_bb)
        # builder = llvm.core.Builder.new(bb)
        for op in self.order_operations:
            op.code_gen(module, bb)
        return module


# функция
class FunctionDefAST(CompoundExpression):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.name = ""
        self.args = []
        self.return_values = []
        self.type = -1
        self.body = None

        self.func = None

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

    def code_gen(self, module, name_bb='entry'):
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

        self.func = func

        # называем аргументы функции
        for i in range(len(self.args)):
            func.args[i].name = self.args[i].name
            self.args[i]._ptr = func.args[i]

        # Задаем базовый блок функции ("basic block") -
        # набор инструций, заканчивающийся return
        # По соглашению первый блок называется «запись».
        bb = func.append_basic_block("entry")

        # Добавление инструкций в блок
        builder = llvm.core.Builder.new(bb)
        # bb = llvm.core.Builder
        # llvm.core.Builder.new()

        # Созднание инструкций в базовом блоке.
        # команда возврата значения - ret
        # TODO: надо обойти ASTтела функции и сгенерить его.
        # tmp = builder.add(f_sum.args[0], f_sum.args[1], "tmp")
        # builder.ret(tmp)

        # self.body.code_gen(module, builder)

        for op in self.order_operations:
            op.code_gen(func, builder)

        # bb_ret = func.append_basic_block("ret_bblc")
        # Добавление инструкций в блок
        # builder = llvm.core.Builder.new(bb_ret)

        ret_bb = func.append_basic_block("ret_bblc")

        # Добавление инструкций в блок
        ret_builder = llvm.core.Builder.new(ret_bb)

        for obj in self.return_values:
            tmp = obj.code_gen(func, ret_builder)
            ret_builder.ret(tmp)

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

        self.ret = None

    def set_parent(self, value):
        self.parent = value

    def set_ret_name(self, name):
        self.ret = name

    def code_gen(self, module, builder=None):
        # ret_type = get_type(self.func_callee.type)

        args = []
        for a in self.args:
            args.append(a.code_gen(module, builder))

        tmp = builder.call(self.func_callee.func, args, name="tmp")
        print(module)
        return tmp

    def get_type(self):
        t = self.func_callee.type
        if t in ["int", my_token.INT]:
            return my_token.INT
        elif t in ["double", my_token.DOUBLE]:
            return my_token.DOUBLE
        else:
            return None


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

    def get_type(self):
        t1 = self.lhs.get_type()
        t2 = self.rhs.get_type()
        if t1 == t2:
            return t1
        else:
            return None

    def code_gen(self, module, builder=None):
        code_lhs = self.lhs.code_gen(module, builder)
        code_rhs = self.rhs.code_gen(module, builder)
        t = self.get_type()
        if t is None:
            return None
        if code_lhs is None or code_rhs is None:
            return None
        if self.operator == my_token.PLUS:
            if t == my_token.INT:
                tmp = builder.add(code_lhs, code_rhs, 'addtmp')
                return tmp
            elif t == "double":
                tmp = builder.fadd(code_lhs, code_rhs, 'addtmp')
                return tmp
        elif self.operator == my_token.MINUS:
            if t == my_token.INT:
                tmp = builder.sub(code_lhs, code_rhs, 'subtmp')
                return tmp
            elif t == "double":
                tmp = builder.fsub(code_lhs, code_rhs, 'subtmp')
                return tmp
        elif self.operator == my_token.OPERATOR_DIV:
            if t == my_token.INT:
                tmp = builder.udiv(code_lhs, code_rhs, 'divtmp')
                return tmp
            elif t == "double":
                tmp = builder.fdiv(code_lhs, code_rhs, 'divtmp')
                return tmp
        elif self.operator == my_token.OPERATOR_MUL:
            if t == my_token.INT:
                tmp = builder.mul(code_lhs, code_rhs, 'multmp')
                return tmp
            elif t == "double":
                tmp = builder.fmul(code_lhs, code_rhs, 'multmp')
                return tmp
        # не нашел есть ли в llvmpy операция возведения в степень
        elif self.operator == my_token.OPERATOR_POWER:
            # TODO: доделать
            pass

        elif self.operator == my_token.LESS:
            if t == my_token.INT:
                tmp = builder.icmp(llvm.core.IPRED_SLT, code_lhs, code_rhs, 'lttmp')
                return tmp
            elif t == "double":
                tmp = builder.fcmp(llvm.core.RPRED_OLT, code_lhs, code_rhs, 'lttmp')
                return tmp
        elif self.operator == my_token.LESS_OR_EQUAL:
            if t == my_token.INT:
                tmp = builder.icmp(llvm.core.IPRED_SLE, code_lhs, code_rhs, 'letmp')
                return tmp
            elif t == "double":
                tmp = builder.fcmp(llvm.core.RPRED_OLE, code_lhs, code_rhs, 'letmp')
                return tmp
        elif self.operator == my_token.LARGER:
            if t == my_token.INT:
                # SLE или ULE, чем отличаются???
                tmp = builder.icmp(llvm.core.IPRED_SGT, code_lhs, code_rhs, 'gttmp')
                return tmp
            elif t == "double":
                tmp = builder.fcmp(llvm.core.RPRED_OGT, code_lhs, code_rhs, 'gttmp')
                return tmp
        elif self.operator == my_token.LARGER_OR_EQUAL:
            if t == my_token.INT:
                # SLE или ULE, чем отличаются???
                tmp = builder.icmp(llvm.core.IPRED_SGE, code_lhs, code_rhs, 'getmp')
                return tmp
            elif t == "double":
                tmp = builder.fcmp(llvm.core.RPRED_OGE, code_lhs, code_rhs, 'getmp')
                return tmp
        elif self.operator == my_token.EQUAL:
            if t == my_token.INT:
                tmp = builder.icmp(llvm.core.IPRED_EQ, code_lhs, code_rhs, 'eqtmp')
                return tmp
            elif t == "double":
                tmp = builder.fcmp(llvm.core.RPRED_OEQ, code_lhs, code_rhs, 'eqtmp')
                return tmp
        elif self.operator == my_token.NOT_EQUAL:
            if t == my_token.INT:
                tmp = builder.icmp(llvm.core.IPRED_NE, code_lhs, code_rhs, 'netmp')
                return tmp
            elif t == "double":
                tmp = builder.fcmp(llvm.core.RPRED_ONE, code_lhs, code_rhs, 'netmp')
                return tmp

        elif self.operator == my_token.ASSIGN:

            tmp = builder.store(code_rhs, code_lhs)
            return tmp
        else:
            return None


# условие if ... {...} else {...}
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

    def code_gen(self, module, builder=None):
        # булево выражение, базовый блок для if, базовый блок для else.
        expr = self.expression.code_gen(module, builder)

        if_true = module.append_basic_block("IfTrue")

        # Добавление инструкций в блок
        if_true_builder = llvm.core.Builder.new(if_true)
        body = self.body.code_gen(module, if_true_builder)

        if self.else_body:
            if_false = module.append_basic_block("IfFalse")
            if_false_builder = llvm.core.Builder.new(if_false)
            else_body = self.else_body.code_gen(module, if_false_builder)

            tmp = builder.cbranch(expr, if_true, if_false)
        else:
            tmp = builder.cbranch(expr, if_true)

        return tmp


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

    def code_gen(self, module, builder=None):
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

    def code_gen(self, module, builder=None):
        pass


def is_valid_type(v1, v2):
    t1 = None
    t2 = None
    if v1.__class__ == VarDecAST:
        t1 = v1.type
    elif v1.__class__ == IntNumericAST:
        t1 = "int"
    elif v1.__class__ == DoubleNumericAST:
        t1 = "double"
    if v2.__class__ == VarDecAST:
        t2 = v2.type
    elif v2.__class__ == IntNumericAST:
        t2 = "int"
    elif v2.__class__ == DoubleNumericAST:
        t2 = "double"
    if (t1 == t2) and all([t1, t2]):
        return t1
    else:
        return None


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
