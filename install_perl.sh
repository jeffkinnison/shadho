#!/usr/bin/env bash

base="$1"
install_python_major_version="$2"
install_python_minor_version="$3"
install_python_prefix="$4"
install_python_executable="$5"


perl_version="$(perl -e 'print $^V' | cut -c 2-)"
maj="$(echo $perl_version | sed -rn 's/^([[:digit:]]+)\.([[:digit:]]+)\.([[:digit:]]+)$/\1/p')"
min="$(echo $perl_version | sed -rn 's/^([[:digit:]]+)\.([[:digit:]]+)\.([[:digit:]]+)$/\2/p')"

if [ "$maj" -ge "5" ] && [ "$min" -ge "26" ]; then
    perl_prefix="$(dirname $(dirname $(perl -e 'print $^X')))"
else
    cd $base
    wget http://www.cpan.org/src/5.0/perl-5.26.0.tar.gz
    tar xzf perl-5.26.0.tar.gz
    cd perl-5.26.0
    ./Configure -des -Dprefix="${base}/perl" -Duseshrplib
    make -j8 && make install -j8
    perl_prefix="$base/perl"
fi

echo "perl_prefix=$perl_prefix" >> $base/cctools_install_env.sh
echo "perl_exec=$perl_prefix/bin/perl" >> $base/cctools_install_env.sh
