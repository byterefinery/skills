#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.10"
# dependencies = ["dspy", "gepa[full]"]
# ///

"""Create dspy.LM instances from ~/.pi/agent/models.json.

# NOTE: this is exactly how `dspy.LM` compatible with llama.cpp llama-server is instantiated
lm = dspy.LM(
    f"openai/{model}", # used model
    api_base=API_BASE,
    api_key=API_KEY,
    model_type="chat",
    temperature=..., # read for used model
    max_tokens=..., # read for used model
    extra_headers={"x-session-affinity": f"dspy-{model_name}-{session_id}"}, # per model + per session
    extra_body={
        "top_p": ..., # read for used model, or omit if missing
        "top_k": ..., # read for used model, or omit if missing
        "min_p": ..., # read for used model, or omit if missing
        "presence_penalty": ..., # read for used model, or omit if missing
        "repeat_penalty": ..., # read for used model, or omit if missing
    },
)
"""

# ruff: noqa: I001
import json
import re
import uuid
from pathlib import Path

import dspy


MODELS_JSON = Path.home() / ".pi" / "agent" / "models.json"
SESSION_ID = uuid.uuid4().hex[:8]  # stable per process: keeps llama-server routing consistent


def _load_models_config(path: Path = MODELS_JSON) -> dict:
    text = path.read_text()
    # models.json may contain trailing commas (pi parses them leniently)
    text = re.sub(r",(\s*[}\]])", r"\1", text)
    return json.loads(text)


def _find_model(cfg: dict, model_name: str) -> tuple[dict, dict]:
    """Return the (provider, model) entries for `model_name` (matched by id)."""
    for provider in cfg["providers"].values():
        for model in provider.get("models", []):
            if model["id"] == model_name:
                return provider, model
    raise ValueError(f"model {model_name!r} not found in {MODELS_JSON}")


def create_lm(model_name: str, thinking: str) -> dspy.LM:
    """Create a dspy.LM for `model_name` with settings read from models.json.

    `thinking` is a thinking level name (e.g. "off", "low", "high"). It is
    resolved through the model's `thinkingLevelMap`; a non-null resolved value
    is sent as `reasoning_effort` in the request body. Levels the model does
    not support (null/missing — e.g. "off" for Qwen) are omitted and the
    server default applies.
    """
    cfg = _load_models_config()
    provider, model = _find_model(cfg, model_name)
    sampling = model.get("samplingParams", {})

    extra_body = {
        key: sampling[key]
        for key in ("top_p", "top_k", "min_p", "presence_penalty", "repeat_penalty")
        if key in sampling
    }

    # thinking: the llama.cpp server's Qwen template only accepts the levels
    # listed in thinkingLevelMap (xhigh/medium/low); it rejects "off" (500),
    # and enable_thinking:false / "/nothink" are ignored, so thinking cannot
    # be switched off — unsupported levels are simply omitted.
    effort = model.get("thinkingLevelMap", {}).get(thinking)

    if effort is not None:
        extra_body["reasoning_effort"] = effort

    return dspy.LM(
        f"openai/{model_name}",
        api_base=provider["baseUrl"],
        api_key=provider["apiKey"],
        model_type="chat",
        temperature=sampling.get("temperature", 1.0),
        max_tokens=model.get("maxTokens"),
        extra_headers={"x-session-affinity": f"dspy-{model_name}-{SESSION_ID}"},
        extra_body=extra_body,
    )


if __name__ == "__main__":
    lm = create_lm("LiquidAI/LFM2.5-2.6B", "high")        # student model
    reflection_lm = create_lm("Qwen/Qwen3.8-27B", "none")  # teacher model

    messages = [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "What is the capital of France?"},
    ]

    print("lm (LiquidAI/LFM2.5-2.6B, thinking=high):")
    print(lm(messages=messages))
    print()
    print("reflection_lm (Qwen/Qwen3.8-27B, thinking=off):")
    print(reflection_lm(messages=messages))
