#!/usr/bin/env bash

base="$1"
install_python_major_version="$2"
install_python_minor_version="$3"
install_python_prefix="$4"
install_python_executable="$5"


pcre_version="$(pcre-config --version)"
echo $pcre_version
maj="$(echo $pcre_version | sed -rn 's/^([[:digit:]]+)\.([[:digit:]]+)$/\1/p')"
min="$(echo $pcre_version | sed -rn 's/^([[:digit:]]+)\.([[:digit:]]+)$/\2/p')"

if [ "$maj" -ge "8" ] && [ "$min" -ge "40" ]; then
    pcre_prefix="$(pcre-config --prefix)"
else
    cd $base
    wget ftp://ftp.csx.cam.ac.uk/pub/software/programming/pcre/pcre-8.40.tar.gz
    tar xzf pcre-8.40.tar.gz
    cd pcre-8.40
    ./configure --prefix="$base/pcre"
    make -j8 && make install -j8
    pcre_prefix="$base/pcre/bin/pcre-config --prefix"
fi

echo "pcre_prefix=$pcre_prefix" >> $base/cctools_install_env.sh
