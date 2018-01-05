"""Facilities for handling hyperparameter values.

Classes
-------
BaseValue
    Base class for the Value data model.
"""


class BaseValue(object):
    """Hyperparameter value data model.

    Hyperparameter search values are of arbitrary type and must be related to
    both a Domain and a Result. This class is essentially a placeholder that
    allows `shadho` to play nicely with both relational and non-relational
    databases.

    Notes
    -----
    I'm open to suggestions about organizing the `shadho` data model much more
    better.
    """

    __tablename__ = 'values'
