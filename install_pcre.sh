#!/usr/bin/env bash

base="$1"

cd $base
wget ftp://ftp.csx.cam.ac.uk/pub/software/programming/pcre/pcre-8.40.tar.gz
tar xzf pcre-8.40.tar.gz
cd pcre-8.40
./configure --prefix="$base/pcre"
make -j8 && make install -j8
