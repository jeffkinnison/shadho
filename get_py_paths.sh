#!/usr/bin/env bash

base="$1"

py2path="$(dirname "$(dirname "$(command -v python2)")")"
py2version="$(python2 -c 'import sys; print("{}.{}".format(*sys.version_info[:2]))')"

py3path=""

for opt in "$@"; do
    if [ "$opt" == "py3" ]; then
        py3path="$(dirname "$(dirname "$(command -v python3)")")"
        py3version="$(python3 -c 'import sys; print("{}.{}".format(*sys.version_info[:2]))')"
    fi
done

cd $base
echo $py2path >> paths.txt
echo $py3path >> paths.txt
