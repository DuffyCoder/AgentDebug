"""Evidence-grounded agent failure diagnosis with one supported method."""

__version__ = "0.4.0"


def analyze(**kwargs):
    """Prepare or run AgentDebug on gold-free processed GAIA manifests."""
    from .method import analyze as run

    return run(**kwargs)


__all__ = ["analyze", "__version__"]
