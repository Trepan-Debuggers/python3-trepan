PYTHON ?= python

PHONY=all check check-short test-functional test-functional-short

#: Same as test-functional
all, test, check:
	$(MAKE) test-functional

#: Same as test-functional-short
check-short:
	$(MAKE) test-functional-short

#: Run functional tests
test-functional:
	$(PYTHON) ./setup.py nosetests

#: Run functional tests reduced verbosity
test-functional-short:
	$(PYTHON) ./setup.py nosetests | \
	$(PYTHON) ../../make-check-filter.py

#: Remove derived files
clean:
	-rm -fr *.egg-info || true

# Whatever else it is you want to do, it should be forwarded to the
# to top-level directories
%:
	$(MAKE) -C ../.. $@
