# Quantization (v5.24.1)

Quantization stores weights (and sometimes activations) in fewer bits to cut memory. Rule of thumb from the docs: an 8B model needs ~16GB in bf16, ~8GB at 8 bits, ~4–5GB at 4 bits. Transformers integrates 20+ methods through `from_pretrained`, so the loading code is identical whichever method you pick.

## v5 API: `quantization_config` only

The bare `load_in_4bit` / `load_in_8bit` kwargs were **removed** in v5. Always pass the method's config object:

```python
from transformers import AutoModelForCausalLM, BitsAndBytesConfig

quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.bfloat16,
)
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8B-Instruct",
    quantization_config=quantization_config,
    device_map="auto",
)
```

## Two usage patterns

| You have | What you do |
|---|---|
| Full-precision checkpoint | Pass the method's config to `quantization_config`; weights are quantized as they load |
| Already-quantized checkpoint | Call `from_pretrained` with no quantization config — the method is read from the checkpoint's `config.json` (or from the named GGUF file) |

Only a few methods (AWQ, AutoRound, AQLM, compressed-tensors, GGUF) can only be loaded from an already-quantized checkpoint — quantize first with the method's own library, then load here.

## Load a pre-quantized checkpoint

```python
model = AutoModelForCausalLM.from_pretrained("TheBloke/zephyr-7B-alpha-AWQ", device_map="auto")
print(model.config.quantization_config.quant_method)
```

Install the library the method depends on before loading. To tweak loading options (e.g. kernel backend), pass a config of the same type — its options are merged with the checkpoint's.

## GGUF

```python
model = AutoModelForCausalLM.from_pretrained(
    "unsloth/Qwen3.5-4B-GGUF",
    gguf_file="Qwen3.5-4B-Q4_K_M.gguf",
)
```

## Backends

Method pages under `docs/source/en/quantization/` (each lists installation and config class):

- **bitsandbytes** — 4-bit/8-bit; the default quick start (`BitsAndBytesConfig`)
- **GPTQ** — calibrates on a dataset while the model loads (the only method that needs a calibration dataset at load time)
- **AWQ**, **AutoRound**, **AQLM**, **SPQR**, **VPTQ**, **HQQ**, **Quark**, **Quanto**, **torchao**
- **FP8 family** — FBGEMM FP8, fine-grained FP8, NVFP4, MXFP4
- **compressed-tensors**, **GGUF**, **BitNet**, **SInQ**, **Higgs**, **4over6** (`fouroversix`), **EETQ**, **Metal**
- Plus guides: `concept_guide.md`, `selecting.md`, `finetune.md` (fine-tuning quantized models), `save.md` (saving quantized models), `dequantize.md`, `compile.md`, `skip_modules.md`, `optimum.md`

## Fine-tuning quantized models

See `quantization/finetune.md` — quantized models can be fine-tuned (e.g. QLoRA-style workflows) with method-specific notes on what stays frozen.
