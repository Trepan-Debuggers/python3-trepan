#/bin/bash
trepan_merge_311_owd=$(pwd)
PYTHON_VERSION=3.11
pyenv local $PYTHON_VERSION
cd $(dirname ${BASH_SOURCE[0]})
if . ./setup-python-3.11.sh; then
    git merge master
fi
cd $trepan_merge_311_owd
