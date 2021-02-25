.. SHADHO documentation master file, created by
   sphinx-quickstart on Sun May 28 14:46:38 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

SHADHO: Optimization Optimized
==============================

.. toctree::
   :hidden:
   :maxdepth: 1
   :caption: Contents

   hyperparam
   spec
   ccs
   examples
   api

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
    python -m shadho.installers.workqueue


**Note** The post-install step may look like it hangs, but it is just
compiling Work Queue behind the scenes and may take a few minutes.

Install manually
----------------

::

    $ git clone https://github.com/jeffkinnison/shadho
    $ cd shadho
    $ pip install .
    $ python -m shadho.installers.workqueue


**Note** The post-install step may look like it hangs, but it is just
compiling Work Queue behind the scenes and may take a few minutes.

Dependencies
------------

* ``scipy >= 0.18.1``
* ``numpy >= 0.12.1``
* ``scikit-learn >= 0.18.1``
* ``pandas >= 0.18.1``
* `pyrameter <https://pyrameter.readthedocs.io?`_
* `Work Queue <https://github.com/cooperative-computing-lab/cctools`_

SHADHO uses parts of the scientific Python stack to manage the search (defining
search spaces, learning from the searches, and more!). It also uses `Work Queue
from the CCTools suite <http://ccl.cse.nd.edu/>`_ to coordinate your distributed
hyperparameter search across any number of compute nodes.

Using SHADHO is Easy
====================

Local Search
------------

::

 """This script uses shadho to minimize the sin function over domain [0, 2*pi]
 """

  # Imports from shadho:
  #   - Shadho is the main driver class
  #   - rand contains helper functions to define search spaces
  from shadho import Shadho, spaces

  import math


  # The objective function is defined here.
  # It accepts one input, a dictionary containing the supplied parameter values,
  # and returns the floating point value sin(x).
  def obj(params):
      # Note that x is stored in the params dictionary.
      # shadho does not unpack or flatten parameter values.
      return math.sin(params['x'])

  # The objective function must return either a single floating point value, or
  # else a dictionary with 'loss' as a key with a floating point value at a minimum.

  # Here, we define the search space: a uniform distribution over [0, 2*pi]
  space = {
      'x': spaces.uniform(0.0, 2.0 * math.pi)
  }


  if __name__ == '__main__':
      # The shadho driver is created here, then configured
      # test hyperparameters on the local machine.
      opt = Shadho('sin_ex', obj, space, timeout=60)
      opt.config.manager = 'local'
      opt.run()

  # After shadho is finished, it prints out the optimal loss and hyperparameters.
  # A database (shadho.json) containing the records of all is also saved to the
  # working directory.


Distributed Search
------------------

sin.py

::

  # shadho sends a small module along with every worker that can wrap the
  # objective function. Start by importing this module.
  import shadho_worker

  # shadho_run_task automatically loads hyperparameter values and saves
  # the resulting output in a format that shadho knows to look for. All
  # you have to do is write a function that takes the parameters as
  # an argument.

  import math

  # The objective function is defined here (same code as in ex1)
  def opt(params):
      return math.sin(params['x'])

  if __name__ == '__main__':
      # To run the worker, just pass the objective function to shadho_worker.run
      shadho_worker.run(opt)

wq_sin.py

::

  """This script runs the hyperparameter search on remote workers.
  """

  # These are imported, same as before
  from shadho import Shadho, spaces

  import math


  # The space is also defined exactly the same.
  space = {
      'x': spaces.uniform(0.0, 2.0 * math.pi)
  }


  if __name__ == '__main__':
      # This time, instead of configuring shadho to run locally,
      # we direct it to the input files that run the optimization task.

      # Instead of the objective function, shadho is given a command that gets
      # run on the remote worker.
      opt = Shadho(''sin_ex', 'bash run_sin.sh', space, timeout=60)

      # Two input files are also added: the first is run directly by the worker
      # and can be used to set up your runtime environment (module load, anyone?)
      # The second is the script we're trying to optimize.
      opt.add_input_file('run_sin.sh')
      opt.add_input_file('sin.py')
      opt.run()

Then, run the search with::

    $ python -m shadho.workers.workqueue -M sin_ex &
    $ python wq_sin.py
