import numpy as np


def reference(x: np.ndarray) -> np.ndarray:
    return np.sum(x, axis=1)
