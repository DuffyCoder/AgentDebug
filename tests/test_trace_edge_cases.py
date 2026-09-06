from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentdebug.trace import (
    IntegrityError,
    load_canonical_trace,
    load_trace_bundle,
    save_canonical_trace,
    validate_trace,
)


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
        encoding="utf-8",
    )


def _session_header(trace_id: str = "trace") -> dict[str, object]:
    return {
        "type": "session",
        "version": 3,
        "id": trace_id,
        "timestamp": "2026-01-01T00:00:00Z",
    }


def _runtime_record(
    record_type: str,
    data: dict[str, object],
    *,
    trace_id: str = "trace",
    sequence: int = 1,
) -> dict[str, object]:
    return {
        "traceSchema": "openclaw-trajectory",
        "schemaVersion": 1,
        "traceId": trace_id,
        "type": record_type,
        "ts": f"2026-01-01T00:00:{sequence:02d}Z",
        "seq": sequence,
        "sessionId": trace_id,
        "runId": "run-1",
        "data": data,
    }


def _text_message(
    message_id: str,
    role: str,
    text: str,
    *,
    parent_id: str | None = None,
    second: int = 1,
) -> dict[str, object]:
    row: dict[str, object] = {
        "type": "message",
        "id": message_id,
        "timestamp": f"2026-01-01T00:00:{second:02d}Z",
        "message": {
            "role": role,
            "content": [{"type": "text", "text": text}],
        },
    }
    if parent_id is not None:
        row["parentId"] = parent_id
    return row


def test_transcript_leaf_selects_active_session_branch(tmp_path: Path) -> None:
    session = tmp_path / "branch.jsonl"
    runtime = tmp_path / "branch.trajectory.jsonl"
    _write_jsonl(
        session,
        [
            _session_header("branch"),
            _text_message("user", "user", "question", second=1),
            _text_message(
                "active", "assistant", "ACTIVE", parent_id="user", second=2
            ),
            _text_message(
                "abandoned",
                "assistant",
                "ABANDONED",
                parent_id="user",
                second=3,
            ),
        ],
    )
    _write_jsonl(
        runtime,
        [
            _runtime_record(
                "context.compiled",
                {"transcriptLeafId": "active", "tools": []},
                trace_id="branch",
            )
        ],
    )

    trace = load_trace_bundle(session, runtime_path=runtime, strict=True)

    assert trace.final_answer == "ACTIVE"
    assert [turn.message_id for turn in trace.assistant_turns] == ["active"]
    assert trace.metadata["branch_selection"]["active_leaf_id"] == "active"


def test_transcript_leaf_fork_is_an_integrity_error(tmp_path: Path) -> None:
    session = tmp_path / "ambiguous.jsonl"
    runtime = tmp_path / "ambiguous.trajectory.jsonl"
    _write_jsonl(
        session,
        [
            _session_header("ambiguous"),
            _text_message("user", "user", "question", second=1),
            _text_message("left", "assistant", "left", parent_id="user", second=2),
            _text_message(
                "right", "assistant", "right", parent_id="user", second=3
            ),
        ],
    )
    _write_jsonl(
        runtime,
        [
            _runtime_record(
                "context.compiled",
                {"transcriptLeafId": "user", "tools": []},
                trace_id="ambiguous",
            )
        ],
    )

    trace = load_trace_bundle(session, runtime_path=runtime)
    assert "ambiguous_session_branch" in {
        issue.code for issue in trace.integrity.issues
    }
    with pytest.raises(IntegrityError):
        validate_trace(trace, strict=True)


def test_partial_session_recovers_visible_runtime_completion(
    tmp_path: Path,
) -> None:
    session = tmp_path / "partial.jsonl"
    runtime = tmp_path / "partial.trajectory.jsonl"
    _write_jsonl(
        session,
        [
            _session_header("partial"),
            _text_message("user", "user", "question", second=1),
            _text_message(
                "old", "assistant", "old answer", parent_id="user", second=2
            ),
        ],
    )
    snapshot = [
        {"role": "user", "content": [{"type": "text", "text": "question"}]},
        {
            "role": "assistant",
            "content": [{"type": "text", "text": "old answer"}],
            "stopReason": "stop",
        },
        {
            "role": "assistant",
            "content": [{"type": "text", "text": "new final answer"}],
            "stopReason": "stop",
        },
    ]
    _write_jsonl(
        runtime,
        [
            _runtime_record(
                "model.completed",
                {"messagesSnapshot": snapshot},
                trace_id="partial",
                sequence=4,
            )
        ],
    )

    trace = load_trace_bundle(session, runtime_path=runtime, strict=True)

    assert trace.final_answer == "new final answer"
    assert len(trace.assistant_turns) == 2
    recovered = trace.assistant_turns[-1]
    assert recovered.metadata["recovered_from_non_authoritative_source"] is True


def test_reused_call_id_is_preserved_and_rejected_by_integrity(
    tmp_path: Path,
) -> None:
    session = tmp_path / "reused-call.jsonl"
    rows: list[dict[str, object]] = [
        _session_header("reused-call"),
        _text_message("user", "user", "question", second=1),
    ]
    parent = "user"
    for occurrence in (1, 2):
        assistant_id = f"assistant-{occurrence}"
        result_id = f"result-{occurrence}"
        rows.append(
            {
                "type": "message",
                "id": assistant_id,
                "parentId": parent,
                "timestamp": f"2026-01-01T00:00:0{occurrence + 1}Z",
                "message": {
                    "role": "assistant",
                    "stopReason": "toolUse",
                    "content": [
                        {
                            "type": "toolCall",
                            "id": "reused",
                            "name": "lookup",
                            "arguments": {"occurrence": occurrence},
                        }
                    ],
                },
            }
        )
        rows.append(
            {
                "type": "message",
                "id": result_id,
                "parentId": assistant_id,
                "timestamp": f"2026-01-01T00:00:0{occurrence + 3}Z",
                "message": {
                    "role": "toolResult",
                    "toolCallId": "reused",
                    "toolName": "lookup",
                    "content": str(occurrence),
                    "isError": False,
                },
            }
        )
        parent = result_id
    rows.append(
        _text_message("final", "assistant", "done", parent_id=parent, second=7)
    )
    _write_jsonl(session, rows)

    trace = load_trace_bundle(session)

    assert len(trace.tool_calls) == 2
    assert [call.arguments for call in trace.tool_calls] == [
        {"occurrence": 1},
        {"occurrence": 2},
    ]
    assert "duplicate_tool_call_id" in {
        issue.code for issue in trace.integrity.issues
    }
    with pytest.raises(IntegrityError):
        validate_trace(trace, strict=True)


def test_integrity_binds_raw_events_and_derived_links(
    tmp_path: Path,
) -> None:
    session = tmp_path / "tamper.jsonl"
    _write_jsonl(
        session,
        [
            _session_header("tamper"),
            _text_message("answer", "assistant", "answer", second=1),
        ],
    )
    trace = load_trace_bundle(session, strict=True)

    trace.events[0].raw["id"] = "changed"
    trace.assistant_turns[0].event_id = "event:missing"
    trace.assistant_turns[0].message_id = "message:missing"
    report = validate_trace(trace)
    codes = {issue.code for issue in report.issues}

    assert {
        "raw_event_content_mismatch",
        "turn_missing_event",
        "turn_missing_message",
    } <= codes
    with pytest.raises(IntegrityError):
        validate_trace(trace, strict=True)


def test_unsupported_session_schema_fails_strict_validation(
    tmp_path: Path,
) -> None:
    session = tmp_path / "v2.jsonl"
    _write_jsonl(
        session,
        [{"type": "session", "version": 2, "id": "old-schema"}],
    )

    trace = load_trace_bundle(session)
    assert "unsupported_session_version" in {
        issue.code for issue in trace.integrity.issues
    }
    with pytest.raises(IntegrityError):
        load_trace_bundle(session, strict=True)


def test_unsupported_canonical_schema_fails_strict_validation(
    tmp_path: Path,
) -> None:
    session = tmp_path / "canonical-schema.jsonl"
    _write_jsonl(
        session,
        [
            _session_header("canonical-schema"),
            _text_message("answer", "assistant", "answer"),
        ],
    )
    trace = load_trace_bundle(session, strict=True)
    trace.schema_version = 99

    with pytest.raises(IntegrityError) as caught:
        validate_trace(trace, strict=True)
    assert "unsupported_canonical_schema" in {
        issue.code for issue in caught.value.report.issues
    }


def test_runtime_records_cannot_mix_trace_declarations(tmp_path: Path) -> None:
    runtime = tmp_path / "mixed.trajectory.jsonl"
    _write_jsonl(
        runtime,
        [
            _runtime_record(
                "model.completed",
                {"messagesSnapshot": []},
                trace_id="trace-a",
                sequence=1,
            ),
            _runtime_record(
                "model.completed",
                {"messagesSnapshot": []},
                trace_id="trace-b",
                sequence=2,
            ),
        ],
    )

    trace = load_trace_bundle(runtime_path=runtime)
    assert "runtime_trace_declaration_mismatch" in {
        issue.code for issue in trace.integrity.issues
    }
    with pytest.raises(IntegrityError):
        validate_trace(trace, strict=True)


def test_runtime_snapshot_deduplication_is_occurrence_aware(
    tmp_path: Path,
) -> None:
    runtime = tmp_path / "duplicates.trajectory.jsonl"
    same = {
        "role": "assistant",
        "content": [{"type": "text", "text": "same"}],
        "stopReason": "stop",
    }
    _write_jsonl(
        runtime,
        [
            _runtime_record(
                "model.completed",
                {"messagesSnapshot": [same, same]},
                trace_id="duplicates",
                sequence=1,
            ),
            _runtime_record(
                "model.completed",
                {"messagesSnapshot": [same, same, same]},
                trace_id="duplicates",
                sequence=2,
            ),
        ],
    )

    trace = load_trace_bundle(None, runtime_path=runtime, strict=True)

    assert len(trace.assistant_turns) == 3
    assert [turn.text_outputs for turn in trace.assistant_turns] == [
        ["same"],
        ["same"],
        ["same"],
    ]


def test_runtime_only_manifest_is_not_selected_without_identity(
    tmp_path: Path,
) -> None:
    runtime = tmp_path / "runtime.trajectory.jsonl"
    manifest = tmp_path / "manifest.jsonl"
    _write_jsonl(
        runtime,
        [
            _runtime_record(
                "model.completed",
                {
                    "messagesSnapshot": [
                        {
                            "role": "assistant",
                            "content": [{"type": "text", "text": "answer"}],
                        }
                    ]
                },
            )
        ],
    )
    _write_jsonl(
        manifest,
        [
            {"session_jsonl": "one.jsonl", "task_id": "T1", "passed": True},
            {"session_jsonl": "two.jsonl", "task_id": "T2", "passed": True},
        ],
    )

    trace = load_trace_bundle(
        None,
        runtime_path=runtime,
        manifest_path=manifest,
    )

    assert trace.evaluations == []
    assert "manifest_selection_unscoped" in {
        issue.code for issue in trace.integrity.issues
    }
    with pytest.raises(IntegrityError):
        validate_trace(trace, strict=True)


def test_yaml_dates_round_trip_through_canonical_json(tmp_path: Path) -> None:
    session = tmp_path / "dated.jsonl"
    task = tmp_path / "task.yaml"
    canonical = tmp_path / "dated.canonical.json"
    _write_jsonl(
        session,
        [
            _session_header("dated"),
            _text_message("answer", "assistant", "answer", second=1),
        ],
    )
    task.write_text(
        "task_id: DATED\nprompt:\n  text: hi\ndeadline: 2026-07-23\n",
        encoding="utf-8",
    )

    trace = load_trace_bundle(session, task_path=task, strict=True)
    save_canonical_trace(trace, canonical)
    restored = load_canonical_trace(canonical, strict=True)

    assert restored.to_dict() == trace.to_dict()
    assert restored.task is not None
    assert restored.task.raw["deadline"] == "2026-07-23"
