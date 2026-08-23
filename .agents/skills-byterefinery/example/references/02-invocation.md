# Invocation and Script Calls

How the `example` skill behaves, step by step.

## Loading

1. The skill's name and description sit in the agent's system prompt at all times (metadata, ~100 words).
2. When the user's request matches the description, the agent loads SKILL.md.
3. Scripts and references load only if the instructions call for them.

## Invoked with no text

"No text" means nothing remains after removing the request for the skill itself (for example, "Use the example skill." leaves nothing). The agent replies exactly:

> This is an example skill. (anchor 4f7a)

No script runs, no references load, no commentary. A skill can be as simple as a fixed reply — this is the demonstration.

## Invoked with "Hello"

The instructions for this case are not in SKILL.md — they live in [03-hello.md](03-hello.md), and the agent must load that file to learn how to respond. No script runs. This is the skill's progressive-disclosure demonstration: a use case's logic sits in a reference file the agent has to open on demand, instead of inline in SKILL.md or in `scripts/`.

## Invoked with other text

Any other text the user gives is forwarded as CLI parameters to `scripts/example.sh`:

```bash
bash scripts/example.sh hello world
```

`example.sh` accepts and ignores the parameters — it always prints:

```
This is example.sh output.
```

The forwarding is the demonstration, not the output.

## "Call script"

If the user asks to "call script", run `example.sh` directly, with any parameters the user named:

```bash
bash scripts/example.sh
```
