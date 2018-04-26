from typing import Union

import llvm.core

from my_token import INT, DOUBLE, BOOL


def get_type(t: Union[str, int]):
    llvm_type = None
    if t in ["int", INT]:
        llvm_type = llvm.core.Type.int()
    elif t in ["double", DOUBLE]:
        llvm_type = llvm.core.Type.double()
    elif t in ['bool', BOOL]:
        llvm_type = llvm.core.Type.int()
    return llvm_type
