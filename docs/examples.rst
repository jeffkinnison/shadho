Examples
========

The following examples will walk through basic SHADHO usage, both local and
distributed. The code and instruction for each example can be found in the
`GitHub repo`_.

.. _GitHub repo: https://github.com/jeffkinnison/shadho

Running SHADHO Locally
----------------------

While SHADHO was designed for distributed optimization, it's more helpful to
prototype the search locally, with instant feedback.

Setup
^^^^^

Running SHADHO locally happens in a single script that defines the objective
function, defines the search space, and sets up/configures the Shadho driver
object.

.. code-block:: python
    :name: sin_local_driver.py

    import math

    # Import the driver and random search from SHADHO
    from shadho import Shadho, spaces


    # Define the function to optimize, which returns a single floating-point
    # value to optimize on. Hyperparameters are passed in as a dictionary with
    # the same structure as `space` below.
    def sin(params):
        return math.sin(params['x'])


    if __name__ == '__main__':
        # Set up the search space, in this case a uniform distribution over the
        # domain [0, pi]
        space = {'x': spaces.uniform(0, math.pi)}

        # Pass the `sin` function, the search space, and a timeout into the
        # SHADHO driver and configure SHADHO to run locally.
        opt = Shadho('sin_local_example', sin, space, timeout=30)
        opt.config.manager = 'local'

        # Run SHADHO, and the optimal `x` value will be printed after 30s.
        opt.run()


Running the Example
^^^^^^^^^^^^^^^^^^^

From the terminal, run::

    python sin_local_driver.py

The value of ``x`` that minimizes ``sin(x)`` from among all evaluated ``x``
values will be printed to screen after 30s. An output file, results.json will
also appear. This file contains a database of all evaluated hyperparameters.




Distributed Search
------------------

In most cases, it is useful to incorporate multiple distributed workers into a
search to speed up the process. Searching over neural networks in particular
essentially requires using distributed search due to long training times and
the need for GPUs and other specialized hardware.

SHADHO is designed for distributed hyperparameter optimization out of the box.
This involves running a shell script on the worker that sets up the environment
that then runs the script with the objective function. This example will cover
a basic distributed search.

Setup: Objective
^^^^^^^^^^^^^^^^

Unlike local search, the objective function must be defined in its own script
and run by a SHADHO worker. The sin function can be set up as

.. code-block:: python
    :name: sin.py

    import math

    # shadho_worker is a python module sent to the worker automatically along
    # with your code that takes care of loading the hyperparmeters and
    # packaging the results in a way that SHADHO understands.
    import shadho_worker


    # Somewhere in this file, you have to define a function to optimize. This will
    # be run by shadho_worker.
    # This function will return a single floating-point value to optimize on.
    def sin(params):
        return math.sin(params['x'])


    if __name__ == '__main__':
        # All you have to do next is pass your objective function (in this
        # case, sin) to shadho_worker.run, and it will take care of the rest.
        shadho_worker.run(sin)

SHADHO provides a Python worker script to every Work Queue worker that wraps
the objective function and standardizes input and output for SHADHO.


Setup: Worker Script
^^^^^^^^^^^^^^^^^^^^

Typically, when working with distributed systems, there is some preamble or
environment setup that has to happen to run a program. Setting up a SHADHO
search is no different--just provide a shell script that does the setup then
executes the objective function script.

.. code-block:: bash
    :name: sin_task.sh

    #!/usr/bin/env bash

    # Use this file to set up the environment on the worker, e.g. load modules,
    # edit PATH/other environment variables, activate a python virtual env, etc.

    # Then run the script with the objective function.
    python sin.py


Setup: Driver File
^^^^^^^^^^^^^^^^^^

Running SHADHO distributed requires setting up the driver and the objective
function in different scripts. SHADHO automatically sends input files to
workers and caches them between evaluations.

In this driver file, we define the search space (``x`` in domain ``[0, pi]``),
add the files to run the objective function, and give SHADHO a command to run
on each worker.


.. code-block:: python
    :name: sin_distributed_driver.py

    import math

    from shadho import Shadho, spaces


    if __name__ == '__main__':
        # Set up the search space for sin(x)
        space = {'x': spaces.uniform(0, math.pi)}

        # Create a SHADHO driver. Unlike the local example, distributed SHADHO
        # requires a shell command to run on the worker.
        opt = Shadho('sin_distributed_example', 'bash ./sin_task.sh', space, timeout=60)

        # Add the files necessary to run the task
        opt.add_input_file('sin_task.sh')
        opt.add_input_file('sin.py')

        # Optionally, provide a name for the Work Queue master that tracks the
        # distributed workers.
        opt.config.workqueue.name = 'shadho_sin_ex'

        # Run the search, and the optimal observed value will be output after 60s.
        opt.run()

The command ``bash sin_task.sh`` passed into the driver is run on the Work Queue
worker, and set up the environment. The objective function is defined in a
separate file. The scripts ``sin_task.sh`` and ``sin.py`` are sent to each
worker after adding them as input files.
