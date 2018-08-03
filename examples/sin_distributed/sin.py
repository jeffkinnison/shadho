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
