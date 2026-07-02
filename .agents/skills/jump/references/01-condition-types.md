# Condition Types

- **Math** (script) — `attempts < 3`, `score >= 90`, `count > max + 10`
- **Logic** (script) — `status == "failed"`, `ready && connected`, `not in_whitelist`
- **Free-form** (LLM) — `output is too verbose`, `user seems confused`, `performance is a concern`

Math/logic → extract vars from context, write script, execute, exit 0 = met. Free-form → LLM judgment only.
