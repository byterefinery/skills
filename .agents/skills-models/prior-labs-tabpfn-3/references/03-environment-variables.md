# TabPFN-3 — Environment Variables

TabPFN uses Pydantic settings, supporting both environment variables and `.env` files.

## Authentication

| Variable | Description |
| --- | --- |
| `TABPFN_TOKEN` | PriorLabs authentication token. Obtain from [priorlabs.ai](https://ux.priorlabs.ai). Required for headless/CI environments. |
| `TABPFN_NO_BROWSER` | Set to disable automatic browser-based login. Useful when opening a browser is undesirable. |

```bash
export TABPFN_TOKEN="your_token_here"
export TABPFN_NO_BROWSER=1
```

## Model Configuration

| Variable | Description |
| --- | --- |
| `TABPFN_MODEL_CACHE_DIR` | Custom directory for caching downloaded models. Default: platform-specific user cache directory. |
| `TABPFN_ALLOW_CPU_LARGE_DATASET` | Allow running on CPU with large datasets (>1,000 samples). Set to `true` to override. Very slow! |
| `TABPFN_MPS_MEMORY_FRACTION` | Fraction of recommended max MPS memory on Apple Silicon (default: `0.7`). Prevents macOS crashes. Set before importing TabPFN. Values above `1.0` not recommended. |

```bash
export TABPFN_MODEL_CACHE_DIR="/path/to/models"
export TABPFN_ALLOW_CPU_LARGE_DATASET=true
export TABPFN_MPS_MEMORY_FRACTION=0.5
```

## PyTorch Settings

| Variable | Description |
| --- | --- |
| `PYTORCH_CUDA_ALLOC_CONF` | CUDA memory allocation config. Default: `max_split_size_mb:512`. See [PyTorch CUDA docs](https://pytorch.org/docs/stable/notes/cuda.html#optimizing-memory-usage-with-pytorch-cuda-alloc-conf). |

```bash
export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:512"
```

## Default Cache Directories

| OS | Path |
| --- | --- |
| Linux | `~/.cache/tabpfn/` |
| macOS | `~/Library/Caches/tabpfn/` |
| Windows | `%APPDATA%\tabpfn\` |

## `.env` File

Place a `.env` file in the working directory:

```
TABPFN_TOKEN=your_token_here
TABPFN_MODEL_CACHE_DIR=/path/to/models
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
```

Variables are loaded automatically via Pydantic settings.
