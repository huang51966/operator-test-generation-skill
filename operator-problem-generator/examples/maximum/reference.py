import numpy as np


def reference(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    return np.maximum(x, y)
