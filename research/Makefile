# Optional research commands; run from the repository root.
UV ?= uv
PYTHON ?= $(UV) run python
.DEFAULT_GOAL := check

.PHONY: check test archive-test test-all snapshot-verify results-verify protocol-check rsi-check rsi-ready proposal-build proposal-check

check: snapshot-verify protocol-check results-verify rsi-check proposal-check test archive-test

test:
	$(PYTHON) -m pytest -q research/tests

archive-test:
	$(PYTHON) -m research.tools.archive_runner test

test-all:
	$(PYTHON) -m research.tools.archive_runner test-all --workspace "$(ARCHIVE_WORKSPACE)"

snapshot-verify:
	$(PYTHON) -m scripts.maintenance.archive verify

protocol-check:
	$(PYTHON) -m research.tools.extract_protocol

results-verify:
	$(PYTHON) -m research.tools.research_release verify

proposal-build:
	$(PYTHON) -m research.tools.rsi.build_proposal_bundle build --no-plots

proposal-check:
	$(PYTHON) -m research.tools.rsi.build_proposal_bundle check

rsi-check:
	$(PYTHON) -m research.tools.rsi.check_readiness

rsi-ready:
	$(PYTHON) -m research.tools.rsi.check_readiness --require-ready
