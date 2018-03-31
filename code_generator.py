from typing import Union

import llvm.core

from my_token import INT_NUMBER, DOUBLE_NUMBER


def get_type(t: Union[str, int]):
    llvm_type = None
    if t in ["int", INT_NUMBER]:
        llvm_type = llvm.core.Type.int()
    elif t == ["double", DOUBLE_NUMBER]:
        llvm_type = llvm.core.Type.double()
    return llvm_type
