# ASR (Audio/Video)

Docling transcribes audio and video files using Whisper models, producing `DoclingDocument` output with paragraph-level timestamps. Audio/video input requires the `audio` or `asr` extra; video additionally needs `ffmpeg` on PATH.

## Installation

```bash
pip install "docling[asr]"        # all inline ASR engines (Whisper, Transformers, mlx-audio)
# macOS Apple Silicon: asr extra needs macOS 14+
```

## Audio transcription

### Basic usage

```python
from pathlib import Path
from docling.datamodel import asr_model_specs
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import AsrPipelineOptions
from docling.document_converter import AudioFormatOption, DocumentConverter
from docling.pipeline.asr_pipeline import AsrPipeline

pipeline_options = AsrPipelineOptions()
pipeline_options.asr_options = asr_model_specs.WHISPER_TURBO

converter = DocumentConverter(
    format_options={
        InputFormat.AUDIO: AudioFormatOption(
            pipeline_cls=AsrPipeline,
            pipeline_options=pipeline_options,
        )
    }
)
result = converter.convert(Path("recording.mp3"))
doc = result.document
print(doc.export_to_markdown())
```

### Supported audio formats

WAV, MP3, M4A, AAC, OGG, FLAC.

### Export formats

`export_to_markdown()` (with timestamps), `export_to_dict()`, `export_to_html()`, `export_to_doctags()`, and `save_as_vtt("out.vtt")` for WebVTT subtitles.

## Whisper model selection

Presets live in `docling.datamodel.asr_model_specs`. Auto-selecting presets pick the best backend for your hardware (MLX on Apple Silicon, native elsewhere):

```python
pipeline_options.asr_options = asr_model_specs.WHISPER_TINY   # ... BASE/SMALL/MEDIUM/LARGE
pipeline_options.asr_options = asr_model_specs.WHISPER_TURBO  # recommended default
```

Force a backend with suffixes: `_NATIVE` (CPU/CUDA), `_MLX` (Apple Silicon), `_S2T` (CTranslate2, high throughput, not on Apple Silicon). The CLI `--asr-model` accepts the full preset list (run `docling models --asr`).

## Video processing

The video pipeline transcribes audio, samples representative frames, and optionally performs speaker diarization.

```python
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import VideoPipelineOptions
from docling.document_converter import DocumentConverter, VideoFormatOption

pipeline_options = VideoPipelineOptions(
    # frame_sampling_mode, scene_change_prominence, enable_diarization, ...
)
converter = DocumentConverter(
    format_options={InputFormat.VIDEO: VideoFormatOption(pipeline_options=pipeline_options)}
)
result = converter.convert(Path("meeting.mp4"))
```

Supported video formats: MP4, AVI, MOV, MKV, WEBM (audio track extracted and transcribed).

### Frame sampling modes (CLI)

| Flag | Default | Description |
|------|---------|-------------|
| `--video-sampling-mode` | `fixed` | `fixed` or `scene` |
| `--video-frame-interval` | `10.0` | Seconds between frames (fixed mode) |
| `--video-cuts-per-minute` | `0.0` | Target cuts/min in scene mode |
| `--video-prominence` | `0.0` (auto) | Scene-change sensitivity; 0 = auto-adapting (recommended) |
| `--video-diarization` | disabled | Speaker diarization (requires resemblyzer) |

Diarization is silently skipped if dependencies are missing — transcription and frame sampling still work.

## CLI usage

```bash
docling --to md recording.mp3                                    # default ASR model whisper_tiny
docling --to md --asr-model whisper_turbo recording.mp3
docling --to md --video-sampling-mode scene --video-prominence 0.03 video.mp4
docling --to md --video-diarization video.mp4
```

## Limitations

- No SRT output — use WebVTT via `save_as_vtt()` or an external tool for SRT
- Paragraph-level timestamps only (no word-level)
- Audio-only has no diarization — use the video pipeline for speaker attribution
- WhisperS2T not available on Apple Silicon — use MLX or native backends on M-series Macs
