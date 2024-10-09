#!/bin/bash
PYTHON_VERSION=3.3

# FIXME put some of the below in a common routine
function checkout_version {
    local repo=$1
    version=${2:-python-3.3-to-3.5}
    echo Checking out $version on $repo ...
    (cd ../$repo && git checkout $version && pyenv local $PYTHON_VERSION) && \
	git pull
    return $?
}

export PATH=$HOME/.pyenv/bin/pyenv:$PATH
trepan3k_owd=$(pwd)
bs=${BASH_SOURCE[0]}
if [[ $0 == $bs ]] ; then
    echo "This script should be *sourced* rather than run directly through bash"
    exit 1
fi

mydir=$(dirname $bs)
fulldir=$(readlink -f $mydir)
(cd $fulldir/.. && \
     setup_version python-uncompyle6 python-3.3 && \
     setup_version python-xdis python-3.3 && \
     setup_version python-filecache python-3.3 && \
     setup_version shell-term-background python-3.3 && \
     setup_version pytracer python-3.3 && \
     setup_version pycolumnize python-3.0 \
     setup_version python-xdis python-3.3 \
    )

cd $trepan3k_owd
rm -v */.python-version 2>/dev/null || true

git checkout python-3.3-to-3.5 && pyenv local $PYTHON_VERSION && git pull
