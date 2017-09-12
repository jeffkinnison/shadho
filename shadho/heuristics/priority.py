"""Claculate the priority of searching a model.
"""
import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF


def priority(feats, losses):
    if losses.ndim == 1:
        losses = losses.reshape((-1, 1))
    train_len = int(np.ceil(len(feats) * 0.8))
    scales = np.zeros((1, 50), dtype=np.float64)
    for i in range(50):
        idx = np.random.permutation(np.arange(len(feats)))
        ls = np.random.uniform(low=0.1, high=2.0)
        kernel = RBF(length_scale=ls)
        gp = GaussianProcessRegressor(kernel=kernel, normalize_y=True)
        gp.fit(feats[idx[:train_len]], losses[idx[:train_len]])
        scales[i] += (1.0 / gp.kernel.theta[0])

    return np.linalg.norm(np.max(scales) - np.min(scales))
