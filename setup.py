#!/usr/bin/env python
from setuptools import setup
from setuptools.command.install import install
import site
import subprocess
import sys

MAJ = sys.version_info[0]


class InstallCCToolsCommand(install):
    """Helper to install CCTools.
    """
    def run(self):
        """Install WorkQueue from the CCTools suite to site-packages.

        SHADHO uses WorkQueue, a member of the `CCTools software suite<http://ccl.cse.nd.edu>`,
        to manage the distributed computing environment. This function installs
        CCTools and moves the related Python module and shared library to the
        site-packages directory.
        """
        if MAJ == 3:
            subprocess.call('bash install_cctools.sh py3')
        else:
            subprocess.call('bash install_cctools.sh')
        install.run()


setup(
    name='shadho',
    version='0.1a1',
    description='Hyperparameter optimizer with distributed hardware at heart',
    url='https://github.com/jeffkinnison/shadho',
    author='Jeff Kinnison',
    author_email='jkinniso@nd.edu',
    packages=['shadho'],
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
        'scikit-learn>=0.18.1',
        'pandas>=0.18.1'
    ],
    extras_require={
        'test': ['nose', 'coverage']
    },
    cmdclass={'install': InstallCCToolsCommand}
)
