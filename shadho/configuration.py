"""Configuration settings for `shadho`.

Classes
-------
ShadhoConfig
    Configurations for running SHADHO.
ConfigGroup
    Object-oriented interface for hierarchical config settings.

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


class ShadhoInstallNotfoundError(Exception):
    def __init__(self, directory):
        msg = "Could not find shadho installation at {}".format(directory)
        super(ShadhoInstallNotfoundError, self).__init__(msg)


class ShadhoConfig(object):
    """Configurations for running SHADHO.

    Configurations consist of the defaults defined in this class, those values
    read from the .shahdorc file, and those set by the user at runtime.

    Parameters
    ----------
    use_defaults : bool, optional
        If true, only use the default configuration. Default: False.

    Attributes
    ----------
    config : dict
        Dictionary of configuration values.

    Notes
    -----
    All config values can be addressed by key index (dictionary style) or by
    dot operator (object-oriented style).

    """

    DEFAULTS = {
        'global': {
            'wrapper': 'shadho_worker.py',
            'utils': 'shadho_utils.py',
            'output': 'out.tar.gz',
            'result_file': 'performance.json',
            'optimize': 'loss',
            'param_file': 'hyperparameters.json',
            'backend': 'json',
            'manager': 'workqueue',
        },
        'workqueue': {
            'port': str(9123),
            'name': 'shadho_master',
            'shutdown': str(True),
            'logfile': 'shadho_master.log',
            'debugfile': 'shadho_master.debug',
            'password': str(False)
        },
        'backend': {
            'type': 'sql',
            'url': 'sqlite:///:memory:'
        }
    }

    def __init__(self, use_defaults=False):

        # Copy the defaults
        if 'shadho_dir' not in ShadhoConfig.DEFAULTS['global']:
            shadho_dir = os.path.join(self.__get_home(), '.shadho')
            ShadhoConfig.DEFAULTS['global']['shadho_dir'] = shadho_dir

        self.config = copy.deepcopy(ShadhoConfig.DEFAULTS)

        if not use_defaults:
            # Get the path to the shadhorc file
            configfile = os.getenv('SHADHORC') if 'SHADHORC' in os.environ \
                         else os.path.join(self.__get_home(), '.shadhorc')
            if not os.path.isfile(configfile):
                raise ShadhorcDoesNotExistError(configfile)

            self.configfile = configfile

            # Load custom settings
            cfg = configparser.ConfigParser()
            with open(configfile, 'r') as f:
                try:
                    cfg.read_file(f)
                except AttributeError:
                    cfg.readfp(f)

            for section in cfg.sections():
                for option in cfg.options(section):
                    try:
                        t = type(ShadhoConfig.DEFAULTS[section][option])
                    except KeyError:
                        t = str

                    if t is bool:
                        val = cfg.getboolean(section, option)
                    elif t is int:
                        val = cfg.getint(section, option)
                    elif t is float:
                        val = cfg.getfloat(section, option)
                    else:
                        val = cfg.get(section, option)

                    self.config[section][option] = val

        if not os.path.isdir(self.config['global']['shadho_dir']):
            raise ShadhoInstallNotfoundError(self.config['global']['shadho_dir'])

        # Instantiate config group objects
        self.shadho = ConfigGroup(self.config['global'])
        self.workqueue = ConfigGroup(self.config['workqueue'])
        self.backend = ConfigGroup(self.config['backend'])

    def __getattr__(self, attr):
        if attr not in self.__dict__:
            if attr in self.__dict__['shadho']:
                return getattr(self.__dict__['shadho'], attr)
            else:
                msg = '{} has no attribute {}'
                raise AttributeError(msg.format(self.__class__.__name__, attr))
        else:
            return self.__dict__[attr]

    def __get_home(self):
        """Get the absolute path to the user's home directory.

        Returns
        -------
        home : str
            Absolute path to the user's home directory.

        Notes
        -----
        This method attempts to be OS-agnostic.
        """
        try:
            home = os.path.expanduser(
                    os.environ['HOME'] if 'HOME' in os.environ
                    else os.environ['USERPROFILE'])
        except KeyError:
            print('Error: Could not find home directory in environment')
            home = ''

        return home

    def save_config(self, path):
        """Write the current config to file.

        Parameters
        ----------
        path : str
            Path to the output config file.
        """
        try:
            config = configparser.ConfigParser()
            config.read_dict(self.config)
        except AttributeError:
            config = configparser.RawConfigParser()
            for section in self.config:
                config.add_section(str(section))
                for entry in self.config[section]:
                    if type(self.config[section]) is dict:
                        config.set(str(section),
                                   str(entry),
                                   str(self.config[section][entry]))
        with open(os.path.join(path, '.shadhorc'), 'w') as f:
            config.write(f)


class ConfigGroup(object):
    """Container class for hierarchical configuration.

    Parameters
    ----------
    data : dict
        Key/value pairs for configuration values.

    Notes
    -----
    Configuration values should be accglobalessed using the ``.`` operator.

    """

    def __init__(self, data=None, **kws):
        if data is None:
            data = {}
        data.update(kws)
        self.data = data

    def __getattr__(self, attr):
        if attr != 'data':
            if attr in self.__dict__['data']:
                return self.__dict__['data'][attr]
            else:
                msg = '{} has no attribute {}'
                raise AttributeError(msg.format(self.__class__.__name__, attr))
        else:
            return self__dict__['data']

    def __setattr__(self, attr, val):
        if attr != 'data':
            self.__dict__['data'][attr] = val
        else:
            self.__dict__[attr] = val

    def __contains__(self, key):
        return key in self.data

    def __str__(self):
        return str(self.data)
