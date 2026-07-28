# CLI Reference

## `docling` command

Convert documents from the command line.

```bash
docling [OPTIONS] source
```

### Arguments

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `source` | text | yes | File path, directory, or URL |

### Input format filtering

```bash
docling --from pdf --from docx input/          # only PDF and DOCX
docling --from pdf input/                      # only PDF
```

Available: `pdf`, `docx`, `pptx`, `xlsx`, `html`, `image`, `asciidoc`, `md`, `csv`, `xml_uspto`, `xml_jats`, `xml_xbrl`, `xml_doclang`, `json_docling`, `audio`, `vtt`, `latex`

### Output formats

```bash
docling --to md document.pdf                    # Markdown (default)
docling --to json document.pdf                  # JSON
docling --to html document.pdf                  # HTML
docling --to text document.pdf                  # Plain text
docling --to doctags document.pdf               # DocTags
docling --to doclang document.pdf               # DocLang XML
docling --to dclx document.pdf                  # DocLang archive
docling --to vtt recording.mp3                  # WebVTT

# Multiple outputs
docling --to md --to json document.pdf
```

### Pipeline selection

```bash
# Standard pipeline (default for PDF)
docling document.pdf

# VLM pipeline
docling --pipeline vlm document.pdf
docling --pipeline vlm --vlm-model granite_docling document.pdf
docling --pipeline vlm --vlm-model smoldocling document.pdf
docling --pipeline vlm --vlm-model pixtral document.pdf
docling --pipeline vlm --vlm-model phi4 document.pdf

# ASR pipeline (auto-selected for audio/video)
docling --asr-model whisper_turbo recording.mp3
```

### PDF options

```bash
# OCR
docling --ocr document.pdf                      # enable OCR
docling --no-ocr document.pdf                   # disable OCR
docling --force-ocr document.pdf                # replace all text with OCR

# Tables
docling --tables document.pdf                   # enable (default)
docling --no-tables document.pdf                # disable

# Enrichments
docling --enrich-code document.pdf
docling --enrich-formula document.pdf
docling --enrich-picture-classes document.pdf
docling --enrich-picture-description document.pdf
docling --enrich-chart-extraction document.pdf

# PDF backend
docling --pdf-backend docling_parse document.pdf   # default
docling --pdf-backend pypdfium2 document.pdf
docling --pdf-backend dlparse_v4 document.pdf

# PDF password
docling --pdf-password "secret" protected.pdf

# Table mode
docling --table-mode accurate document.pdf  # default
docling --table-mode fast document.pdf
```

### OCR options

```bash
docling --ocr --ocr-engine tesseract document.pdf
docling --ocr --ocr-engine easyocr document.pdf
docling --ocr --ocr-engine rapidocr document.pdf
docling --ocr --ocr-engine auto document.pdf        # default

# Language (engine-specific codes)
docling --ocr --ocr-lang eng,deu document.pdf

# Page segmentation mode (Tesseract)
docling --psm 6 document.pdf
```

### Device and performance

```bash
docling --device cuda document.pdf       # NVIDIA GPU
docling --device mps document.pdf        # Apple Silicon
docling --device cpu document.pdf        # CPU only
docling --num-threads 8 document.pdf     # CPU threads (default: 4)
docling --page-batch-size 16 document.pdf  # pages per batch (default: 4)
```

### Video options

```bash
docling --to md video.mp4                                    # default: fixed-interval sampling
docling --to md --video-sampling-mode scene video.mp4        # scene-change sampling
docling --to md --video-sampling-mode scene --video-prominence 0.03 video.mp4
docling --to md --video-diarization video.mp4                 # speaker diarization
docling --to md --video-frame-interval 5.0 video.mp4          # frame interval
```

### Remote services and plugins

```bash
docling --enable-remote-services document.pdf                 # allow remote API calls
docling --allow-external-plugins --ocr-engine my_plugin document.pdf
docling --show-external-plugins                               # list available plugins
```

### Debug and profiling

```bash
docling --show-layout document.pdf            # visualize bounding boxes
docling --debug-visualize-cells document.pdf
docling --debug-visualize-ocr document.pdf
docling --debug-visualize-layout document.pdf
docling --debug-visualize-tables document.pdf
docling --profiling document.pdf              # print profiling summary
docling --save-profiling document.pdf         # save profiling to JSON
docling -v document.pdf                       # info logging
docling -vv document.pdf                      # debug logging
```

### Output and error handling

```bash
docling --output ./results document.pdf       # output directory (default: .)
docling --abort-on-error input/               # stop on first error
docling --artifacts-path /local/models document.pdf  # offline model path
docling --document-timeout 300 document.pdf   # per-document timeout (seconds)
docling --headers '{"Authorization": "Bearer ..."}' https://url/to.pdf
```

### Image export mode

```bash
docling --image-export-mode embedded document.pdf    # base64 in output (default)
docling --image-export-mode referenced document.pdf  # separate PNG files
docling --image-export-mode placeholder document.pdf # position markers only
```

## `docling-tools` command

Utility commands for model management.

### Download models

```bash
# Download all default models
docling-tools models download

# Download specific models
docling-tools models download layout tableformer code_formula picture_classifier

# Download EasyOCR models for specific languages
docling-tools models download easyocr --easyocr-lang ch_sim --easyocr-lang ja

# Download arbitrary HuggingFace repo
docling-tools models download-hf-repo ds4sd/SmolDocling-256M-preview

# Custom output directory
docling-tools models download -o /local/path/to/models

# Force re-download
docling-tools models download --force

# All available models
docling-tools models download --all

# Quiet mode
docling-tools models download -q
```

Available model names: `layout`, `tableformer`, `tableformerv2`, `code_formula`, `picture_classifier`, `smolvlm`, `granitedocling`, `granitedocling_mlx`, `smoldocling`, `smoldocling_mlx`, `granite_vision`, `granite_chart_extraction`, `rapidocr`, `easyocr`

### Models path

Models are cached to `~/.cache/docling/models` by default. Override with:

```bash
export DOCLING_ARTIFACTS_PATH="/local/path/to/models"
docling --artifacts-path "/local/path/to/models" document.pdf
```
