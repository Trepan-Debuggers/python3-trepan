#!/bin/bash
PACKAGE=trepan

# FIXME put some of the below in a common routine
function finish {
  cd $owd
}

cd $(dirname ${BASH_SOURCE[0]})
owd=$(pwd)
trap finish EXIT

if ! source ./pyenv-newest-versions ; then
    exit $?
fi
if ! source ./setup-master.sh ; then
    exit $?
fi

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
    # We can't use a universal wheel because depdencies on the decompiler changes
    # for 3.7 and 3.8
    python wheel .
    if [[ $first_two =~ py* ]]; then
	if [[ $first_two =~ pypy* ]]; then
	    # For PyPy, remove the what is after the dash, e.g. pypy37-none-any.whl instead of pypy37-7-none-any.whl
	    first_two=${first_two%-*}
	fi
	mv -v dist/${PACKAGE}-$__version__-{py3,$first_two}-none-any.whl
    else
	mv -v dist/${PACKAGE}-$__version__-{py3,py$first_two}-none-any.whl
    fi
done

pyenv local 3.12
python ./setup.py sdist
# mv -v dist/${PACKAGE}-$VERSION.tar.gz dist/${PACKAGE}3k-$VERSION.tar.gz
