#!/usr/bin/env python
from setuptools import setup
from setuptools.command.install import install

try:
    import configparser
except:
    import ConfigParser as configparser
import json
import os
import site
import shutil
import subprocess
import sys
import tempfile

MAJ = sys.version_info[0]
SHADHO_DIR = os.path.join(os.environ['HOME'], '.shadho')
DEFAULT_CONFIG = {
    'global': {
        'wrapper': 'shadho_worker.py',
        'output': 'out.tar.gz',
        'result_file': 'performance.json',
        'optimize': 'loss',
        'param_file': 'hyperparameters.json',
        'backend': 'json',
        'manager': 'workqueue'
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


class InstallError(Exception):
    """Raised when an error occurs installing Work Queue"""
    def __init__(self, logfile):
        fname = logfile.name
        logfile.close()
        logfile = open(fname, 'r')
        super(InstallError, self).__init__(logfile.read())


class InstallCCToolsCommand(install):
    """Helper to install CCTools."""
    description = "Install CCTools and set up SHADHO working directory"

    def run(self):
        """Install WorkQueue from the CCTools suite to site-packages.

        SHADHO uses WorkQueue, a member of the
        `CCTools software suite<http://ccl.cse.nd.edu>`,
        to manage the distributed computing environment. This function installs
        CCTools and moves the related Python module and shared library to the
        site-packages directory.
        """
        print('Installing CCTools suite')
        global MAJ
        global SHADHO_DIR
        global DEFAULT_CONFIG
        # CCTools distinguishes between Python 2/3 SWIG bindings, and the
        # Python 3 bindings require extra effort. Install based on the user's
        # version
        if not os.path.isdir(SHADHO_DIR):
            os.mkdir(SHADHO_DIR)

        DEFAULT_CONFIG['global']['shadho_dir'] = SHADHO_DIR

        cfg = configparser.ConfigParser()
        try:
            import work_queue
            print("Found Work Queue, skipping install")
        except ImportError:

            tmpdir = tempfile.mkdtemp(prefix='shadho_install_')

            try:
                # Install Perl
                logfile = open("perl_install.log", 'w')
                args = [
                    'bash',
                    os.path.join(
                        os.path.dirname(__file__),
                        'install_perl.sh')
                    ]
                args.append(tmpdir)

                subprocess.check_call(args, stdout=logfile,
                                      stderr=subprocess.STDOUT)
                logfile.close()

                logfile = open("pcre_install.log", 'w')

                # Install PCRE
                args = [
                    'bash',
                    os.path.join(
                        os.path.dirname(__file__),
                        'install_pcre.sh')
                    ]
                args.append(tmpdir)

                subprocess.check_call(args, stdout=logfile,
                                      stderr=subprocess.STDOUT)
                logfile.close()

                # Get paths to Python installs
                logfile = open("python_paths.log", 'w')
                args = [
                    'bash',
                    os.path.join(
                        os.path.dirname(__file__),
                        'get_py_paths.sh')
                    ]
                args.append(tmpdir)
                if MAJ == 3:
                    args.append('py3')

                subprocess.check_call(args, stdout=logfile,
                                      stderr=subprocess.STDOUT)
                logfile.close()

                # Install SWIG
                logfile = open("swig_install.log", 'w')
                args = [
                    'bash',
                    os.path.join(
                        os.path.dirname(__file__),
                        'install_swig.sh')
                    ]
                args.append(tmpdir)

                subprocess.check_call(args, stdout=logfile,
                                      stderr=subprocess.STDOUT)
                logfile.close()

                # Install CCTools
                logfile = open("cctools_install.log", 'w')
                args = [
                    'bash',
                    os.path.join(
                        os.path.dirname(__file__),
                        'install_cctools.sh')
                    ]
                args.append(tmpdir)

                if MAJ == 3:
                    args.append('py3')

                if '--user' in sys.argv:
                    args.append('--user')

                subprocess.check_call(args, stdout=logfile,
                                      stderr=subprocess.STDOUT)
                logfile.close()

                shutil.rmtree(tmpdir)
            except subprocess.CalledProcessError:
                shutil.rmtree(tmpdir)
                raise InstallError(logfile)

        try:
            cfg.read_dict(DEFAULT_CONFIG)
        except AttributeError:
            for key, val in DEFAULT_CONFIG.iteritems():
                cfg.add_section(key)
                for k, v in val.iteritems():
                    cfg.set(key, k, v)

        print('Installing shadho_worker')
        shutil.copy(os.path.join('.', 'scripts', 'shadho_worker.py'),
                    SHADHO_DIR)

        home = os.path.expanduser(os.environ['HOME'] if 'HOME' in os.environ
                                      else os.environ['USERPROFILE'])
        if not os.path.isfile(os.path.join(home, '.shadhorc')):
            print('Copying default .shadhorc to home directory')
            with open(os.path.join(home, '.shadhorc'), 'w') as f:
                cfg.write(f)

        install.run(self)

setup(
    name='shadho',
    version='0.1a1',
    description='Hyperparameter optimizer with distributed hardware at heart',
    url='https://github.com/jeffkinnison/shadho',
    author='Jeff Kinnison',
    author_email='jkinniso@nd.edu',
    packages=['shadho',
              'shadho.managers'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Users',
        'License :: MIT',
        'Topic :: Machine Learning :: Hyperparameter Optimization',
        'Topic :: Distributed Systems :: Task Allocation',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Operating System :: MacOS',
    ],
    keywords='machine_learning hyperparameters distributed_computing',
    install_requires=[
        'scipy>=0.18.1',
        'numpy>=1.12.0',
        'scikit-learn>=0.18.1'
    ],
    scripts=[
        'bin/shadho_wq_worker',
        'bin/shadho_wq_factory'
    ],
    tests_require=['pytest'],
    cmdclass={'install': InstallCCToolsCommand}
)
