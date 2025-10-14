#!/usr/bin/bash
PACKAGE_NAME=trepan3k
PACKAGE_MODULE=trepan
trepan3k_owd=$(pwd)
bs=${BASH_SOURCE[0]}
mydir=$(dirname $bs)
trepan3k_fulldir=$(readlink -f $mydir)
cd $trepan3k_fulldir
. ./checkout_common.sh

pyenv_file="pyenv-3.6-3.10-versions"
if ! source $pyenv_file ; then
    echo "Having trouble reading ${pyenv_file} version $(pwd)"
    exit 1
fi

source ../${PACKAGE_MODULE}/version.py
if [[ ! $__version__ ]] ; then
    echo "Something is wrong: __version__ should have been set."
    exit 1
fi

cd ../dist/

install_file="trepan3k_36-${__version__}.tar.gz"
install_check_command="trepan3k --help"
for version in $PYVERSIONS; do
    echo "*** Installing ${install_file} for Python ${version} ***"
    echo $version
    pyenv local $version
    pip install $install_file
    $install_check_command
    echo "----"
done
