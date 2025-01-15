#!/bin/bash
PYTHON_VERSION=3.3

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
(cd $mydir/../../../rocky && \
     setup_version python-uncompyle6 python-3.3 && \
     setup_version python-xdis python-3.3 && \
     setup_version python-filecache python-3.3 && \
     setup_version shell-term-background python-3.3 && \
     setup_version pytracer python-3.3 && \
     setup_version pycolumnize python-3.3 \
     setup_version python-xdis python-3.3 \
    )

cd $trepan3k_owd
rm -v */.python-version 2>/dev/null || true

checkout_finish python-3.3-to-3.5
