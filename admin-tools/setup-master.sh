#!/bin/bash
PYTHON_VERSION=3.7.10

# FIXME put some of the below in a common routine
function finish {
  cd $owd
}

export PATH=$HOME/.pyenv/bin/pyenv:$PATH
owd=$(pwd)
bs=${BASH_SOURCE[0]}
mydir=$(dirname $bs)
fulldir=$(readlink -f $mydir)
(cd ../python-uncompyle6 && ./admin-tools/setup-master)
cd $fulldir/..
git checkout master && pyenv local $PYTHON_VERSION && git pull
cd $owd
