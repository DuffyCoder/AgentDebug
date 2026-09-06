# Tests

`make test` runs every test in this directory. Tests cover the current method,
trace tools, explicit scoring/release commands, archive restoration, protocol
relocation, package boundaries and publication safeguards.

Inputs are synthetic or repository-contained artifacts; model execution is
stubbed. No private corpus or model credentials are required. See the
[root Makefile](../Makefile) and [testing guide](../docs/development.md).

Historical tests are stored with their original source, not mixed into this
directory. `make research-check` checks maintained research tools and runs the
frozen research suite in a temporary restored tree. `make test-all
ARCHIVE_WORKSPACE=/path/to/restored-source` runs all original test files in
separate processes; some require separately obtained local data and outputs.
Restoration instructions and unresolved historical failures are recorded in the
[research archive](../research/README.md).

Add focused regression tests with temporary inputs. Never make tests depend on
a contributor's account, machine-specific directory, or paid service. A current
suite pass does not mean every historical test passes.
