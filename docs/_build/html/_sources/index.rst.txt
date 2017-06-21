.. SHADHO documentation master file, created by
   sphinx-quickstart on Sun May 28 14:46:38 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

SHADHO: Optimization Optimized
==============================

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   hyperparam
   spec
   ccs
   workqueue
   reference

SHADHO stands for **S**\ calable **H**\ ardware-\ **A**\ ware **D**\ istributed
**H**\ yperparameter **O**\ ptimizer. All hardware is not created equal, and all
machine learning models are not created equal: in most cases, a GPU is faster
than a CPU, and a Decision Tree is faster to train than a Neural Network. Machine
learning models will also (usually) perform differently on the same dataset.
SHADHO tries to help you make the best use of your time and hardware by figuring
out which hardware should test which models based on their size and performance.
SHADHO is optimizing optimization.

Installation
============

Install with ``pip``
--------------------

::

    pip install shadho

Install with ``conda``
----------------------

::

    conda install -c jeffkinnison shadho

Install manually
----------------

::

    $ git clone https://github.com/jeffkinnison/shadho
    $ cd shadho
    $ pip install .
    $ sh install_cctools.sh

Dependencies
------------

* ``scipy >= 0.18.1``
* ``numpy >= 0.12.1``
* ``scikit-learn >= 0.18.1``
* ``pandas >= 0.18.1``
* `Work Queue <https://github.com/nkremerh/cctools/tree/hyperopt_worker>`_

SHADHO uses parts of the scientific Python stack to manage the search (defining
search spaces, learning from the searches, and more!). It also uses `Work Queue
from the CCTools suite <http://ccl.cse.nd.edu/>`_ to coordinate your distributed
hyperparameter search across any number of compute nodes.

.. Indices and tables
.. ==================

.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`
