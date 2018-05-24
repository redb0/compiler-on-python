#  /usr/local/bin/charm
import sys

import llvm
import llvm.core
import os

import parser
from tokenizer import get_token


def main():
    # examples/example1.txt
    # examples/functions.txt
    # examples/cycle.txt
    # examples/expr.txt
    script_path = os.path.dirname(os.path.abspath(__file__))
    file_name = sys.argv[1]
    abs_path = os.path.join(script_path, file_name)

    with open(abs_path, 'r', encoding='utf-8') as f:
        code = f.read()

    tokens_str, tokens_type = get_token(code)
    root, i, error = parser.base_parse(tokens_str, tokens_type)
    if error != "":
        print(error)
        return

    module = llvm.core.Module.new('my_module')
    root.code_gen(module)
    print(module)


if __name__ == "__main__":
    main()



