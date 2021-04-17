PACKAGE=chainlib

build:
	python setup.py bdist_wheel

.PHONY clean:
	rm -rf build
	rm -rf dist
	rm -rf $(PACKAGE).egg-info

.PHONY dist: clean build
