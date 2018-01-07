"""Base backend class that splits search spaces into disjoint models.

Classes
-------
BaseBackend
    Base class for other backends to subclass.
"""
from shadho.backend.base.model import BaseModel
from shadho.backend.base.domain import BaseDomain
from shadho.backend.base.result import BaseResult
from shadho.backend.base.value import BaseValue
from shadho.heuristics import complexity, priority

import copy

import numpy as np


class BaseBackend(object):
    """Base class with common functionality for other backend classes."""

    def count(self, objclass):
        """Count the number of objects of a class.

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
            Name of the object class to search.
        id : int or str
            The id to find in the database.

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

    def find_all(self, objclass):
        """Find all objects of a particular class.

        Parameters
        ----------
        objclass : {'model', 'domain', 'result', 'value'}
            Name of the object class to search.

        Returns
        -------
        obj : list of {BaseModel, BaseDomain, BaseResult, BaseValue}
            A list containing all objects of class ``objclass``.
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
            The ids of each model in the forest. If ``use_complexity`` is True,
            ids are ordered by model complexity.
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

        return self.update_rank(models)

    def split_spec(self, spec, path=''):
        """Split a specification into a forest of models.

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
        Instead of creating an explicit model, this method takes advantage of
        the fact that 1) Python dictionary keys are unique to a particular
        dictionary and 2) keys from nested dictionaries can form a unique
        root-to-leaf path similar to a URL. Since a single hyperparameter
        search space is always a leaf in its model, the entire model can be
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

        # Recurse through submodels to create the path from root to leaf and
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

    def order_models(self, models=None):
        """Order the models in the forest by their rank.

        Returns
        -------
        models : list of str
            The id of each model in the forest, ordered by ``Tree.rank``.
        """
        if models is None:
            models = self.find_all('model')
        if models[0].rank is not None:
            models.sort(key=lambda x: x.rank)
        return [model.id for model in models]

    def update_rank(self, models=None):
        """Update the rank of the modelsby complexity and priority heuristics.

        Parameters
        ----------
        models : list of str, optional
            The list of model ids. Loaded from the database if not provided.

        Returns
        -------
        The list of model ids, sorted by ``Tree.rank``.
        """
        if models is None:
            models = self.find_all('model')

        for model in models:
            model.rank = 1 if model.rank is not None else None

        if models[0].priority is not None:
            models.sort(key=lambda x: x.priority, reverse=True)
            for i in range(len(models)):
                models[i].rank *= i

        if models[0].complexity is not None:
            models.sort(key=lambda x: x.complexity, reverse=True)
            for i in range(len(models)):
                models[i].rank *= i

        map(self.update, models)

        return self.order_models(models=models)

    def generate(self, model_id):
        """Generate hyperparameter values from a model.

        Parameters
        ----------
        model_id : int or str
            The id of the model to generate from.

        Returns
        -------
        params : dict
            The generated hyperparameter values, structured in the same shape
            as the `Model` instance referenced by ``id``.

        Notes
        -----
        The model structure is created by nesting dictionaries, with each
        hyperparameter value stored at the first key in a path down the model
        that is not a dictionary.
        """
        model = self.find('model', model_id)
        result = self.create('result')
        params = {}

        for domain in model.domains:
            try:
                domain = self.find('domain', domain)
            except InvalidObjectError:
                pass

            path = domain.path.split('/')
            value = self.create('value')

            value.domain = domain.id
            value.result = result.id
            value.value = domain.generate()

            if len(path) > 0:
                curr = params
                for i in range(len(path) - 1):
                    if path[i] not in curr:
                        curr[path[i]] = {}
                    curr = curr[path[i]]
                curr[path[-1]] = value.value
            elif len(path) == 1 and path[0] == '':
                params = value.value
            else:
                params = None

            result.add_value(value)
            domain.add_value(value)
            self.update(value)
            self.update(space)

        self.update(result)
        return(result.id, params)

    def register_result(self, result_id, loss, results=None):
        """Register a returned result in the database.

        Parameters
        ----------
        result_id : int or str
            The id of the Result to update.
        loss : float
            The performance of the parameters evaluated for Result.
        results : dict, optional
            Additional information to store.

        Returns
        -------
        update : bool
            Whether or not model order has been updated.
        """
        result = self.find('result', result_id)

        update = False

        if loss is not None:
            result.loss = loss
            result.results = results
            self.update(result)

            model = self.find('model', result.model)
            model.add_result(result)
            reorder = self.count('results') % self.update_frequency
            if model.priority is not None and reorder == 0:
                self.update_priority(model)
                update = True
        # TODO: Add resubmission logic here
        return update

    def calculate_priority(self, model):
        """Calculate the priority of a model.

        Parameters
        ----------
        model : BaseModel
            The model in need of a priority update.
        """
        feats = np.zeros((len(model.results), len(model.domains)),
                         dtype=np.float64)
        losses = np.zeros((feats.shape[0]), dtype=np.float64)

        for i in range(len(model.results)):
            try:
                result = self.find('result', model.results[i])
            except InvalidObjectIdError:
                result = model.results[i]
            losses[i] += result.loss

        for i in range(len(model.domains)):
            try:
                domain = self.find('domains', model.domains[i])
            except InvalidObjectIdError:
                domain = model.domains[i]

            for j in range(len(domain.values)):
                try:
                    value = self.find('values', domain.values[i])
                except InvalidObjectIdError:
                    value = domain.values[i]
                feats[i][j] += domain.get_label(value.value)

        model.priority.append(priority(feats, losses.transpose()))

    def get_optimal(self, mode='global'):
        opt = None
        loss = None
        params = {}

        results = self.find_all('results')
        for result in results:
            if opt is None or \
                           (l is not None and loss is not None and l < loss):
                opt = result
                loss = result.loss

        try:
            for value in opt.values:
                try:
                    value = self.find('values', value)
                    domain = self.find('domains', value.domain)
                except InvalidObjectIdError:
                    domain = value.domain

                path = domain.path.split('/')
                curr = params
                for i in range(len(path) - 1):
                    if path[i] not in curr:
                        curr[path[i]] = {}
                    curr = cur[path[i]]
                curr[path[-1]] = value.value
        except TypeError:
                pass

        return (loss, params, opt.results)
