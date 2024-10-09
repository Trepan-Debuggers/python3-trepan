#!/bin/bash
# Check out 3.6-to-3.10 branch and dependent development branches

bs=${BASH_SOURCE[0]}
if [[ $0 == $bs ]] ; then
    echo "This script should be *sourced* rather than run directly through bash"
    exit 1
fi

PYTHON_VERSION=3.6

export PATH=$HOME/.pyenv/bin/pyenv:$PATH
trepan3k_owd=$(pwd)
mydir=$(dirname $bs)
cd $mydir
. ./checkout_common.sh
(cd $fulldir/.. && \
     setup_version python-uncompyle6 python-3.6 && \
     setup_version python-filecache python-3.6 && \
     setup_version shell-term-background python-3.3 && \
     setup_version pytracer python-3.6 \
     setup_version pycolumnize master && \
     setup_version python-xdis python-3.6 \
    )

checkout_finish python-3.6-to-3.10
