"""This example sets up a search over Support Vector Machine kernel
   hyperparameters.
"""
from shadho import Shadho, spaces


if __name__ == '__main__':
    # Domains can be stored as variables and used more than once in the event
    # that the domain is used multilpe times.
    C = spaces.log2_uniform(-5, 15)
    gamma = spaces.log10_uniform(-3, 3)
    coef0 = spaces.uniform(-1000, 1000)

    # The search space in this case is hierarchical with mutually exclusive
    # subspaces for each SVM kernel. The 'exclusive' tag instructs SHADHO to
    # select one of the subspaces from among 'linear', 'rbf', 'sigmoid', and
    # 'poly' at a time and only generate hyperprameters for that subspace.
    space = {
        'exclusive': True,
        'linear': {
            'kernel': 'linear',  # add the kernel name for convenience
            'C': C
        },
        'rbf': {
            'kernel': 'rbf',  # add the kernel name for convenience
            'C': C,
            'gamma': gamma
        },
        'sigmoid': {
            'kernel': 'sigmoid',  # add the kernel name for convenience
            'C': C,
            'gamma': gamma,
            'coef0': coef0
        },
        'poly': {
            'kernel': 'poly',  # add the kernel name for convenience
            'C': C,
            'gamma': gamma,
            'coef0': coef0
            'degree': spaces.randint(2, 15)
        },
    }

    # Set up the SHADHO driver like usual
    opt = Shadho('bash svm_task.sh', space, timeout=600)
    opt.config.workqueue.name = 'shadho_svm_ex'

    # Add the task files to the optimizer
    opt.add_input_file('svm_task.sh')
    opt.add_input_file('svm.py')
    opt.add_input_file('mnist.npz')

    # We can divide the work over different compute classes, or sets of workers
    # with commmon hardware resources, if such resources are available. SHADHO
    # will attempt to divide work across hardware in a way that balances the
    # search.
    # For example, in a cluster with 20 16-core, 25 8-core, and 50 4-core
    # nodes, we can specify:
    # opt.add_compute_class('16-core', 'cores', 16, max_tasks=20)
    # opt.add_compute_class('8-core', 'cores', 8, max_tasks=25)
    # opt.add_compute_class('4-core', 'cores', 4, max_tasks=50)

    opt.run()
