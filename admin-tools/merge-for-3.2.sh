#/bin/bash
owd=$(pwd)
cd $(dirname ${BASH_SOURCE[0]})
if . ./setup-python-3.2.sh; then
    git merge python-3.6-to-3.10
fi
cd $owd
