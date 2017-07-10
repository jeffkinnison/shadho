"""Helper functions to scale values linearly or logarithmically.

Functions
---------
linear
ln
log_10
log_2

Notes
-----
The functions in this module attempt to preserve the input type when possible.
The user will expect to see an integer when an integer is input, or a string
when a string is input.
"""
import numpy as np


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
        t = type(x)
        x = t(coeff * np.power(x, degree))
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
    return np.exp(value)


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
    :math:`2^x`

    Notes
    -----
    This function preserves the type of `x` using an explicit cast. Passing
    an int will return an int, a float will return a float, a string will
    return a string, etc.

    The exception to this rule is when an `x` less than 0 is supplied. In this
    case the return value will always be floating-point.
    """
    t = type(x)
    res = np.exp2(x)
    if x < 0:
        return res
    else:
        return t(res)
