Library Reference
=================


.. currentmodule:: shadho

Core
----

.. autosummary::
    :toctree: generated/

    HyperparameterSearch
    OrderedSearchForest
    ComputeClass
    WQConfig
    WQFile

Specification Helpers
---------------------

.. autosummary::
    :toctree: generated/

    uniform
    ln_uniform
    log10_uniform
    log2_uniform
    normal
    ln_normal
    log10_normal
    log2_normal
    randint
    log10_randint
    log2_randint
    choose

Tree
----

.. currentmodule:: shadho.tree

.. autosummary::
    :toctree: generated/

    SearchTree
    SearchTreeNode
    SearchTreeLeaf

Search Spaces
-------------

.. currentmodule:: shadho.spaces

.. autosummary::
    :toctree: generated/

    BaseSpace
    ConstantSpace
    ContinuousSpace
    DiscreteSpace

Search Strategies
-----------------

.. currentmodule:: shadho.strategies

.. autosummary::
    :toctree: generated/

    random

Scaling Functions
-----------------

.. currentmodule:: shadho.scales

.. autosummary::
    :toctree: generated/

    linear
    ln
    log10
    log2
