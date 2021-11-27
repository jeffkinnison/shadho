#!/usr/bin/env python3
"""Install script for Work Queue and SHADHO config.

This executable performs post-install steps to get the Work Queue library and
set up SHADHO config and extra scripts. By default, these are installed to
`$HOME/.shadhorc` and `$HOME/.shadho/`.
"""

import argparse
import configparser
import os
import pathlib
import shutil
import site
import subprocess
import sys
import tempfile


def parse_args(args=None):
    homedir = str(pathlib.Path().home())

    p = argparse.ArgumentParser(
        description="""
            Install the .shadho support directory, Work Queue, and additional
            files needed to run SHADHO.
        """)

    p.add_argument('--prefix', type=str, default=homedir,
                   help='install directory of the .shadho directory')
    p.add_argument('--user', action='store_true',
                   help='pass to perform a Python user-level install')

    return p.parse_args(args=None)


def install_workqueue(prefix):
    """Install Work Queue and SHADHO supplementary files.

    Parameters
    ----------
    prefix : str
        Install directory of the .shadho directory.

    Returns
    -------
    prefix : str or None
        Identical to ``prefix``. Set to None if intallation failed.
    """
    try:
        if os.path.basename(prefix) != '.shadho':
            prefix = os.path.join(prefix, '.shadho')
        tempdir = tempfile.mkdtemp(prefix='shadho_install.')

        os.makedirs(prefix, exist_ok=True)
        print('Building and installing Work Queue to {}.'.format(prefix))

        installer = os.path.join(os.path.dirname(__file__),
                                 'install_workqueue.sh')
        subprocess.check_output(
            ['sh', installer, tempdir, prefix],
            stderr=subprocess.STDOUT)
        result = 'not None'

    except subprocess.CalledProcessError as e:
        logfile = os.path.abspath('shadho_install.log')
        print('Error installing Work Queue.')
        print('Dumping install logs to {}'.format(logfile))
        with open(logfile, 'w') as f:
            f.write(e.output.decode())
        result = None
    finally:
        shutil.rmtree(tempdir)

    return result

def write_shadhorc(shadho_dir):
    """Create the .shadhorc config file.

    Parameters
    ----------
    prefix : str
        Path to install SHADHO config and Work Queue to.
    shadho_dir : str
        Path to the .shadho install directory.
    """
    # Set up the default config values
    default_config = {
        'global': {
            'wrapper': 'shadho_worker.py',
            'utils': 'shadho_utils.py',
            'output': 'out.tar.gz',
            'result_file': 'performance.json',
            'optimize': 'loss',
            'param_file': 'hyperparameters.json',
            'backend': 'json',
            'manager': 'workqueue'
        },
        'workqueue': {
            'port': '9123',
            'name': 'shadho_master',
            'shutdown': 'True',
            'logfile': 'shadho_master.log',
            'debugfile': 'shadho_master.debug',
            'password': 'False'
        },
        'backend': {
            'type': 'sql',
            'url': 'sqlite:///:memory:'
        }
    }

    default_config['global']['shadho_dir'] = str(shadho_dir)

    # Load the default config into a ConfigParser. The try block is for
    # Python3+, the except block is for Python 2.7.
    try:
        config = configparser.ConfigParser()
        config.read_dict(default_config)
    except AttributeError:
        config = configparser.RawConfigParser()
        for section in default_config:
            config.add_section(str(section))
            for entry in default_config[section]:
                if type(default_config[section]) is dict:
                    config.set(str(section),
                               str(entry),
                               str(default_config[section][entry]))

    # Write the .shadhorc.
    homedir = str(pathlib.Path().home())
    with open(os.path.join(homedir, '.shadhorc'), 'w') as f:
        config.write(f)


def install_shadho_files(prefix, sp_prefix):
    """Setup up additional SHADHO files.

    Parameters
    ----------
    prefix : str
        Install directory of the .shadho directory.
    sp_prefix : str
        Path to the site-packages directory where work_queue was installed.
    """
    maj = sys.version_info.major
    min = sys.version_info.minor
    source = os.path.join(prefix, 'lib', f'python{maj}.{min}', 'site-packages')
    shutil.copy(os.path.join(source, 'work_queue.py'), sp_prefix)
    shutil.copy(os.path.join(source, '_work_queue.so'), sp_prefix)


def main(prefix='~', user=False):
    homedir = str(pathlib.Path().home())

    if '~' in prefix:
        prefix = os.path.expanduser(prefix)
        prefix = os.path.join(prefix, '.shadho')

    maj = sys.version_info.major
    min = sys.version_info.minor

    sp_prefix = os.path.join('lib',
                             'python{}.{}'.format(maj, min),
                             'site-packages')

    if user:
        dest_prefix = os.path.join(site.USER_BASE, sp_prefix)
    else:
        dest_prefix = os.path.join(sys.prefix, sp_prefix)

    if not os.path.isfile(os.path.join(prefix, 'work_queue.py')):
        prefix, sp_prefix = install_workqueue(prefix, user=user)
    else:
        if user:
            sp_prefix = os.path.join(site.USER_BASE, sp_prefix)
        else:
            sp_prefix = os.path.join(sys.prefix, sp_prefix)

    if prefix is not None:
        install_shadho_files(prefix, sp_prefix)

    write_shadhorc(prefix)


if __name__ == '__main__':
    args = parse_args()
    main(prefix=args.prefix, user=args.user)
