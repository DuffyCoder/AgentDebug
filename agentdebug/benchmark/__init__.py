"""AgentErrorBench adapter and evaluation pipeline.

This package is deliberately separate from :mod:`agentdebug.diagnostics`.
Benchmark release formats are converted here; the production diagnostic API
continues to accept only :class:`agentdebug.trace.CanonicalTrace`.
"""

from .adapter import (
    AdapterError,
    adapt_trajectory,
    validate_conversion,
)
from .cohort import (
    CohortManifest,
    CohortManifestError,
    build_gaia_smoke_cohort_document,
    build_default_cohort_documents,
    load_cohort_manifest,
    write_gaia_smoke_cohort_manifest,
    write_default_cohort_manifests,
)
from .dataset import load_agent_error_bench
from .metrics import compute_metrics
from .models import (
    BenchmarkDataset,
    BenchmarkExample,
    ConversionReport,
    GoldLabel,
    StepMapping,
    TraceMapping,
)

__all__ = [
    "AdapterError",
    "BenchmarkDataset",
    "BenchmarkExample",
    "CohortManifest",
    "CohortManifestError",
    "ConversionReport",
    "GoldLabel",
    "StepMapping",
    "TraceMapping",
    "adapt_trajectory",
    "build_default_cohort_documents",
    "build_gaia_smoke_cohort_document",
    "compute_metrics",
    "load_agent_error_bench",
    "load_cohort_manifest",
    "validate_conversion",
    "write_default_cohort_manifests",
    "write_gaia_smoke_cohort_manifest",
]
