#/bin/bash
trepan_merge_36_owd=$(pwd)
PYTHON_VERSION=3.6
cd $(dirname ${BASH_SOURCE[0]})
if . ./setup-python-3.6.sh; then
    git merge master
fi
cd $trepan_merge_36_owd
