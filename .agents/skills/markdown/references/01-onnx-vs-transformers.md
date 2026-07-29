# ONNX Runtime vs Transformers (PyTorch) — Docling Analysis

## Key Finding: ONNX export exists for granite-docling-258M!

**Repo:** [onnx-community/granite-docling-258M-ONNX](https://huggingface.co/onnx-community/granite-docling-258M-ONNX)

However, **docling does not support loading ONNX VLM models** — its VLM pipeline only supports `transformers` (PyTorch), `mlx`, and `vllm` inference frameworks. The ONNX model would need custom integration.

## Model Size Comparison

### PyTorch (Transformers)
| Component | File | Size |
|-----------|------|------|
| Full model | `model.safetensors` | **515 MB** |
| **Total** | | **515 MB** |

### ONNX Runtime (multiple quantization levels)
| Variant | Vision Encoder | Embed Tokens | Decoder | **Total** |
|---------|---------------|-----------------------|---------|----------|
| FP32 (full) | 374 MB | 231 MB | 658 MB | **1.26 GB** |
| FP16 | 187 MB | 116 MB | 329 MB | **632 MB** |
| Int8 / Quantized | 94 MB | 58 MB | 166 MB | **318 MB** |
| Q4 | 64 MB | 231 MB | 105 MB | **400 MB** |
| **Q4F16** ⭐ | **55 MB** | **116 MB** | **93 MB** | **~264 MB** |
| BNB4 (vision only) | 58 MB | — | — | partial |

**Winner for size:** ONNX Q4F16 at **~264 MB** vs PyTorch at **515 MB** (49% smaller)
**Winner for quality:** PyTorch FP32 or ONNX FP16 (Q4 may lose quality)

## Performance Characteristics

### ONNX Runtime
| Aspect | Detail |
|--------|--------|
| **CPU inference** | Highly optimized (AVX, AVX2, AVX-512), often 2-5x faster than PyTorch on CPU |
| **Memory** | Lower RAM footprint, no PyTorch overhead |
| **GPU** | CUDA execution provider available, but less mature than PyTorch CUDA |
| **Startup** | Faster model loading (no PyTorch init) |
| **Limitation** | Docling VLM pipeline does **not** support ONNX models yet |

### Transformers (PyTorch)
| Aspect | Detail |
|--------|--------|
| **CPU inference** | Slower, general-purpose |
| **GPU inference** | Mature CUDA support, often faster than ONNX CUDA |
| **Memory** | Higher (PyTorch overhead + model) |
| **Startup** | Slower (PyTorch init + model loading) |
| **Integration** | Native support in docling VLM pipeline |

## Pipeline Architecture Comparison

### Standard Pipeline (`--pipeline standard`)
Uses **ONNX Runtime** for layout detection and image classification:
- Layout: `docling-layout-heron-onnx` (171 MB ONNX)
- OCR: RapidOCR (ONNX Runtime) or Tesseract
- Table: TableFormer (PyTorch)
- **Already uses ONNX where it makes sense**

### VLM Pipeline (`--pipeline vlm --vlm-model granite_docling`)
Uses **PyTorch (Transformers)** only:
- Single model: `granite-docling-258M` (515 MB safetensors)
- Processes each page as image → doctags → markdown
- No ONNX option in docling currently

## Can We Use ONNX with Docling?

**Not directly.** Docling's VLM pipeline hardcodes `InferenceFramework.TRANSFORMERS`:

```python
# docling/datamodel/vlm_model_specs.py
GRANITEDOCLING_TRANSFORMERS = InlineVlmOptions(
    repo_id="ibm-granite/granite-docling-258M",
    inference_framework=InferenceFramework.TRANSFORMERS,  # Only option
    ...
)
```

`InferenceFramework` enum: `MLX`, `TRANSFORMERS`, `VLLM` — **no ONNX**.

### Workaround: Custom ONNX integration
To use the ONNX model, we'd need to:
1. Download `onnx-community/granite-docling-258M-ONNX` (Q4F16 variant: ~264 MB)
2. Implement the generation loop (vision encode → embed → decode loop) using `onnxruntime`
3. Parse doctag output into markdown
4. Bypass docling's VLM pipeline entirely

This is non-trivial but feasible. The ONNX Runtime Python example from the model card shows the pattern.

## Recommendations for markdown.sh

### Option A: Use docling as-is (current approach)
```bash
# Standard pipeline — fast, ONNX for layout, no OCR
uvx --from docling docling convert --pipeline standard --no-ocr --to md ...

# VLM pipeline — PyTorch, full page understanding
uvx --from docling docling convert --pipeline vlm --vlm-model granite_docling --to md ...
```

### Option B: Custom ONNX path (future)
If we implement ONNX support directly in markdown.sh:
- ~264 MB model download (Q4F16) vs 515 MB (PyTorch)
- Faster CPU inference
- No PyTorch dependency (just onnxruntime + transformers for processor)
- More complex code, maintained separately from docling

### Option C: Hybrid (recommended for now)
| Scenario | Pipeline | Reason |
|----------|----------|--------|
| Text-layer PDF | Standard + `--no-ocr` | Fast, ONNX layout, extracts text/tables |
| Mixed (text + scanned) | Standard + `--ocr --ocr-engine rapidocr` | ONNX OCR for scanned pages |
| Scanned PDF, best quality | VLM + granite_docling | Full visual understanding (PyTorch) |
| CPU-only, speed critical | Standard + ONNX models | ONNX Runtime is CPU-optimized |
| GPU available | VLM + granite_docling | PyTorch CUDA |

## Summary

| Metric | PyTorch (Transformers) | ONNX Runtime (Q4F16) |
|--------|------------------------|---------------------|
| Model size | 515 MB | ~264 MB |
| CPU speed | Baseline | ~2-5x faster |
| GPU speed | Fast (mature CUDA) | OK (less mature) |
| RAM usage | ~1-2 GB | ~0.5-1 GB |
| Docling support | ✅ Native | ❌ Not supported |
| Quality | Full precision | Q4 quantized (minor loss) |
| Setup complexity | `uvx --from docling` | Custom ONNX code needed |

**Bottom line:** ONNX is clearly better for size and CPU performance, but docling doesn't support it for VLM yet. For now, use standard pipeline (which already uses ONNX for layout) for text-layer PDFs, and VLM pipeline (PyTorch) only when full visual understanding is needed.
