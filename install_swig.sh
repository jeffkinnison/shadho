#!/usr/bin/env bash

base="$1"

cd $base

# get python paths from paths.txt
py2path="$(head -2 ${base}/paths.txt | tail -1)"
py3path="$(head -3 ${base}/paths.txt | tail -1)"

wget http://prdownloads.sourceforge.net/swig/swig-3.0.12.tar.gz
tar xzf swig-3.0.12.tar.gz
cd swig-3.0.12
PATH="${py3path}/bin:$PATH" LDFLAGS="-L${py3path}/lib" CFLAGS="-I${py3path}/include" ./configure \
    --prefix="$base/swig" \
    --with-pcre-prefix="$base/pcre" \
    --with-perl5="${base}/bin/perl" \
    --with-python="${py2path}/bin/python2" \
    --with-python="${py3path}/bin/python3.5m"

make -j8 && make install -j8
