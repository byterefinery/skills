# Hardware Acceleration

## Overview

Hardware acceleration offloads encoding, decoding, and filtering to GPU/VPU. Three main approaches:

1. **Hardware decoding** — decode on GPU, process/encode on CPU or GPU
2. **Hardware encoding** — encode on GPU (NVENC, QSV, VAAPI, VideoToolbox)
3. **Hardware filtering** — apply filters on GPU (scale, overlay via VAAPI/CUDA)

## Device Initialization

```bash
# Initialize hardware device
-init_hw_device type[=name][:device]

# VAAPI (Intel/AMD on Linux)
-init_hw_device vaapi:/dev/dri/renderD128

# CUDA (NVIDIA)
-init_hw_device cuda:0

# QSV (Intel)
-init_hw_device qsv:hw

# VideoToolbox (macOS)
-init_hw_device videotoolbox:[]
```

## VAAPI (Linux — Intel/AMD)

### Hardware Decoding + CPU Encoding

```bash
# Decode on GPU, encode on CPU
ffmpeg -hwaccel vaapi -hwaccel_device /dev/dri/renderD128 \
  -hwaccel_output_format vaapi -i input.mp4 \
  -vf "format=nv12,hwupload" -c:v libx264 -crf 23 output.mp4
```

### Hardware Encoding (VAAPI)

```bash
# H.264 VAAPI encode
ffmpeg -hwaccel vaapi -hwaccel_device /dev/dri/renderD128 \
  -hwaccel_output_format vaapi -i input.mp4 \
  -vf "format=nv12,hwupload" -c:v h264_vaapi -b:v 5M output.mp4

# HEVC VAAPI encode
ffmpeg -hwaccel vaapi -hwaccel_device /dev/dri/renderD128 \
  -hwaccel_output_format vaapi -i input.mp4 \
  -vf "format=nv12,hwupload" -c:v hevc_vaapi -b:v 5M output.mp4

# Constant quality mode
-c:v h264_vaapi -cq 22 -qp 22

# CBR mode
-c:v h264_vaapi -b:v 5M -maxrate 5M
```

### VAAPI Filter Operations

```bash
# Hardware-accelerated scaling + encoding
ffmpeg -hwaccel vaapi -hwaccel_device /dev/dri/renderD128 \
  -hwaccel_output_format vaapi -i input.mp4 \
  -vf "scale_vaapi=1280:720,format=nv12,hwupload" \
  -c:v h264_vaapi -b:v 5M output.mp4

# Hardware overlay
ffmpeg -hwaccel vaapi -hwaccel_device /dev/dri/renderD128 \
  -hwaccel_output_format vaapi -i bg.mp4 -i logo.png \
  -vf "format=nv12,hwupload,overlay_vaapi=x=10:y=10" \
  -c:v h264_vaapi -b:v 5M output.mp4
```

## NVENC (NVIDIA — Linux/Windows)

### Hardware Encoding

```bash
# H.264 NVENC
ffmpeg -i input.mp4 -c:v h264_nvenc -b:v 5M -preset p2 output.mp4

# HEVC NVENC
ffmpeg -i input.mp4 -c:v hevc_nvenc -b:v 5M -preset p2 output.mp4

# AV1 NVENC (RTX 40-series+)
ffmpeg -i input.mp4 -c:v av1_nvenc -b:v 5M -preset p2 output.mkv
```

### NVENC Presets

| Preset | Speed | Quality |
|--------|-------|---------|
| `p1` | Fastest | Lowest |
| `p2` | — | — |
| `p3` | — | — |
| `p4` | — | — |
| `p5` | — | — |
| `p6` | — | — |
| `p7` | Slowest | Highest |
| `hq` | High quality | — |
| `hdq` | Higher quality | — |
| `bq` | Best quality | — |

### NVENC Options

```bash
# CBR (for streaming)
-c:v h264_nvenc -b:v 6M -maxrate 6M -minrate 6M

# VBR
-c:v h264_nvenc -b:v 6M -maxrate 8M

# 10-bit (Turing+)
-c:v hevc_nvenc -pix_fmt p010le

# Temporal AQ (Ampere+)
-c:v h264_nvenc -temporal-aq 1 -lookahead 20

# Two-pass (Ampere+)
-c:v h264_nvenc -b:v 5M -twopass 1

# Profile
-c:v h264_nvenc -profile high -level 4.2

# B-frames
-c:v h264_nvenc -bframes 8 -bf.strategy 1
```

### CUDA Decoding + NVENC Encoding

```bash
# Full GPU pipeline
ffmpeg -hwaccel cuda -hwaccel_output_format cuda -i input.mp4 \
  -vf "scale_cuda=1280:720" -c:v h264_nvenc -b:v 5M output.mp4

# With overlay
ffmpeg -hwaccel cuda -hwaccel_output_format cuda -i bg.mp4 -i fg.mp4 \
  -filter_complex "[0:v][1:v]overlay_cuda=x=10:y=10" \
  -c:v h264_nvenc -b:v 5M output.mp4
```

## QSV (Intel Quick Sync Video)

### Linux (via VAAPI)

```bash
# H.264 QSV
ffmpeg -i input.mp4 -c:v h264_qsv -b:v 5M -preset medium output.mp4

# HEVC QSV
ffmpeg -i input.mp4 -c:v hevc_qsv -b:v 5M output.mp4

# With explicit device
-init_hw_device qsv=hw:/dev/dri/renderD128

# Quality-based
-c:v h264_qsv -global_quality 23

# CBR
-c:v h264_qsv -b:v 5M -maxrate 5M
```

### Windows (via DXVA/D3D11)

```bash
# H.264 QSV on Windows
ffmpeg -init_hw_device dxva2 -i input.mp4 -c:v h264_qsv -b:v 5M output.mp4
```

### QSV Filter Operations

```bash
# Hardware scaling
-vf "scale_qsv=1280:720"

# Hardware deinterlacing
-vf "deinterlace_qsv"
```

## VideoToolbox (macOS)

```bash
# H.264 VideoToolbox
ffmpeg -i input.mp4 -c:v h264_videotoolbox -b:v 5M output.mp4

# HEVC VideoToolbox
ffmpeg -i input.mp4 -c:v hevc_videotoolbox -b:v 5M output.mp4

# With bitrate
-c:v h264_videotoolbox -b:v 5M -maxrate 6M

# Quality (macOS 12+)
-c:v h264_videotoolbox -videotoolbox_quality 2
# 0=fastest, 1=balanced (default), 2=highest quality
```

## Hardware Decoding

```bash
# VAAPI decode
ffmpeg -hwaccel vaapi -hwaccel_device /dev/dri/renderD128 -i input.mp4 -c copy output.mkv

# CUDA decode
ffmpeg -hwaccel cuda -i input.mp4 -c copy output.mkv

# QSV decode
ffmpeg -hwaccel qsv -i input.mp4 -c copy output.mkv

# VideoToolbox decode
ffmpeg -hwaccel videotoolbox -i input.mp4 -c copy output.mkv

# DXVA2 decode (Windows)
ffmpeg -hwaccel dxva2 -i input.mp4 -c copy output.mkv
```

## Hardware Transfer

```bash
# GPU to CPU (for CPU encoding)
-vf "hwdownload,format=nv12"

# CPU to GPU (for GPU encoding)
-vf "format=nv12,hwupload"

# GPU to GPU (different devices)
-vf "hwmap=derive_device=cuda"
```

## Common Patterns

### Live streaming with NVENC

```bash
ffmpeg -re -i input.mp4 \
  -c:v h264_nvenc -preset p2 -b:v 6M -maxrate 6M \
  -c:a aac -b:a 128k -ar 48000 \
  -f flv "rtmp://server/app/streamkey"
```

### Transcode with VAAPI (full GPU)

```bash
ffmpeg -hwaccel vaapi -hwaccel_device /dev/dri/renderD128 \
  -hwaccel_output_format vaapi -i input.mp4 \
  -vf "scale_vaapi=1920:1080,format=nv12,hwupload" \
  -c:v h264_vaapi -b:v 8M -c:a copy output.mp4
```

### GPU decode + CPU encode

```bash
ffmpeg -hwaccel vaapi -hwaccel_device /dev/dri/renderD128 \
  -hwaccel_output_format vaapi -i input.mp4 \
  -vf "hwdownload,format=yuv420p" \
  -c:v libx264 -crf 23 output.mp4
```

### Check available hardware

```bash
# List available hwaccels
ffmpeg -hwaccels

# List available devices
ffmpeg -init_hw_device help

# Check NVENC support
ffmpeg -encoders | grep nvenc

# Check VAAPI support
ffmpeg -encoders | grep vaapi
```

## Gotchas

- **Pixel format matters**: GPU encoders typically need `nv12` (VAAPI/QSV) or `p010le` (10-bit NVENC). Always use `format=nv12,hwupload` before GPU encoding.
- **Quality gap**: Hardware encoders (especially older ones) produce lower quality than software at same bitrate. Compensate with higher bitrate or use quality-based modes.
- **Feature support varies**: B-frames, HDR, specific profiles, and two-pass encoding depend on GPU generation. Check your GPU's capabilities.
- **Driver requirements**: VAAPI needs up-to-date Mesa drivers. NVENC needs NVIDIA drivers 450+. QSV needs Intel Media SDK or libvpl.
- **macOS limitations**: VideoToolbox has fewer options than other backends. No direct control over GOP, B-frames, or profiles in older macOS versions.
