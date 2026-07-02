# Execution Flow

1. **Classify**: deterministic (math/logic) or free-form (natural language)?
2. **Deterministic**:
   a. Extract variable values from context — variables may be introduced in the condition itself
   b. Write script to `/tmp/jump_cond_<label>_<timestamp>.sh`
   c. Execute via `bash`
   d. Exit 0 → condition met; non-zero → not met
   e. Clean up script
3. **Free-form**: evaluate via LLM judgment against current context
4. **Output**:
   - Condition met → write exactly `jump LABEL_NAME`, stop
   - Condition not met → write exactly `continue`, let agent/harness/LLM decide next step
