# Jump Trigger

`jump LABEL_NAME` is the activation signal. When it appears in generated output:

1. Agent/harness locates matching `label LABEL_NAME` marker in conversation
2. Label not found → output exactly `error: LABEL_NAME does not exist`
3. Label found → processing resumes from that point onward
4. Everything between jump and label is skipped

`jump LABEL_NAME` can result from condition evaluation or be emitted organically — either way, it triggers an immediate jump.
