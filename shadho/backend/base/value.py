"""Facilities for handling hyperparameter values.

Classes
-------
BaseValue
    Base class for the Value data model.
"""

class BaseValue(object):
    """Hyperparameter value data model.


    """

    

    def to_numeric(self):
        """Transform the value into its numeric representation.

        Returns
        -------
        The value of this object, transformed according to
        `shadho.backend.BaseSpace.get_label`

        See Also
        --------
        `shadho.backend.BaseSpace.get_label`
        """
        return self.space.get_label(self.value)
