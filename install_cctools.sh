#!/usr/bin/env bash

# Get the CCTools source
git clone -b hyperopt_worker https://github.com/nkremerh/cctools

# Set paths to the Python and swig executables
py2path=`which python2`
py3path=`which python3`

py2path=`dirname $py2path`
py2path=`dirname $py2path`
py3path=`dirname $py3path`
py3path=`dirname $py3path`

# Configure, make, and install
cd cctools
./configure \
    --with-python-path=$py2path \
    --with-python3-path=$py3path

make -j 8
make install -j 8
