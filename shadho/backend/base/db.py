"""Base backend class that splits search spaces into disjoint trees.

Classes
-------
BaseBackend
    Base class for other backends to subclass.
"""
from shadho.backend.base.model import Model
from shadho.backend.base.domain import Domain
from shadho.backend.base.result import Result
from shadho.backend.base.value import Value

import copy


class BaseBackend(object):
    """Base class with common functionality for other backend classes."""

    def create(self, objclass):
        """Create a new instance of a data model object.

        Parameters
        ----------
        objclass : {'model', 'domain', 'result', 'value'}
            Name of the object class to be created.

        Returns
        -------
        obj : {Model, Domain, Result, Value}
            A new instance of the specified object class.

        Raises
        ------
        InvalidObjectClassError
            Raised when an invalid object class is supplied.
        """
        raise NotImplementedError

    def find(self, objclass, id):
        """Find an object in the database by class and id.

        Parameters
        ----------
        objclass : {'model', 'domain', 'result', 'value'}
            Name of the object class to be created.

        Returns
        -------
        obj : {BaseModel, BaseDomain, BaseResult, BaseValue} or None
            The object of class ``objclass`` with id ``id`` if it exists,
            otherwise None.

        Raises
        ------
        InvalidObjectClassError
            Raised when an invalid object class is supplied.
        """
        raise NotImplementedError

    def update(self, obj):
        """Update an object in the database.

        Parameters
        ----------
        obj : object id or BaseModel or BaseDomain or BaseResult or BaseValue
            Id or instance of the object to update.

        Notes
        -----
        If the supplied object does not exist in the database, updating will
        add an entry for it.
        """
        raise NotImplementedError

    def delete(self, obj):
        """Remove an existing object from the database.

        Parameters
        ----------
        obj : object id or BaseModel or BaseDomain or BaseResult or BaseValue
            Id or instance of the object to delete.

        Notes
        -----
        If the specified object does not exist in the database, no action is
        taken.
        """
        raise NotImplementedError

    def commit(self):
        """Commit pending changes.

        Notes
        -----
        Subclasses should use this method to implement batch updates for
        performance.
        """
        raise NotImplementedError

    def make_forest(self, spec, use_complexity=True, use_priority=True):
        """Create the forest of models and search spaces.

        Parameters
        ----------
        spec : dict
            The forest specification.
        use_complexity : bool, optional
            If True, initialize the forest to use the complexity heuristic.
        use_priority : bool, optional
            If True, initialize the forest to use the priority heuristic.

        Returns
        -------
        models : list of object ids
            The ids of each tree in the forest. If ``use_complexity`` is True,
            ids are ordered by tree complexity.
        """
        leaves = self.split_spec(spec)
        complexity = 0 if use_complexity else None
        priority = [1] if use_priority else None  # Record priority over time
        rank = 1 if use_complexity or use_priority else None

        models = []
        for leafset in leaves:
            model = self.create('model', priority=priority,
                                complexity=complexity, rank=rank)
            for leaf in leafset:
                domain = self.create('domain')
                model.add_domain(domain)
                self.update(domain)
                if use_complexity:
                    model.complexity += domain.complexity
            model.spaces.sort(key=lambda x: x.complexity)
            self.update(model)
        models.append(model)

        return self.update_rank(trees)

    def split_spec(self, spec, path=''):
        """Split a specification into a forest of trees.

        Parameters
        ----------
        spec : dict
            The specification to build from.
        path : str
            The string denoting the current place within the specification.

        Returns
        -------
        spaces : list of list of dict
            The set of disjoint search spaces created from this specification.

        Notes
        -----
        Instead of creating an explicit tree, this method takes advantage of
        the fact that 1) Python dictionary keys are unique to a particular
        dictionary and 2) keys from nested dictionaries can form a unique
        root-to-leaf path similar to a URL. Since a single hyperparameter
        search space is always a leaf in its tree, the entire tree can be
        reconstructed on-the-fly by keeping track of the search spaces it
        contains and storing the path to each space as an attribute in each
        space.
        """
        # Recursive base case.
        if not isinstance(spec, dict):
            spec = {
                'domain': spec,
                'strategy': 'random',
                'scaling': 'linear',
            }

        if all(key in spec for key in ('domain', 'strategy', 'scaling')):
            # To facilitate domain reuse, create a deep copy of spec and
            # assign it a path.
            c = copy.deepcopy(spec)
            c['path'] = path
            return [[c]]

        # Recurse through subtrees to create the path from root to leaf and
        # split into disjoint search spaces.
        exclusive = 'exclusive' in spec and spec['exclusive']
        optional = 'optional' in spec and spec['optional']
        spaces = [] if exclusive else [[]]
        for key in spec:
            if key not in ('exclusive', 'optional'):
                subpath = '/'.join([path, str(key)]) if path != '' \
                          else str(key)
                split = self.split_spec(spec[key], path=subpath)
                if exclusive:
                    spaces.extend(split)
                else:
                    newspaces = []
                    for space in spaces:
                        for s in split:
                            newspace = [c for c in space]
                            newspace.extend(s)
                            newspaces.append(newspace)
                    spaces = newspaces
        if optional:
            spaces.append([])
        return spaces

    def update_rank(self, ):
