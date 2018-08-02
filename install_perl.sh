#!/usr/bin/env bash

base="$1"

cd $base
wget http://www.cpan.org/src/5.0/perl-5.26.0.tar.gz
tar xzf perl-5.26.0.tar.gz
cd perl-5.26.0
./Configure -des -Dprefix="${base}/perl" -Duseshrplib
make -j8 && make install -j8
