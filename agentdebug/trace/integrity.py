"""Integrity gate for canonical trajectories."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from typing import Iterable

from ._common import sha256_text, stable_json
from .models import (
    CanonicalTrace,
    IntegrityIssue,
    IntegrityReport,
    IntegritySeverity,
    IntegrityStatus,
    SourceKind,
    ToolCallStatus,
)


class IntegrityError(ValueError):
    """Raised when a trace fails the integrity gate in strict mode."""

    def __init__(self, report: IntegrityReport):
        self.report = report
        codes = ", ".join(
            issue.code
            for issue in report.issues
            if issue.severity
            in {IntegritySeverity.ERROR, IntegritySeverity.CRITICAL}
        )
        super().__init__(f"canonical trace failed integrity validation: {codes}")


def _duplicates(values: Iterable[str]) -> list[str]:
    counts = Counter(values)
    return [value for value, count in counts.items() if count > 1]


def validate_trace(
    trace: CanonicalTrace, *, strict: bool = False
) -> IntegrityReport:
    """Validate source preservation and cross-entity referential integrity."""

    issues: list[IntegrityIssue] = []

    def add(
        code: str,
        severity: IntegritySeverity,
        message: str,
        *,
        entities: list[str] | None = None,
        refs: list | None = None,
        details: dict | None = None,
    ) -> None:
        issues.append(
            IntegrityIssue(
                code=code,
                severity=severity,
                message=message,
                entity_ids=entities or [],
                source_refs=refs or [],
                details=details or {},
            )
        )

    if not trace.sources:
        add(
            "no_sources",
            IntegritySeverity.CRITICAL,
            "The canonical trace has no source artifacts.",
        )
    if not trace.events:
        add(
            "no_events",
            IntegritySeverity.CRITICAL,
            "The canonical trace has no source events.",
        )
    if trace.schema_version != 1:
        add(
            "unsupported_canonical_schema",
            IntegritySeverity.CRITICAL,
            "Canonical trace schema_version must be 1.",
            details={"schema_version": trace.schema_version},
        )

    duplicate_sources = _duplicates(source.source_id for source in trace.sources)
    if duplicate_sources:
        add(
            "duplicate_source_id",
            IntegritySeverity.ERROR,
            "Source identifiers are not unique.",
            entities=duplicate_sources,
        )
    duplicate_events = _duplicates(event.event_id for event in trace.events)
    if duplicate_events:
        add(
            "duplicate_event_id",
            IntegritySeverity.ERROR,
            "Canonical event identifiers are not unique.",
            entities=duplicate_events,
        )

    parse_errors = [event for event in trace.events if event.parse_error]
    for event in parse_errors:
        add(
            "source_parse_error",
            IntegritySeverity.CRITICAL,
            f"Source line could not be parsed: {event.parse_error}",
            entities=[event.event_id],
            refs=[event.provenance],
        )

    bad_raw_hashes = [
        event
        for event in trace.events
        if sha256_text(event.provenance.raw_text)
        != event.provenance.raw_sha256
    ]
    for event in bad_raw_hashes:
        add(
            "raw_line_hash_mismatch",
            IntegritySeverity.CRITICAL,
            "Stored raw source text does not match its provenance hash.",
            entities=[event.event_id],
            refs=[event.provenance],
        )

    json_line_kinds = {
        SourceKind.SESSION_V3,
        SourceKind.RUNTIME_V1,
        SourceKind.CLAW_EVAL,
        SourceKind.AGENT_ERROR_BENCH,
        SourceKind.MANIFEST,
    }
    raw_content_mismatches = []
    for event in trace.events:
        if event.source_kind not in json_line_kinds or event.parse_error:
            continue
        try:
            parsed_raw = json.loads(event.provenance.raw_text)
        except (json.JSONDecodeError, UnicodeError):
            parsed_raw = {"__agentdebug_unparseable_source_line__": True}
        if stable_json(parsed_raw) != stable_json(event.raw):
            raw_content_mismatches.append(event)
    for event in raw_content_mismatches:
        add(
            "raw_event_content_mismatch",
            IntegritySeverity.CRITICAL,
            "Canonical event.raw does not match its preserved JSON source line.",
            entities=[event.event_id],
            refs=[event.provenance],
        )

    events_by_source = defaultdict(list)
    for event in trace.events:
        events_by_source[event.source_id].append(event)
    source_coverage: dict[str, dict[str, int | float]] = {}
    for source in trace.sources:
        source_events = events_by_source.get(source.source_id, [])
        if source.kind == SourceKind.TASK:
            expected = 1
        elif source.kind == SourceKind.AGENT_ERROR_BENCH:
            # AgentErrorBench stores one JSON document containing message
            # records and metadata, rather than one JSON object per physical
            # line.  Its adapter records the exact logical-record count.
            expected = int(source.metadata.get("record_count", 0))
        else:
            expected = source.nonblank_line_count
        actual = len(source_events)
        ratio = 1.0 if expected == 0 else min(actual / expected, 1.0)
        source_coverage[source.source_id] = {
            "expected_records": expected,
            "canonical_events": actual,
            "ratio": ratio,
        }
        if actual != expected:
            add(
                "source_event_coverage_mismatch",
                IntegritySeverity.CRITICAL,
                "Not every source record has exactly one canonical event.",
                entities=[source.source_id],
                details={"expected": expected, "actual": actual},
            )

        structured_events = [
            event
            for event in source_events
            if not event.parse_error and isinstance(event.raw, dict)
        ]
        if source.kind == SourceKind.SESSION_V3:
            headers = [
                event
                for event in structured_events
                if event.raw.get("type") == "session"
            ]
            if len(headers) != 1:
                add(
                    "session_declaration_count",
                    IntegritySeverity.ERROR,
                    "Session v3 source must contain exactly one session declaration.",
                    entities=[source.source_id],
                    details={"count": len(headers)},
                )
            elif headers[0].raw.get("version") != 3:
                add(
                    "unsupported_session_version",
                    IntegritySeverity.CRITICAL,
                    "Session source does not declare schema version 3.",
                    entities=[headers[0].event_id],
                    refs=[headers[0].provenance],
                    details={"declared_version": headers[0].raw.get("version")},
                )
            if headers and not headers[0].raw.get("id"):
                add(
                    "missing_session_trace_id",
                    IntegritySeverity.ERROR,
                    "Session declaration has no trace/session identifier.",
                    entities=[headers[0].event_id],
                    refs=[headers[0].provenance],
                )

        elif source.kind == SourceKind.RUNTIME_V1:
            invalid_schema = [
                event
                for event in structured_events
                if event.raw.get("traceSchema") != "openclaw-trajectory"
                or event.raw.get("schemaVersion") != 1
            ]
            if invalid_schema:
                add(
                    "unsupported_runtime_schema",
                    IntegritySeverity.CRITICAL,
                    "Runtime records must declare openclaw-trajectory schema version 1.",
                    entities=[event.event_id for event in invalid_schema],
                    refs=[event.provenance for event in invalid_schema],
                )
            runtime_trace_ids = {
                str(event.raw.get("traceId"))
                for event in structured_events
                if event.raw.get("traceId") is not None
            }
            missing_runtime_ids = [
                event
                for event in structured_events
                if event.raw.get("traceId") is None
            ]
            if len(runtime_trace_ids) != 1 or missing_runtime_ids:
                add(
                    "runtime_trace_declaration_mismatch",
                    IntegritySeverity.ERROR,
                    "Runtime source must consistently declare exactly one traceId.",
                    entities=[
                        source.source_id,
                        *[event.event_id for event in missing_runtime_ids],
                    ],
                    details={"trace_ids": sorted(runtime_trace_ids)},
                )

        elif source.kind == SourceKind.CLAW_EVAL:
            starts = [
                event
                for event in structured_events
                if event.raw.get("type") == "trace_start"
            ]
            eval_trace_ids = {
                str(event.raw.get("trace_id") or event.raw.get("traceId"))
                for event in structured_events
                if event.raw.get("trace_id") is not None
                or event.raw.get("traceId") is not None
            }
            missing_eval_ids = [
                event
                for event in structured_events
                if event.raw.get("trace_id") is None
                and event.raw.get("traceId") is None
            ]
            if len(starts) != 1:
                add(
                    "claw_eval_declaration_count",
                    IntegritySeverity.ERROR,
                    "Claw-Eval source must contain exactly one trace_start record.",
                    entities=[source.source_id],
                    details={"count": len(starts)},
                )
            if len(eval_trace_ids) != 1 or missing_eval_ids:
                add(
                    "claw_eval_trace_declaration_mismatch",
                    IntegritySeverity.ERROR,
                    "Claw-Eval records must consistently declare exactly one trace ID.",
                    entities=[
                        source.source_id,
                        *[event.event_id for event in missing_eval_ids],
                    ],
                    details={"trace_ids": sorted(eval_trace_ids)},
                )

        if (
            source.kind == SourceKind.MANIFEST
            and source.metadata.get("selection_scoped") is False
        ):
            add(
                "manifest_selection_unscoped",
                IntegritySeverity.ERROR,
                "Manifest rows could not be associated without a session or task identity.",
                entities=[source.source_id],
            )

    branch_selection = trace.metadata.get("branch_selection")
    if isinstance(branch_selection, dict):
        branch_status = branch_selection.get("status")
        if branch_status == "ambiguous":
            add(
                "ambiguous_session_branch",
                IntegritySeverity.ERROR,
                "The active session branch cannot be selected unambiguously.",
                entities=list(branch_selection.get("candidate_leaf_ids") or []),
                details=dict(branch_selection),
            )
        elif branch_status == "missing_anchor":
            add(
                "missing_transcript_leaf",
                IntegritySeverity.ERROR,
                "Runtime transcriptLeafId does not resolve in the session graph.",
                entities=[
                    str(branch_selection.get("selected_anchor_id") or "")
                ],
                details=dict(branch_selection),
            )

    duplicate_messages = _duplicates(message.message_id for message in trace.messages)
    if duplicate_messages:
        add(
            "duplicate_message_id",
            IntegritySeverity.ERROR,
            "Message identifiers are not unique after reconciliation.",
            entities=duplicate_messages,
        )
    duplicate_turns = _duplicates(turn.turn_id for turn in trace.assistant_turns)
    if duplicate_turns:
        add(
            "duplicate_turn_id",
            IntegritySeverity.ERROR,
            "Assistant turn identifiers are not unique.",
            entities=duplicate_turns,
        )
    duplicate_calls = _duplicates(call.call_id for call in trace.tool_calls)
    if duplicate_calls:
        add(
            "duplicate_tool_call_id",
            IntegritySeverity.ERROR,
            "Tool call identifiers are not unique.",
            entities=duplicate_calls,
        )
    duplicate_results = _duplicates(result.result_id for result in trace.tool_results)
    if duplicate_results:
        add(
            "duplicate_tool_result_id",
            IntegritySeverity.ERROR,
            "Tool result identifiers are not unique.",
            entities=duplicate_results,
        )
    duplicate_dispatches = _duplicates(
        dispatch.dispatch_id for dispatch in trace.dispatches
    )
    if duplicate_dispatches:
        add(
            "duplicate_dispatch_id",
            IntegritySeverity.ERROR,
            "Tool dispatch identifiers are not unique.",
            entities=duplicate_dispatches,
        )

    source_ids = {source.source_id for source in trace.sources}
    event_ids = {event.event_id for event in trace.events}
    message_ids = {message.message_id for message in trace.messages}
    messages_by_id = {message.message_id: message for message in trace.messages}
    turns_by_id = {turn.turn_id: turn for turn in trace.assistant_turns}
    turn_ids = set(turns_by_id)
    call_ids = {call.call_id for call in trace.tool_calls}
    result_ids = {result.result_id for result in trace.tool_results}
    dispatch_ids = {dispatch.dispatch_id for dispatch in trace.dispatches}

    events_with_unknown_source = [
        event
        for event in trace.events
        if event.source_id not in source_ids
        or event.provenance.source_id != event.source_id
        or event.provenance.source_kind != event.source_kind
    ]
    if events_with_unknown_source:
        add(
            "event_source_mismatch",
            IntegritySeverity.CRITICAL,
            "Canonical event source/provenance does not resolve to a source artifact.",
            entities=[event.event_id for event in events_with_unknown_source],
            refs=[event.provenance for event in events_with_unknown_source],
        )

    missing_message_events = [
        message for message in trace.messages if message.event_id not in event_ids
    ]
    if missing_message_events:
        add(
            "message_missing_event",
            IntegritySeverity.ERROR,
            "Canonical message references an event that was not preserved.",
            entities=[message.message_id for message in missing_message_events],
            refs=[
                ref
                for message in missing_message_events
                for ref in message.source_refs
            ],
        )

    missing_turn_events = [
        turn for turn in trace.assistant_turns if turn.event_id not in event_ids
    ]
    if missing_turn_events:
        add(
            "turn_missing_event",
            IntegritySeverity.ERROR,
            "Assistant turn references an event that was not preserved.",
            entities=[turn.turn_id for turn in missing_turn_events],
            refs=[ref for turn in missing_turn_events for ref in turn.source_refs],
        )
    turns_without_messages = [
        turn for turn in trace.assistant_turns if turn.message_id not in message_ids
    ]
    if turns_without_messages:
        add(
            "turn_missing_message",
            IntegritySeverity.ERROR,
            "Assistant turn references a message that was not preserved.",
            entities=[turn.turn_id for turn in turns_without_messages],
            refs=[ref for turn in turns_without_messages for ref in turn.source_refs],
        )
    turn_message_event_mismatches = [
        turn
        for turn in trace.assistant_turns
        if turn.message_id in messages_by_id
        and messages_by_id[turn.message_id].event_id != turn.event_id
    ]
    if turn_message_event_mismatches:
        add(
            "turn_message_event_mismatch",
            IntegritySeverity.ERROR,
            "Assistant turn and its canonical message reference different events.",
            entities=[turn.turn_id for turn in turn_message_event_mismatches],
            refs=[
                ref
                for turn in turn_message_event_mismatches
                for ref in turn.source_refs
            ],
        )

    missing_call_events = [
        call for call in trace.tool_calls if call.event_id not in event_ids
    ]
    if missing_call_events:
        add(
            "tool_call_missing_event",
            IntegritySeverity.ERROR,
            "Tool call references an event that was not preserved.",
            entities=[call.call_id for call in missing_call_events],
            refs=[ref for call in missing_call_events for ref in call.source_refs],
        )
    missing_result_events = [
        result for result in trace.tool_results if result.event_id not in event_ids
    ]
    if missing_result_events:
        add(
            "tool_result_missing_event",
            IntegritySeverity.ERROR,
            "Tool result references an event that was not preserved.",
            entities=[result.result_id for result in missing_result_events],
            refs=[
                ref for result in missing_result_events for ref in result.source_refs
            ],
        )
    missing_dispatch_events = [
        dispatch for dispatch in trace.dispatches if dispatch.event_id not in event_ids
    ]
    if missing_dispatch_events:
        add(
            "tool_dispatch_missing_event",
            IntegritySeverity.ERROR,
            "Tool dispatch references an event that was not preserved.",
            entities=[
                dispatch.dispatch_id for dispatch in missing_dispatch_events
            ],
            refs=[
                ref
                for dispatch in missing_dispatch_events
                for ref in dispatch.source_refs
            ],
        )
    runs_with_missing_events: list[tuple[str, list[str]]] = []
    for run in trace.runs:
        linked = run.metadata.get("event_ids", [])
        if not isinstance(linked, list):
            linked = []
        missing = [str(event_id) for event_id in linked if event_id not in event_ids]
        if missing:
            runs_with_missing_events.append((run.run_id, missing))
    if runs_with_missing_events:
        add(
            "run_missing_event",
            IntegritySeverity.ERROR,
            "Canonical run references events that were not preserved.",
            entities=[
                entity_id
                for run_id, missing in runs_with_missing_events
                for entity_id in (run_id, *missing)
            ],
        )

    calls_without_turn = [
        call for call in trace.tool_calls if not call.turn_id or call.turn_id not in turn_ids
    ]
    for call in calls_without_turn:
        add(
            "tool_call_missing_turn",
            IntegritySeverity.ERROR,
            "Tool call is not linked to an assistant completion.",
            entities=[call.call_id],
            refs=call.source_refs,
        )
    calls_missing_from_turn = [
        call
        for call in trace.tool_calls
        if call.turn_id in turns_by_id
        and call.call_id not in turns_by_id[call.turn_id].tool_call_ids
    ]
    for call in calls_missing_from_turn:
        add(
            "turn_missing_linked_tool_call",
            IntegritySeverity.ERROR,
            "Tool call's assistant turn does not link back to the call.",
            entities=[call.turn_id or "", call.call_id],
            refs=call.source_refs,
        )

    orphan_results = [
        result
        for result in trace.tool_results
        if not result.call_id or result.call_id not in call_ids
    ]
    for result in orphan_results:
        add(
            "orphan_tool_result",
            IntegritySeverity.ERROR,
            "Tool result has no matching observed tool call.",
            entities=[result.result_id, result.call_id or ""],
            refs=result.source_refs,
        )

    orphan_dispatches = [
        dispatch
        for dispatch in trace.dispatches
        if not dispatch.call_id or dispatch.call_id not in call_ids
    ]
    for dispatch in orphan_dispatches:
        add(
            "orphan_tool_dispatch",
            IntegritySeverity.ERROR,
            "Tool dispatch has no matching observed tool call.",
            entities=[dispatch.dispatch_id, dispatch.call_id or ""],
            refs=dispatch.source_refs,
        )

    missing_results = [
        call
        for call in trace.tool_calls
        if call.status == ToolCallStatus.MISSING_RESULT or not call.result_ids
    ]
    for call in missing_results:
        add(
            "missing_tool_result",
            IntegritySeverity.ERROR,
            "Observed tool call has no matching result.",
            entities=[call.call_id],
            refs=call.source_refs,
        )

    for call in trace.tool_calls:
        invalid_results = [value for value in call.result_ids if value not in result_ids]
        invalid_dispatches = [
            value for value in call.dispatch_ids if value not in dispatch_ids
        ]
        if invalid_results or invalid_dispatches:
            add(
                "broken_tool_link",
                IntegritySeverity.ERROR,
                "Tool call contains links to missing results or dispatches.",
                entities=[call.call_id, *invalid_results, *invalid_dispatches],
                refs=call.source_refs,
            )

    for turn in trace.assistant_turns:
        invalid_calls = [
            call_id for call_id in turn.tool_call_ids if call_id not in call_ids
        ]
        invalid_results = [
            result_id
            for result_id in turn.tool_result_ids
            if result_id not in result_ids
        ]
        if invalid_calls:
            add(
                "turn_missing_tool_call",
                IntegritySeverity.ERROR,
                "Assistant turn references a tool call that was not preserved.",
                entities=[turn.turn_id, *invalid_calls],
                refs=turn.source_refs,
            )
        if invalid_results:
            add(
                "turn_missing_tool_result",
                IntegritySeverity.ERROR,
                "Assistant turn references a tool result that was not preserved.",
                entities=[turn.turn_id, *invalid_results],
                refs=turn.source_refs,
            )
        stop_reason = (turn.stop_reason or "").lower()
        if stop_reason in {"tooluse", "tool_use", "tool-call", "tool_calls"} and not turn.tool_call_ids:
            add(
                "tool_stop_without_call",
                IntegritySeverity.ERROR,
                "Completion stopped for tool use but contains no observable tool call.",
                entities=[turn.turn_id],
                refs=turn.source_refs,
            )

    # Validate raw parent references inside v3 session sources.  These are
    # source graph links, distinct from canonical cross-source links.
    session_ids_by_source: dict[str, set[str]] = defaultdict(set)
    for event in trace.events:
        if event.source_kind == SourceKind.SESSION_V3 and isinstance(event.raw, dict):
            raw_id = event.raw.get("id")
            if raw_id is not None:
                session_ids_by_source[event.source_id].add(str(raw_id))
    for event in trace.events:
        if (
            event.source_kind == SourceKind.SESSION_V3
            and event.parent_id
            and event.parent_id not in session_ids_by_source[event.source_id]
        ):
            add(
                "missing_session_parent",
                IntegritySeverity.WARNING,
                "Session event parentId does not resolve inside the provided artifact.",
                entities=[event.event_id, event.parent_id],
                refs=[event.provenance],
            )

    if trace.assistant_turns and trace.final_answer is None:
        add(
            "missing_final_answer",
            IntegritySeverity.WARNING,
            "No visible final assistant answer was observed.",
        )
    if (
        trace.final_turn_id is not None
        and trace.final_turn_id not in turn_ids
    ):
        add(
            "invalid_final_turn",
            IntegritySeverity.ERROR,
            "final_turn_id does not refer to a preserved assistant turn.",
            entities=[trace.final_turn_id],
        )
    elif trace.final_turn_id is not None:
        final_turn = turns_by_id[trace.final_turn_id]
        expected_final_answer = "".join(final_turn.text_outputs)
        if trace.final_answer != expected_final_answer:
            add(
                "final_answer_mismatch",
                IntegritySeverity.ERROR,
                "final_answer does not match the referenced assistant turn.",
                entities=[trace.final_turn_id],
                refs=final_turn.source_refs,
            )

    known_outcomes = {
        evaluation.passed
        for evaluation in trace.evaluations
        if evaluation.passed is not None
    }
    if len(known_outcomes) > 1:
        add(
            "evaluation_conflict",
            IntegritySeverity.WARNING,
            "External evaluators disagree about task success.",
            entities=[
                evaluation.evaluation_id for evaluation in trace.evaluations
            ],
        )

    source_trace_ids = trace.metadata.get("source_trace_ids", {})
    if isinstance(source_trace_ids, dict):
        session_trace = source_trace_ids.get(SourceKind.SESSION_V3.value)
        runtime_trace = source_trace_ids.get(SourceKind.RUNTIME_V1.value)
        if session_trace and runtime_trace and session_trace != runtime_trace:
            add(
                "session_runtime_trace_mismatch",
                IntegritySeverity.ERROR,
                "Session and runtime artifacts identify different traces.",
                details={
                    "session_trace_id": session_trace,
                    "runtime_trace_id": runtime_trace,
                },
            )

    matched_call_result_count = sum(bool(call.result_ids) for call in trace.tool_calls)
    matched_call_dispatch_count = sum(
        bool(call.dispatch_ids) for call in trace.tool_calls
    )
    metrics = {
        "source_count": len(trace.sources),
        "source_event_count": len(trace.events),
        "source_line_coverage": source_coverage,
        "parse_error_count": len(parse_errors),
        "raw_hash_mismatch_count": len(bad_raw_hashes),
        "raw_event_content_mismatch_count": len(raw_content_mismatches),
        "message_count": len(trace.messages),
        "assistant_turn_count": len(trace.assistant_turns),
        "tool_call_count": len(trace.tool_calls),
        "tool_result_count": len(trace.tool_results),
        "dispatch_count": len(trace.dispatches),
        "evaluation_count": len(trace.evaluations),
        "matched_call_result_count": matched_call_result_count,
        "matched_call_dispatch_count": matched_call_dispatch_count,
        "missing_tool_result_count": len(missing_results),
        "orphan_tool_result_count": len(orphan_results),
        "orphan_dispatch_count": len(orphan_dispatches),
        "final_answer_char_count": len(trace.final_answer or ""),
    }

    if any(
        issue.severity in {IntegritySeverity.ERROR, IntegritySeverity.CRITICAL}
        for issue in issues
    ):
        status = IntegrityStatus.FAIL
    elif any(issue.severity == IntegritySeverity.WARNING for issue in issues):
        status = IntegrityStatus.WARN
    else:
        status = IntegrityStatus.PASS
    report = IntegrityReport(status=status, issues=issues, metrics=metrics)
    trace.integrity = report
    if strict and status == IntegrityStatus.FAIL:
        raise IntegrityError(report)
    return report
