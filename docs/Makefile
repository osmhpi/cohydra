# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

BUILD_TAG ?= $(shell git rev-parse --abbrev-ref HEAD)
export BUILD_TAG := ${BUILD_TAG}

.PHONY: all keep-autosummary clean clean-autosummary Makefile

all: keep-autosummary
	$(MAKE) clean-autosummary

keep-autosummary: clean
	$(MAKE) sphinx-dirhtml
	$(MAKE) sphinx-clean
	$(MAKE) sphinx-dirhtml
	$(MAKE) sphinx-dirhtml

clean: sphinx-clean clean-autosummary

clean-autosummary:
	$(RM) -r api

help: sphinx-help

sphinx-%: Makefile
	$(SPHINXBUILD) -M $(@:sphinx-%=%) "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
