# арифметические операции
# OPERATOR_UP = 1
OPERATOR_UM = 0  # '-'
OPERATOR_POWER = 1  # '**'
OPERATOR_MUL = 2  # '*'
OPERATOR_DIV = 3  # '/'
PLUS = 4  # '+'
MINUS = 5  # '-'

# операции сравнения
LARGER = 6  # '>'
LARGER_OR_EQUAL = 7  # '>='
LESS = 8  # '<'
LESS_OR_EQUAL = 9  # '<='

EQUAL = 10  # '=='
NOT_EQUAL = 11  # '!='

# оператор присваивания
ASSIGN = 12  # '='

# логические операторы
AND = 13  # 'and'
OR = 14  # 'or'
NOT = 15  # 'not'

IDENTIFIER = 16
NUMBER = 17

DEF_FUNC = 18  # "def"
# DEC_FUNC = 19

# DEF_VAR = 20
# DEC_VAR = 21

IF = 19  # 'if'
ELSE = 20  # 'else'

WHILE = 21  # 'while'
DO = 22  # 'do'

LPAR = 23  # '('
RPAR = 24  # ')'

LBRACE = 25  # '{'
RBRACE = 26  # '}'

COMMA = 27  # ','
SEMI = 28  # ';'

DEF_VAR = 29  # 'var'

INT = 30
DOUBLE = 31
BOOL = 32
RETURN = 33
ARROW = 34

END_OF_STR = 49
END_OF_FILE = 50

tokens = {"def": DEF_FUNC,
          "if": IF,
          "else": ELSE,
          "while": WHILE,
          "do": DO,
          "and": AND,
          "or": OR,
          "not": NOT,
          "(": LPAR,
          ")": RPAR,
          "{": LBRACE,
          "}": RBRACE,
          ",": COMMA,
          ";": SEMI,
          "\n": END_OF_STR,
          "-": MINUS,
          "+": PLUS,
          "*": OPERATOR_MUL,
          "/": OPERATOR_DIV,
          "**": OPERATOR_POWER,
          ">": LARGER,
          ">=": LARGER_OR_EQUAL,
          "<": LESS,
          "<=": LESS_OR_EQUAL,
          "==": EQUAL,
          "=": ASSIGN,
          "!=": NOT_EQUAL,
          "var": DEF_VAR,
          "int": INT,
          "double": DOUBLE,
          "bool": BOOL,
          "return": RETURN,
          "->": ARROW}


def is_operator(token: int) -> bool:
    op = [OPERATOR_UM, OPERATOR_POWER, OPERATOR_MUL, OPERATOR_DIV,
          PLUS, MINUS,
          LARGER, LARGER_OR_EQUAL, LESS, LESS_OR_EQUAL, EQUAL, NOT_EQUAL,
          ASSIGN,
          AND, OR, NOT]
    if token in op:
        return True
    else:
        return False
