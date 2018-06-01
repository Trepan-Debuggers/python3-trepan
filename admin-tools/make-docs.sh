#!/bin/bash

# Get location of file in a cwd-position-independent and invocation-independent way..
bs=${BASH_SOURCE[0]}
MY_DIR=$(dirname $bs)
cd $MY_DIR
MY_DIR=$(pwd)

# Set names of locations
DOCS_DIR=$MY_DIR/../docs
CONF=$DOCS_DIR/conf.py
DOCS_BUILD=$MY_DIR/build_docs

# Clean out filesystem from preview runs
rm -fr $DOCS_BUILD || /bin/true

# # Build HTML...
# mkdir -p $DOCS_BUILD/html
# cd $DOCS_BUILD/html
# sphinx-build -T -b html -C $DOCS_DIR -E -D language=en $DOCS_DIR .
# mkdir -p $DOCS_BUILD/doctrees-readthedocs

# # and JSON files
# mkdir -p $DOCS_BUILD/json
# cd $DOCS_BUILD/html
# sphinx-build -T -b json -C $DOCS_DIR -E -D language=en $DOCS_DIR .

# Build PDF via LaTeX
mkdir -p $DOCS_BUILD/latex
cd $DOCS_BUILD/latex
sphinx-build -b latex -D language=en $DOCS_DIR .
rc=$?
if (( $? != 0 )); then
    print 2>&1 "Something went wrong with sphinx-build, exit code: $?"
    exit $rc
fi
if [[ ! -r trepan.tex ]]; then
    print 2>&1 "Failed to create trepan.tex"
    exit 1
fi

pdflatex -interaction=nonstopmode ./trepan.tex
makeindex -s python.ist trepan.idx
pdflatex -interaction=nonstopmode ./trepan.tex
