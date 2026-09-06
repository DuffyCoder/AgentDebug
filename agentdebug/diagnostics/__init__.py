"""Evidence projection and the single supported AgentDebug diagnosis API.

Private protocol components are implementation details, not selectable methods.
Historical analyzers and provider-specific experiment APIs live in the source
snapshot and are no longer loaded by the installed framework.
"""
from agentdebug import analyze
from .judge_view import JUDGE_VIEW_VERSION, JudgeView, build_judge_view
from .taxonomy import AgentModule, ErrorType, is_valid_classification

__all__ = ["analyze", "JUDGE_VIEW_VERSION", "JudgeView", "build_judge_view",
           "AgentModule", "ErrorType", "is_valid_classification"]
