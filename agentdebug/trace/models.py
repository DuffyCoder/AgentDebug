"""Lossless canonical data model for OpenClaw trajectories.

The classes in this module intentionally model observable events, not inferred
``memory/reflection/planning`` modules.  Every derived object points back to one
or more source lines through :class:`Provenance`, while :class:`CanonicalEvent`
keeps the complete parsed source object.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import date, datetime, time
from enum import Enum
from typing import Any, Iterable, Mapping, Optional


class StringEnum(str, Enum):
    """A JSON-friendly enum base."""


class SourceKind(StringEnum):
    SESSION_V3 = "openclaw_session_v3"
    RUNTIME_V1 = "openclaw_runtime_v1"
    CLAW_EVAL = "claw_eval_trace"
    AGENT_ERROR_BENCH = "agent_error_bench"
    MANIFEST = "manifest"
    TASK = "task"
    CANONICAL = "canonical"


class MessageRole(StringEnum):
    USER = "user"
    ASSISTANT = "assistant"
    TOOL_RESULT = "tool_result"
    SYSTEM = "system"
    DEVELOPER = "developer"
    CUSTOM = "custom"
    UNKNOWN = "unknown"


class ToolCallStatus(StringEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    ERROR = "error"
    MISSING_RESULT = "missing_result"


class ToolResultStatus(StringEnum):
    SUCCESS = "success"
    ERROR = "error"
    UNKNOWN = "unknown"


class DispatchStatus(StringEnum):
    SUCCESS = "success"
    ERROR = "error"
    UNKNOWN = "unknown"


class EvaluationStatus(StringEnum):
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    UNKNOWN = "unknown"


class IntegritySeverity(StringEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class IntegrityStatus(StringEnum):
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"


def _json_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    # PyYAML deliberately materializes ISO date/timestamp scalars.  Canonical
    # JSON must nevertheless remain serializable and deterministic.
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()
    if is_dataclass(value):
        return {key: _json_value(item) for key, item in asdict(value).items()}
    if isinstance(value, Mapping):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_value(item) for item in value]
    return value


@dataclass
class JsonModel:
    def to_dict(self) -> dict[str, Any]:
        return _json_value(self)


@dataclass
class Provenance(JsonModel):
    source_id: str
    source_kind: SourceKind
    path: str
    line_start: int
    line_end: int
    raw_sha256: str
    # Exact source text is retained so a canonical JSON file remains
    # independently auditable even after the original artifact is moved.
    raw_text: str

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Provenance":
        return cls(
            source_id=str(data["source_id"]),
            source_kind=SourceKind(data["source_kind"]),
            path=str(data["path"]),
            line_start=int(data["line_start"]),
            line_end=int(data.get("line_end", data["line_start"])),
            raw_sha256=str(data["raw_sha256"]),
            raw_text=str(data.get("raw_text", "")),
        )


@dataclass
class SourceArtifact(JsonModel):
    source_id: str
    kind: SourceKind
    path: str
    sha256: str
    line_count: int
    nonblank_line_count: int
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "SourceArtifact":
        return cls(
            source_id=str(data["source_id"]),
            kind=SourceKind(data["kind"]),
            path=str(data["path"]),
            sha256=str(data["sha256"]),
            line_count=int(data.get("line_count", 0)),
            nonblank_line_count=int(data.get("nonblank_line_count", 0)),
            metadata=dict(data.get("metadata") or {}),
        )


@dataclass
class ContentBlock(JsonModel):
    block_type: str
    text: Optional[str] = None
    # The complete block as it appeared in the source message.
    data: Any = None
    source_refs: list[Provenance] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ContentBlock":
        return cls(
            block_type=str(data.get("block_type", "unknown")),
            text=data.get("text"),
            data=data.get("data"),
            source_refs=[
                Provenance.from_dict(item) for item in data.get("source_refs", [])
            ],
        )


@dataclass
class CanonicalEvent(JsonModel):
    event_id: str
    source_id: str
    source_kind: SourceKind
    event_type: str
    timestamp: Optional[str]
    sequence: Optional[int]
    run_id: Optional[str]
    parent_id: Optional[str]
    raw: Any
    provenance: Provenance
    parse_error: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "CanonicalEvent":
        return cls(
            event_id=str(data["event_id"]),
            source_id=str(data["source_id"]),
            source_kind=SourceKind(data["source_kind"]),
            event_type=str(data.get("event_type", "unknown")),
            timestamp=data.get("timestamp"),
            sequence=data.get("sequence"),
            run_id=data.get("run_id"),
            parent_id=data.get("parent_id"),
            raw=data.get("raw"),
            provenance=Provenance.from_dict(data["provenance"]),
            parse_error=data.get("parse_error"),
        )


@dataclass
class CanonicalMessage(JsonModel):
    message_id: str
    event_id: str
    role: MessageRole
    timestamp: Optional[str]
    run_id: Optional[str]
    parent_id: Optional[str]
    content_blocks: list[ContentBlock]
    metadata: dict[str, Any] = field(default_factory=dict)
    source_refs: list[Provenance] = field(default_factory=list)

    @property
    def text(self) -> str:
        return "".join(
            block.text or ""
            for block in self.content_blocks
            if block.block_type in {"text", "thinking", "reasoning"}
        )

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "CanonicalMessage":
        return cls(
            message_id=str(data["message_id"]),
            event_id=str(data["event_id"]),
            role=MessageRole(data.get("role", MessageRole.UNKNOWN.value)),
            timestamp=data.get("timestamp"),
            run_id=data.get("run_id"),
            parent_id=data.get("parent_id"),
            content_blocks=[
                ContentBlock.from_dict(item)
                for item in data.get("content_blocks", [])
            ],
            metadata=dict(data.get("metadata") or {}),
            source_refs=[
                Provenance.from_dict(item) for item in data.get("source_refs", [])
            ],
        )


@dataclass
class AssistantTurn(JsonModel):
    """One assistant/model completion, containing zero or more tool calls."""

    turn_id: str
    message_id: str
    event_id: str
    timestamp: Optional[str]
    run_id: Optional[str]
    parent_id: Optional[str]
    content_blocks: list[ContentBlock]
    thinking_texts: list[str]
    text_outputs: list[str]
    tool_call_ids: list[str]
    tool_result_ids: list[str] = field(default_factory=list)
    stop_reason: Optional[str] = None
    error_message: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    model_api: Optional[str] = None
    response_id: Optional[str] = None
    usage: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    source_refs: list[Provenance] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "AssistantTurn":
        return cls(
            turn_id=str(data["turn_id"]),
            message_id=str(data["message_id"]),
            event_id=str(data["event_id"]),
            timestamp=data.get("timestamp"),
            run_id=data.get("run_id"),
            parent_id=data.get("parent_id"),
            content_blocks=[
                ContentBlock.from_dict(item)
                for item in data.get("content_blocks", [])
            ],
            thinking_texts=list(data.get("thinking_texts") or []),
            text_outputs=list(data.get("text_outputs") or []),
            tool_call_ids=list(data.get("tool_call_ids") or []),
            tool_result_ids=list(data.get("tool_result_ids") or []),
            stop_reason=data.get("stop_reason"),
            error_message=data.get("error_message"),
            provider=data.get("provider"),
            model=data.get("model"),
            model_api=data.get("model_api"),
            response_id=data.get("response_id"),
            usage=dict(data.get("usage") or {}),
            metadata=dict(data.get("metadata") or {}),
            source_refs=[
                Provenance.from_dict(item) for item in data.get("source_refs", [])
            ],
        )


@dataclass
class ToolCall(JsonModel):
    call_id: str
    turn_id: Optional[str]
    event_id: str
    name: str
    normalized_name: str
    arguments: Any
    partial_arguments: Any
    timestamp: Optional[str]
    run_id: Optional[str]
    result_ids: list[str] = field(default_factory=list)
    dispatch_ids: list[str] = field(default_factory=list)
    status: ToolCallStatus = ToolCallStatus.PENDING
    metadata: dict[str, Any] = field(default_factory=dict)
    source_refs: list[Provenance] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ToolCall":
        return cls(
            call_id=str(data["call_id"]),
            turn_id=data.get("turn_id"),
            event_id=str(data["event_id"]),
            name=str(data.get("name", "")),
            normalized_name=str(data.get("normalized_name", data.get("name", ""))),
            arguments=data.get("arguments"),
            partial_arguments=data.get("partial_arguments"),
            timestamp=data.get("timestamp"),
            run_id=data.get("run_id"),
            result_ids=list(data.get("result_ids") or []),
            dispatch_ids=list(data.get("dispatch_ids") or []),
            status=ToolCallStatus(data.get("status", ToolCallStatus.PENDING.value)),
            metadata=dict(data.get("metadata") or {}),
            source_refs=[
                Provenance.from_dict(item) for item in data.get("source_refs", [])
            ],
        )


@dataclass
class ToolResult(JsonModel):
    result_id: str
    call_id: Optional[str]
    event_id: str
    name: Optional[str]
    normalized_name: Optional[str]
    content_blocks: list[ContentBlock]
    is_error: Optional[bool]
    status: ToolResultStatus
    timestamp: Optional[str]
    run_id: Optional[str]
    details: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)
    source_refs: list[Provenance] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ToolResult":
        return cls(
            result_id=str(data["result_id"]),
            call_id=data.get("call_id"),
            event_id=str(data["event_id"]),
            name=data.get("name"),
            normalized_name=data.get("normalized_name"),
            content_blocks=[
                ContentBlock.from_dict(item)
                for item in data.get("content_blocks", [])
            ],
            is_error=data.get("is_error"),
            status=ToolResultStatus(
                data.get("status", ToolResultStatus.UNKNOWN.value)
            ),
            timestamp=data.get("timestamp"),
            run_id=data.get("run_id"),
            details=data.get("details"),
            metadata=dict(data.get("metadata") or {}),
            source_refs=[
                Provenance.from_dict(item) for item in data.get("source_refs", [])
            ],
        )


@dataclass
class ToolDispatch(JsonModel):
    dispatch_id: str
    call_id: Optional[str]
    event_id: str
    tool_name: str
    normalized_name: str
    request: Any
    response: Any
    response_status: Any
    status: DispatchStatus
    timestamp: Optional[str]
    started_at: Optional[str]
    latency_ms: Optional[float]
    run_id: Optional[str]
    endpoint_url: Optional[str] = None
    error: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)
    source_refs: list[Provenance] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ToolDispatch":
        return cls(
            dispatch_id=str(data["dispatch_id"]),
            call_id=data.get("call_id"),
            event_id=str(data["event_id"]),
            tool_name=str(data.get("tool_name", "")),
            normalized_name=str(
                data.get("normalized_name", data.get("tool_name", ""))
            ),
            request=data.get("request"),
            response=data.get("response"),
            response_status=data.get("response_status"),
            status=DispatchStatus(data.get("status", DispatchStatus.UNKNOWN.value)),
            timestamp=data.get("timestamp"),
            started_at=data.get("started_at"),
            latency_ms=data.get("latency_ms"),
            run_id=data.get("run_id"),
            endpoint_url=data.get("endpoint_url"),
            error=data.get("error"),
            metadata=dict(data.get("metadata") or {}),
            source_refs=[
                Provenance.from_dict(item) for item in data.get("source_refs", [])
            ],
        )


@dataclass
class CanonicalRun(JsonModel):
    run_id: str
    session_id: Optional[str]
    started_at: Optional[str]
    ended_at: Optional[str]
    status: Optional[str]
    provider: Optional[str]
    model: Optional[str]
    model_api: Optional[str]
    tool_inventory: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    source_refs: list[Provenance] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "CanonicalRun":
        return cls(
            run_id=str(data["run_id"]),
            session_id=data.get("session_id"),
            started_at=data.get("started_at"),
            ended_at=data.get("ended_at"),
            status=data.get("status"),
            provider=data.get("provider"),
            model=data.get("model"),
            model_api=data.get("model_api"),
            tool_inventory=list(data.get("tool_inventory") or []),
            metadata=dict(data.get("metadata") or {}),
            source_refs=[
                Provenance.from_dict(item) for item in data.get("source_refs", [])
            ],
        )


@dataclass
class Evaluation(JsonModel):
    evaluation_id: str
    evaluator: str
    status: EvaluationStatus
    passed: Optional[bool]
    score: Optional[float]
    failure_reason: Optional[str]
    timestamp: Optional[str]
    task_id: Optional[str]
    trace_id: Optional[str]
    details: dict[str, Any] = field(default_factory=dict)
    source_refs: list[Provenance] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Evaluation":
        return cls(
            evaluation_id=str(data["evaluation_id"]),
            evaluator=str(data.get("evaluator", "unknown")),
            status=EvaluationStatus(
                data.get("status", EvaluationStatus.UNKNOWN.value)
            ),
            passed=data.get("passed"),
            score=data.get("score"),
            failure_reason=data.get("failure_reason"),
            timestamp=data.get("timestamp"),
            task_id=data.get("task_id"),
            trace_id=data.get("trace_id"),
            details=dict(data.get("details") or {}),
            source_refs=[
                Provenance.from_dict(item) for item in data.get("source_refs", [])
            ],
        )


@dataclass
class CanonicalTask(JsonModel):
    task_id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    user_request: Optional[str] = None
    obligations: list[Any] = field(default_factory=list)
    prohibitions: list[Any] = field(default_factory=list)
    tool_inventory: list[dict[str, Any]] = field(default_factory=list)
    raw_text: Optional[str] = None
    raw: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)
    source_refs: list[Provenance] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "CanonicalTask":
        return cls(
            task_id=data.get("task_id"),
            title=data.get("title"),
            description=data.get("description"),
            user_request=data.get("user_request"),
            obligations=list(data.get("obligations") or []),
            prohibitions=list(data.get("prohibitions") or []),
            tool_inventory=list(data.get("tool_inventory") or []),
            raw_text=data.get("raw_text"),
            raw=data.get("raw"),
            metadata=dict(data.get("metadata") or {}),
            source_refs=[
                Provenance.from_dict(item) for item in data.get("source_refs", [])
            ],
        )


@dataclass
class IntegrityIssue(JsonModel):
    code: str
    severity: IntegritySeverity
    message: str
    entity_ids: list[str] = field(default_factory=list)
    source_refs: list[Provenance] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "IntegrityIssue":
        return cls(
            code=str(data["code"]),
            severity=IntegritySeverity(data["severity"]),
            message=str(data["message"]),
            entity_ids=list(data.get("entity_ids") or []),
            source_refs=[
                Provenance.from_dict(item) for item in data.get("source_refs", [])
            ],
            details=dict(data.get("details") or {}),
        )


@dataclass
class IntegrityReport(JsonModel):
    status: IntegrityStatus
    issues: list[IntegrityIssue] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.status != IntegrityStatus.FAIL

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "IntegrityReport":
        return cls(
            status=IntegrityStatus(data.get("status", IntegrityStatus.PASS.value)),
            issues=[
                IntegrityIssue.from_dict(item) for item in data.get("issues", [])
            ],
            metrics=dict(data.get("metrics") or {}),
        )


@dataclass
class TraceFragment(JsonModel):
    """Output of one source parser before cross-source reconciliation."""

    source_kind: SourceKind
    trace_id_hint: Optional[str] = None
    session_id_hint: Optional[str] = None
    task_id_hint: Optional[str] = None
    sources: list[SourceArtifact] = field(default_factory=list)
    events: list[CanonicalEvent] = field(default_factory=list)
    messages: list[CanonicalMessage] = field(default_factory=list)
    assistant_turns: list[AssistantTurn] = field(default_factory=list)
    tool_calls: list[ToolCall] = field(default_factory=list)
    tool_results: list[ToolResult] = field(default_factory=list)
    dispatches: list[ToolDispatch] = field(default_factory=list)
    runs: list[CanonicalRun] = field(default_factory=list)
    evaluations: list[Evaluation] = field(default_factory=list)
    task: Optional[CanonicalTask] = None


@dataclass
class CanonicalTrace(JsonModel):
    schema_version: int
    trace_id: str
    session_id: Optional[str]
    sources: list[SourceArtifact]
    events: list[CanonicalEvent]
    messages: list[CanonicalMessage]
    assistant_turns: list[AssistantTurn]
    tool_calls: list[ToolCall]
    tool_results: list[ToolResult]
    dispatches: list[ToolDispatch]
    runs: list[CanonicalRun]
    evaluations: list[Evaluation]
    task: Optional[CanonicalTask]
    tool_inventory: list[dict[str, Any]]
    final_turn_id: Optional[str]
    final_answer: Optional[str]
    integrity: Optional[IntegrityReport] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def turns(self) -> list[AssistantTurn]:
        """Convenience alias used by downstream diagnostics."""

        return self.assistant_turns

    def call_by_id(self, call_id: str) -> Optional[ToolCall]:
        return next((call for call in self.tool_calls if call.call_id == call_id), None)

    def result_by_id(self, result_id: str) -> Optional[ToolResult]:
        return next(
            (result for result in self.tool_results if result.result_id == result_id),
            None,
        )

    def turn_by_id(self, turn_id: str) -> Optional[AssistantTurn]:
        return next(
            (turn for turn in self.assistant_turns if turn.turn_id == turn_id), None
        )

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "CanonicalTrace":
        task_data = data.get("task")
        integrity_data = data.get("integrity")
        return cls(
            schema_version=int(data.get("schema_version", 1)),
            trace_id=str(data["trace_id"]),
            session_id=data.get("session_id"),
            sources=[
                SourceArtifact.from_dict(item) for item in data.get("sources", [])
            ],
            events=[
                CanonicalEvent.from_dict(item) for item in data.get("events", [])
            ],
            messages=[
                CanonicalMessage.from_dict(item)
                for item in data.get("messages", [])
            ],
            assistant_turns=[
                AssistantTurn.from_dict(item)
                for item in data.get("assistant_turns", [])
            ],
            tool_calls=[
                ToolCall.from_dict(item) for item in data.get("tool_calls", [])
            ],
            tool_results=[
                ToolResult.from_dict(item)
                for item in data.get("tool_results", [])
            ],
            dispatches=[
                ToolDispatch.from_dict(item)
                for item in data.get("dispatches", [])
            ],
            runs=[CanonicalRun.from_dict(item) for item in data.get("runs", [])],
            evaluations=[
                Evaluation.from_dict(item)
                for item in data.get("evaluations", [])
            ],
            task=CanonicalTask.from_dict(task_data) if task_data else None,
            tool_inventory=list(data.get("tool_inventory") or []),
            final_turn_id=data.get("final_turn_id"),
            final_answer=data.get("final_answer"),
            integrity=(
                IntegrityReport.from_dict(integrity_data) if integrity_data else None
            ),
            metadata=dict(data.get("metadata") or {}),
        )


def merge_source_refs(*groups: Iterable[Provenance]) -> list[Provenance]:
    """Return unique provenance references while preserving source order."""

    result: list[Provenance] = []
    seen: set[tuple[str, int, int, str]] = set()
    for group in groups:
        for item in group:
            key = (
                item.source_id,
                item.line_start,
                item.line_end,
                item.raw_sha256,
            )
            if key not in seen:
                seen.add(key)
                result.append(item)
    return result
