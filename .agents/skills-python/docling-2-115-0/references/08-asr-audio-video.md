# ASR (Audio/Video)

Docling transcribes audio and video files using OpenAI Whisper models, producing `DoclingDocument` output with paragraph-level timestamps.

## Installation

```bash
# ASR pipeline (audio transcription)
pip install "docling[asr]"

# Video processing (transcription + frame sampling + diarization)
pip install "docling-slim[format-video]"
```

Requires `ffmpeg` on PATH.

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
# Output:
# [time: 0.0-4.0]  Title of the recording
# [time: 5.28-9.96]  First paragraph of transcript...
```

### Supported audio formats

WAV, MP3, M4A, AAC, OGG, FLAC

### Export formats

```python
doc.export_to_markdown()   # Markdown with timestamps
doc.export_to_dict()       # JSON-serializable
doc.export_to_html()       # HTML
doc.export_to_doctags()    # DocTags
doc.save_as_vtt("out.vtt") # WebVTT subtitles
```

## Whisper model selection

### Auto-selecting presets

These pick the best backend for your hardware automatically:

```python
from docling.datamodel import asr_model_specs

# Model sizes (auto-selects MLX on Apple Silicon, native elsewhere)
pipeline_options.asr_options = asr_model_specs.WHISPER_TINY
pipeline_options.asr_options = asr_model_specs.WHISPER_BASE
pipeline_options.asr_options = asr_model_specs.WHISPER_SMALL
pipeline_options.asr_options = asr_model_specs.WHISPER_MEDIUM
pipeline_options.asr_options = asr_model_specs.WHISPER_LARGE
pipeline_options.asr_options = asr_model_specs.WHISPER_TURBO  # recommended default
```

### Forcing a specific backend

```python
# Native Whisper (CPU/CUDA)
pipeline_options.asr_options = asr_model_specs.WHISPER_TURBO_NATIVE

# MLX Whisper (Apple Silicon)
pipeline_options.asr_options = asr_model_specs.WHISPER_TURBO_MLX

# WhisperS2T (CPU/CUDA, experimental, high throughput)
pipeline_options.asr_options = asr_model_specs.WHISPER_LARGE_V3_S2T
```

### WhisperS2T presets

High-throughput batched decoding via CTranslate2. Not available on Apple Silicon.

| Preset | Model | Multilingual? |
|--------|-------|---------------|
| `WHISPER_TINY_S2T` | tiny | yes |
| `WHISPER_TINY_EN_S2T` | tiny.en | English-only |
| `WHISPER_BASE_S2T` | base | yes |
| `WHISPER_SMALL_S2T` | small | yes |
| `WHISPER_MEDIUM_S2T` | medium | yes |
| `WHISPER_LARGE_V3_S2T` | large-v3 | yes |
| `WHISPER_DISTIL_LARGE_V3_S2T` | distil-large-v3 | English-only |
| `WHISPER_LARGE_V3_TURBO_S2T` | large-v3-turbo | yes (no translate) |

### Custom WhisperS2T options

```python
from docling.datamodel.pipeline_options_asr_model import (
    InferenceAsrFramework, InlineAsrWhisperS2TOptions
)

pipeline_options.asr_options = InlineAsrWhisperS2TOptions(
    repo_id="large-v3",
    inference_framework=InferenceAsrFramework.WHISPER_S2T,
    language="en",
    torch_dtype="float16",
    batch_size=8,     # higher = more throughput, more VRAM
    beam_size=1,      # 1 = greedy (fastest)
)
```

## Video processing

The `VideoPipeline` transcribes audio, samples representative frames, and optionally performs speaker diarization.

```python
from pathlib import Path
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import VideoPipelineOptions
from docling.document_converter import DocumentConverter, VideoFormatOption
from docling.utils.video_frame_sampling import VideoFrameSamplingMode

pipeline_options = VideoPipelineOptions(
    frame_sampling_mode=VideoFrameSamplingMode.SCENE_CHANGE,
    scene_change_prominence=0.03,  # for meetings
    enable_diarization=True,       # speaker attribution
)

converter = DocumentConverter(
    format_options={
        InputFormat.VIDEO: VideoFormatOption(pipeline_options=pipeline_options)
    }
)

result = converter.convert(Path("meeting.mp4"))
doc = result.document
print(doc.export_to_markdown())
```

### Supported video formats

MP4, AVI, MOV, MKV, WEBM

### Frame sampling modes

| Mode | Value | Behavior |
|------|-------|----------|
| Fixed interval | `FIXED_INTERVAL` (default) | One frame every N seconds |
| Scene change | `SCENE_CHANGE` | One frame per scene, picked for sharpness |

```python
# Fixed interval
pipeline_options.frame_sampling_mode = VideoFrameSamplingMode.FIXED_INTERVAL
pipeline_options.frame_interval_seconds = 10.0

# Scene change
pipeline_options.frame_sampling_mode = VideoFrameSamplingMode.SCENE_CHANGE
pipeline_options.scene_change_prominence = 0.03  # meetings
pipeline_options.cuts_per_minute = 2.0            # lectures
pipeline_options.max_sampled_frames = 100         # cap total frames
```

### Speaker diarization

```python
pipeline_options.enable_diarization = True
```

Requires `resemblyzer`, `soundfile`, `scikit-learn`, `librosa` (bundled in `format-video` extra). Auto-detects speaker count. Silently skipped if dependencies missing — transcription and frames still work.

## CLI usage

```bash
# Audio transcription
docling --to md recording.mp3

# With specific model
docling --to md --asr-model whisper_turbo recording.mp3
docling --to md --asr-model whisper_large_native recording.mp3
docling --to md --asr-model whisper_distil_large_v3_s2t recording.mp3

# Video with scene-change sampling
docling --to md --video-sampling-mode scene --video-prominence 0.03 video.mp4

# Video with diarization
docling --to md --video-sampling-mode scene --video-diarization video.mp4
```

| Flag | Default | Description |
|------|---------|-------------|
| `--asr-model` | `whisper_tiny` | ASR model preset |
| `--video-sampling-mode` | `fixed` | `fixed` or `scene` |
| `--video-frame-interval` | `10.0` | Seconds between frames |
| `--video-prominence` | `0.0` (auto) | Scene-change sensitivity |
| `--video-diarization` | disabled | Enable speaker diarization |

## Limitations

- **No SRT output** — use WebVTT via `doc.save_as_vtt()` or `openai-whisper` CLI for SRT
- **No word-level timestamps** — only paragraph-level timestamps available
- **Audio-only has no diarization** — use `VideoPipeline` for diarization, or `pyannote-audio` separately
- **WhisperS2T not on Apple Silicon** — use MLX or native backends on M-series Macs
