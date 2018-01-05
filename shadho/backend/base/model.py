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

    def calculate_complexity(self):
        """Calculate the complexity of the search respresented by this model.

        The complexity is an approximation of the size of the search as the sum
        of the size of each degree of freedom (leaf node). Trees with a higher
        complexity score will be allocated more searches on higher-performing
        hardware or a greater number of searches in the case that hardware is
        not specified.

        Notes
        -----
        The complexity is stored internally in each instance of the Tree class.

        See Also
        --------
        `shadho.heuristics.priority`
        """
        c = 0.0
        for domain in self.domains:
            c += domain.complexity

        self.complexity = c

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
