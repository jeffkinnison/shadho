# -*- coding: utf-8 -*-
"""Implementation of the Ordered Search Forest (OSF) data structure.

The OSF is a collection of trees on which an ordering is imposed. These trees
are initially specified as a single tree, then split into a forest of distinct
trees representing non-overlapping spaces.

References
----------
Coming soon to theaters near you.
"""

from .spaces import BaseSpace, ConstantSpace
from .tree import SearchTree, SearchTreeNode, SearchTreeLeaf

import uuid

import numpy as np


class OrderedSearchForest(object):
    """A collection of trees containing spaces to search.

    The OSF is a collection of trees that have some ordering imposed on them.
    OSFs are defined by a single specification tree that contains information
    about split points at which two trees are created.

    Parameters
    ----------
    spec : dict
        Dictionary containing a tree specification.

    See Also
    --------
    shadho.tree.SearchTree : a single search tree, contained within OSF

    """

    def __init__(self, spec):
        self.orig_tree = self.build(spec)
        priority = 1.0
        forest = [SearchTree(root=tree, priority=priority)
                  for tree in self.orig_tree.split_spaces()]
        self.trees = {tree.id: tree for tree in forest}

    def build(self, spec, name='root'):
        """Build the OSF trees from a specification.

        Parameters
        ----------
        spec : dict
            The specification tree in dictionary format.
        name : {'root', str}, optional
            The name of the tree.

        Returns
        -------
        node : shadho.tree.SearchTreeNode or shadho.tree.SearchTreeLeaf
            The single search tree defined by spec.

        See Also
        --------
        shadho.tree.SearchTreeNode:
        shadho.tree.SearchTreeNode:
        """
        # If a Python non-BaseSpace or dict value is encountered,
        # create a ConstantSpace
        if not isinstance(spec, (dict, BaseSpace)):
            spec = ConstantSpace(spec)

        # If a BaseSpace is encountered, create a TreeLeafNode
        if isinstance(spec, BaseSpace):
            return SearchTreeLeaf(name, value=spec)

        # Otherwise, create a TreeInteriorNode and fill it with children
        exc = spec['exclusive'] if 'exclusive' in spec else False
        opt = spec['optional'] if 'optional' in spec else False
        node = SearchTreeNode(name, exclusive=exc, optional=opt)
        for key in spec:
            if key != 'exclusive' and key != 'optional':
                node.add_child(self.build(spec[key], key))

        return node

    def generate(self):
        """Generate values from a random tree in the OSF.

        Returns
        -------
        vals : tuple(str, dict)
            A pair containing the unique id of the selected tree and the values
            generated from that tree.

        Notes
        -----
        This function is used by shadho.HyperparameterSearch when no compute
        classes are defined. The proportions are based on the rank of each tree
        if priority and/or complexity are used, otherwise the tree is selected
        entirely at random.

        See Also
        --------
        shadho.tree.SearchTree.generate()
        """
        # TODO: incorporate weighted choices
        idx = np.random.randint(len(self.trees))
        key = list(self.trees.keys())[idx]
        tree = self.trees[key]
        return (tree.id, tree.generate())

    def write_all(self):
        """Write the OSF state to file.

        This function writes the state of each tree in the OSF to file. Each
        file contains the specification used to construct the tree and the list
        of tested search values/results.

        See Also
        --------
        shadho.tree.SearchTree.write()
        """
        for tree in self.trees:
            self.trees[tree].write()

    def set_ranks(self, use_complexity=False, use_priority=False):
        trees = [self.trees[key] for key in self.trees]

        for tree in trees:
            tree.rank = 1
            tree.clear_assignments()

        if use_complexity:
            trees.sort(key=lambda x: x.complexity, reverse=True)
            for i in range(len(trees)):
                trees[i].rank *= i

        if use_priority:
            trees.sort(key=lambda x: x.priority, reverse=True)
            for i in range(len(trees)):
                trees[i].rank *= i

    # DEPRECATED
    def update_assignments(self, ccs):
        x = max(len(self.trees), len(ccs)) / min(len(self.forest), len(ccs))

        if len(self.trees) < len(ccs):
            j = 0
            y = x - 1
            for i in range(len(self.trees)):
                if i > y:
                    j += 1
                    y += x
                if j > 0:
                    j
                ccs[j].assignments.append(self.trees[i])
        else:
            i = 0
            y = x - 1
            for j in range(len(self.trees)):
                if j > y:
                    i += 1
                    y += x
                ccs[j].assignments.append(self.trees[i])
