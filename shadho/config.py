"""Configuration settings for `shadho`.

Notes
-----
`shadho` can be configured using the `.shadhorc` file, by passing arguments to
the `shadho.Shadho` object initializer, or by passing values to the `cfg`
attribute of an initialized `shadho.Shadho` object.
"""
try:
    import configparser
except ImportError:
    import ConfigParser as configparser

import copy
import os


class ShadhorcDoesNotExistError(Exception):
    def __init__(self, configfile):
        msg = "{} is not a valid shadho config file".format(configfile)
        super(ShadhorcDoesNotExistError, self).__init__(msg)


class ShadhoConfig(object):
    DEFAULTS = {
        'global': {
            'wrapper': 'shadho_run_task.py',
            'output': 'out.tar.gz',
            'result_file': 'performance.json',
            'optimize': 'loss',
            'param_file': 'hyperparameters.json'
        },
        'workqueue': {
            'port': 9123,
            'name': 'shadho_master',
            'exclusive': True,
            'shutdown': True,
            'catalog': False,
            'logfile': 'shadho_master.log',
            'debugfile': 'shadho_master.debug',
            'password': False
        },
        'backend': {
            'type': 'sql',
            'url': 'sqlite:///:memory:'
        }
    }

    def __init__(self, use_defaults=False):
        # Copy the defaults
        self.config = copy.deepcopy(ShadhoConfig.DEFAULTS)

        if not use_defaults:
            # Get the path to the shadhorc file
            configfile = os.getenv('SHADHORC') if 'SHADHORC' in os.environ \
                         else os.path.join(self.__get_home(), '.shadhorc')
            if not os.path.isfile(configfile):
                raise ShadhorcDoesNotExistError(configfile)

            # Load custom settings
            cfg = configparser.ConfigParser()
            with open(configfile, 'r') as f:
                try:
                    cfg.read_file(f)
                except AttributeError:
                    cfg.readfp(f)

            for section in cfg.sections():
                for option in cfg.options(section):
                    t = type(ShadhoConfig.DEFAULTS[section][option])
                    if t is bool:
                        val = cfg.getboolean(section, option)
                    elif t is int:
                        val = cfg.getint(section, option)
                    elif t is float:
                        val = cfg.getfloat(section, option)
                    else:
                        val = cfg.get(section, option)

                    self.config[section][option] = val

    def __getitem__(self, key):
        return self.config[key]

    def __get_home(self):
        try:
            home = os.path.expanduser(
                    os.environ['HOME'] if 'HOME' in os.environ
                    else os.environ['USERPROFILE'])
        except KeyError:
            print('Error: Could not find home directory in environment')
            home = ''

        return home
