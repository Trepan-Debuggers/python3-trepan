PYTHON ?= python

PHONY=all check check-short test-unit test-unit-short

#: Run unit tests
all, check, test-unit: 
	$(PYTHON) ./setup.py nosetests

#: Run unit tests reduced verbosity
check-short, test-unit-short: 
	$(PYTHON) ./setup.py nosetests) | \
	$(PYTHON) ../../make-check-filter.py

#: Remove derived files
clean: 
	-rm -fr *.egg-info || true

# Whatever else it is you want to do, it should be forwarded to the 
# to top-level directories
%: 
	$(MAKE) -C ../.. $@
