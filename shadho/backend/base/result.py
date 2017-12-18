"""Facilities for working with hyperparameter optimization task results.

Classes
-------
BaseResult
    Base class for Result data models.

"""
import numpy as np


class BaseResult(object):
    """Base class for Result data models"""
    
    def to_feature_vector(self):
        """Transform this result and its associated values into a vector.

        Returns
        -------
        v : `numpy.ndarray`
            A vector length n containing n - 1 hyperparameter values and their
            associated loss. Loss is stored in the last element.

        Notes
        -----
        There is no standardized order to the features across all runs of
        `shadho`, however for a particular run the features are ordered by the
        `id` attribute of the space that generated them. This ensures that the
        order always the same for a particular tree or set of search spaces.
        """
        v = np.zeros(len(self.values) + 1, dtype=np.float64)
        self.values.sort(key=lambda x: x.space_id)
        for i in range(len(self.values)):
            try:
                v[i] += self.values[i].to_numeric()
            except TypeError:
                continue
        try:
            v[-1] += self.loss
        except TypeError:
            # Happens in the case that result.loss is non-numeric
            pass
        return v
