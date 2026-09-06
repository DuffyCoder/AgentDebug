# Examples

`moltbot_failure_session.jsonl` is a synthetic email-triage session paired with
`email_triage_task.yaml`. It contains invented message IDs and tool responses;
running it does not connect to Gmail or retrieve real email.

The session illustrates a coverage failure: the task asks for all messages
requiring a reply, but the agent inspects one message and declares the rest
unnecessary. Structural validation can succeed even though the task failed.

Use the commands in [Getting started](../docs/getting-started.md). All generated
outputs should go to `output/`, not overwrite the source fixture.

When contributing examples, use synthetic content and remove credentials,
personal information, production endpoints, and copied private transcripts.
