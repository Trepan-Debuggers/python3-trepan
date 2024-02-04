PYTHON ?= python

PHONY=all check check-short test-functional test-functional-short

#: Same as test-functional
all, test, check:
	$(PYTHON) -m pytest .

#: Same as test-functional-short
check-short:
	$(MAKE) test-functional-short

# Whatever else it is you want to do, it should be forwarded to the
# to top-level directories
%:
	$(MAKE) -C ../.. $@
