# 04 — Inference client

`InferenceClient` (sync) and `AsyncInferenceClient` (async, auto-generated from the sync client by `utils/generate_async_inference_client.py`) call deployed models through a unified API.

## Constructor

Verified from `inference/_client.py`:

```python
InferenceClient(
    model: str | None = None,
    *,
    provider: PROVIDER_OR_POLICY_T | None = None,
    token: str | None = None,
    timeout: float | None = None,
    headers: dict[str, str] | None = None,
    cookies: dict[str, str] | None = None,
    bill_to: str | None = None,
    ...
)
```

`PROVIDER_OR_POLICY_T = Union[PROVIDER_T, Literal["auto"]]` — a provider string (hyphenated, see below) or `"auto"` to let the client pick per task/model.

## Providers (19, verified from `PROVIDER_T`)

`baseten`, `cerebras`, `cohere`, `deepinfra`, `fal-ai`, `featherless-ai`, `fireworks-ai`, `groq`, `hf-inference`, `novita`, `nscale`, `openai`, `ovhcloud`, `publicai`, `replicate`, `scaleway`, `together`, `wavespeed`, `zai-org`

Each provider lives in `inference/_providers/<name>.py` (e.g. `fal_ai.py` → `"fal-ai"`). `hf-inference` is the Hub's own serverless backend.

## Task methods (29, verified from the client source)

- `audio_classification`
- `audio_to_audio`
- `automatic_speech_recognition`
- `chat_completion`
- `document_question_answering`
- `feature_extraction`
- `fill_mask`
- `image_classification`
- `image_segmentation`
- `image_to_image`
- `image_to_video`
- `image_to_text`
- `object_detection`
- `question_answering`
- `sentence_similarity`
- `summarization`
- `table_question_answering`
- `tabular_classification`
- `tabular_regression`
- `text_classification`
- `text_generation`
- `text_to_image`
- `text_to_video`
- `text_to_speech`
- `token_classification`
- `translation`
- `visual_question_answering`
- `zero_shot_classification`
- `zero_shot_image_classification`

Plus utilities: `get_endpoint_info(...)` and `health_check(...)`.

## Streaming and futures

- `chat_completion` and `text_generation` have overloads that stream chunks (`ChatCompletionStreamOutput`, `TextGenerationStreamOutput` dataclasses).
- All task methods accept `run_as_future=True` to return a `concurrent.futures.Future` instead of blocking.

## Output types

Each task has strict input/output dataclasses in `inference/_generated/` (auto-generated, do not hand-edit): `ChatCompletionInput/Output`, `TextGenerationInput/Output`, `ImageClassificationOutput`, `AutomaticSpeechRecognitionOutput`, etc. `ChatCompletionOutput` mirrors the OpenAI shape (`choices[0].message.content`), so `chat_completion` works as an OpenAI-compatible entry point.

## Errors

- `InferenceTimeoutError` (HTTPError + TimeoutError)
- `TextGenerationError` base with `ValidationError`, `GenerationError`, `OverloadedError`, `IncompleteGenerationError`, `UnknownError`
