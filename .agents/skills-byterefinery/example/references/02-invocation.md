# Invocation and Script Calls

How the `example` skill behaves, step by step.

## Loading

1. The skill's name and description sit in the agent's system prompt at all times (metadata, ~100 words).
2. When the user's request matches the description, the agent loads SKILL.md.
3. Scripts and references load only if the instructions call for them.

## Invoked with no text

The agent replies exactly:

> This is an example skill.

No script runs, no references load, no commentary. A skill can be as simple as a fixed reply — this is the demonstration.

## Invoked with "Hello"

The agent replies exactly:

> world

No script runs. This fixed "Hello" → "world" mapping is hardcoded in the skill itself, showing that a skill's logic can live entirely in SKILL.md without touching `scripts/`.

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
