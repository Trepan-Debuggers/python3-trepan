#/bin/bash
trepan_merge_32_owd=$(pwd)
PYTHON_VERSION=3.2
pyenv local $PYTHON_VERSION
cd $(dirname ${BASH_SOURCE[0]})
if . ./setup-python-3.2.sh; then
    git merge python-3.6-to-3.10
fi
cd $trepan_merge_32_owd
