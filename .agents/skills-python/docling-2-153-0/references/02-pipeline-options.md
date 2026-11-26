# Pipeline options

Pipeline option classes live in `docling.datamodel.pipeline_options` and configure each pipeline's stages.

## PdfPipelineOptions (standard PDF/image pipeline)

Key fields:

- `do_ocr` — enable OCR on bitmap content
- `ocr_options` — the OCR engine options instance (`EasyOcrOptions`, `TesseractOcrOptions`, `TesseractCliOcrOptions`, `OcrMacOptions`, `RapidOcrOptions`)
- `artifacts_path` — path to prefetched model weights (offline use)
- `enable_remote_services` — opt-in for remote/API engines (default False; raises `OperationNotAllowed()` otherwise)
- `do_code_enrichment`, `do_formula_enrichment`, `do_picture_classification`, `do_picture_description`, `do_chart_extraction` — enrichment toggles (see enrichments reference)
- `generate_picture_images` — required before picture classification/description
- `images_scale` — picture resolution scale factor (default 1)
- `accelerator_options` — CPU/GPU/threads selection

```python
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, TesseractOcrOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = True
pipeline_options.ocr_options = TesseractOcrOptions()

converter = DocumentConverter(
    format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
)
```

The CLI flags `--layout-engine`, `--table-structure-engine`, and `--ocr-engine` select engines; without `--allow-external-plugins` the built-in values are limited (e.g. OCR: auto, easyocr, kserve_v2_ocr, nemotron-ocr, ocrmac, rapidocr, tesserocr, tesseract).

## VlmPipelineOptions (VLM pipeline)

Configure via `vlm_options`, which can be a preset from `docling.datamodel.vlm_model_specs` or an inline/API options object:

```python
from docling.datamodel.pipeline_options import VlmPipelineOptions
from docling.datamodel import vlm_model_specs

pipeline_options = VlmPipelineOptions(
    vlm_options=vlm_model_specs.GRANITEDOCLING_TRANSFORMERS,
)
```

Remote inference sets `enable_remote_services=True` and passes a URL/params dict. See the VLM pipeline reference for full details.

## AsrPipelineOptions (audio/video)

Set `asr_options` to a preset from `docling.datamodel.asr_model_specs` (Whisper sizes, MLX/native/S2T variants):

```python
from docling.datamodel import asr_model_specs
from docling.datamodel.pipeline_options import AsrPipelineOptions

pipeline_options = AsrPipelineOptions()
pipeline_options.asr_options = asr_model_specs.WHISPER_TURBO
```

`VideoPipelineOptions` adds frame sampling mode and diarization. See the ASR reference.

## Accelerator options

```python
from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions

accelerator_options = AcceleratorOptions(device=AcceleratorDevice.AUTO)  # or CUDA/MPS/XPU/CPU
```
