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

if [ ! -f "$py3path/bin/python3-config" ]; then
    sed -i "s@prefix_build=PREFIXBUILD@prefix_build=\"$py3path\"@" "./travis_helpers/python3-config"
    sed -i "s@VERSION=\"3.5\"@VERSION=\"$TRAVIS_PYTHON_VERSION\"@" "./travis_helpers/python3-config"
    mv "./travis_helpers/python3-config" "$py3path/bin"
    chmod 755 "$py3path/bin/python3-config"
fi

# Configure, make, and install
cd cctools
libpy=`find /opt -name "libpython${TRAVIS_PYTHON_VERSION}m.so"`
echo $libpy
libpydir=`dirname $libpy`
libpybase=`basename $libpy`

export CPATH="$py3path/include/python${TRAVIS_PYTHON_VERSION}m:$CPATH"
export LD_LIBRARY_PATH="$libpydir:$py3path/lib:$py3path/lib64:$LD_LIBRARY_PATH"

LDFLAGS="-L$libpydir -l$libpybase" CFLAGS="-I$py3path/include/python${TRAVIS_PYTHON_VERSION}m" ./configure \
    --with-python-path=$py2path \
    --with-python3-path=$py3path

make -j 8
make install -j 8
