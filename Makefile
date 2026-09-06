UV ?= uv
PYTHON := $(UV) run python
.DEFAULT_GOAL := help

.PHONY: help check verify docs-check layout-check hygiene release-verify test test-public research-check test-research test-all prepare-commit

help:
	@echo "make check          Public tests, documentation, hygiene, and artifact checks"
	@echo "make test           Synthetic/public tests only; no model calls"
	@echo "make verify         Documentation, hygiene, and saved release integrity"
	@echo "make prepare-commit Validate and generate a review-only commit inventory"
	@echo "make research-check Optional archive and authoring-contract checks"
	@echo "make test-all       Historical tests in an explicit restored ARCHIVE_WORKSPACE"

check: test-public verify

verify: docs-check layout-check release-verify hygiene

release-verify:
	$(PYTHON) -m scripts.reproduction.release verify

docs-check:
	$(PYTHON) -m scripts.maintenance.check_public_docs

layout-check:
	$(PYTHON) -m scripts.maintenance.check_layout

hygiene:
	$(PYTHON) -m scripts.maintenance.check_repository_hygiene

test: test-public

test-public:
	$(PYTHON) -m pytest -q tests

prepare-commit: check
	$(PYTHON) -m scripts.maintenance.prepare_commit --scan-history

research-check:
	$(MAKE) -f research/Makefile check PYTHON="$(PYTHON)"

test-research:
	$(MAKE) -f research/Makefile test PYTHON="$(PYTHON)"

test-all:
	$(MAKE) -f research/Makefile test-all PYTHON="$(PYTHON)" ARCHIVE_WORKSPACE="$(ARCHIVE_WORKSPACE)"
