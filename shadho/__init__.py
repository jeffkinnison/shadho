"""Top-level imports for SHADHO.

At the top level, the SHADHO package should grant access to the `Shadho` object
that drives hyperparameter optimization and the configuration.

See Also
--------
shadho.shadho
    Main driver for hyperparameter optimization.
shadho.configuration
    Utility for configuring SHADHO.

"""

from .shadho import Shadho
from .configuration import ShadhoConfig

config = ShadhoConfig()

__all__ = ['Shadho', 'config', 'managers', 'spaces']
