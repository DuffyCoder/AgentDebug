"""Compare real builders and validators against a restored original package."""
import json
import os
import subprocess
import sys

from agentdebug import method
from scripts.maintenance.archive import ROOT, extract
from research.tools.extract_protocol import relocate
from test_supported_method import complete_stage, inputs  # noqa: F401; shared synthetic fixture


def test_all_stage_prompts_and_validation_match_original_after_declared_relocation(inputs, tmp_path):
    requests = []

    def execute(request):
        requests.append(request)
        complete_stage(request)

    method.analyze(**inputs, execute=True, executor=execute)
    manifest = next((inputs["output_dir"] / "inputs").glob("*/prediction-manifest.json"))
    cohort = manifest.parent / "cohort.json"
    arguments = []
    for request in requests:
        paths = [str(manifest), str(cohort)]
        if request.stage != "anchor":
            paths += [str(request.work_dir / name) for name in
                      ("anchor-predictions.json", "step-candidates.json", "step-freeze.json")]
        if request.stage == "arbiter":
            paths.append(str(request.work_dir / "challenger.json"))
        paths.append(str(request.artifact_path))
        arguments.append(paths)
    old_root = tmp_path / "original"
    extract(old_root)
    script = '''
import json, sys
from agentdebug.diagnostics import agent_judge_gaia_v3_83_clean_v3p20_model_only_gpt55_medium as protocol
arguments = json.loads(sys.argv[1])
output = []
for stage, paths in zip(("anchor", "challenger", "arbiter"), arguments):
    validator = "validate_anchor_predictions" if stage == "anchor" else "validate_" + stage
    output.append({"prompt": getattr(protocol, "build_" + stage + "_task")(*paths),
                   "audit": getattr(protocol, validator)(*paths)})
print(json.dumps(output))
'''
    completed = subprocess.run([sys.executable, "-c", script, json.dumps(arguments)],
        cwd=old_root, env={**os.environ, "PYTHONPATH": str(old_root), "PYTHONDONTWRITEBYTECODE": "1"},
        capture_output=True, text=True, check=True, timeout=30)
    originals = json.loads(completed.stdout)
    for request, paths, original in zip(requests, arguments, originals):
        # Only the declared module identifiers and installation root may change.
        assert request.task == relocate(original["prompt"]).replace(str(old_root), str(ROOT))
        validator = "validate_anchor_predictions" if request.stage == "anchor" else "validate_" + request.stage
        assert getattr(method._protocol, validator)(*paths) == original["audit"]
