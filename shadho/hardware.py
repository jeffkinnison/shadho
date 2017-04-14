# -*- coding: utf-8 -*-
"""Helper for grouping similar hardware.

Classes
-------
ComputeClass: Group distributed compute nodes by hardware properties.
"""
import numpy as np

import work_queue


class ComputeClass(object):
    """Group distributed compute nodes by hardware properties.

    Parameters
    ----------
    name : str
        The name of the compute class.
    resource : str
        The name of the required resource.
    value : str | int
        The value of the required resource.
    max_tasks : int
        The expected maximum number of concurrent tasks to run.
    assignments : {None, list(shadho.tree.SearchTree)}
        The list of search spaces assigned to this compute class.

    Notes
    -----
    The assignments are set by shadho.HyperparameterSearch as searches are
    conducted. When using the two together, there is no need to explicity
    assign search spaces to hardware.

    """
    def __init__(self, name, resource, value, max_tasks, assignments=None):
        self.name = name
        self.resource = resource
        self.value = value
        self.max_tasks = max_tasks
        self.submitted_tasks = 0
        self.assignments = assignments if assignments is not None else []

    def clear_assignments(self):
        """Clear the current set of assignments.

        Notes
        -----
        This method is called by shadho.HyperparameterSearch when updating
        assignments.
        """
        self.assignments = []

    def assign(self, a):
        """Add an assignment.

        Parameters
        ----------
        a : shadho.tree.SearchTree
            A search space that should be run on the hardware specified by this
            ComputeClass.
        """
        self.assignments.append(a)

    def generate(self):
        """Generate sets of values to search from the assignments.

        Because a ComputeClass may have multiple assignments, each assignment
        is weighted by its rank (position within the Ordered Search Forest).
        Values are generated proportional to the rank.

        Returns
        -------
        specs : list(dict)
            The list of hyperparameters to search.
        """
        n_tasks = self.max_tasks - self.submitted_tasks
        specs = []

        ranks = np.array([float(a.rank) for a in self.assignments])
        ranks = (ranks / np.sum(ranks))[::-1]
        print(ranks)

        for i in range(n_tasks):
            idx = np.random.choice(len(self.assignments), p=ranks)
            specs.append((self.assignments[idx].id,
                          self.assignments[idx].generate()))

        self.submitted_tasks = self.max_tasks

        return specs

    def __str__(self):
        kids = ' '.join([str(a.root.children[0].name)
                         for a in self.assignments])
        return ' '.join([self.name, ': [', kids, ']'])
