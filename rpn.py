import my_token


def get_rpn(i: int, tokens_type):
    res = []
    stack_idx = []
    error = ""
    while tokens_type[i] != my_token.SEMI:
        if tokens_type[i] == my_token.INT_NUMBER or tokens_type[i] == my_token.DOUBLE_NUMBER or tokens_type[i] in [my_token.FALSE, my_token.TRUE]:
            res.append(i)
            i += 1
            continue
        elif tokens_type[i] == my_token.IDENTIFIER:
            res.append(i)
            if tokens_type[i + 1] == my_token.LPAR:
                i += 1
                while tokens_type[i] != my_token.RPAR:
                    i += 1
                # if tokens_type[i] == my_token.LPAR:
                #     i += 1
            i += 1
            continue
        elif my_token.is_operator(tokens_type[i]):
            if tokens_type[i] == my_token.OPERATOR_POWER:  # оператор возведения в степень правоассоциативна
                if len(stack_idx) == 0:
                    stack_idx.append(i)
                else:
                    while my_token.get_priority(tokens_type[i]) > my_token.get_priority(tokens_type[stack_idx[-1]]):
                        res.append(stack_idx.pop())
                        if len(stack_idx) == 0:
                            break
                    stack_idx.append(i)
            else:
                if len(stack_idx) == 0:
                    stack_idx.append(i)
                else:
                    while (tokens_type[stack_idx[-1]] != my_token.LPAR) and \
                          (my_token.get_priority(tokens_type[i]) >= my_token.get_priority(tokens_type[stack_idx[-1]])):
                        res.append(stack_idx.pop())
                        if len(stack_idx) == 0:
                            break
                    stack_idx.append(i)
            i += 1
            continue
        elif tokens_type[i] == my_token.LPAR:
            stack_idx.append(i)
            i += 1
            continue
        elif tokens_type[i] == my_token.RPAR:
            # if len(stack_idx) != 0:
            while tokens_type[stack_idx[-1]] != my_token.LPAR:
                res.append(stack_idx.pop())
                if len(stack_idx) == 0:
                    break
            # else:
            #     stack_idx.append(i)
            if tokens_type[stack_idx[-1]] == my_token.LPAR:
                stack_idx.pop()
            else:
                error = "В выражжении неправельно расставлены скобки"
            i += 1
            continue
        else:
            break
    if len(stack_idx) != 0:
        while len(stack_idx) != 0:
            res.append(stack_idx.pop())
    print(res)
    return i, res, error


