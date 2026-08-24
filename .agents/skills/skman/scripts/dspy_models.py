#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.10"
# dependencies = ["dspy", "gepa[full]"]
# ///

'''
# NOTE: this is exactly how `dspy.LM` compatible with llama.cpp llama-server is instantiated
lm = dspy.LM(
    f"openai/{model}", # used model
    api_base=API_BASE,
    api_key=API_KEY,
    model_type="chat",
    temperature=..., # read for used model
    max_tokens=16384,
    extra_headers={"x-session-affinity": f"dspy-{model_name}-{session_id}"}, # per model + per REQUEST
    extra_body={
        "top_k": ..., # read for used model, or omit if missing
        "min_p": ..., # read for used model, or omit if missing
        "presence_penalty": ..., # read for used model, or omit if missing
        "repeat_penalty": ..., # read for used model, or omit if missing
    },
)
'''

# write function to read `~/.pi/agent/models.json` to get OPENAI_API_KEY and OPENAI_BASE_URL, and model settigs
lm = ... # 'LiquidAI/LFM2.5-2.6B' thinkinh `high`, aka student model
reflection_lm = ... # use 'Qwen/Qwen3.8-27B' thinkinh off, aka teacher model

# in `if __name__ == '__main__:', make calls to `lm` and `reflection_lm` to check if they are working.
