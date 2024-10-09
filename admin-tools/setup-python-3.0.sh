#!/bin/bash
# Check out 3.0-to-3.1 branch and dependent development branches

bs=${BASH_SOURCE[0]}
if [[ $0 == $bs ]] ; then
    echo "This script should be *sourced* rather than run directly through bash"
    exit 1
fi

PYTHON_VERSION=3.1

export PATH=$HOME/.pyenv/bin/pyenv:$PATH
trepan3k_owd=$(pwd)
mydir=$(dirname $bs)
cd $mydir
. ./checkout_common.sh
fulldir=$(readlink -f $mydir)
(cd $fulldir/.. && \
     setup_version_trepan3k python-uncompyle6 python-3.0 \
     setup_version trepan3k python-xdis python-3.0 && \
     setup_version_trepan3k python-filecache python-3.0 && \
     setup_version_trepan3k pycolumnize python-3.0 \
    )

checkout_finish python-3.0-to-3.1
