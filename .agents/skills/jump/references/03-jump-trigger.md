# Jump Trigger

`jump LABEL_NAME` is the activation signal. When it appears in generated output:

1. Harness locates matching `label LABEL_NAME` marker in conversation
2. Label not found → output exactly `error: LABEL_NAME does not exist`, execution halts
3. Label found → harness injects context from that point, agent resumes execution
4. Everything between jump and label is skipped

`jump LABEL_NAME` yields control to the harness. Harness decides next step, injects label context, and continues execution. Agent does not stop on its own — it waits for the harness to resume.

`jump LABEL_NAME` can result from condition evaluation or be emitted organically — either way, it triggers an immediate jump.
