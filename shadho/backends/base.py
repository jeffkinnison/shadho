"""
"""


class BaseBackend(object):
        def new_experiment(self, **kwargs):
            return Experiment(**kwargs)

        def new_tree(self, **kwargs):
            return Tree(**kwargs)

        def new_node(self, **kwargs):
            return Node(**kwargs)

        def new_space(self, **kwargs):
            return Space(**kwargs)

        def new_value(self, **kwargs):
            return Value(**kwargs)

        def new_result(self, **kwargs):
            return Result(**kwargs)
