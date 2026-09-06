# Security and sensitive data

## Report a vulnerability privately

Do not put exploitable details, credentials, private traces, or user data in a
public issue. Use GitHub's private vulnerability reporting for this repository
if the maintainers have enabled it. Otherwise, request a private reporting
channel without including sensitive details. This repository does not promise
a response-time SLA or a bug bounty.

Include the affected commit/version, impact, and a minimal synthetic
reproduction. Do not send real credentials to demonstrate an issue.

## Trace handling

Canonical traces retain source contents and may include personal information,
secrets, or untrusted tool output. Diagnosis sends a derived JudgeView to the
configured provider. Review authorization, privacy, and provider retention
before running it.

The supported diagnosis adapter uses tool-capable Codex sessions. Its
workspace-write sandbox restricts writes, not all reads. Gold-free manifests,
disabled web search and prompt allowlists do not seal hidden data away from
the process. Use a separate container/account with only permitted inputs;
do not run beside sensitive files or hidden labels and assume they are isolated.

Report redaction recognizes common credential patterns; it is not comprehensive
anonymization. Raw model responses, trace inputs, and intermediate files may
still be sensitive. Keep them outside Git and package distributions.

## Runtime boundary

Treat trace text and model output as untrusted data. Evidence validation checks
format and reference consistency; it is not a sandbox or a guarantee of semantic
correctness. Run tool-capable reproduction workflows in a least-privilege,
isolated environment. Do not grant access to unrelated files or credentials.

If a secret has been committed or uploaded, revoke or rotate it first. Removing
the current file is not enough: prior commits, forks, caches, and artifacts may
retain it. Coordinate repository-history cleanup with the owner.

See [the publication checklist](PUBLISHING.md) before distributing a checkout
or evidence bundle.
