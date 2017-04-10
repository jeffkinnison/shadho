#!/usr/bin/env python

from distutils.core import setup

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
        'Intended Audience :: Users',
        'Topic :: Machine Learning :: Hyperparameter Optimization',
        'Topic :: Distributed Systems :: Task Allocation',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='machine_learning hyperparameters distributed_computing',
    install_requires=[
        'scipy',
        'numpy',
        'scikit-learn',
        'pandas'
    ],
    extras_require={
        'test': ['nose', 'coverage']
    }
)
