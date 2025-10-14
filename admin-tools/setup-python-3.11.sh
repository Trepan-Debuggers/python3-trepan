#!/bin/bash
# Check out 3.11 branch and dependent development branches
PYTHON_VERSION=3.11

trepan3k_owd=$(pwd)
bs=${BASH_SOURCE[0]}
if [[ $0 == $bs ]] ; then
    echo "This script should be *sourced* rather than run directly through bash"
    exit 1
fi

mydir=$(dirname $bs)
trepan3k_fulldir=$(readlink -f $mydir)
. $trepan3k_fulldir/checkout_common.sh

(cd $trepan3k_fulldir/../../../rocky && \
     setup_version python-uncompyle6 master && \
     setup_version python-filecache master && \
     setup_version pytracer master && \
     setup_version pycolumnize master
    )

checkout_finish python-3.11
