#!/usr/bin/env bash

# Get BASE
base="$1"

# Get USER
user=""

#if [ "$3" == "--user" ]; then
#    user="0"
#fi

# Get the CCTools source
cd $base
git clone -b hyperopt_worker https://github.com/nkremerh/cctools

# Get paths
perlpath="$base/perl"  # "$(head -1 ${base}/paths.txt | tail -1)"
#py2path="$(head -2 ${base}/paths.txt | tail -1)"
#py2version="$(python2 -c 'import sys; print("{}.{}".format(*sys.version_info[:2]))')"
#py3path="$(head -3 ${base}/paths.txt | tail -1)"
#py3version="$(python3 -c 'import sys; print("{}.{}".format(*sys.version_info[:2]))')"
swigpath="$base/swig"  # "$(head -4 ${base}/paths.txt | tail -1)"

py2path="$(dirname "$(dirname "$(command -v python2)")")"
py2version="$(python2 -c 'import sys; print("{}.{}".format(*sys.version_info[:2]))')"

py3path=""

for opt in "$@"; do
    if [ "$opt" == "py3" ]; then
        py3path="$(dirname "$(dirname "$(command -v python3)")")"
        py3version="$(python3 -c 'import sys; print("{}.{}".format(*sys.version_info[:2]))')"
    elif [ "$opt" == "--user" ]; then
        user="0"
    fi
done

# Configure, make, and install
cd cctools

prefix="$HOME/.shadho"

export LD_LIBRARY_PATH="${base}/pcre/lib:$LD_LIBRARY_PATH"
export LIBRARY_PATH="${base}/pcre/lib:$LIBRARY_PATH"

# pyh="$(dirname $(locate Python.h))"
# export CFLAGS="$pyh:$CFLAGS"

if [ ! -z "$py3path" ]; then
    ./configure \
        --prefix=$prefix \
        --with-python-path=$py2path \
        --with-python3-path=$py3path \
        --with-perl-path=$perlpath \
        --with-swig-path=$swigpath \
        --without-system-resource_monitor \
        --without-system-umbrella \
        --without-system-weaver

    if [ $? -ne 0 ]; then
        exit 1
    fi


else
    ./configure \
        --prefix=$prefix \
        --with-python-path=$py2path \
        --with-perl-path=$perlpath \
        --with-swig-path=$swigpath

    if [ $? -ne 0 ]; then
        exit 1
    fi

fi


make -j 8 && make install -j 8

if [ $? -ne 0 ]; then
    exit 1
fi


# Move the Work Queue install into site-packages so that it can be used without
# additional configuration
if [ ! -z "$py2path" ]; then
    cclib="${prefix}/lib/python${py2version}/site-packages"
    if [ -z "$user" ]; then
        sitepath="${py2path}/lib/python${py2version}/site-packages"
    else
        sitepath="$(python2 -c 'import site; print(site.USER_SITE)')"
    fi

    if [ ! -d "$cclib" ]; then
        mkdir -p "$sitepath"
    fi

    cp "${cclib}/work_queue.py" "${cclib}/_work_queue.so" \
        "$sitepath"
fi

if [ ! -z "$py3path" ]; then
    cclib="${prefix}/lib/python${py3version}/site-packages"
    if [ -z "$user" ]; then
        sitepath="${py3path}/lib/python${py3version}/site-packages"
    else
        sitepath="$(python3 -c 'import site; print(site.USER_SITE)')"
    fi

    if [ ! -d "$cclib" ]; then
        mkdir -p "$cclib"
    fi

    cp "${cclib}/work_queue.py" "${cclib}/_work_queue.so" \
        "$sitepath"
fi
