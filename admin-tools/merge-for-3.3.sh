#/bin/bash
trepan_merge_33_owd=$(pwd)
PYTHON_VERSION=3.3
pyenv local $PYTHON_VERSION
cd $(dirname ${BASH_SOURCE[0]})
if . ./setup-python-3.3.sh; then
    git merge python-3.6-to-3.10
fi
cd $trepan_merge_33_owd
