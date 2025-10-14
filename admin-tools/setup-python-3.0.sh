#!/bin/bash
# Check out 3.0-to-3.2 branch and dependent development branches
PYTHON_VERSION=3.0

trepan3k_owd=$(pwd)
bs=${BASH_SOURCE[0]}
if [[ $0 == $bs ]] ; then
    echo "This script should be *sourced* rather than run directly through bash"
    exit 1
fi

trepan3k_owd=$(pwd)
mydir=$(dirname $bs)
trepan3k_fulldir=$(readlink -f $mydir)
. $trepan3k_fulldir/checkout_common.sh

(cd $trepan3k_fuilldir/../../../rocky && \
     setup_version python-uncompyle6 python-3.0 \
     setup_version python-filecache python-3.0 && \
     setup_version pytracer python-3.0 \
     setup_version pycolumnize python-3.0 && \
     setup_version python-xdis python-3.0 \
    )

checkout_finish python-3.0-to-3.2
