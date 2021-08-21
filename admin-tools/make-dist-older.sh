#!/bin/bash
PACKAGE=trepan

# FIXME put some of the below in a common routine
function finish {
  cd $owd
}

cd $(dirname ${BASH_SOURCE[0]})
owd=$(pwd)
trap finish EXIT

if ! source ./pyenv-older-versions ; then
    exit $?
fi
if ! source ./setup-python-3.2.sh ; then
    exit $?
fi

<<<<<<< HEAD
. ./setup-python-3.2.sh
=======
. ./admin-tools/setup-python-3.2.sh
>>>>>>> e16b8a13936c86d7dd194090694fd423456df1bd

cd ..
source $PACKAGE/version.py
echo $VERSION

for pyversion in $PYVERSIONS; do
    if ! pyenv local $pyversion ; then
	exit $?
    fi
    # pip bdist_egg create too-general wheels. So
    # we narrow that by moving the generated wheel.

    # Pick out first two number of version, e.g. 3.5.1 -> 35
    first_two_dot=$(echo $pyversion | cut -d'.' -f 1-2 )
    first_two=$(echo $pyversion | cut -d'.' -f 1-2 | sed -e 's/\.//')
    rm -fr build
    python setup.py bdist_egg bdist_wheel
done

# mv -v dist/${PACKAGE}-$VERSION.tar.gz dist/${PACKAGE}3k-$VERSION.tar.gz
