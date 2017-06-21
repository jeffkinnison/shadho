Example: Choosing a SVM
=======================

Setting up and Running SHADHO
-----------------------------

Suppose that you want to make a Support Vector Machine that can classify digits
from the MNIST dataset. Your code may look something like this:

::

    #svm_mnist.py
    from sklearn.svm import SVC
    from sklearn.ensemble import BaggingClassifier
    from sklearn.multiclass import OneVsRestClassifier
    from sklearn.metrics import log_loss, accuracy_score

    from sklearn.preprocessing import label_binarize

    # Keras, Tensorflow, and other libraries have useful functions for loading
    # MNIST and other datasets
    (X_train, y_train), (X_test, y_test) = load_mnist()

    X_train = X_train.reshape((X_train.shape[0],
                               X_train.shape[1] * X_train.shape[2])).astype('f')
    X_test = X_test.reshape((X_test.shape[0],
                             X_test.shape[1] * X_test.shape[2])).astype('f')

    X_train /= 255.0
    X_Test /= 255.0

    svm = OneVsRestClassifier(
                BaggingClassifier(
                        SVC(),
                        n_esitmators=10,
                        max_samples=0.1,
                        n_jobs=-1))

    svm.fit(X_train, y_train)
    predictions = svm.predict(X_test)
    loss = log_loss(y_test, label_binarize(predictions, list(range(10))))
    acc = accuracy_score(y_test, predictions)

    print("Loss: {}, Accuracy: {}".format(loss, acc))

This will train an SVM with RBF kernel on normalized MNIST data and then print
the log loss and accuracy on a test set. This may do a good job on its own, but
the RBF kernel has two parameters that can be tuned: the soft-margin constant
*C* and the kernel coefficient :math:`\gamma`. We can set these by hand by
changing

::

    # svm_mnist.py
    svm = OneVsRestClassifier(
                BaggingClassifier(
                        SVC(),
                        n_esitmators=10,
                        max_samples=0.1,
                        n_jobs=-1))

to

::

    # svm_mnist.py
    svm = OneVsRestClassifier(
                BaggingClassifier(
                        SVC(
                            C=0.03,
                            gamma=7.482
                           ),
                        n_esitmators=10,
                        max_samples=0.1,
                        n_jobs=-1))

But wait...those are both real numbers! Practically speaking, this means you
are selecting values from two different infinite ranges. There are a host of
other questions as well: How are the two values related (if at all)? How do you
select the next value to test? And most importantly, you don't have time to sit
and test values all day (or month, or year, or century...), so how can this be
automated?

SHADHO steps in at this point. You can set up a search over the *C* and :math:`\gamma`
parameters that randomly selects and tests values for both parameters.

::

    # param_search.py
    from shadho import HyperparameterSearch
    from shadho import uniform, ln_uniform

    space = {
        'C': ln_uniform(0, 15),
        'gamma': uniform(0, 1000)
    }

    opt = HyperparameterSearch(opt,
                               cmd='python svm_mnist.py',
                               inputs=['svm_mnist.py']
                               )
    opt.optimize()

This defines a search over the log-scaled uniform distribution of *C*-values
and the linear-scaled uniform distribution of :math:`\gamma`-values. It then
tells SHADHO to run ``python svm_mnist.py`` and gives ``shadho`` the location
of ``svm_mnist.py``. To use this with ``svm_mnist.py``, update the code like so

::

    #svm_mnist.py
    from sklearn.svm import SVC
    from sklearn.ensemble import BaggingClassifier
    from sklearn.multiclass import OneVsRestClassifier
    from sklearn.metrics import log_loss, accuracy_score

    from sklearn.preprocessing import label_binarize

    import shadho_task

    def train_svm(spec):
        # Keras, Tensorflow, and other libraries have useful functions for loading
        # MNIST and other datasets
        (X_train, y_train), (X_test, y_test) = load_mnist()

        X_train = X_train.reshape((X_train.shape[0],
                                   X_train.shape[1] * X_train.shape[2])).astype('f')
        X_test = X_test.reshape((X_test.shape[0],
                                 X_test.shape[1] * X_test.shape[2])).astype('f')

        X_train /= 255.0
        X_Test /= 255.0

        svm = OneVsRestClassifier(
                    BaggingClassifier(
                            SVC(
                                C=spec['C'],
                                gamma=spec['gamma']
                            ),
                            n_esitmators=10,
                            max_samples=0.1,
                            n_jobs=-1))

        svm.fit(X_train, y_train)
        predictions = svm.predict(X_test)
        loss = log_loss(y_test, label_binarize(predictions, list(range(10))))
        acc = accuracy_score(y_test, predictions)

        return loss

    if __name__ == "__main__":
        shadho_task.run(train_svm)

There are only a few changes here:

1. The script now imports ``shadho_task``. This is a wrapper that runs the
   specified function with parameters supplied by ``shadho``.
2. The training code has been wrapped in a function, allowing it to be run
   through ``shadho_task``. This function has an argument called ``spec``,
   which is a dictionary containing the values of *C* and :math:`\gamma`
   generated by ``shadho``.
3. The ``SVC`` class is now instantiated with ``C=spec['C']`` and
   ``gamma=spec['gamma']``. This is how you extract the values provided by
   ``shadho``.
4. Instead of printing the loss value, it is now returned. This allows the
   ``shadho_task`` to pass the value back to ``shadho`` for optimization
   purposes.
5. The ``train_svm`` function is passed to ``shadho_task.run``.

To conduct the search, run these two commands in a terminal

::

    $ work_queue_worker -M shadho_master -t 90  --cores=0 &
    $ python param_search.py

The first command starts a worker in the background on your local machine. This
worker waits for tasks from the master called ``shadho_master`` and shuts down
after 90 seconds if no tasks arrive. The second commands starts the hyperparameter
search, including starting ``shadho_master``. The search will end after ten minutes
and print the best set of hyperparameters found to the screen.

Extending the Search
--------------------

Now you have the search up and running, but there are still a lot of parameters
to be tuned. Would a different kernel work better? Which kernel and hyperparameters
lead to the best performance?

To extend the search over multiple kernels, modify ``param_search.py`` like so

::

    # param_search.py
    from shadho import HyperparameterSearch
    from shadho import uniform, ln_uniform, randint

    C = ln_uniform(0, 15)
    gamma = uniform(0, 1000)
    coef0 = uniform(-1000, 1000)
    degree = randint(2, 10)

    space = {
        'exclusive': True
        'linear': {
            'kernel': 'linear',
            'C': C
        },
        'rbf': {
            'kernel': 'rbf',
            'C': C,
            'gamma': gamma
        },
        'sigmoid': {
            'kernel': 'sigmoid',
            'C': C,
            'gamma': gamma,
            'coef0': coef0
        },
        'poly': {
            'kernel': 'poly',
            'C': C,
            'gamma': gamma,
            'coef0': coef0,
            'degree': degree
        }
    }

    opt = HyperparameterSearch(opt,
                               cmd='python svm_mnist.py',
                               inputs=['svm_mnist.py']
                               )
    opt.optimize()

The search space now includes subspaces for each kernel. This creates a tree
with four subtrees: one for each kernel. The 

Note that the kernels share defined spaces (for example, the ``C`` variable is
shared across all four). This is shorthand for using the same set of values
multiple times. Once ``shadho`` starts, each instance of the space uses its own
random number generator.

The next new piece is the line ``'exclusive': True``. This is a directive that
tells ``shadho``, "Each time you generate values, I want you to include exactly
one of these subspaces."
