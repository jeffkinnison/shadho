"""Facilities for representing machine learning models.

Classes
-------
BaseModel
    Base class for the Model data model.
"""

from shadho.heuristics import priority


class BaseModel(object):
    """Machine learning model data model"""

    __tablename__ = 'models'

    def add_domain(self, domain):
        """Add a hyperparameter domain to the model.

        Parameters
        ----------
        domain : `BaseDomain`
            The domain to add to this model.

        Notes
        -----
        This method should be overridden in subclasses to add appropriate
        handling for the data storage backend.
        """
        raise NotImplementedError

    def add_result(self, result):
        """Add a task result to the model.

        Parameters
        ----------
        result : `BaseResult`
            The result to add to this model.

        Notes
        -----
        This method should be overridden in subclasses to add appropriate
        handling for the data storage backend.
        """
        raise NotImplementedError
