"""Helper functions to scale values linearly or logarithmically.

Functions
---------
scale_value
linear
ln
log_10
log_2

Notes
-----
The functions in this module attempt to preserve the input type when possible.
The user will expect to see an integer when an integer is input, a float when
a float is input, or a string when a string is input. The only function where
integer preservation is not possible is `ln`.
"""
import numbers
import warnings

import numpy as np


def scale_value(value, scaling):
    """Scale a value.

    Parameters
    ----------
    value
        The value to scale.
    scaling : {'linear', 'ln', 'log_10', 'log_2'} or callable
        The name of the `shadho.scaling` function to use or a function/callable
        object to apply to value.

    Returns
    -------
    scaled
        `value` scaled by `scaling` or `value` if `scaling` cannot be applied.

    Notes
    -----
    In the case that `scaling` cannot be used (i.e. it is not the name of a
    valid `shadho.scaling` function and cannot be called), a warning is issued
    and the value is returned without modification.
    """
    SCALES = {
        'linear': linear,
        'ln': ln,
        'log_10': log_10,
        'log_2': log_2
    }
    try:
        scaled = SCALES[scaling](value) if scaling in SCALES \
                 else scaling(value)
    except TypeError:
        msg = "Invalid scaling {}. {} will not be altered.".format(scaling,
                                                                   value)
        warnings.warn(msg)
        scaled = value

    return scaled


def linear(x, coeff=1.0, degree=1.0):
    """Scale a value linearly.

    The passed value will be scaled according to
    :math:`coeff\,*\,x^{degree}`.

    Parameters
    ----------
    x
        The value to scale linearly.
    coeff : float
        Multiply `x` by this.
    degree : float
        Raise `x` to this power.

    Returns
    -------
    The scaled value, or `x` if non-numeric.

    Notes
    -----
    This function preserves the type of `x` using an explicit cast. Passing
    an int will return an int, a float will return a float, a string will
    return a string, etc.
    """
    try:
        if not isinstance(x, np.ndarray):
            t = type(x)
            x = t(coeff * np.power(x, degree))
        else:
            dtype = x.dtype
            x = (coeff * np.power(x, degree)).astype(dtype)
    except TypeError:
        x = x

    return x


def ln(x):
    """Scale exponentially to base *e*.

    Parameters
    ----------
    x
        The value to scale.

    Returns
    -------
    :math:`e^x`

    Raises
    ------
    TypeError
        Raised when `x` is non-numeric.

    Notes
    -----
    This function is the only scaling function that does not preserve
    the input type. All return values are converted to floating point
    as a consequence of using base *e*.
    """
    try:
        if not isinstance(x, numbers.Number):
            raise TypeError
        x = np.exp(x)
    except TypeError:
        x = x
    return x


def log_10(x):
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
    :math:`10^x`

    Notes
    -----
    This function preserves the type of `x` using an explicit cast. Passing
    an int will return an int, a float will return a float, a string will
    return a string, etc.

    The exception to this rule is when an `x` less than 0 is supplied. In this
    case the return value will always be floating-point.
    """
    try:
        if isinstance(x, numbers.Number):
            t = type(x)
            x = np.power(10.0, x)
            if t(x) == x:
                x = t(x)
        elif isinstance(x, np.ndarray):
            dtype = x.dtype
            x = np.power(10.0, x).astype(dtype)
        else:
            raise TypeError('{} is not a numeric type, cannot take log'.format(x))
    except TypeError:
        x = x

    return x


def log_2(x):
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
    :math:`2^x`

    Notes
    -----
    This function preserves the type of `x` using an explicit cast. Passing
    an int will return an int, a float will return a float, a string will
    return a string, etc.

    The exception to this rule is when an `x` less than 0 is supplied. In this
    case the return value will always be floating-point.
    """
    try:
        if isinstance(x, numbers.Number):
            t = type(x)
            x = np.exp2(x)
            if t(x) == x:
                x = t(x)
        elif isinstance(x, np.ndarray):
            dtype = x.dtype
            x = np.exp2(x).astype(x.dtype)
        else:
            raise TypeError('{}  is not a numeric type, cannot take log'.format(x))
    except TypeError:
        x = x

    return x
