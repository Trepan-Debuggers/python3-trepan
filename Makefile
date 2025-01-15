# Compatibility for us old-timers.

# Note: This makefile include remake-style target comments.
# These comments before the targets start with #:
# remake --tasks to shows the targets and the comments

GIT2CL ?= git2cl
PYTHON ?= $(shell command -v python)
RM      ?= rm
LINT    =o flake8

PHONY=check clean dist distclean test test-unit test-functional rmChangeLog nosetests flake8

#: Default target - same as "check"
all: check

#: Same as "check"
test: check

# Check StructuredText long description formatting
check-rst:
	$(PYTHON) setup.py --long-description | ./rst2html.py > python3-trepan.html

#: Lint program
flake8:
	flake8 trepan

#: Run all tests: unit, functional and integration verbosely
check: test-unit test-functional test-integration

#: Run unit (transparent-box) tests
test-unit:
	$(PYTHON) -m pytest test/unit

#: Run functional tests
check-functional test-functional:
	(cd test/functional && $(PYTHON) -m pytest .)

#: Run integration (black-box) tests
test-integration:
	 (cd test/integration && $(PYTHON) -m pytest .)

#: Clean up temporary files
clean:
	find . | grep -E '\.pyc' | xargs rm -rvf;
	find . | grep -E '\.pyo' | xargs rm -rvf;
	$(PYTHON) ./setup.py $@

#: Create source (tarball) and binary (egg) distribution
dist: check-rst
	bash ./admin-tools/make-dist-newer.sh

#: HTML document via Sphinx
doc html htmldoc:
	$(MAKE) -C docs html

#: Create source tarball
sdist: check-rst
	$(PYTHON) ./setup.py sdist

#: Style check. Set env var LINT to pyflakes, flake, or flake8
lint:
	$(LINT) trepan

#: Create binary egg distribution
bdist_egg:
	$(PYTHON) ./setup.py bdist_egg


# It is too much work to figure out how to add a new command to distutils
# to do the following. I'm sure distutils will someday get there.
DISTCLEAN_FILES = build dist

#: Remove ALL derived files
distclean: clean
	-rm -fr $(DISTCLEAN_FILES) || true
	-find . -name \*.pyc -exec rm -v {} \;
	-find . -name __pycache__ -exec rm -vr {} \;
	-find . -name \*.egg-info -exec rm -vr {} \;

#: Install package locally
verbose-install:
	$(PYTHON) ./setup.py install

#: Install package locally without the verbiage
install:
	$(PYTHON) ./setup.py install >/dev/null

#: Install setup.py requirements
install-requirements:
	pip install -e .

rmChangeLog:
	rm ChangeLog || true

#: Create a ChangeLog from git via git log and git2cl
ChangeLog: rmChangeLog
	git log --pretty --numstat --summary | $(GIT2CL) >$@
	patch -p0 < ChangeLog-spell-corrected.diff

.PHONY: $(PHONY)
