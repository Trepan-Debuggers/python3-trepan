# Compatibility for us old-timers.

# Note: This makefile include remake-style target comments. 
# These comments before the targets start with #:
# remake --tasks to shows the targets and the comments

GIT2CL ?= git2cl
PYTHON ?= python3

#EXTRA_DIST=ipython/ipy_pydbgr.py pydbgr
PHONY=check clean dist distclean test test-unit test-functional rmChangeLog

#: Default target - same as "check"
all: check

#: Same as "check" 
test: check

#: Run all tests: unit, functional and integration
check-short: test-unit-short test-functional-short test-integration-short

#: Run all tests: unit, functional and integration verbosely
check: test-unit test-functional test-integration

#: Run unit (white-box) tests
test-unit: 
	$(PYTHON) ./setup.py nosetests

#: Run unit (white-box) tests
test-unit-short: 
	$(PYTHON) ./setup.py nosetests --quiet | \
	$(PYTHON) ./make-check-filter.py

#: Run functional tests
test-functional: 
	(cd test/functional && $(PYTHON) ./setup.py nosetests)

#: Run functional tests
test-functional-short: 
	(cd test/functional && $(PYTHON) ./setup.py nosetests) | \
	$(PYTHON) ./make-check-filter.py

#: Run integration (black-box) tests
test-integration: 
	 (cd test/integration && $(PYTHON) ./setup.py nosetests)

#: Run integration (black-box) tests
test-integration-short: 
	(cd test/integration && $(PYTHON) ./setup.py nosetests) | \
	$(PYTHON) ./make-check-filter.py

#: Clean up temporary files
clean: 
	$(PYTHON) ./setup.py $@

#: Create source (tarball) and binary (egg) distribution
dist: 
	$(PYTHON) ./setup.py sdist bdist_egg

#: Create source tarball
sdist: 
	$(PYTHON) ./setup.py sdist

#: Create binary egg distribution
bdist_egg: 
	$(PYTHON) ./setup.py bdist_egg


# It is too much work to figure out how to add a new command to distutils
# to do the following. I'm sure distutils will someday get there.
DISTCLEAN_FILES = build dist *.pyc

#: Remove ALL dervied files 
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

rmChangeLog: 
	rm ChangeLog || true

#: Create a ChangeLog from git via git log and git2cl
ChangeLog: rmChangeLog
	git log --pretty --numstat --summary | $(GIT2CL) >$@

.PHONY: $(PHONY)
