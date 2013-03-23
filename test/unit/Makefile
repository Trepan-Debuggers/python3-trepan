PYTHON ?= python3

PHONY=all check check-short test-unit test-unit-short

#: Run unit tests reduced verbosity
test-unit-short: 
	$(MAKE) -C ../.. $@

#: Remove derived files
clean: 
	-rm -fr *.egg-info || true

# Whatever else it is you want to do, it should be forwarded to the 
# to top-level directories
%: 
	$(MAKE) -C ../.. $@
