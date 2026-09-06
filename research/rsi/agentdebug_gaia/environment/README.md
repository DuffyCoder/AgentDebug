# Agent image allowlist — not a build context yet

Once the proposal is approved, export only the reviewed weak starter, its
minimal dependency closure, the gold-free visible inputs, visible-only scoring
feedback, and the fixed-model client. Install dependencies at image-build time.
The model client's real credentials belong to a trusted service, not this image.

Do not include the research repository, `.git`, `output`, `artifacts`, raw label
directories, experiment reports, stronger reference methods or hidden inputs.
The method directory is the only submitted artifact. Build an explicit export
manifest and test the resulting image filesystem, not just the source directory.

No Dockerfile is supplied here because the approved runtime, data license and
actual starter entry point are not finalized. Copying this README is not a task.
