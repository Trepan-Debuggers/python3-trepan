PYTHON ?= python

PHONY=all check check-short clean test-integration test-integration-short

#: Same as test-integration
all, check, test:
	$(MAKE) test-integration

#: Run integration tests
test-integration:
	$(PYTHON) ./setup.py nosetests

#: Run integration tests reduced verbosity
check-short, test-integration-short:
	$(PYTHON) ./setup.py nosetests | \
	$(PYTHON) ../../make-check-filter.py

#: Remove derived files
clean:
	-rm -fr *.egg-info || true

# Whatever else it is you want to do, it should be forwarded to the
# to top-level directories
%:
	$(MAKE) -C ../.. $@
