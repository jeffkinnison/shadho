#!/usr/bin/env bash

base="$1"
install_python_major_version="$2"
install_python_minor_version="$3"
install_python_prefix="$4"
install_python_executable="$5"

source $base/cctools_install_env.sh


cd $base

wget http://ccl.cse.nd.edu/software/files/cctools-7.0.9-source.tar.gz

if [ "$?" -ne "0" ]; then
    curl -o cctools-7.0.9-source.tar.gz http://ccl.cse.nd.edu/software/files/cctools-7.0.9-source.tar.gz
fi

if [ ! -f "cctools-7.0.9-source.tar.gz" ]; then
    exit 1
fi

cd $base

tar xf cctools-7.0.9-source.tar.gz
cd cctools-7.0.9-source

mkdir -p $HOME/.shadho

if [ "$install_python_major_version" -eq "3" ]; then
    python2_prefix="$(python2 -c 'import sys; print(sys.prefix)')"
    ./configure \
        --prefix="$HOME/.shadho" \
        --with-swig-path="$swig_prefix" \
        --with-perl-path="$perl_prefix" \
        --with-python-path="$python2_prefix" \
        --with-python3-path="$install_python_prefix" \
        --without-system-sand \
        --without-system-allpairs \
        --without-system-wavefront \
        --without-system-chirp \
        --without-system-parrot \
        --without-system-umbrella
else
    ./configure \
        --prefix="$HOME/.shadho" \
        --with-swig-path="$swig_prefix" \
        --with-perl-path="$perl_prefix" \
        --with-python-path="$install_python_prefix" \
        --without-system-sand \
        --without-system-allpairs \
        --without-system-wavefront \
        --without-system-chirp \
        --without-system-parrot \
        --without-system-umbrella
fi

make -j8 && make install -j
