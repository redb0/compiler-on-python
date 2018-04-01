from typing import Union

import llvm.core

from my_token import INT, DOUBLE


def get_type(t: Union[str, int]):
    llvm_type = None
    if t in ["int", INT]:
        llvm_type = llvm.core.Type.int()
    elif t == ["double", DOUBLE]:
        llvm_type = llvm.core.Type.double()
    return llvm_type
