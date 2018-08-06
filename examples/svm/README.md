# Running SHADHO with Disjoint Search Spaces

Oftentimes, multiple machine learning algorithms with distinct sets of
hyperparameters will be searched. SHADHO's search space definition allows for
hierarchical, disjoint hyperparameter spaces to be defined by nesting search
spaces and using the `exclusive` tag.

## Dependencies

For this example, you will also need to install `numpy` and `scikit-learn`.

## Setup: Driver

Running SHADHO locally happens in a single script that defines the objective
function, defines the search space, and sets up/configures the SHADHO driver.
In this example, the root search space uses the `'exclusive'` tag to
distinguish between kernels and their associated search spaces.

### driver.py
```python
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
            'coef0': coef0,
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

```

The command `'bash sin_task.sh'` passed into the driver is run on the Work
Queue worker, and set up the environment. The objective function is defined in
a separate file. The scripts `svm_task.sh` and `svm.py` are sent to each
worker after adding them as input files.

## Setup: Objective Function

The objective function must be defined in its own file, which will be sent to
the distributed worker.

### svm.py
```python
"""This script trains an SVM on MNIST using supplied hyperparameters."""

# shadho_worker is a python module sent to the worker automatically along with
# your code that takes care of loading the hyperparmeters and packaging the
# results in a way that SHADHO understands.
import shadho_worker

import time

# These imports are from the numpy and scikit-learn libraries, used to work
# with data and SVMs. SHADHO doesn't place any restrictions on what can be
# imported: as long as the module we want exists on the worker, it can be
# imported and used.
import numpy as np
from sklearn.svm import SVC
from sklearn.ensemble import BaggingClassifier
from sklearn.multiclass import OneVsRestClassifier
from sklearn.metrics import accuracy_score, precision_score, \
                            recall_score, roc_auc_score, log_loss
from sklearn.preprocessing import LabelBinarizer


def load_data():
    """Load the MNIST dataset and return it in a friendly way.

    Returns
    -------
    X_train : numpy.ndarray
    y_train : numpy.ndarray
        The training images and labels.
    X_test: numpy.ndarray
    y_test: numpy.ndarray
        The testing images and labels.
    """
    data = np.load('mnist.npz')
    X_train = data['x_train']
    y_train = data['y_train']
    X_test = data['x_test']
    y_test = data['y_test']
    data.close()
    shapes = X_train.shape
    X_train = X_train.reshape(shapes[0], shapes[1] * shapes[2])
    shapes = X_test.shape
    X_test = X_test.reshape(shapes[0], shapes[1] * shapes[2])
    return (X_train, y_train), (X_test, y_test)


def main(params):
    """Train and evaluate the SVM with supplied hyperparameters.

    Parameters
    ----------
    params : dict
        Dictionary of hyperparameter values.

    Returns
    -------
    out : dict
        Dictionary of performance metrics to send to SHADHO.
    """
    # Extract the kernel name and parameters. This is just a short expression
    # to get the only dictionary entry, which should have our hyperparameters.
    kernel_params = list(params.values())[0]

    # Load the training and test sets.
    (X_train, y_train), (X_test, y_test) = load_data()

    X_train = X_train.astype(np.float32) / 255.0
    X_test = X_test.astype(np.float32) / 255.0

    # Set up the SVM with its parameterized kernel. The long form of instantiation
    # is done here to show what `kernel_params` looks like internally.
    # This can be shortened to `svc = SVC(**kernel_params)`
    svc = SVC(kernel=kernel_params['kernel'],
              C=kernel_params['C'],
              gamma=kernel_params['gamma'] if 'gamma' in kernel_params else None,
              coef0=kernel_params['coef0'] if 'coef0' in kernel_params else None,
              degree=kernel_params['degree'] if 'degree' in kernel_params else None)

    # Set up parallel training across as many cores as are available on the
    # worker.
    s = OneVsRestClassifier(
        BaggingClassifier(
            svc,
            n_estimators=10,
            max_samples=0.1,
            n_jobs=-1))

    # Train and compute the training time.
    start = time.time()
    s.fit(X_train, y_train)
    train_time = time.time() - start

    # Generate and encode testing set predictions, along with prediction time.
    start = time.time()
    predictions = s.predict(X_test)
    test_time = time.time()
    encoder = LabelBinarizer()
    loss_labels = encoder.fit_transform(predictions)

    # Compute performance metrics on the test set to return to SHADHO
    loss = log_loss(y_test, loss_labels, labels=encoder.classes_)
    acc = accuracy_score(y_test, predictions)
    p = precision_score(y_test, predictions, average='micro')
    r = recall_score(y_test, predictions, average='micro')

    # Output of the objective function can be stored in a dictionary to return
    # multiple values (e.g., accuracy, precision, recall). The dictionary must
    # have a key 'loss' with a floating point value--this is the value SHADHO
    # optimizes on.
    out = {
        'loss': loss,
        'accuracy': acc,
        'precision': p,
        'recall': r,
        'params': svm,
        'train_time': train_time,
        'test_time': test_time
    }

    return out


if __name__ == '__main__':
    # All you have to do next is pass your objective function (in this case,
    # main) to shadho_worker.run, and it will take care of the rest.
    shadho_worker.run(main)
```

## Setup: Worker Script

The worker script allows you to set up your environment (e.g., load modules,
activate virtual environments, etc.) before running your objective function.

### svm_task.sh
```bash
#!/usr/bin/env bash

# Use this file to set up the environment on the worker, e.g. load modules,
# edit PATH/other environment variables, activate a python virtual env, etc.

# For this task, activate an environment that has scikit-learn installed.

python svm.py
```

## Running SHADHO

In your terminal, run

```
$ python driver.py
```

Then on your worker machine (can be another terminal window), run

```
$ shadho_wq_worker -M shadho_svm_ex
```

The worker will now receive hyperparameters from the SHADHO driver for 60s and
process as many as possible.
