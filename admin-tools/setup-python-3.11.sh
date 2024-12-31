#!/bin/bash
# Check out 3.11 branch and dependent development branches
PYTHON_VERSION=3.11

bs=${BASH_SOURCE[0]}
if [[ $0 == $bs ]] ; then
    echo "This script should be *sourced* rather than run directly through bash"
    exit 1
fi

export PATH=$HOME/.pyenv/bin/pyenv:$PATH
trepan3k_owd=$(pwd)
mydir=$(dirname $bs)
cd $mydir
. ./checkout_common.sh
(cd $mydir/../../rocky && \
     setup_version python-uncompyle6 master && \
     setup_version python-filecache master && \
     setup_version shell-term-background master && \
     setup_version pytracer master \
     setup_version pycolumnize master && \
     setup_version python-xdis master \
    )

checkout_finish python-3.11
