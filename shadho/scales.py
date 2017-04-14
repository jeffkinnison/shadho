# -*- coding: utf-8 -*-
"""Helper functions to standardize scaling search spaces.

Functions
---------
get_scale : function
    Get a scaling function by name.
linear : numeric
    Scale linearly.
ln : numeric
    Scale to e**x.
log10 : numeric
    Scale to 10**x.
log2 : numeric
    Scale to 2**x.
"""
import numbers

import numpy as np


def get_scale(name):
    """Get a scaling function from this module.

    Parameters
    ----------
    name : str
        Name of the scaling function to retrieve. One of 'linear', 'ln',
        'log10', or 'log2'.

    Returns
    -------
    The specified scaling function.
    """
    if name == 'ln':
        return ln
    elif name == 'log10':
        return log10
    elif name == 'log2':
        return log2
    else:
        return linear


def linear(x, coeff=1.0, degree=1.0):
    """Scale x linearly.

    This function is used for both numeric and non-numeric values (e.g.,
    strings). Because of this, linear attempts to preserve the type of x in the
    numeric case and simply returns x in the non-numeric case.

    Parameters
    ---------
    x : numeric
        The value to scale.
    coeff : float
        Coefficient to scale by.
    degree : float
        Polynomial degree of x.

    Returns
    -------
    coeff * (x ** degree)
    """
    if isinstance(x, numbers.Number):
        t = type(x)
        return t(coeff * np.power(x, degree))
    else:
        return x


def ln(x):
    """Scale exponentially to base e.

    Parameters
    ----------
    x : numeric
        The value to scale.

    Returns
    -------
    e ** x
    """
    return np.exp(x)


def log10(x):
    """Scale exponentially to base 10.

    This function attempts to maintain the type of the input value x. The
    typical use case for this type of scaling is to generate a range of integer
    powers of 10 (e.g, [1, 10, 100, 1000, 10000]), however floating-point
    values in range (0, 1) are also common.

    Parameters
    ----------
    x : numeric
        The value to scale.

    Returns
    -------
    10 ** x
    """
    t = type(x)
    res = np.power(10.0, x)
    if x < 0:
        return res
    else:
        return t(res)


def log2(x):
    """Scale exponentially to base 2.

    This function attempts to maintain the type of the input value x. The
    typical use case for this type of scaling is to generate a range of integer
    powers of 2 (e.g, [16, 32, 64, 128, 256]).

    Parameters
    ----------
    x : numeric
        The value to scale.

    Returns
    -------
    2 ** x
    """
    t = type(x)
    res = np.exp2(x)
    if x < 0:
        return res
    else:
        return t(res)
