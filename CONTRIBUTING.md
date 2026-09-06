# Contributing

Contributions to trace adapters, diagnosis contracts, benchmark tooling, tests,
and documentation are welcome. For large API changes, open an issue describing
the use case and compatibility impact before starting implementation.

## Development setup

Use Python 3.11 and the committed dependency lock:

```bash
uv sync --frozen --extra dev
make check
```

See [the development guide](docs/development.md) for individual test targets.
The default checks do not require private data or model credentials.

## Make a focused change

- Keep trace parsing, model judgment, and score computation separate.
- Preserve evidence references and fail clearly on invalid input.
- Add synthetic fixtures and stub model responses; tests must not make paid calls.
- Document public API or CLI changes and update [the changelog](CHANGELOG.md).
- Keep frozen protocol files and result artifacts unchanged. Use a new version
  for a method change rather than changing the meaning of an existing result.
- Avoid unrelated dependency updates or reformatting.

## Before opening a pull request

```bash
make check
git diff --check
```

Optional local commit hooks run only validation; they never reformat frozen
source or result files:

```bash
uv run pre-commit validate-config
uv run pre-commit install
```

Hook installation is opt-in. For a hashed file inventory and commit-message
draft without changing the index, use `make prepare-commit`; see
[the publication guide](PUBLISHING.md).

Explain the problem, implementation, and tests performed. Include a minimal
synthetic reproduction for bugs. If a check fails or requires unavailable data,
report it explicitly rather than claiming all tests passed.

Keep credentials, private traces, model transcripts, and generated datasets out
of issues, commits, and attachments. A sanitized filename does not make the
contents safe to share. Follow [SECURITY.md](SECURITY.md) and the
[data policy](docs/data-provenance.md).

Research-specific recording and verification procedures are collected in the
[research archive](research/README.md). They are not prerequisites for ordinary
framework contributions.
