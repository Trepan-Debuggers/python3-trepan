#!/bin/bash
# Check out 3.6-to-3.10 branch and dependent development branches
PYTHON_VERSION=3.6

trepan3k_owd=$(pwd)
bs=${BASH_SOURCE[0]}
if [[ $0 == $bs ]] ; then
    echo "This script should be *sourced* rather than run directly through bash"
    exit 1
fi

mydir=$(dirname $bs)
trepan3k_fulldir=$(readlink -f $mydir)
. $trepan3k_fulldir/checkout_common.sh

(cd $mydir/../../../rocky && \
     setup_version python-uncompyle6 python-3.6 && \
     setup_version python-filecache python-3.6 && \
     setup_version shell-term-background python-3.6 && \
     setup_version pytracer python-3.6
    )

checkout_finish python-3.6-to-3.10
