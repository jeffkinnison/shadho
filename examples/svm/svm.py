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
              gamma=kernel_params['gamma'] if 'gamma' in kernel_params else 'auto',
              coef0=kernel_params['coef0'] if 'coef0' in kernel_params else 0,
              degree=kernel_params['degree'] if 'degree' in kernel_params else 3)

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
    encoder.fit(np.unique(y_test))
    loss_labels = encoder.transform(predictions)

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
        'params': params,
        'train_time': train_time,
        'test_time': test_time
    }

    return out


if __name__ == '__main__':
    # All you have to do next is pass your objective function (in this case,
    # main) to shadho_worker.run, and it will take care of the rest.
    shadho_worker.run(main)
