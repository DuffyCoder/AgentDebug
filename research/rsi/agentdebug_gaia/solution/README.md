# Reference candidate — author only

The best accepted historical candidate in the Codex SDK method family is v3.83:
26/50 Step Exact, executed through host-orchestrated Codex agents. Its semantics
are a candidate reference for the final task, not an already validated app-server port.

Use the frozen semantics of SDK v3.107 as the already executed app-server
stronger-method candidate. Its
historical GPT-5.5/medium GAIA-50 result is 23/50 Step Exact, 18/50 Step+Module,
13/50 All Correct. Official SDK v3 is 19/50, 9/50, 6/50. The stronger run happened
first, so this is a cross-sectional comparison, not a chronological improvement.

See `configs/reproduction/research-profiles.json` from the repository root and
the SDK family reproduction guide. All three belong to the same reporting
family; their actual execution backend, output contract and budgets stay explicit.

Do not copy this reference into the agent image. Port both candidates to the
same trusted output/model contract and measure them on the final sealed split
before setting anchors. No reference code is duplicated here yet: the official
task API and fixed-model service require approval first.
