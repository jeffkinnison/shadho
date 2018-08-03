# Running SHADHO Distributed

SHADHO is designed for distributed hyperparameter optimization out of the box.
This involves running a shell script on the worker that sets up the environment
that then runs the script with the objective function.

## Setup: Driver

Running SHADHO locally happens in a single script that defines the objective
function, defines the search space, and sets up/configures the SHADHO driver.

```python
import math

from shadho import Shadho, rand


if __name__ == '__main__':
    # Set up the search space for sin(x)
    space = {'x': rand.uniform(0, math.pi)}

    # Create a SHADHO driver. Unlike the local example, distributed SHADHO
    # requires a shell command to run on the worker.
    opt = Shadho('bash ./sin_task.sh', space, timeout=60)

    # Add the files necessary to run the task
    opt.add_input_file('sin_task.sh')
    opt.add_input_file('sin.py')

    # Optionally, provide a name for the Work Queue master that tracks the
    # distributed workers.
    opt.config.workqueue.name = 'shadho_sin_ex'

    # Run the search, and the optimal observed value will be output after 60s.
    opt.run()
```

The command `'bash sin_task.sh'` passed into the driver is run on the Work
Queue worker, and set up the environment. The objective function is defined in
a separate file. The scripts `sin_task.sh` and `sin.py` are sent to each
worker after adding them as input files.

## Setup: Objective Function

The objective function must be defined in its own file and wrapped in a SHADHO


```python
import math

# shadho_worker is a python module sent to the worker automatically along with
# your code that takes care of loading the hyperparmeters and packaging the
# results in a way that SHADHO understands.
import shadho_worker


# Somewhere in this file, you have to define a function to optimize. This will
# be run by shadho_worker.
# This function will return a single floating-point value to optimize on.
def sin(params):
    return math.sin(params['x'])


if __name__ == '__main__':
    # All you have to do next is pass your objective function (in this case,
    # sin) to shadho_worker.run, and it will take care of the rest.
    shadho_worker.run(sin)
```

SHADHO provides a Python worker script to every Work Queue worker that wraps
the objective function and standardizes input and output for SHADHO.

## Setup: Worker Script

```bash
#!/usr/bin/env bash

# Use this file to set up the environment on the worker, e.g. load modules,
# edit PATH/other environment variables, activate a python virtual env, etc.

# Then run the script with the objective function.
python sin.py
```

## Running SHADHO

In your terminal, run

```
$ python driver.py
```

Then on your worker machine (can be another terminal window), run

```
$ shadho_wq_worker -M shadho_sin_ex
```

The worker will now receive hyperparameters from the SHADHO driver for 60s and
process as many as possible.
