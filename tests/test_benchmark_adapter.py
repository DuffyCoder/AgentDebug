import json
from pathlib import Path

from agentdebug.benchmark.adapter import adapt_trajectory, validate_conversion
from agentdebug.benchmark.models import GoldLabel
from agentdebug.trace import IntegrityStatus


def _trajectory(path: Path) -> dict:
    document = {
        "messages": [
            {"role": "user", "content": "Task and first observation"},
            {
                "role": "assistant",
                "content": "<plan>repeat the wrong plan</plan>",
            },
            {"role": "user", "content": "That did not work"},
            {"role": "assistant", "content": "<action>try again</action>"},
        ],
        "metadata": {"model": "fixture-model", "steps": 2, "won": False},
    }
    path.write_text(json.dumps(document), encoding="utf-8")
    return document


def _gold(path: Path) -> GoldLabel:
    return GoldLabel(
        trajectory_id="fixture-trajectory",
        environment="alfworld",
        source_llm="fixture-model",
        original_step=1,
        raw_module="plan",
        module="planning",
        raw_error_type="inefficient_plan",
        error_type="inefficient_plan",
        reasoning="The first plan repeats a failed action.",
        label_path=str(path),
    )


def test_adapter_preserves_messages_and_maps_steps_bidirectionally(tmp_path):
    path = tmp_path / "fixture-trajectory.json"
    source = _trajectory(path)
    trace, mapping = adapt_trajectory(
        path,
        trajectory_id="fixture-trajectory",
    )
    report = validate_conversion(
        source_document=source,
        trace=trace,
        mapping=mapping,
        gold=_gold(path),
    )

    assert report.valid
    assert report.input_message_count == report.preserved_message_count == 4
    assert len(trace.events) == 5  # four messages plus metadata
    assert len(trace.assistant_turns) == 2
    assert trace.integrity.status == IntegrityStatus.WARN

    first_event = mapping.event_for_step(1)
    second_event = mapping.event_for_step(2)
    assert first_event
    assert second_event
    assert mapping.step_for_event(first_event) == 1
    assert mapping.step_for_event(second_event) == 2
    assert mapping.step_for_event(trace.events[-1].event_id) is None
    assert mapping.steps[0].tool_call_ids == ()
    assert mapping.steps[0].source_message_indices == (0, 1)
    assert mapping.steps[1].source_message_indices == (2, 3)

    for index, message in enumerate(source["messages"]):
        event = next(
            event
            for event in trace.events
            if event.event_id == trace.messages[index].event_id
        )
        assert event.raw == message


def test_gold_step_outside_observed_assistant_steps_is_conversion_error(tmp_path):
    path = tmp_path / "fixture-trajectory.json"
    source = _trajectory(path)
    trace, mapping = adapt_trajectory(path, trajectory_id="fixture-trajectory")
    gold = _gold(path)
    gold = GoldLabel(**{**gold.to_dict(), "original_step": 3})

    report = validate_conversion(
        source_document=source,
        trace=trace,
        mapping=mapping,
        gold=gold,
    )

    assert not report.valid
    assert "gold_step_unmapped" in {issue.code for issue in report.issues}
