# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd

def _to_np(a):
    if isinstance(a, (pd.Series, pd.DataFrame)):
        return a.to_numpy()
    return np.asarray(a)

def mae(y, yhat):
    y, yhat = _to_np(y), _to_np(yhat)
    return np.mean(np.abs(y - yhat))

def rmse(y, yhat):
    y, yhat = _to_np(y), _to_np(yhat)
    return np.sqrt(np.mean((y - yhat) ** 2))

def mape(y, yhat, eps=1e-8):
    y, yhat = _to_np(y), _to_np(yhat)
    mask = y > 0
    if np.sum(mask) == 0:
        return np.nan
    return np.mean(np.abs((yhat[mask] - y[mask]) / (y[mask] + eps)))

def wmape(y, yhat, eps=1e-8):
    y, yhat = _to_np(y), _to_np(yhat)
    denom = np.sum(np.abs(y)) + eps
    return np.sum(np.abs(y - yhat)) / denom
