Search Space Specification
==========================

Search spaces are defined using native Python dictionaries and SHADHO's inbuilt
helper functions. To get a feel for this, let's begin by defining a few toy
search spaces.

::

    space = {
        'num': 4
    }

This is the most basic search space that can be defined, containing a single
constant value named 'num'. Note that a search space is defined using a key/value
pair, where the key is the name of the search space and the value is the space
itself. This is because search spaces are specified using standard Python
dictionaries.

Python's dictionary structure allows us to do interesting things, such as nest
search spaces and include metadata to better structure our search. We will see
more on these features later. For now, let's look at some more basic examples.

Integer Search Spaces
---------------------

Searching only a single value is valid, but not terribly useful for optimization.
Instead, we want to define a range of values to search, for example the integers
*i* such that :math:`0 \leq i < 11`.

::

    from shadho import rand

    space = {
        'ints': rand.randint(0, 11)
    }

This creates a space called 'ints' containing all integers in range
[0, 10]. During the optimization process, SHADHO will randomly generate one of
0, 1, 2, 3, 4, 5, 6, 7, 8, 9, or 10. What if we want to use these integers
to search over powers of two instead?

::

    from shadho import rand

    space = {
        'pow2': rand.log2_randint(0, 11)
    }

Now, instead of generating one of 0, ..., 10, SHADHO will randomly
generate one of 0, 2, 4, 8, ..., 1024. Could this be done in the code
being optimized? Absolutely. But these types of utilities are here for your
convenience.

Continuous Search Spaces
------------------------

Randomly drawing integers is useful, but it will only get us so far. To fill in
the gaps, we need to be able to draw from continuous, real-valued ranges as
well. Since we can't enumerate all real-valued numbers in a range, we instead
define a continuous space using a probability distribution.

::

    from shadho import rand

    space = {
        'uni': rand.uniform(-7.0, 32.4)
    }


This search space is a uniform distribution defined over the range [-7.0, 32.4).
While running, SHADHO will draw real numbers from this range with equal
probability.

Choice Search Spaces
--------------------

The last of the basic search spaces allows us to provide arbitrary values to
search. These can be numeric or non-numeric, and are drawn randomly in the same
way integers are.

::

    from shadho import rand

    space = {
        'vals': rand.choice(['hi', 4.2, None, True, 78])
    }

This space will randomly choose one of the values passed to it with equal
probability. Notice that we are mixing types in this space. This allows the
choose space a great deal of flexibility. These spaces can be used to search,
e.g., activation functions in neural networks or optimizers, without having to
map them to integers.

Multidimensional Search Spaces
------------------------------

So far, we have only set up searches in a single dimension. For most practical
applications, however, a search must be conducted over multiple parameters,
meaning that multiple dimensions are necessary.

::

    from shadho import rand

    space = {
        'ints1': rand.randint(0, 11, step=2)
        'ints2': rand.randint(1, 11, step=2)
    }

This search space now has two dimensions: ints1 which includes even numbers in
[0, 10], and ints2 which includes odd numbers in [1, 10]. When searching this
space, SHADHO will randomly draw one value from ints1 and one value from ints2.

Now let's look at a more complicated multidimenisonal space.

::

    from shadho import rand

    space = {
        'ints': rand.randint(0, 10),
        'uni': rand.uniform(-7.0, 34.2),
        'vals': rand.choice(['hi', 4.2, None, True, 78])
    }

We've added a few new things here, so let's break this search space down. First,
there are three dimensions to this search space. SHADHO allows you to search
over any number of dimensions (provided the space can fit in memory!). Second,
each of the three dimensions of the search is over a different "type" of space.
This search space includes an integer search, a continuous search, and a choice
search. By mixing and matching search types and by adding additional dimensions
to the search space, we can create rich searches that meet the needs of the
optimization problem.

Nested Search Spaces
--------------------

While multidimensional searches are nice, adding dimensions to a flat search
space does not lend itself to a good organizational structure. To help structure
the search, we can use nested dictionaries.

::

    from shadho import rand

    space = {
        'nest1': {
            'ints': rand.randint(0, 10),
            'uni': rand.uniform(-7.0, 34.2)
        },
        'nest2': {
            'vals': rand.choice(['hi', 4.2, None, True, 78])
        }
    }

We now have a space with two nested levels. The nested structure is maintained
when SHADHO generates values from the space. Nesting in this way allows us to
structure search values in a way that is meaningful to us. Internally, SHADHO
treats the nested dictionaries as a tree, with branching at each nested layer.

Structuring the search space as a tree provides some nice qualities: parameters
can be grouped logically, different spaces can be made disjoint, and additional
constraints can be placed on individual subtrees.

Optional Search Spaces
----------------------

Sometimes it's helpful to test the effect of excluding values from the search.
**Optional** search spaces do just that: they are either included or excluded
when values are generated. These are denoted by adding the "optional" flag to
a nested space.

::

    from shadho import rand

    space = {
        'nest1': {
            'ints': rand.randint(0, 10),
            'uni': rand.uniform(-7.0, 34.2)
        },
        'nest2': {
            'optional': True,
            'vals': rand.choice(['hi', 4.2, None, True, 78])
        }
    }

Here, ``nest2`` has been made optional. When values are generated, you can check
for ``nest2`` with the condition

::

    if 'nest2' in space:
        # Do something awesome with values in nest2
    else:
        # Handle the case where nest2 is excluded

Optional spaces/subspaces are nice for testing things like data preprocessing
steps or additional neural network layers. They allow you to see how including
and excluding a particular part of your model affects the performance.

Exclusive Search Spaces
-----------------------

Exclusive spaces allow you to test disjoint models, for example different kernel
functions with different hyperparameter sets or different neural network layers.
Like optional spaces, exclusive spaces are indicated using a flag::

    from shadho import rand

    space = {
        'nest1': {
            'exclusive': True,
            'ints': rand.randint(0, 10),
            'uni': rand.uniform(-7.0, 34.2)
        },
        'nest2': {
            'vals': rand.choice(['hi', 4.2, None, True, 78])
        }
    }

When hyperparameter values are generated, either ``space['nest1']['ints']`` or
``space['nest1']['uni']`` will be included, but not both. Exclusive spaces may
also be made optional::

    from shadho import rand

    space = {
        'nest1': {
            'exclusive': True,
            'optional': True,
            'ints': rand.randint(0, 10),
            'uni': rand.uniform(-7.0, 34.2)
        },
        'nest2': {
            'vals': rand.choice(['hi', 4.2, None, True, 78])
        }
    }

In this case, there is also the possibility that ``space['nest1']`` will be
excluded entirely. This may be handled like so::

    if 'nest1' in space:
        if 'ints' in space['nest1']:
            # Handle using space['nest1']['ints']
        elif 'uni' in spaces['nest1']:
            # Handle using space['nest1']['uni']
    else:
        # Handle excluding space['nest1']

Example: Optimizing a Decision Tree
-----------------------------------

Example: Searching SVM Kernels
------------------------------

Example: Scaling a Convolutional Net
------------------------------------
