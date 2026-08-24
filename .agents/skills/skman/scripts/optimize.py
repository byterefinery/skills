#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.10"
# dependencies = ["gepa[full]"]
# ///

import subprocess
from tempfile import TemporaryDirectory

import gepa.optimize_anything as oa
from gepa.optimize_anything import optimize_anything, GEPAConfig, EngineConfig, ReflectionConfig


STUDENT_MODEL = 'LiquidAI/LFM2.5-2.6B'
STUDENT_MODEL_THINKING = 'high'

TEACHER_MODEL = 'Qwen/Qwen3.8-27B'
TEACHER_MODEL_THINKING = 'off' # 'xhigh'

objective = '''\
Generate simple python function that implements basic string comparisson algorithm, which returns one of: -1, 0, 1 .
'''

background = '''\
You are using `pi` coding agent harness in the background to do optimization and fullfil your objective.
You work in random temp directory. Never polute current working dir.
If code is generated as a candidate, do not run generate code, just return it.
'''


def pi(model: str, thinking: str, prompt: str, temp: bool=True) -> str:
    cmd = [
        'pi',
        '--model', model,
        '--thinking', thinking,
        '--no-skills',
        '--no-tools',
        '--tools',
        '"read,write,edit,bash"',
        '--no-context-files',
        '-p',
        prompt,
    ]

    # print(f'{cmd=}')
    proc_kwargs = {}
    temp_dir: TemporaryDirectory | None = None

    if temp:
        temp_dir = TemporaryDirectory()
        proc_kwargs['cwd'] = temp_dir.name

    proc = subprocess.run( # type: ignore # noqa
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        **proc_kwargs,
    )

    del temp_dir

    if proc.stderr:
        raise RuntimeError(proc.stderr)

    stdout = proc.stdout.decode()
    # print('reflection_lm:', stdout)
    return stdout


def reflection_lm(prompt: str) -> str:
    # print('reflection_lm', prompt)
    content = pi(TEACHER_MODEL, TEACHER_MODEL_THINKING, prompt)
    return content


def evaluate(candidate) -> float:
    # pi - student

    # pi - teacher
    score: str | float = pi(
        TEACHER_MODEL,
        TEACHER_MODEL_THINKING,
        (
            'score solution candidate on scale from `0.0` to `1.0`\n'
            f'<objective>{objective}</objective>\n'
            f'<candidate>{candidate}</candidate>\n'
            'Output is single float number.'
        )
    )

    try:
        score = float(score)
    except ValueError:
        score = 0.0

    # oa.log(f'{candidate=} {score=}')
    # print(f'{candidate=} {score=}')
    return score


result = oa.optimize_anything(
    evaluator=evaluate,
    objective=objective,
    background=background,
    config=GEPAConfig(
        engine=EngineConfig(
            # display_progress_bar=True,
            parallel=False,
            max_metric_calls=10,
        ),
        reflection=ReflectionConfig(
            reflection_lm=reflection_lm, # type: ignore
        ),
    )
)

print(result)
print(result.best_candidate)
