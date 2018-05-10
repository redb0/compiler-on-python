import llvm
import llvm.core

import my_token
from code_generator import get_type


# базовый класс
class BaseAST:
    reserved_names = {"print": None}

    def __init__(self, parent=None):
        self.parent = parent
        self.names = {}
        # self.reserved_names = {"print": None}

    def code_gen(self, module):
        pass

    def get_names(self, name: str):
        try:
            obj = self.names[name]
            return obj
        except KeyError:
            return self.parent.get_names(name) if self.parent is not None else None
            # if self.parent is not None:
            #     obj = self.parent.get_names(name)
            #     return obj
            # else:
            #     try:
            #         return self.reserved_names[name]
            #     except KeyError:
            #         return None

    def is_reserved_name(self, name: str) -> bool:
        return name in self.reserved_names.keys()
        # try:
        #     obj = self.reserved_names[name]
        #     return True
        # except KeyError:
        #     return False

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

    def get_ptr(self):
        return self._ptr

    def code_gen(self, module, builder=None):
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
        if type(self.var_dec._ptr) == llvm.core.Argument:
            return self.var_dec._ptr
        else:
            tmp = builder.load(self.var_dec._ptr, name=self.var_dec.name)
            return tmp  # self.var_dec._ptr


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
        const = llvm.core.Constant.real(double_type, self.value)
        return const

    def get_type(self):
        return my_token.DOUBLE


class BoolConstAST(BaseAST):
    def __init__(self, value: int, parent=None):
        super().__init__(parent=parent)
        if type(value) in [int, float]:
            if value == 0:
                self.value = 0
            else:
                self.value = 1
        elif type(value) is str:
            if value == "true":
                self.value = 1
            elif value == "false":
                self.value = 0

    def code_gen(self, module, builder=None):
        bool_type = llvm.core.Type.int(1)
        const = llvm.core.Constant.int(bool_type, self.value)
        return const

    def get_type(self):
        return my_token.BOOL


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

    def print_code_gen(self, module, name_bb='entry'):
        """Print Function"""
        # fn_type = llvm.core.Type.function(llvm.core.Type.void(), [llvm.core.Type.pointer(llvm.core.Type.int(8))], True)
        fn_type = llvm.core.Type.function(llvm.core.Type.int(), [llvm.core.Type.pointer(llvm.core.Type.int(8))], True)
        my_print = module.add_function(fn_type, "print")

        bb = my_print.append_basic_block(name_bb)  # ???
        builder = llvm.core.Builder.new(bb)
        builder.printf("%s\n", builder.args[0])
        builder.ret()

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

        # Созднание инструкций в базовом блоке.
        for op in self.order_operations:
            op.code_gen(func, builder)

        # print(module)

    def print_func_cg(self, module, name_bb=''):
        # кодогенераци для функции вывода print
        pass


class ReturnAst(BaseAST):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.values = []

    def add_values(self, value):
        self.values.append(value)

    def code_gen(self, func, builder=None):
        for obj in self.values:
            if isinstance(obj, VarDefAST):
                tmp = obj.var_dec.get_ptr()
            else:
                tmp = obj.code_gen(func, builder)
            builder.ret(tmp)


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
        if t1 == t2 and my_token.is_arithmetic_operator(self.operator):
            return t1
        elif t1 == t2 and my_token.is_logic_operator(self.operator):
            return my_token.BOOL
        # if t1 == t2:
        #     return t1
        else:
            return None

    def code_gen(self, module, builder=None):
        if self.operator != my_token.ASSIGN:
            code_lhs = self.lhs.code_gen(module, builder)
            code_rhs = self.rhs.code_gen(module, builder)
            if code_lhs is None or code_rhs is None:
                return None
        t = self.get_type()
        if t is None:
            return None
        # if code_lhs is None or code_rhs is None:
        #     return None
        if self.operator == my_token.PLUS:
            # if t == my_token.INT:
            if self.lhs.get_type() == my_token.INT:  #  == self.rhs.get_type()
                tmp = builder.add(code_lhs, code_rhs, 'addtmp')
                return tmp
            # elif t == my_token.DOUBLE:
            elif self.lhs.get_type() == my_token.DOUBLE:  #  == self.rhs.get_type()
                tmp = builder.fadd(code_lhs, code_rhs, 'addtmp')
                return tmp
        elif self.operator == my_token.MINUS:
            # if t == my_token.INT:
            if self.lhs.get_type() == my_token.INT:  #  == self.rhs.get_type()
                tmp = builder.sub(code_lhs, code_rhs, 'subtmp')
                return tmp
            # elif t == my_token.DOUBLE:
            elif self.lhs.get_type() == my_token.DOUBLE:  #  == self.rhs.get_type()
                tmp = builder.fsub(code_lhs, code_rhs, 'subtmp')
                return tmp
        elif self.operator == my_token.OPERATOR_DIV:
            # if t == my_token.INT:
            if self.lhs.get_type() == my_token.INT:  #  == self.rhs.get_type()
                tmp = builder.udiv(code_lhs, code_rhs, 'divtmp')
                return tmp
            # elif t == my_token.DOUBLE:
            elif self.lhs.get_type() == my_token.DOUBLE:  #  == self.rhs.get_type()
                tmp = builder.fdiv(code_lhs, code_rhs, 'divtmp')
                return tmp
        elif self.operator == my_token.OPERATOR_MUL:
            # if t == my_token.INT:
            if self.lhs.get_type() == my_token.INT:  #  == self.rhs.get_type()
                tmp = builder.mul(code_lhs, code_rhs, 'multmp')
                return tmp
            # elif t == my_token.DOUBLE:
            elif self.lhs.get_type() == my_token.DOUBLE:  #  == self.rhs.get_type()
                tmp = builder.fmul(code_lhs, code_rhs, 'multmp')
                return tmp
        # не нашел есть ли в llvmpy операция возведения в степень
        elif self.operator == my_token.OPERATOR_POWER:
            # TODO: доделать
            pass

        elif self.operator == my_token.LESS:
            # if t == my_token.INT:
            if self.lhs.get_type() == my_token.INT or self.lhs.get_type() == my_token.BOOL:  #  == self.rhs.get_type()
                tmp = builder.icmp(llvm.core.IPRED_SLT, code_lhs, code_rhs, 'lttmp')
                return tmp
            elif self.lhs.get_type() == my_token.DOUBLE:  #  == self.rhs.get_type()
            # elif t == my_token.DOUBLE:
                tmp = builder.fcmp(llvm.core.RPRED_OLT, code_lhs, code_rhs, 'lttmp')
                return tmp
        elif self.operator == my_token.LESS_OR_EQUAL:
            # if t == my_token.INT:
            if self.lhs.get_type() == my_token.INT or self.lhs.get_type() == my_token.BOOL:
                tmp = builder.icmp(llvm.core.IPRED_SLE, code_lhs, code_rhs, 'letmp')
                return tmp
            # elif t == my_token.DOUBLE:
            elif self.lhs.get_type() == my_token.DOUBLE:
                tmp = builder.fcmp(llvm.core.RPRED_OLE, code_lhs, code_rhs, 'letmp')
                return tmp
        elif self.operator == my_token.LARGER:
            # if t == my_token.INT:
            if self.lhs.get_type() == my_token.INT or self.lhs.get_type() == my_token.BOOL:  #  == self.rhs.get_type()
                # SLE или ULE, чем отличаются???
                tmp = builder.icmp(llvm.core.IPRED_SGT, code_lhs, code_rhs, 'gttmp')
                return tmp
            # elif t == my_token.DOUBLE:
            elif self.lhs.get_type() == my_token.DOUBLE:
                tmp = builder.fcmp(llvm.core.RPRED_OGT, code_lhs, code_rhs, 'gttmp')
                return tmp
        elif self.operator == my_token.LARGER_OR_EQUAL:
            # if t == my_token.INT:
            if self.lhs.get_type() == my_token.INT or self.lhs.get_type() == my_token.BOOL:
                # SLE или ULE, чем отличаются???
                tmp = builder.icmp(llvm.core.IPRED_SGE, code_lhs, code_rhs, 'getmp')
                return tmp
            # elif t == my_token.DOUBLE:
            elif self.lhs.get_type() == my_token.DOUBLE:
                tmp = builder.fcmp(llvm.core.RPRED_OGE, code_lhs, code_rhs, 'getmp')
                return tmp
        elif self.operator == my_token.EQUAL:
            # if t == my_token.INT:
            if self.lhs.get_type() == my_token.INT or self.lhs.get_type() == my_token.BOOL:
                tmp = builder.icmp(llvm.core.IPRED_EQ, code_lhs, code_rhs, 'eqtmp')
                return tmp
            # elif t == my_token.DOUBLE:
            elif self.lhs.get_type() == my_token.DOUBLE:
                tmp = builder.fcmp(llvm.core.RPRED_OEQ, code_lhs, code_rhs, 'eqtmp')
                return tmp
        elif self.operator == my_token.NOT_EQUAL:
            # if t == my_token.INT:
            if self.lhs.get_type() == my_token.INT or self.lhs.get_type() == my_token.BOOL:
                tmp = builder.icmp(llvm.core.IPRED_NE, code_lhs, code_rhs, 'netmp')
                return tmp
            # elif t == my_token.DOUBLE:
            elif self.lhs.get_type() == my_token.DOUBLE:
                tmp = builder.fcmp(llvm.core.RPRED_ONE, code_lhs, code_rhs, 'netmp')
                return tmp

        elif self.operator == my_token.ASSIGN:
            code_rhs = self.rhs.code_gen(module, builder)
            builder.store(code_rhs, self.lhs.var_dec._ptr)
            return self.lhs.var_dec._ptr
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

        func = builder.basic_block.function

        # Создание базовых блоков the и else.
        # Последовательная вставка блоков в конец текущего блока.
        then_block = func.append_basic_block('then')
        else_block = func.append_basic_block('else')
        merge_block = func.append_basic_block('ifcond')

        builder.cbranch(expr, then_block, else_block)

        # Добавить then блок в конец текущего.
        builder.position_at_end(then_block)
        then_value = self.body.code_gen(module, builder)
        builder.branch(merge_block)

        # Codegen of 'Then' can change the current block; update then_block
        # for the PHI node.
        then_block = builder.basic_block

        # Добавить else блок в конец текущего.
        builder.position_at_end(else_block)
        if self.else_body:
            else_value = self.else_body.code_gen(module, builder)
        builder.branch(merge_block)

        # Codegen of 'Else' can change the current block, update else_block
        # for the PHI node.
        else_block = builder.basic_block

        # Добалвение блока слияния
        builder.position_at_end(merge_block)
        phi = builder.phi(llvm.core.Type.double(), 'iftmp')

        phi.add_incoming(then_value, then_block)
        if self.else_body:
            phi.add_incoming(else_value, else_block)

        return phi


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
        # expr = self.expression.code_gen(module, builder)

        func = builder.basic_block.function

        expr_block = func.append_basic_block('expr')
        body_loop = func.append_basic_block('loop')
        after_block = func.append_basic_block('after')

        builder.branch(expr_block)

        builder.position_at_end(expr_block)
        expr = self.expression.code_gen(module, builder)
        print(expr)
        # end_condition_bool = builder.fcmp(
        #     llvm.core.RPRED_ONE, expr, llvm.core.Constant.real(llvm.core.Type.double(), 0),
        #     'loopcond')
        # print(end_condition_bool)
        builder.cbranch(expr, body_loop, after_block)

        expr_block = builder.basic_block

        builder.position_at_end(body_loop)
        body_code = self.body.code_gen(module, builder)
        builder.branch(expr_block)

        body_loop = builder.basic_block

        builder.position_at_end(after_block)
        # phi = builder.phi(llvm.core.Type.double(), 'looptmp')

        # phi.add_incoming(then_value, then_block)
        # if self.else_body:
        #     phi.add_incoming(else_value, else_block)

        after_block = builder.basic_block

        return after_block


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
        func = builder.basic_block.function

        body_loop = func.append_basic_block('loop')
        expr_block = func.append_basic_block('expr_block')
        before_loop = func.append_basic_block('before')

        builder.branch(body_loop)

        builder.position_at_end(body_loop)
        body_code = self.body.code_gen(module, builder)
        builder.branch(expr_block)

        body_loop = builder.basic_block

        builder.position_at_end(expr_block)
        expr = self.expression.code_gen(module, builder)
        builder.cbranch(expr, body_loop, before_loop)

        expr_block = builder.basic_block

        builder.position_at_end(before_loop)

        before_loop = builder.basic_block

        return before_loop


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
