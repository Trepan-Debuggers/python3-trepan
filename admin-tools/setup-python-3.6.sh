#!/bin/bash
PYTHON_VERSION=3.6.15

# FIXME put some of the below in a common routine
function setup_version {
    local repo=$1
    version=$2
    echo Running setup $version on $repo ...
    (cd ../$repo && . ./admin-tools/setup-${version}.sh)
    return $?
}

export PATH=$HOME/.pyenv/bin/pyenv:$PATH
trepan3_owd=$(pwd)
bs=${BASH_SOURCE[0]}
if [[ $0 == $bs ]] ; then
    echo "This script should be *sourced* rather than run directly through bash"
    exit 1
fi

mydir=$(dirname $bs)
fulldir=$(readlink -f $mydir)
(cd $fulldir/.. && \
     setup_version python-uncompyle6 master && \
     setup_version python-filecache master && \
     setup_version pycolumnize master && \
     setup_version python-xdis python-3.6 \
    )
cd $trepan3_owd
for file in */.python; do
    rm -v $file || true
done

git checkout python-3.6-to-3.10 && pyenv local $PYTHON_VERSION && git pull
