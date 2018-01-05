"""Facilities for organizing hyperparameter searches.

Classes
-------
BaseExperiment
    Base class for the Experiment data model.
"""


class BaseExperiment(object):
    """Hyperparameter optimization experiment organization."""

    __tablename__ = 'experiments'

    def add_model(self, model):
        """Add a model to the experiment.

        Parameters
        ----------
        model : `BaseModel`
            The model to add to this experiment.

        Notes
        -----
        This method should be overridden in subclasses to add appropriate
        handling for the data storage backend.
        """
        raise NotImplementedError
