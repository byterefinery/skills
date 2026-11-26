# CLI Reference

From `docs/reference/cli.md` (generated from the live Typer apps). Verify with `docling --help`.

## `docling` command

Subcommands:

- `docling convert` — convert locally
- `docling convert-remote` — convert via a remote docling-serve service
- `docling models` — list VLM and ASR models and their backends (`--vlm`, `--asr`)
- `docling options` — show KEY=VALUE options an engine accepts

## `docling convert` key options

```text
docling convert [OPTIONS] source     # source: local path / directory / URL
```

Input/output:

- `--from` (repeatable) — input formats to accept; defaults to all
- `--to` (repeatable) — output formats: `md`, `json`, `yaml`, `html`, `html_split_page`, `text`, `doctags`, `vtt`, `doclang`, `dclx`, `chunks`, `latex`. Default Markdown.
- `--chunks-type` (`hybrid`|`hierarchical`, default hybrid), `--chunks-max-tokens`, `--chunks-tokenizer` (default `sentence-transformers/all-MiniLM-L6-v2`)

Pipeline and models:

- `--pipeline` — `legacy`|`standard`|`native`|`vlm`|`asr` (default standard, or vlm when `--vlm-model` given)
- `--vlm-model` — VLM preset (selects the vlm pipeline; default `granite_docling`)
- `--vlm-max-new-tokens`, `--trust-remote-code`, `--debug-vlm-native-output`
- `--asr-model` — ASR preset (default `whisper_tiny`); run `docling models --asr` to list
- `--asr-language`, `--asr-timestamps`/`--no-asr-timestamps`, `--asr-speakers`/`--no-asr-speakers`

OCR:

- `--ocr`/`--no-ocr` (default true), `--ocr-mode` (`full_page`|`layout_regions`|`pdf_aware_layout_regions`|`default`)
- `--force-ocr` — **deprecated**, use `--ocr-mode full_page`
- `--replace-broken-text-layer` — replace a page's text with OCR when its text layer is broken
- `--ocr-engine` (auto, easyocr, kserve_v2_ocr, nemotron-ocr, ocrmac, rapidocr, tesserocr, tesseract)
- `--ocr-option` (repeatable) — set an engine option, e.g. `--ocr-option model_size=tiny`

Tables / structure:

- `--tables`/`--no-tables` (default true), `--table-structure-engine`, `--layout-engine`
- `--extract-form-fields` — AcroForm widgets to fillable fields (standard/legacy, docling-parse backend)
- `--reading-order-separators` (default true), `--heading-hierarchy` (infer section-header levels; standard/legacy only)

Images and output:

- `--image-export-mode` (`placeholder`|`embedded`|`referenced`, default embedded)
- `--html-image-fetch` (`none`|`local`|`remote`|`all`), `--headers`, `--html-image-headers`
- `--show-layout` — draw bounding boxes on page images

Video:

- `--video-sampling-mode` (`fixed`|`scene`), `--video-frame-interval` (10.0), `--video-cuts-per-minute`, `--video-prominence` (0=auto), `--video-diarization`

Misc:

- `--artifacts-path` — local model path (offline)
- `--enable-remote-services`, `--allow-external-plugins`, `--show-external-plugins`

## `docling-tools models download`

Prefetch models for offline use into `$HOME/.cache/docling/models`:

```bash
docling-tools models download                    # default set
docling-tools models download easyocr --easyocr-lang iso:zh-Hans --easyocr-lang ja
docling-tools models download whisper_tiny --output-dir /models
docling-tools models download --all --asr --output-dir /models   # includes native Whisper sizes
docling-tools models download-hf-repo ds4sd/SmolDocling-256M-preview
```

`--all` does not include ASR models by default; add `--asr`. Use the downloaded dir via `--artifacts-path` or `DOCLING_ARTIFACTS_PATH`.
