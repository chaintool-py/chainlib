PACKAGE=chainlib
PREFIX ?= /usr/local
BUILD_DIR = man/build/

build:
	python setup.py bdist_wheel

.PHONY clean:
	rm -rf build
	rm -rf dist
	rm -rf $(PACKAGE).egg-info

.PHONY dist: man clean build

.PHONY: man

man:
	mkdir -vp $(BUILD_DIR)
	#./scripts/chainlib-man.py -v -n chainlib-gen -d $(BUILD_DIR)/ man
	cp -v man/chainlib-gen.groff man/build/chainlib-gen.1

