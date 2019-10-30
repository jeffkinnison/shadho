# `shadho` - Scalable Hardware-Aware Distributed Hyperparameter Optimizer

`shadho` is framework for distributed hyperparameter optimization developed for
machine/deep learning applications.

- Website/Documentation: <https://shadho.readthedocs.io>
- Bug Reports: <https://github.com/jeffkinnison/shadho/issues>

# Installation

**Note:** The post-install step may look like it hangs, but it is just
compiling Work Queue behind the scenes and my take a few minutes.

```
$ pip install shadho
$ python -m shadho.installers.workqueue
```

## Installing on a Shared System

The owner of the shared installation should follow the steps above. Then,
another user installs with

```
$ pip install shadho
$ python -m shadho.installers.workqueue --prefix <path to shared install>
```

# Dependencies

- numpy
- scipy
- [pyrameter](https://github.com/jeffkinnison/pyrameter)
- [Work Queue](http://ccl.cse.nd.edu/software/workqueue/) (Built and installed by setup.py)
