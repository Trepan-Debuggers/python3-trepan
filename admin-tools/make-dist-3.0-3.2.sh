#!/bin/bash
PACKAGE=trepan3k

# FIXME put some of the below in a common routine
function finish {
  cd $make_trepan_dist_30_owd
}

make_trepan_dist_30_owd=$(pwd)

trap finish EXIT

cd $(dirname ${BASH_SOURCE[0]})

if ! source ./pyenv-3.0-3.2-versions ; then
    exit $?
fi
if ! source ./setup-python-3.0.sh ; then
    exit $?
fi

cd ..
source trepan/version.py
if [[ ! -n $__version__ ]]; then
    echo "You need to set __version__ first"
fi
echo $__version__

for pyversion in $PYVERSIONS; do
    echo --- $pyversion ---
    if [[ ${pyversion:0:4} == "pypy" ]] ; then
	echo "$pyversion - PyPy does not get special packaging"
	continue
    fi
    if ! pyenv local $pyversion ; then
	exit $?
    fi
    # pip bdist_egg create too-general wheels. So
    # we narrow that by moving the generated wheel.

    # Pick out first two number of version, e.g. 3.5.1 -> 35
    first_two=$(echo $pyversion | cut -d'.' -f 1-2 | sed -e 's/\.//')
    rm -fr build
    python setup.py bdist_egg bdist_wheel
    mv -v dist/${PACKAGE}-$__version__-{py3,$first_two}-none-any.whl
done

python ./setup.py sdist
tarball=dist/${PACKAGE}-${__version__}.tar.gz
if [[ -f $tarball ]]; then
    mv -v $tarball dist/${PACKAGE}_30-${__version__}.tar.gz
fi
finish
