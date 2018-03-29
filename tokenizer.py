import re

from my_token import tokens, NUMBER, IDENTIFIER, SEMI, INT_NUMBER, DOUBLE_NUMBER


comment = re.compile(r"[/]{2}.*[\n]?")
operators = "+-*/!=<>"
brackets = "(){}"


def get_token(code: str):
    code = comment.sub('', code)
    # print(code)
    tokens_str = []
    tokens_type = []
    token = ""
    error = ""
    i = 0
    while i < len(code):
        print(i)
        c = code[i]
        if (c == ' ') or (c == '\n') or (c == ','):
            i += 1
            continue
        if c == ';':
            tokens_str.append(c)
            token = ""
            tokens_type.append(SEMI)
            i += 1
            continue
        if c.isdigit() or (c == '.'):
            while code[i].isdigit() or (code[i] == '.'):
                if code[i].isdigit():
                    token += code[i]
                    i += 1
                    continue
                if (code[i] == '.') and ('.' not in token):
                    token += code[i]
                    i += 1
                else:
                    error = "Ошибка"
                    return [], error
            if token.find('.') != -1:
                tokens_type.append(DOUBLE_NUMBER)
            else:
                tokens_type.append(INT_NUMBER)
            tokens_str.append(token)
            token = ""
            continue
        if c.isalnum() or (c == '_'):
            if (token == "") and c.isdigit():
                error = "Ошибка! Идентификатор не может начинаться с цыфры."
                return [], error
            else:
                while code[i].isalnum() or (code[i] == '_'):
                    token += code[i]
                    i += 1
                tokens_str.append(token)
                if token in tokens:
                    tokens_type.append(tokens.get(token))
                else:
                    tokens_type.append(IDENTIFIER)
                token = ""
                continue
        if c in brackets:
            if token == "":
                tokens_str.append(c)
                tokens_type.append(tokens.get(c))
                token = ""
                i += 1
                continue
        if c in operators:
            while code[i] in operators:
                token += code[i]
                i += 1
            if token in tokens:
                tokens_str.append(token)
                tokens_type.append(tokens.get(token))
                token = ""
                continue
            else:
                error = "Некорректный оператор"
                return [], error
    return tokens_str, tokens_type


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


# def lexer(tokens_str, tokens_type):
#     i = 0
#     while i < len(tokens_type):
#         t = tokens_type[i]
#         if t ==


def main():
    with open("code.txt", 'r', encoding='utf-8') as f:
        code = f.read()
    print(code)
    tokens_str, tokens_type = get_token(code)
    print(tokens_str)
    print(tokens_type)


if __name__ == "__main__":
    main()
