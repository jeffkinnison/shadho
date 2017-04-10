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

if [ ! -f "$py3path/bin/2to3" ]; then
    echo $'#!/usr/bin/env python3\nimport sys\nfrom lib2to3.main import main\n\nsys.exit(main("lib2to3.fixes"))' > "$py3path/bin/2to3"
    chmod 755 "$py3path/bin/2to3"
fi

# Configure, make, and install
cd cctools
./configure \
    --with-python-path=$py2path \
    --with-python3-path=$py3path

make -j 8
make install -j 8
