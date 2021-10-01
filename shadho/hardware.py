"""Facilities for grouping distributed hardware and search spaces.

Classes
-------
ComputeClass
    Group hardware by a common property.
"""
import uuid
import sys

from pyrameter.optimizer import FMin


class ComputeClass(object):
    """Group hardware by a common property.

    When working with heterogeneous distributed hardware (e.g., multiple
    clusters, multiple cloud services), it is often useful to group machines by
    a common resource. ComputeClass allows SHADHO to target specific hardware
    for running specific tasks. Hardware may be grouped by:

        * CPU count
        * Available RAM
        * GPU model
        * GPU count
        * Other accelerators
        * and by arbitrary, user-defined values.

    Parameters
    ----------
    name : str
        User-level name for the compute class (e.g. "8-core", "1080ti", etc.).
    resource : str
        The name of the resource common to this group.
    value
        The value of the resource common to this group.
    max_queued_tasks : int
        The maximum number of tasks to queue. Recommended to be 1.5-2x the
        number of expected nodes with this resource.
    
    Attributes
    ----------
    id : str
        Internal id of this ComputeClass.
    name : str
        User-level name for the compute class (e.g. "8-core", "1080ti", etc.).
    resource : str
        The name of the resource common to this group.
    value
        The value of the resource common to this group.
    max_queued_tasks : int
        The maximum number of tasks to queue. Recommended to be 1.5-2x the
        number of expected nodes with this resource.
    current_tasks : int
        The current number of queued tasks.

    See Also
    --------
    `pyrameter.ModelGroup`
    """
    def __init__(self, name, resource, value, max_queued_tasks):
        self.id = str(uuid.uuid4())
        self.name = name
        self.resource = resource
        self.value = value
        self.max_queued_tasks = max_queued_tasks
        self.current_tasks = 0
        self.searchspaces = []

    def __hash__(self):
        return hash((self.id, self.name, self.resource, self.value))

    def add_searchspace(self, searchspace):
        """Add a search space to this compute class.

        Parameters
        ----------
        searchspace : `pyrameter.searchspace.SearchSpace` or list
            The search space(s) to add to this compute class.
        """
        if isinstance(searchspace, list):
            self.searchspaces.extend(searchspace)
        else:
            self.searchspaces.append(searchspace)

    def remove_searchspace(self, ssid):
        """Remove a search space from this compute class.

        Parameters
        ----------
        model_id : str
        """
        idx = None
        for i, ss in enumerate(self.searchspaces):
            if ss.id == ssid:
                idx = i
                break
        if idx is not None:
            self.searchspaces.pop(idx)

    def clear(self):
        """Remove all models from this compute class."""
        self.searchspaces = []

