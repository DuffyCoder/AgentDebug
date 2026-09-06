"""The original AgentErrorTaxonomy used by both LLM judge phases.

There are five modules and seventeen unique error type names.  ``hallucination``
is intentionally valid in both memory and reflection, so the number of valid
module/type pairs is eighteen.
"""

from __future__ import annotations

from enum import Enum
from typing import Final


class StringEnum(str, Enum):
    """A JSON-friendly enum base."""


class AgentModule(StringEnum):
    MEMORY = "memory"
    REFLECTION = "reflection"
    PLANNING = "planning"
    ACTION = "action"
    SYSTEM = "system"


class ErrorType(StringEnum):
    OVER_SIMPLIFICATION = "over_simplification"
    MEMORY_RETRIEVAL_FAILURE = "memory_retrieval_failure"
    HALLUCINATION = "hallucination"
    PROGRESS_MISJUDGE = "progress_misjudge"
    OUTCOME_MISINTERPRETATION = "outcome_misinterpretation"
    CAUSAL_MISATTRIBUTION = "causal_misattribution"
    CONSTRAINT_IGNORANCE = "constraint_ignorance"
    IMPOSSIBLE_ACTION = "impossible_action"
    INEFFICIENT_PLAN = "inefficient_plan"
    MISALIGNMENT = "misalignment"
    INVALID_ACTION = "invalid_action"
    FORMAT_ERROR = "format_error"
    PARAMETER_ERROR = "parameter_error"
    STEP_LIMIT = "step_limit"
    TOOL_EXECUTION_ERROR = "tool_execution_error"
    LLM_LIMIT = "llm_limit"
    ENVIRONMENT_ERROR = "environment_error"


TAXONOMY: Final[dict[AgentModule, dict[ErrorType, str]]] = {
    AgentModule.MEMORY: {
        ErrorType.OVER_SIMPLIFICATION: (
            "Definition: the agent oversimplifies complex information from "
            "earlier steps, dropping details or key factors and then making a "
            "decision from the partial summary. Example: it reduces several "
            "product requirements to 'item found' while forgetting price, "
            "features, or inventory constraints."
        ),
        ErrorType.MEMORY_RETRIEVAL_FAILURE: (
            "Definition: relevant information is present in the observable "
            "history but the agent fails to retrieve it when needed. Example: "
            "after observing a knife on a kitchen counter, it later searches "
            "unrelated rooms because it does not recall the knife location."
        ),
        ErrorType.HALLUCINATION: (
            "Definition: the agent recalls events, observations, object states, "
            "or actions that never occurred and uses the invented memory for "
            "reasoning. Example: it claims a knife was seen in a drawer that "
            "was never opened successfully."
        ),
    },
    AgentModule.REFLECTION: {
        ErrorType.PROGRESS_MISJUDGE: (
            "Definition: the agent incorrectly evaluates progress toward the "
            "overall task goal, either optimistically or pessimistically. "
            "Example: after merely entering the kitchen it says a find-and-fill "
            "task is almost complete, or abandons a task whose main work is done."
        ),
        ErrorType.OUTCOME_MISINTERPRETATION: (
            "Definition: the action was issued, but the agent incorrectly "
            "interprets its direct result or environment feedback. Example: "
            "after a Put action returns 'Nothing happens', it claims the object "
            "was placed successfully."
        ),
        ErrorType.CAUSAL_MISATTRIBUTION: (
            "Definition: the agent recognizes a failure phenomenon but assigns "
            "the wrong cause. Example: it blames a mechanical arm when pickup "
            "actually failed because the target remained inside a locked safe."
        ),
        ErrorType.HALLUCINATION: (
            "Definition: the agent treats a planned, imagined, or unexecuted "
            "operation as one it actually completed. Example: a later reflection "
            "describes operations from an earlier plan as finished despite no "
            "corresponding actions."
        ),
    },
    AgentModule.PLANNING: {
        ErrorType.CONSTRAINT_IGNORANCE: (
            "Definition: the plan ignores an explicit task constraint, coverage "
            "requirement, resource limit, prerequisite, or prohibition. "
            "Example: it selects a $55 product for a $40 budget or disregards "
            "the interaction limit."
        ),
        ErrorType.IMPOSSIBLE_ACTION: (
            "Definition: the plan proposes an action or subtask that is "
            "fundamentally impossible under current physical, logical, or "
            "prerequisite conditions. Example: it plans to put a mug into a "
            "sink while holding no mug."
        ),
        ErrorType.INEFFICIENT_PLAN: (
            "Definition: the plan could theoretically complete the task but is "
            "unnecessarily long, wasteful, repetitive, or illogical. Example: "
            "instead of carrying an apple directly from the living room to the "
            "kitchen, it detours through unrelated rooms."
        ),
    },
    AgentModule.ACTION: {
        ErrorType.MISALIGNMENT: (
            "Definition: the concrete action contradicts the intention stated "
            "in the current plan. Example: after planning to slice an apple with "
            "a located knife, it instead moves to an unrelated bedroom."
        ),
        ErrorType.INVALID_ACTION: (
            "Definition: the agent invokes an action or tool that does not exist "
            "in the available action space. Example: it calls a tool absent from "
            "the supplied inventory."
        ),
        ErrorType.FORMAT_ERROR: (
            "Definition: the selected action is expressed in invalid syntax and "
            "cannot be parsed. Example: it emits click\"product\" when the "
            "required syntax is click[\"product\"]."
        ),
        ErrorType.PARAMETER_ERROR: (
            "Definition: an available action is selected but its parameters are "
            "missing, malformed, unreasonable, or incorrect. Example: it sends "
            "an unsuitable target identifier or repeats a search query an "
            "unreasonable number of times."
        ),
    },
    AgentModule.SYSTEM: {
        ErrorType.STEP_LIMIT: (
            "Definition: the agent is acting reasonably but task completion is "
            "prevented by the system's maximum step limit. Example: it completes "
            "the first half of a two-object task and hits the limit while "
            "correctly searching for the second object."
        ),
        ErrorType.TOOL_EXECUTION_ERROR: (
            "Definition: an external tool or API fails or behaves unpredictably "
            "despite a valid call. Example: an object-recognition tool "
            "misidentifies an apple as a tomato and causes later failures."
        ),
        ErrorType.LLM_LIMIT: (
            "Definition: a model-side limitation such as a timeout, token limit, "
            "refusal, or truncated response causes the task failure."
        ),
        ErrorType.ENVIRONMENT_ERROR: (
            "Definition: the surrounding runtime, simulator, or network violates "
            "expected behavior and causes failure. Example: a valid drawer-open "
            "action crashes the simulator or makes the object disappear."
        ),
    },
}


def is_valid_classification(module: AgentModule, error_type: ErrorType) -> bool:
    """Return whether an error type belongs to the selected module."""

    return error_type in TAXONOMY[module]


def taxonomy_prompt() -> str:
    """Render the complete taxonomy for an LLM prompt."""

    sections: list[str] = []
    for module, definitions in TAXONOMY.items():
        lines = [f"{module.value}:"]
        for error_type, definition in definitions.items():
            lines.append(f"- {error_type.value}: {definition}")
        sections.append("\n".join(lines))
    return "\n\n".join(sections)


UNIQUE_ERROR_TYPE_COUNT: Final[int] = len(ErrorType)
