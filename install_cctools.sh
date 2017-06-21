#!/usr/bin/env bash

# Set paths to the Python and swig executables

mkdir /tmp/shadho

py2path="$(dirname "$(dirname "$(command -v python2)")")"
py2version="$(python2 -c 'import sys; print("{}.{}".format(*sys.version_info[:2]))')"

py3path=""

for opt in "$@"; do
    if [ "$opt" == "py3" ]; then
        py3path="$(dirname "$(dirname "$(command -v python3)")")"
        py3version="$(python3 -c 'import sys; print("{}.{}".format(*sys.version_info[:2]))')"
    fi
done

cd /tmp/shadho
wget http://www.cpan.org/src/5.0/perl-5.26.0.tar.gz
tar xzf perl-5.26.0.tar.gz
cd perl-5.26.0
./Configure -des -Dprefix=/tmp/shadho -Duseshrplib
make -j8 && make install -j8
perlpath="/tmp/shadho"

cd /tmp/shadho
wget ftp://ftp.csx.cam.ac.uk/pub/software/programming/pcre/pcre-8.40.tar.gz
tar xzf pcre-8.40.tar.gz
cd pcre-8.40
./configure --prefix=/tmp/shadho
make -j8 && make install -j8


cd /tmp/shadho
wget http://prdownloads.sourceforge.net/swig/swig-3.0.12.tar.gz
tar xzf swig-3.0.12.tar.gz
cd swig-3.0.12
PATH="${py3path}/bin:$PATH" LDFLAGS="-L${py3path}/lib" CFLAGS="-I${py3path}/include" ./configure \
    --prefix=/tmp/shadho \
    --with-pcre-prefix=/tmp/shadho \
    --with-perl5=/tmp/shadho/bin/perl \
    --with-python="${py2path}/bin/python2" \
    --with-python="${py3path}/bin/python3.5m"

make -j8 && make install -j8
swigpath="/tmp/shadho"

# Get the CCTools source
cd /tmp/shadho
git clone -b hyperopt_worker https://github.com/nkremerh/cctools

# Configure, make, and install
cd cctools

prefix="$HOME/.shadho"

export LD_LIBRARY_PATH="/tmp/shadho/lib:$LD_LIBRARY_PATH"
export LIBRARY_PATH="/tmp/shadho/lib:$LIBRARY_PATH"

if [ ! -z "$py3path" ]; then
    ./configure \
        --prefix=$prefix \
        --with-python-path=$py2path \
        --with-python3-path=$py3path \
        --with-perl-path=$perlpath \
        --with-swig-path=$swigpath
else
    ./configure \
        --prefix=$prefix \
        --with-python-path=$py2path \
        --with-perl-path=$perlpath \
        --with-swig-path=$swigpath
fi

make -j 8
make install -j 8

# Move the Work Queue install into site-packages so that it can be used without
# additional configuration
if [ ! -z "$py2path" ]; then
    cclib="${prefix}/lib/python${py2version}/site-packages"
    cp "${cclib}/work_queue.py" "${cclib}/_work_queue.so" \
        "$py2path/lib/python${py2version}/site-packages"
fi

if [ ! -z "$py3path" ]; then
    cclib="${prefix}/lib/python${py3version}/site-packages"
    cp "${cclib}/work_queue.py" "${cclib}/_work_queue.so" \
        "$py3path/lib/python${py3version}/site-packages"
fi

# Clean up
rm -rf /tmp/shadho
