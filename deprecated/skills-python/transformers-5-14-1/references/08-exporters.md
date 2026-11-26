# Exporters

Transformers provides model export pipelines for ONNX, TorchScript, and ExecuTorch. Exported models can run in optimized inference engines without the full Transformers dependency.

## ONNX Export

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.export import export_model, onnx

# Automatic ONNX export
from transformers import pipeline

export_model(
    model=model,
    output_path="./model.onnx",
    config=onnx.OnnxConfig.from_model-production(model),
)

# Using the CLI
# transformers-export --model model_id --task text-generation --output model.onnx

# Or use the exporters module directly
from transformers.exporters.onnx import main as export_onnx

export_onnx(
    model=model,
    output="./model.onnx",
    device="cpu",
    optimize="O2",
)
```

### ONNX Runtime Inference

```python
import onnxruntime as ort
import numpy as np

# Load ONNX model
session = ort.InferenceSession("./model.onnx")

# Get input/output names
input_names = [input.name for input in session.get_inputs()]
output_names = [output.name for output in session.get_outputs()]

# Prepare inputs
inputs = tokenizer("Hello, world!", return_tensors="np")

# Run inference
outputs = session.run(output_names, {input_names[0]: inputs["input_ids"]})

# Decode
print(tokenizer.decode(outputs[0][0]))
```

### ONNX Optimization Levels

| Level | Description |
|---|---|
| `O0` | No optimization |
| `O1` | Basic graph optimization |
| `O2` | Standard optimization (recommended) |
| `O3` | Aggressive optimization |

## TorchScript

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("model")
model.eval()

# Trace-based (requires example input)
inputs = tokenizer("Hello", return_tensors="pt")
traced_model = torch.jit.trace(model, example_inputs=(inputs["input_ids"], inputs["attention_mask"]))

# Script-based (handles control flow)
scripted_model = torch.jit.script(model)

# Save
traced_model.save("./model-traced.pt")
scripted_model.save("./model-scripted.pt")

# Load
loaded = torch.jit.load("./model-traced.pt")

# Run inference
with torch.no_grad():
    outputs = loaded(inputs["input_ids"], inputs["attention_mask"])
```

### TorchScript Export via Transformers

```python
from transformers.exporters import export

# Export to TorchScript
export(
    model=model,
    output="./model",
    format="torchscript",
    task="text-generation",
)
```

## ExecuTorch

```python
from transformers.exporters import export

# Export to ExecuTorch (for mobile/embedded)
export(
    model=model,
    output="./model",
    format="executorch",
    task="text-generation",
)
```

## Dynamic Axes

For variable-length inputs:

```python
from transformers.export import export_model, onnx

# Define dynamic axes
dynamic_axes = {
    "input_ids": {0: "batch_size", 1: "sequence_length"},
    "attention_mask": {0: "batch_size", 1: "sequence_length"},
    "logits": {0: "batch_size", 1: "sequence_length"},
}

config = onnx.OnnxConfig.from_model_production(model)
config.dynamic_axes = dynamic_axes

export_model(
    model=model,
    output_path="./model-dynamic.onnx",
    config=config,
)
```

## Export Pipeline

```python
from transformers import AutoModelForCausalLM
from transformers.exporters import export

model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-1.5B")

# Full export pipeline
export(
    model=model,
    output="./exported-model",
    task="text-generation",
    # format="onnx",  # Default
    # optimize="O2",
    # device="cpu",
    # dtype="float32",
)
```

## Gotchas

- **ONNX requires CPU-compatible model** — export on CPU or move model to CPU first. GPU operations may not export cleanly.
- **TorchScript `trace` vs `script`** — `trace` records operations for specific inputs. `script` compiles the Python code. Use `script` for models with control flow.
- **`generate()` doesn't export to ONNX** — ONNX exports the forward pass. For generation, use a decoding loop with the exported model or use an ONNX-compatible generation library.
- **Dynamic shapes need explicit axes** — without `dynamic_axes`, ONNX models have fixed input sizes. Define batch and sequence dimensions as dynamic.
- **`past_key_values` in ONNX** — for incremental decoding, the model needs past key value inputs/outputs. Check the ONNX config for decoder support.
- **Optimization level `O2` is recommended** — `O3` can break some models. Start with `O2` and verify outputs match the PyTorch model.
- **TorchScript compatibility** — not all Transformers models script cleanly. Check with `torch.jit.script(model)` and fix any errors.
- **`model.eval()` before export** — always set evaluation mode before exporting. Training-specific operations (dropout) behave differently.
- **`torch.no_grad()` during export** — wrap export in `torch.no_grad()` to avoid building computation graphs.
- ** ExecuTorch for mobile** — requires the ExecuTorch SDK. Export produces `.pte` files for Android/iOS deployment.
- **`trust_remote_code` models** — custom architectures may not export. Check exporter compatibility.
- **Sequence length limits** — exported models may have max sequence length constraints. Check the ONNX model's input shapes.
- **Quantized ONNX** — use ONNX Runtime's quantization tools post-export for additional optimization.
