# Exporters & CLI (v5.24.1)

## Exporters

Exporters live inside Transformers (not a downstream library), so architecture changes, new attention patterns, and custom cache types are supported at export time as soon as they land in the modeling code. They are **experimental** — treat the patches as tied to the versions in the test suite and pin them in production tooling.

| Exporter | Program | Saved as | Runtime |
|---|---|---|---|
| `DynamoExporter` | `ExportedProgram` | `model.pt2` | Any PyTorch runtime, AOT compilation |
| `OnnxExporter` | `onnx_ir.Model` | `model.onnx` | Any ONNX runtime (ORT, TensorRT, OpenVINO) |
| `ExecutorchExporter` | `ExecutorchProgramManager` | `model.pte` | Mobile and edge devices (ExecuTorch) |
| `OpenVINOExporter` | `openvino.Model` | `openvino_model.xml` + `.bin` | OpenVINO runtime (Intel CPU/GPU/NPU) |

```python
from transformers import DynamoExporter, DynamoConfig  # or OnnxExporter, ExecutorchExporter

exporter = DynamoExporter()
config = DynamoConfig(dynamic=True)
exported = exporter.export(model, inputs, config=config)
```

Docs: `exporters.md`, `exporters_quantization.md` (quantizing exports), `exporters_extend.md`, and the production guide `serialization.md` (ExecuTorch, ONNX via optimum).

Note: torchscript and torch.fx support were dropped in v5 — use dynamo and torch.export.

## CLI

The entry point is `transformers` (Typer-based). `transformers-cli` is deprecated and `transformers run` was removed in v5.

Subcommands in v5.24.1 (`src/transformers/cli/`): `serve`, `chat`, `download`, `system`.

### transformers serve

A lightweight OpenAI-compatible server for local or self-hosted inference — no vLLM-style runtime overhead; good for evaluation, experimentation, and moderate load (use vLLM/SGLang for large-scale production, with transformers as the model backend).

```bash
pip install transformers[serving]
transformers serve          # default http://localhost:8000
```

REST API:
- `/v1/chat/completions` — text, image, audio, video requests
- `/v1/completions` — legacy text completions from a freeform prompt
- `/v1/responses` — OpenAI Responses API
- `/v1/audio/transcriptions` — audio transcription
- `/v1/systemone` — typed questions (choice, score, yes/no) with per-answer probabilities
- `/v1/models` — list available models
- `/load_model` — streams model loading progress via SSE

Works with the OpenAI SDK, `huggingface_hub.InferenceClient`, and plain curl. Continuous batching (`continuous_batching.md`) increases throughput.

### transformers chat

A terminal UI client for chatting with a model — the server-side functionality that lived here in v4 moved to `transformers serve`.

```sh
# Against a running transformers serve (default endpoint)
transformers chat HuggingFaceTB/SmolLM3-3B

# Against any OpenAI-compatible endpoint
transformers chat HuggingFaceTB/SmolLM3-3B https://router.huggingface.co/v1
```

Docs: `serve-cli/serving.md`, `serve-cli/serving_optims.md` (server optimizations), plus integration guides for Cursor, Jan, Open WebUI, and tiny-agents under `serve-cli/`.

### transformers download

Download models/files from the Hub (mirrors `hf download`).
