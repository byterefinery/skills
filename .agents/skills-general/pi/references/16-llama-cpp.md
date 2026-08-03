# llama.cpp

Pi supports the [llama.cpp](https://github.com/ggml-org/llama.cpp) router server for local model inference.

## Start the Router

Start `llama-server` without `--model` or `-m` (passing a model starts single-model mode, not router mode):

```bash
llama-server \
  --models-dir ~/models \
  --no-models-autoload \
  --jinja \
  --host 127.0.0.1 \
  --port 8080 \
  -ngl 999 \
  -c 32768
```

Important options:
- `--models-dir ~/models` — discovers local GGUF files
- `--no-models-autoload` — keeps loading explicit through `/llama`
- `--jinja` — enables compatible chat templates and tool calling
- `-ngl 999` — offloads as many layers as possible to GPU
- `-c 32768` — context window per loaded model (omit for native context, may need more memory)

### Model Directory Layout

```
~/models/
├── llama-3.2-1b-Q4_K_M.gguf
├── gemma-3-4b-it-Q4_K_M/
│   ├── gemma-3-4b-it-Q4_K_M.gguf
│   └── mmproj-F16.gguf
└── large-model-Q4_K_M/
    ├── large-model-Q4_K_M-00001-of-00003.gguf
    ├── large-model-Q4_K_M-00002-of-00003.gguf
    └── large-model-Q4_K_M-00003-of-00003.gguf
```

Single-file models sit directly in the model directory. Multimodal and multi-shard models go in subdirectories. Restart the router after manually adding files.

## Configure Pi

```text
/login llama.cpp
```

Enter the router URL and optional API key. Default URL is `http://127.0.0.1:8080`.

Or use environment variables:

```bash
export LLAMA_BASE_URL=http://127.0.0.1:8080
export LLAMA_API_KEY=optional-secret
pi
```

## Manage Models

Run `/llama` in pi:

- Select an unloaded model to load it
- Select a loaded model to unload it
- Select **Download model…** to search Hugging Face, then choose repository and quantization
- Exact `owner/repository[:quant]` values also work
- Press Escape during load/download to confirm cancellation

Hugging Face search uses `HF_TOKEN` when set. Search works without authentication subject to lower rate limits. Pi warns before downloading gated repositories.

If other models are loaded, pi asks whether to unload them first. Pi never silently unloads models or deletes model files.

Only loaded models appear in `/model`. After loading, run `/model` to select it.

If the router disconnects, `/llama` shows **Retry** and **Close**.

## Troubleshooting

Check router is reachable:

```bash
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/models
```

- **No models in `/llama`:** Check `--models-dir`, directory layout, restart router
- **Model missing from `/model`:** Load it with `/llama` first
- **Load fails or uses too much memory:** Lower `-c` or unload another model
- **Server not in router mode:** Start without `--model`, `-m`, or `-hf`
