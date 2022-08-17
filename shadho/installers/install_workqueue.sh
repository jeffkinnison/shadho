#!/usr/bin/env bash

# base is a temporary directory for the install
# shadho_dir is where relevant SHADHO files are installed
if [ "$#" -ge "2" ]; then
    base="$1"
    shadho_dir="$2"
elif [ "$#" -eq "1" ]; then
    base="/tmp/$(mktemp shadho_install.XXXXXXXXXX)"
    mkdir $base
    shadho_dir="$1"
else
    base="/tmp/$(mktemp shadho_install.XXXXXXXXXX)"
    mkdir $base
    shadho_dir="$HOME/.shadho"
fi

# Set some variables for later
cctools_version="cctools-7.4.2-source"

# For reasons known only to Cthulhu himself, SWIG requires a Python 2 install
# to generate Python 3 bindings. To this day, scholars (read: the SHADHO devs)
# are driven mad by this requirement. Anyway, find Python 2 or install it if it
# isn't around.
cd $base

install_python_major_version="$(python3 -c 'import sys; print(sys.version_info.major)')"
install_python_minor_version="$(python3 -c 'import sys; print(sys.version_info.minor)')"
install_python_prefix="$(python3 -c 'import sys; print(sys.base_prefix)')"
install_python_executable="$(python3 -c 'import sys; print(sys.base_exec_prefix + "/bin")')"

python2_version="$(python2 --version)"
if [ "$?" -eq "0" ] || [ ! -z "$python2_version" ]; then
    maj="$(python2 -c 'import sys; print(sys.version_info.major)')"
    min="$(python2 -c 'import sys; print(sys.version_info.minor)')"
else
    maj="0"
    min="0"
fi

echo "$maj $min"

if [ "$maj" -eq "2" ] && [ "$min" -eq "7" ]; then
    python2_prefix="$(python2 -c 'import sys; print(sys.exec_prefix)')"
    python2_exec="$(python2 -c 'import sys; print(sys.executable)')"
else
    wget https://www.python.org/ftp/python/2.7.16/Python-2.7.16.tgz
    tar xzf Python-2.7.16.tgz
    cd Python-2.7.16
    ./configure --prefix="${base}/python"
    make -j8 && make install -j8
    python2_prefix="$base/python"
    python2_exec="$python2_prefix/bin/python2"
fi

maj="0"
min="0"
# PCRE must be v8.40+ to compile the correct version of SWIG.
echo "BASE!!!!!!!!!!!! $base"
cd $base
pcre_version="$(pcre-config --version)"
if [ "$?" -eq "0" ] || [ ! -z "$pcre_version" ]; then
    maj="$(echo $pcre_version | sed -En 's/^([[:digit:]]+)\.([[:digit:]]+)$/\1/p')"
    min="$(echo $pcre_version | sed -En 's/^([[:digit:]]+)\.([[:digit:]]+)$/\2/p')"
else
    maj="0"
    min="0"
fi

# If the installed version is insufficient, temporarily install 8.40
if [ "$maj" -ge "8" ]; then
    pcre_prefix="$(pcre-config --prefix)"
else
    cd $base
    wget https://ftp.pcre.org/pub/pcre/pcre-8.44.tar.gz # ftp://ftp.csx.cam.ac.uk/pub/software/programming/pcre/pcre-8.40.tar.gz
    tar xzf pcre-8.44.tar.gz
    cd pcre-8.44
    ./configure --prefix="$base/pcre"
    make -j8 && make install -j8
    pcre_prefix="$base/pcre"
fi

maj="0"
min="0"

echo "BASE!!!!!!!!!!!! $base"
cd $base
swig_version="$(swig -version)"

if [ "$?" -eq 0 ] && [ ! -z "$swig_version" ]; then
    swig_version="$(echo $swig_version | grep SWIG | cut -d \  -f 3)"
fi

if [ "$?" -eq "0" ] || [ ! -z "$swig_version" ]; then
    maj="$(echo $swig_version | sed -En 's/^([[:digit:]]+)\.([[:digit:]]+)\.([[:digit:]]+)$/\1/p')"
    min="$(echo $swig_version | sed -En 's/^([[:digit:]]+)\.([[:digit:]]+)\.([[:digit:]]+)$/\2/p')"
else
    maj="0"
    min="0"
fi

if [ "$maj" -ge "4" ] && [ "$min" -ge "0" ]; then
    swig_prefix="$(dirname $(dirname $(command -v swig)))"
else
    wget http://prdownloads.sourceforge.net/swig/swig-4.0.2.tar.gz
    tar xzf swig-4.0.2.tar.gz
    cd swig-4.0.2

    python2_exec="$(python2 -c 'import sys; print(sys.executable)')"
    ./configure \
        --prefix="$base/swig" \
        --with-pcre-prefix="$pcre_prefix" \
        --without-perl5 \
        --with-python="$python2_exec" \
        --with-python3="$install_python_executable"
    make -j8 && make install -j
    swig_prefix=$base/swig
fi

maj="0"
min="0"

# Attempt to wget CCTools, fall back to curl if things go south
cd $base
wget "http://ccl.cse.nd.edu/software/files/${cctools_version}.tar.gz"
if [ "$?" -ne "0" ]; then
    curl -o "${cctools_version}.tar.gz" "http://ccl.cse.nd.edu/software/files/${cctools_version}.tar.gz"
fi

if [ ! -f "${cctools_version}.tar.gz" ]; then
    exit 1
fi

tar xf "${cctools_version}.tar.gz"
cd "${cctools_version}"

python2_prefix="$(python2 -c 'import sys; print(sys.prefix)')"
./configure \
    --prefix="$shadho_dir" \
    --with-swig-path="$swig_prefix" \
    --with-perl-path=no \
    --with-python-path="$install_python_prefix" \
    --without-system-parrot

make -j8 && make install -j
