---
name: ffmpeg-8-1-2
description: FFmpeg 8.1.2 — universal media conversion framework. Use when the user needs to encode, decode, transcode, mux, demux, stream, filter, or convert audio/video/subtitle files. Covers ffmpeg CLI commands, ffprobe inspection, hardware acceleration (NVENC, VAAPI, QSV, VideoToolbox), codec selection (libx264, libx265, libaom-av1, libsvtav1, libvpx, AAC, Opus), filter graphs (scale, overlay, concat, drawtext, loudnorm, complex filtergraphs), stream mapping, format conversion, live streaming (RTMP, HLS, DASH), screen/device capturing, and all FFmpeg 8.1.2 features.
metadata:
  tags:
    - media
    - video
    - audio
    - encoding
    - transcoding
    - cli
---

# ffmpeg 8.1.2

FFmpeg is a complete, cross-platform solution for recording, converting, and streaming audio and video. Version 8.1.2 is part of the n8.1 release series, continuing the major version 8 line with bug fixes and improvements.

## Overview

- **Version**: 8.1.2 (n8.1.2 branch)
- **Architecture**: CLI tools (`ffmpeg`, `ffprobe`, `ffplay`) backed by libraries (`libavcodec`, `libavformat`, `libavfilter`, `libswscale`, `libswresample`, `libavutil`, `libavdevice`)
- **Pipeline model**: demuxer → decoder → filtergraph → encoder → muxer
- **Key strength**: 500+ filters, 200+ codecs, 100+ formats/protocols, hardware acceleration

### Pipeline Model

```
INPUT ──► demuxer ──► decoder ──► filtergraph ──► encoder ──► muxer ──► OUTPUT
          (split    (decompress  (transform    (compress   (combine
           container)  packets)    frames)      frames)      streams)
```

Streamcopy bypasses decoder + filtergraph + encoder: `ffmpeg -i input -c copy output`

### Quick Start

```bash
# Transcode video to H.264/MP4
ffmpeg -i input.mkv -c:v libx264 -crf 23 -c:a aac -b:a 128k output.mp4

# Streamcopy (recontainer only, no re-encoding)
ffmpeg -i input.mkv -c copy output.mp4

# Resize and change frame rate
ffmpeg -i input.mp4 -vf "scale=1280:720,fps=30" output.mp4

# Extract audio
ffmpeg -i input.mp4 -vn -c:a libopus -b:a 96k output.opus

# Concatenate files (same codec, same format)
ffmpeg -i concat:"a.mp4|b.mp4|c.mp4" -c copy output.mp4

# Probe file info (JSON)
ffprobe -v quiet -print_format json -show_format -show_streams input.mp4
```

## Usage

### Command Syntax

```
ffmpeg [global_options] {[input_file_options] -i input_url} ... {[output_file_options] output_url} ...
```

Options apply to the **next** file only. Global options (verbosity, hw devices) apply everywhere and should come first.

### Essential Options

| Option | Scope | Description |
|--------|-------|-------------|
| `-i url` | input | Input file URL |
| `-c[:spec] codec` | input/output | Codec name or `copy` for streamcopy |
| `-c:v`, `-c:a`, `-c:s` | output | Codec for all video/audio/subtitle streams |
| `-map spec` | output | Manual stream selection |
| `-f fmt` | input/output | Force format (demuxer/muxer) |
| `-t duration` | input/output | Limit duration |
| `-to position` | input/output | Stop at position |
| `-ss position` | input/output | Seek (before `-i`: fast seek; after: precise) |
| `-vf filtergraph` | output | Simple video filtergraph (alias: `-filter:v`) |
| `-af filtergraph` | output | Simple audio filtergraph (alias: `-filter:a`) |
| `-filter_complex graph` | output | Complex filtergraph (multiple inputs/outputs) |
| `-b:v`, `-b:a` | output | Bitrate for video/audio |
| `-r fps` | input/output | Frame rate |
| `-s WxH` | output | Video resolution |
| `-ar rate` | output | Audio sample rate |
| `-ac channels` | output | Audio channel count |
| `-vn`, `-an`, `-sn` | output | Disable video/audio/subtitle |
| `-y` | global | Overwrite output without asking |
| `-loglevel level` | global | Verbosity: `quiet`, `panic`, `fatal`, `error`, `warning`, `info`, `verbose`, `debug`, `trace` |
| `-threads n` | output | Thread count |
| `-progress url` | global | Machine-readable progress output |

### Stream Specifiers

Append `:spec` to options to target specific streams:

```bash
# All video streams
-c:v libx264

# Second audio stream
-c:a:1 libopus

# First video, second audio
-map 0:v:0 -map 0:a:1

# By stream index
-b:0 1M

# By metadata tag
-c:v:m:language=eng libx264

# Only usable streams
-c:u libx264
```

### ffprobe Basics

```bash
# Human-readable stream info
ffprobe input.mp4

# JSON output for scripting
ffprobe -v quiet -print_format json -show_format -show_streams input.mp4

# Compact key=value output
ffprobe -v quiet -of compact -show_entries stream=codec_name,width,height,r_frame_rate,duration input.mp4

# Extract duration only
ffprobe -v quiet -show_entries format=duration -of csv=p=0 input.mp4

# List available decoders/encoders/formats
ffmpeg -decoders | grep h264
ffmpeg -encoders | grep libx264
ffmpeg -formats | grep mp4
```

## Gotchas

- **Option ordering matters**: options apply to the **next** file only. `-c copy -i input.mp4 output.mp4` applies `-c copy` to the input, not the output. Put codec options **after** `-i` and **before** the output file.
- **`-ss` before vs after `-i`**: before `-i` uses fast (keyframe) seeking; after `-i` uses precise (frame-accurate) seeking but must decode from the start. For streamcopy, use `-ss` before `-i` and add `-noaccurate_seek` to avoid the extra segment.
- **Automatic stream selection**: without `-map`, ffmpeg picks one video (highest resolution), one audio (most channels), and possibly one subtitle. This often selects unexpected streams from multi-stream inputs. Always use explicit `-map` for production work.
- **`-c copy` is not always compatible**: codec/container mismatches (e.g., H.265 in MP4 without proper compatibility level, AAC in MKV with certain flags) cause failures. When streamcopy fails, transcode instead.
- **CRF is not bitrate**: `-crf` controls quality, not bitrate. Output file size varies with content complexity. Use `-b:v` for bitrate constraints (e.g., streaming platforms).
- **`-pix_fmt` matters**: many encoders require specific pixel formats. H.264 typically needs `yuv420p`; HEVC may need `yuv420p10le` for 10-bit. Add `-pix_fmt` explicitly when needed.
- **Filter graphs must balance**: complex filtergraphs with labeled outputs must map every label exactly once with `-map '[label]'`. Unlabeled outputs auto-map to the first output file.
- **`-preset` tradeoff**: slower presets (e.g., `veryslow`, `slow`) give better quality at same bitrate but take longer. Default is `medium`. For real-time use `veryfast` or `realtim`.
- **Audio sample rate**: always set `-ar` explicitly (e.g., 48000 for video, 44100 for music). Mismatched sample rates between streams cause sync issues.
- **Hardware encoding**: NVENC, QSV, VAAPI, VideoToolbox have different option names and quality characteristics. Not all features (B-frames, HDR, specific profiles) are available on all hardware.
- **Two-pass encoding**: requires running ffmpeg twice with `-pass 1` (output to `/dev/null`) and `-pass 2`. Only useful for strict CBR/VBR targets, not CRF mode.
- **Concat demuxer vs concat filter**: the concat demuxer (`-i concat:"a|b"`) is fast but requires identical codecs. The concat filter (`-filter_complex`) handles different codecs but requires re-encoding.
- **GIF animation**: use `palettegen` + `paletteuse` for quality GIFs. Direct encoding produces poor color. See references for the two-pass palette workflow.

## References

- [01-stream-selection-and-specifiers](references/01-stream-selection-and-specifiers.md) — -map syntax, stream specifiers, automatic vs manual selection
- [02-video-encoding](references/02-video-encoding.md) — libx264, libx265, libaom-av1, libsvtav1, NVENC, VAAPI encoding
- [03-audio-encoding](references/03-audio-encoding.md) — AAC, Opus, MP3, FLAC encoding and audio processing
- [04-video-filters](references/04-video-filters.md) — scale, overlay, concat, drawtext, fps, crop, color, palette
- [05-audio-filters](references/05-audio-filters.md) — loudnorm, aresample, volume, pan, amix, equalizer, tempo
- [06-formats-and-protocols](references/06-formats-and-protocols.md) — demuxers, muxers, protocols (HTTP, RTMP, file, pipe)
- [07-hardware-acceleration](references/07-hardware-acceleration.md) — VAAPI, CUDA, NVENC, QSV, VideoToolbox, device init
- [08-ffprobe](references/08-ffprobe.md) — ffprobe output formats, JSON parsing, stream inspection
- [09-bitstream-filters](references/09-bitstream-filters.md) — h264_mp4toannexb, extract_extradata, metadata BSFs
- [10-devices-and-capture](references/10-devices-and-capture.md) — v4l2, x11grab, dshow, avfoundation, ALSA, PulseAudio
- [11-common-workflows](references/11-common-workflows.md) — GIF creation, subtitles, HDR, two-pass, trimming, thumbnails
