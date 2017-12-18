from shadho.heuristics import priority


class BaseModel(object):
    def generate(self):
        """Generate a set of hyperparameter values.

        Returns
        -------
        params : dict
            Dictionary containing the generated hyperparameter values in their
            original tree structure.

        Notes
        -----
        The returned dictionary will never be flattened. This is to ensure that
        data is represented consistently throughout `shadho` within the master
        and workers. Ultimately, the user will expect their search to be
        structured the same way it was specified.
        """
        params = {}

        for space in self.spaces:
            path = space.path.split('/')
            curr = params
            for i in range(len(path) - 1):
                if path[i] not in curr:
                    curr[path[i]] = {}
                curr = curr[path[i]]
            curr[path[-1]] = space.generate()
        return params

    def calculate_priority(self):
        """Calculate the priority of searching this tree.

        The priority is a measure of the covariance between hyperparameter
        values and the resulting loss. Trees with a higher priority score will
        be allocated more searches on higher-performing hardware or a greater
        number of searches in the case that hardware is not specified.

        NotesTree
        -----
        The priority is stored internally in each instance of the Tree class.
        """
        try:
            feats = np.zeros((len(self.results), len(self.spaces)),
                             dtype=np.float64)
            losses = np.zeros((1, len(self.results)), dtype=np.float64)
        except IndexError:
            return

        for i in len(self.results):
            v = result.to_feature_vector()
            feats[i] += v[:-1]
            losses[i] += v[-1]

        self.priority = priority(feats, losses)

    def calculate_complexity(self):
        """Calculate the complexity of the search respresented by this tree.

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
        for space in self.spaces:
            c += space.complexity

        self.complexity = c

    @property
    def optimal_parameters(self):
        """Retrieve the parameters that result in an optimal loss.

        Returns
        -------
        loss : float
            The loss associated with the optimal parameters.
        params : dict
            The parameters that resulted in the optimal loss.

        See Also
        --------
        `shadho.heuristics.complexity`

        Notes
        -----
        This function returns the optimal parameters observed in a single tree
        instance. To compare across trees, acess this property once for each
        tree.
        """
        res = None
        for result in self.results:
            if res is None or result.loss < res.loss:
                res = result
        params = {}
        for value in res.values:
            path = value.space.path.split('/')
            curr = params
            for i in range(len(path) - 1):
                if path[i] not in curr:
                    curr[path[i]] = {}
                curr = curr[path[i]]
            curr[path[-1]] = value.value

        loss = res.loss if res is not None else None

        return (loss, params)
