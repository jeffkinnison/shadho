"""Routines for automatically running functions and commands through `shadho`.

Functions
---------
load_config
    Load configurations sent from the `shadho` master.
run_task
    Run the user-defined task and save the result to file.
"""
try:
    import configparser
except ImportError:
    import ConfigParser as configparser
import copy
import json
import os
try:
    import cPickle as pickle
except ImportError:
    import pickle
import tarfile
from typing import Iterable, Mapping

# If running on a remote system, try to import from the clobbered module name.
# Otherwise, import from the standard module name.
try:
    from shadho_utils import ShadhoEncoder, ShadhoDecoder
except ImportError:
    from utils import ShadhoEncoder, ShadhoDecoder


DEFAULTS = {
    'global': {
        'wrapper': 'shadho_run_task.py',
        'output': 'out.tar.gz',
        'result_file': 'performance.json',
        'optimize': 'loss',
        'param_file': 'hyperparameters.json'
    }
}


def load_config(path='.shadhorc'):
    """Load the configuration for this task.

    In most cases, the ``path`` parameter should be omitted in favor of using
    the configuration provided by the `shadho` master. This will ensure that
    the local configuration matches the global configuration and reduce
    headaches.

    Parameters
    ----------
    path : str, optional
        Path to the configuration file. It is recommended to use the default
        value in most cases. This will load the configuration provided by the
        `shadho` master and ensure that the local configuration matches the
        global configuration.

    Returns
    -------
    cfg : dict
        The configuration to use with this task.
    """
    config = copy.deepcopy(DEFAULTS)

    if os.path.isfile(path):
        cfg = configparser.ConfigParser()
        with open(path, 'r') as f:
            try:
                cfg.read_file(f)
            except AttributeError:
                cfg.readfp(f)
        for section in cfg.sections():
            for option in cfg.options(section):
                try:
                    t = type(DEFAULTS[section][option])
                except KeyError:
                    continue
                if t is bool:
                    val = cfg.getboolean(section, option)
                elif t is int:
                    val = cfg.getint(section, option)
                elif t is float:
                    val = cfg.getfloat(section, option)
                else:
                    val = cfg.get(section, option)

                config[section][option] = val

    return config


def run(task, cfgpath='.shadhorc'):
    """Run a function with arguments pulled from a JSON source.

    For simple use cases, SHADHO should be able to run without user-defined
    bash scripts, JSON parsing, etc. Users will expect this to be automated in
    the standard case.

    Parameters
    ----------
    task : callable
        The function/callable object to run.
    cfgpath : str, optional
        The path to the `shadho` configuration file for this task.
    """
    # Load the configuration
    cfg = load_config(path=cfgpath)

    # Load hyperparameters to test
    spec = {}
    if os.path.isfile(cfg['global']['param_file']):
        with open(cfg['global']['param_file'], 'r') as f:
            spec = json.load(f, cls=ShadhoDecoder)

    # Run the task and save the results in a format `shahdo` recognizes.
    result = task(spec)
    if isinstance(result, float) or isinstance(result, Iterable) and all([isinstance(i, float) for i in result]):
        result = {cfg['global']['optimize']: result}
    elif not isinstance(result, Mapping):
        raise ValueError(
            'Training result mush be a float, sequence of floats, ' +
            f'or dictionary of JSON-compatible results. Got {type(result)}')

    # Dump the results to file.
    with open(cfg['global']['result_file'], 'w') as f:
        json.dump(result, f, cls=ShadhoEncoder)

    # Compress into the expected output file.
    ext = os.path.splitext(cfg['global']['output'])
    mode = ':'.join(['w', ext]) if ext in ['gz', 'bz2'] else 'w'
    with tarfile.open(cfg['global']['output'], mode) as f:
        f.add(cfg['global']['result_file'])
