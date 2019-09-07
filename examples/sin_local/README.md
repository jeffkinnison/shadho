# Running SHADHO Locally

While SHADHO was designed for distributed optimization, it's more helpful to
prototype the search locally, with instant feedback.

## Setup

Running SHADHO locally happens in a single script that defines the objective
function, defines the search space, and sets up/configures the Shadho driver.

```python
import math

# Import the driver and random search from SHADHO
from shadho import Shadho, spaces


# Define the function to optimize, which returns a single floating-point value
# to optimize on. Hyperparameters are passed in as a dictionary with the
# same structure as `space` below.
def sin(params):
    return math.sin(params['x'])


if __name__ == '__main__':
    # Set up the search space, in this case a uniform distribution over the
    # domain [0, pi]
    space = {'x': spaces.uniform(0, math.pi)}

    # Pass the `sin` function, the search space, and a timeout into the SHADHO
    # driver and configure SHAHDO to run locally.
    opt = Shadho('sin_local_example', sin, space, timeout=30)
    opt.config.manager = 'local'

    # Run SHADHO, and the optimal `x` value will be printed after 30s.
    opt.run()
```

## Running SHADHO

In your terminal, run

```
$ python driver.py
```

The value of `x` that minimizes `sin(x)` from among those evaluated will be
printed to screen after 30s.

An output file, `results.json` will also appear. This file contains a database
of all evaluated hyperparameters.
