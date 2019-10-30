#!/usr/bin/env python
from setuptools import setup
from setuptools.command.install import install


setup(
    name='shadho',
    version='0.2',
    description='Hyperparameter optimizer with distributed hardware at heart',
    url='https://github.com/jeffkinnison/shadho',
    author='Jeff Kinnison',
    author_email='jkinniso@nd.edu',
    python_requires='>=3.5',
    packages=['shadho',
              'shadho.installers',
              'shadho.managers',
              'shadho.workers',],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Operating System :: POSIX',
        'Operating System :: Unix',
    ],
    keywords='machine_learning hyperparameters distributed_computing',
    install_requires=[
        'numpy',
        'scipy',
        'scikit-learn',
        'pyrameter'
    ],
    tests_require=['pytest'],
    include_package_data=True,
)
