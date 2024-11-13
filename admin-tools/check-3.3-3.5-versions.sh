#!/bin/bash
function finish {
  cd $trepan3k_owd
}

# FIXME put some of the below in a common routine
trepan3k_owd=$(pwd)
# trap finish EXIT

cd $(dirname ${BASH_SOURCE[0]})
if ! source ./pyenv-3.3-3.5-versions ; then
    exit $?
fi

if ! source ./setup-python-3.3.sh ; then
    exit $?
fi

cd ..
for version in $PYVERSIONS; do
    if ! pyenv local $version ; then
	exit $?
    fi
    python --version
    make clean && pip install -e .
    if ! make check; then
	exit $?
    fi
    echo === $version ===
done
finish
