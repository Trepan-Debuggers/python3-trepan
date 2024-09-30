#!/bin/bash
# Check out master branch and dependent development master branches
bs=${BASH_SOURCE[0]}
if [[ $0 == $bs ]] ; then
    echo "This script should be *sourced* rather than run directly through bash"
    exit 1
fi

PYTHON_VERSION=3.12

mydir=$(dirname $bs)
trepan3_owd=$(pwd)
cd $mydir
. ./checkout_common.sh
fulldir=$(readlink -f $mydir)
cd $fulldir/..
(cd $fulldir/.. && \
     setup_version_trepan3k python-uncompyle6 master && \
     setup_version_trepan3k python-filecache master && \
     setup_version_trepan3k pytracer master && \
     setup_version_trepan3k pycolumnize master \
)

checkout_finish master
