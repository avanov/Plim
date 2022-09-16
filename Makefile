# https://www.gnu.org/software/make/manual/html_node/Special-Variables.html
# https://ftp.gnu.org/old-gnu/Manuals/make-3.80/html_node/make_17.html
PROJECT_MKFILE_PATH       := $(word $(words $(MAKEFILE_LIST)),$(MAKEFILE_LIST))
PROJECT_MKFILE_DIR        := $(shell cd $(shell dirname $(PROJECT_MKFILE_PATH)); pwd)

PROJECT_NAME              := plim
PROJECT_ROOT              := $(PROJECT_MKFILE_DIR)

BUILD_DIR                 := $(PROJECT_ROOT)/build
DIST_DIR                  := $(PROJECT_ROOT)/dist

PROJECT=plim

.PHONY: test
test:
	pytest -s  --cov=plim --cov-report xml $(PROJECT_ROOT)/tests

.PHONY: typecheck
typecheck:
	mypy --config-file setup.cfg --strict --package $(PROJECT_NAME)

.PHONY: prepare-dist
prepare-dist:
	rm -rf $(BUILD_DIR) $(DIST_DIR)
	python $(PROJECT_ROOT)/setup.py sdist bdist_wheel

.PHONY: publish
publish: | test publish
	twine upload $(DIST_DIR)/*

.PHONY: shell
shell:
	nix-shell $(PROJECT_ROOT)/shell.nix
