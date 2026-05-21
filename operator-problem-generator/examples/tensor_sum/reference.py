import numpy as np


def impl(x_list, initial, bias, p, need_norm=False):
    out = initial.copy()
    for x in x_list:
        out += x
    if bias is not None:
        out += bias
    if not need_norm:
        return out, None

    norm = 0.0
    for x in x_list:
        norm += np.linalg.norm(x, p)
    return out, np.float32(norm)
