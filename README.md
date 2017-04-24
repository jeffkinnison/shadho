# `shadho` - Scalable Hardware-Aware Distributed Hyperparameter Optimizer

`shadho` is framework for distributed hyperparameter optimization developed for
machine/deep learning applications.

## Dependencies

Python Packages:

- `scipy >= 0.18.1`
- `numpy >= 1.12.0`
- `scikit-learn >= 0.18.1`
- `pandas >= 0.18.1`

Additionally, `shadho` uses [Work Queue](http://ccl.cse.nd.edu/software/workqueue/ "Work Queue home")
to manage the distributed computing environment. Work Queue is compatible with
Amazon EC2; the HTCondor distributed environment; and the SGE, PBS, and Torque
batch systems; and it may be extended to work with other distributed/cloud
environments and batch systems.

## Installation

### With `pip`

```
pip install shadho
```

### With `conda`

```
conda install shadho
```

### From GitHub

```
git clone https://github.com/jeffkinnison/shadho
cd shadho
pip install .
bash install_cctools.sh
```

## Usage

For detailed instructions on how to use `shadho`, see the documentation at
