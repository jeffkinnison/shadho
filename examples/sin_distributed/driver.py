"""This script shows an example of setting up a distributed Shadho search."""
import math

from shadho import Shadho, spaces


if __name__ == '__main__':
    # Set up the search space for sin(x)
    space = {'x': spaces.uniform(0, math.pi)}

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
