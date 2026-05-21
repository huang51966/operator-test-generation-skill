import numpy as np


def impl(x: np.ndarray, axis: int, keepdims: bool = False) -> np.ndarray:
    return np.sum(x, axis=axis, keepdims=keepdims)
