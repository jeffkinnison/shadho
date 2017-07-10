"""Claculate the priority of searching a model.
"""
from .check import heuristic_check

import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF


@heuristic_check
def priority(tree):
    results = np.zeros((1, len(tree.results)), dtype=np.float32)
    values = None
    for result in tree.results:
        if values is None:
            values = np.zeros((len(results, len(result.values))))
        results.append(result.loss)
        values.append([val.value for val in result.values])

    train_len = int(np.ceil(len(results) * 0.8))
    scales = np.zeros((1, 50))
    for i in range(50):
        idx = np.random.permutation(np.arange(len(results)))
        ls = np.random.uniform(low=0.1, high=2.0)
        kernel = RBF(length_scale=ls)
        gp = GaussianProcessRegressor(kernel=kernel, normalize_y=True)
        gp.fit(values[idx[:train_len]],
               results[idx[:train_len]].reshape((-1, 1)))
        scales[i] += (1.0 / gp.kernel.theta[0])

    return np.linalg.norm(np.max(scales) - np.min(scales))
