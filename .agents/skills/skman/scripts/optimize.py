#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.10"
# dependencies = ["gepa[full]", "openai"]
# ///

import os
import re
import json
import uuid
import subprocess
from pathlib import Path
from random import random

from openai import OpenAI
import gepa.optimize_anything as oa
from gepa.optimize_anything import optimize_anything, GEPAConfig, EngineConfig, ReflectionConfig


MODELS_JSON_PATH = Path.home() / ".pi" / "agent" / "models.json"


def _load_models_json() -> dict | None:
    """Load `~/.pi/agent/models.json`, tolerating trailing commas (pi writes lenient JSON)."""
    if not MODELS_JSON_PATH.is_file():
        return None

    try:
        text = MODELS_JSON_PATH.read_text()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return json.loads(re.sub(r",(\s*[}\]])", r"\1", text))
    except (OSError, json.JSONDecodeError):
        return None


def find_openai_api_key_base_url() -> tuple[str | None, str | None]:
    # check env vars `OPENAI_API_KEY` and `OPENAI_BASE_URL`
    # as fallback check `~/.pi/agent/models.json`
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL")

    if api_key or base_url:
        return api_key, base_url

    data = _load_models_json()

    if data is None:
        return None, None

    providers = data.get("providers", {})

    def _usable(provider: dict) -> tuple[str, str] | None:
        api_key, base_url = provider.get("apiKey"), provider.get("baseUrl")
        if api_key and base_url:
            return api_key, base_url

        return None

    # prefer OpenAI-compatible endpoints, then any provider with credentials
    for api in ("openai-completions", None):
        for provider in providers.values():
            if api and provider.get("api") != api:
                continue

            if found := _usable(provider):
                return found

    return None, None


def get_model_config(model_name) -> dict:
    """Build LM sampling config for `model_name` from `~/.pi/agent/models.json`.

    Returns dict with keys:
    ```
    max_tokens=..., # read for used model
    temperature=..., # read for used model
    "top_k": ..., # read for used model, or omit if missing
    "min_p": ..., # read for used model, or omit if missing
    "presence_penalty": ..., # read for used model, or omit if missing
    "repeat_penalty": ..., # read for used model, or omit if missing
    ```

    Returns empty dict if `~/.pi/agent/models.json` is missing or the model is not found.
    """
    data = _load_models_json()

    if data is None:
        return {}

    for provider in data.get("providers", {}).values():
        for model in provider.get("models", []):
            if model.get("id") != model_name and model.get("name") != model_name:
                continue

            config: dict = {}
            sampling = model.get("samplingParams", {})

            if (max_tokens := model.get("maxTokens")) is not None:
                config["max_tokens"] = max_tokens

            if (temperature := sampling.get("temperature")) is not None:
                config["temperature"] = temperature

            for key in ("top_k", "min_p", "presence_penalty", "repeat_penalty"):
                if (value := sampling.get(key)) is not None:
                    config[key] = value

            return config

    return {}


OPENAI_API_KEY, OPENAI_BASE_URL = find_openai_api_key_base_url()

STUDENT_MODEL = 'LiquidAI/LFM2.5-2.6B'
STUDENT_MODEL_THINKING = 'high'
# STUDENT_MODEL_CONFIG = get_model_config(STUDENT_MODEL)

TEACHER_MODEL = 'Qwen/Qwen3.8-27B'
TEACHER_MODEL_THINKING = "none" # 'xhigh'
TEACHER_MODEL_CONFIG = get_model_config(TEACHER_MODEL)


objective = f'''\
Generate simple python function that implements basic string comparisson algorithm, which returns one of: -1, 0, 1 .
''' # noqa

background = f'''\
Directly run `pi` command using `subprocess` in random temp dir (`TEMP_DIR_1`), reaching a goal and producing a candidate.
`pi` is a coding agent harness, and expect that it is already installed.

When calling `pi` command:
- Pass custom CLI args `--model {STUDENT_MODEL} --thinking {"off" if STUDENT_MODEL_THINKING in [None, "none", "off"] else STUDENT_MODEL_THINKING} --no-tools --tools 'read,write,edit,bash' --no-extensions`.
- Save your goal to temp file in demp dir `TEMP_DIR_1` under name `GOAL.md`.
- In temp dir `TEMP_DIR_1`, run `pi` in bash shell pasing all CLI args, plus goal and prompt how to solve goal and report back to use what was a candiate produced by `pi`:
  ```bash
  pi <CLI args go here> @GOAL.md -p "solve @GOAL.md"
  ```
'''


# student_client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
teacher_client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
reflection_session_id = uuid.uuid4()


def tool_bash(command: str, timeout: int | float | None=None) -> str:
    timeout: float | None = float(timeout) if isinstance(timeout, (int, float)) else timeout
    stdout = subprocess.check_output(command, timeout=timeout, shell=True)
    stdout = stdout.decode()
    return stdout


def reflection_lm(prompt) -> str:
    """GEPA `LanguageModel` backed by the teacher client: (str | list[dict]) -> str."""
    print('reflection_lm:\n', prompt)

    messages = [
        {'role': 'user', 'content': prompt}
    ]

    extra_body: dict = {}
    top_k = TEACHER_MODEL_CONFIG.get('top_k')
    min_p = TEACHER_MODEL_CONFIG.get('min_p')
    repeat_penalty = TEACHER_MODEL_CONFIG.get('repeat_penalty')

    if isinstance(top_k, (int, float)):
        extra_body['top_k'] = top_k

    if isinstance(min_p, (int, float)):
        extra_body['min_p'] = min_p

    if isinstance(repeat_penalty, (int, float)):
        extra_body['repeat_penalty'] = repeat_penalty

    tools = [
        {
            "type": "function",
            "function": {
                "name": "bash",
                "description": "Execute a bash command in the current working directory. Returns stdout and stderr. Output is truncated to last 2000 lines or 50KB (whichever is hit first). If truncated, full output is saved to a temp file. Optionally provide a timeout in seconds.",
                "parameters": {
                    "type": "object",
                    "required": ["command"],
                    "properties": {
                        "command": {"type": "string", "description": "Bash command to execute"},
                        "timeout": {
                            "type": "number",
                            "description": "Timeout in seconds (optional, no default timeout)",
                        },
                    },
                },
                "strict": False,
            },
        }
    ]

    extra_headers: dict = {
        'x-session-affinity': f'gepa-{TEACHER_MODEL}-{reflection_session_id}'
    }

    teacher_client_kwargs = dict( # noqa
        model=TEACHER_MODEL,
        max_tokens=TEACHER_MODEL_CONFIG.get('max_tokens'),
        presence_penalty=TEACHER_MODEL_CONFIG.get('presence_penalty'),
        reasoning_effort=TEACHER_MODEL_THINKING,
        temperature=TEACHER_MODEL_CONFIG.get('temperature'),
        top_p=TEACHER_MODEL_CONFIG.get('top_p'),
        tools=tools,
        extra_body=extra_body,
        extra_headers=extra_headers,
    )

    response = teacher_client.chat.completions.create( # type: ignore
        messages=messages,
        **teacher_client_kwargs
    )

    while True:
        assistant_message = response.choices[0].message
        content: str

        if assistant_message.tool_calls:
            messages.append(assistant_message)
            is_error: bool = False

            for tool_call in assistant_message.tool_calls:
                # tool/function call
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                print(f"Model requested tool: {function_name} with args: {function_args}")

                if function_name == "bash":
                    try:
                        tool_output = tool_bash(**function_args)
                    except Exception as e: # noqa
                        tool_output = json.dumps({'error': str(e)})
                        is_error = True

                    print('Output:', tool_output)

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": tool_output,
                    })

                if is_error:
                    break

            response = teacher_client.chat.completions.create( # type: ignore
                messages=messages,
                **teacher_client_kwargs,
            )
        else:
            content = assistant_message.content
            break

    return content


def evaluate(candidate) -> float:
    print(f'{candidate=}')
    # score, diagnostic = run_my_system(candidate)
    # oa.log(f"Error: {diagnostic}")  # captured as ASI
    # return score
    score = random()
    oa.log(f'{candidate=} {score=}')
    return score


result = oa.optimize_anything(
    evaluator=evaluate,
    objective=objective,
    background=background,
    config=GEPAConfig(
        engine=EngineConfig(
            display_progress_bar=True,
            parallel=False,
            max_metric_calls=10,
        ),
        reflection=ReflectionConfig(
            reflection_lm=reflection_lm, # type: ignore
        ),
    )
)

print(result.best_candidate)
