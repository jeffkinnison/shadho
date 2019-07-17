#!/usr/bin/env bash

base="$1"
install_python_major_version="$2"
install_python_minor_version="$3"
install_python_prefix="$4"
install_python_executable="$5"

source $base/cctools_install_env.sh


swig_version="$(swig -version | grep SWIG | cut -d \  -f 3)"
echo $swig_version
maj="$(echo $swig_version | sed -rn 's/^([[:digit:]]+)\.([[:digit:]]+)\.([[:digit:]]+)$/\1/p')"
echo $maj
min="$(echo $swig_version | sed -rn 's/^([[:digit:]]+)\.([[:digit:]]+)\.([[:digit:]]+)$/\2/p')"

if [ "$maj" -ge "3" ] && [ "$min" -ge "0" ]; then
    swig_prefix="$(dirname $(dirname $(command -v swig)))"
else
    cd $base
    wget http://prdownloads.sourceforge.net/swig/swig-3.0.12.tar.gz
    tar xzf swig-3.0.12.tar.gz
    cd swig-3.0.12

    if [ "$install_python_major_version" -eq "3" ]; then
        python2_exec="$(python2 -c 'import sys; print(sys.executable)')"
        ./configure \
            --prefix="$base/swig" \
            --with-pcre-prefix="$pcre_prefix" \
            --with-perl5="$perl_exec" \
            --with-python="$python2_exec" \
            --with-python3="$install_python_executable"
    else
        ./configure \
            --prefix="$base/swig" \
            --with-pcre-prefix="$pcre_prefix" \
            --with-perl5="$perl_exec" \
            --with-python="$install_python_executable"
    fi

    make -j8 && make install -j
    swig_prefix="$base/swig"
fi

echo "swig_prefix=$swig_prefix" >> $base/cctools_install_env.sh
