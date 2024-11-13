#!/bin/bash
function finish {
  cd $trepan3k_owd
}

# FIXME put some of the below in a common routine
trepan3k_owd=$(pwd)
# trap finish EXIT

cd $(dirname ${BASH_SOURCE[0]})
if ! source ./pyenv-newest-versions ; then
    exit $?
fi

. ./setup-master.sh

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
