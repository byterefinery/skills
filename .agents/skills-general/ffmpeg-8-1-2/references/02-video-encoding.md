# Video Encoding

## libx264 (H.264/AVC)

Most widely compatible video codec. Requires `--enable-libx264` at build time.

### CRF Mode (Recommended)

```bash
# Quality-based encoding (most common)
ffmpeg -i input.mp4 -c:v libx264 -crf 23 -preset medium output.mp4

# CRF range: 0 (lossless) to 51 (worst quality)
# Default: 23. Typical range: 18-28.
# Lower = better quality, larger file
```

### Presets (Speed vs Quality)

From fastest to slowest: `ultrafast`, `superfast`, `veryfast`, `faster`, `fast`, `medium` (default), `slow`, `slower`, `veryslow`, `placebo`.

```bash
# Fast encoding (good for real-time)
ffmpeg -i input.mp4 -c:v libx264 -crf 23 -preset veryfast output.mp4

# High quality (slower)
ffmpeg -i input.mp4 -c:v libx264 -crf 23 -preset slow output.mp4
```

### Tunes

```bash
# For grainy film content
-c:v libx264 -crf 23 -tune film

# For screen capture
-c:v libx264 -crf 23 -tune stillimage

# For streaming
-c:v libx264 -crf 23 -tune zerolatency -preset veryfast

# Available: film, animation, grain, stillimage, psnr, ssim, fastdecode, zerolatency
```

### Bitrate Mode

```bash
# Constant bitrate (for streaming)
ffmpeg -i input.mp4 -c:v libx264 -b:v 5000k -maxrate 5000k -bufsize 10000k output.mp4

# Two-pass for strict bitrate control
ffmpeg -i input.mp4 -c:v libx264 -b:v 5000k -pass 1 -f null /dev/null
ffmpeg -i input.mp4 -c:v libx264 -b:v 5000k -pass 2 output.mp4
```

### Profiles and Levels

```bash
# Restrict to Baseline profile (max compatibility)
-c:v libx264 -profile:v baseline -level 3.0

# High profile (default, best quality)
-c:v libx264 -profile:v high -level 4.2

# Profiles: baseline, main, high, high10, high422, high444
```

### Pixel Format

```bash
# Standard (required for most players)
-c:v libx264 -pix_fmt yuv420p

# 10-bit HDR
-c:v libx264 -pix_fmt yuv420p10le -profile:v high10
```

### x264 Parameters

```bash
# Pass raw x264 options
-c:v libx264 -x264-params keyint=250:min-keyint=25:scenecut=40

# Common useful params
-c:v libx264 -x264-params deblock=-1:-1:psy-rd=1.0:0.0
```

## libx265 (H.265/HEVC)

~30-50% better compression than H.264 at same quality. Requires `--enable-libx265`.

```bash
# Basic HEVC encoding
ffmpeg -i input.mp4 -c:v libx265 -crf 28 -preset medium output.mp4

# 10-bit HEVC (recommended for HDR)
ffmpeg -i input.mp4 -c:v libx265 -crf 28 -pix_fmt yuv420p10le output.mp4

# CRF range: 0-51, default 28. Typical: 20-30.
# HEVC CRF values are ~5 higher than equivalent x264 values.
```

### Main Options

```bash
-c:v libx265 -crf 28 -preset medium -profile main
-c:v libx265 -crf 28 -preset slow -x265-params crf=28:psy-rd=1
```

## libsvtav1 (AV1 — SVT encoder)

Very fast AV1 encoder from Intel. Requires `--enable-libsvtav1`. Best speed/quality ratio for AV1.

```bash
# Basic SVT-AV1 encoding
ffmpeg -i input.mp4 -c:v libsvtav1 -crf 30 -preset 9 output.webm

# Preset range: 0 (slowest/best quality) to 13 (fastest)
# Typical: 6-10. Default: 9.
# CRF range: 0-63. Typical: 25-35.
```

### Options

```bash
# Quality-focused
-c:v libsvtav1 -crf 28 -preset 6

# Speed-focused
-c:v libsvtav1 -crf 35 -preset 12

# Bitrate mode
-c:v libsvtav1 -b:v 2M -maxrate 2M

# 10-bit
-c:v libsvtav1 -crf 30 -pix_fmt yuv420p10le
```

## libaom-av1 (AV1 — AOM reference encoder)

Reference AV1 encoder. Highest quality but slowest. Requires `--enable-libaom`.

```bash
# Basic AV1 encoding
ffmpeg -i input.mp4 -c:v libaom-av1 -crf 30 -cpu-used 4 output.webm

# cpu-used: 0 (slowest) to 8 (fastest). Default: 1.
# CRF range: 0-63. Typical: 20-40.
```

### Options

```bash
# Quality-focused (very slow)
-c:v libaom-av1 -crf 25 -cpu-used 0 -row-mt 1

# Balanced
-c:v libaom-av1 -crf 30 -cpu-used 4 -row-mt 1

# Adaptive quantization modes
-c:v libaom-av1 -aq-mode variance    # 0=none, 1=variance, 2=complexity, 3=cyclic

# Tune for SSIM
-c:v libaom-av1 -tune ssim
```

## libvpx-vp9 (VP9)

Google's VP9 encoder. Requires `--enable-libvpx`. Good for WebM.

```bash
# Basic VP9 encoding
ffmpeg -i input.mp4 -c:v libvpx-vp9 -b:v 1M output.webm

# Two-pass (recommended for VP9)
ffmpeg -i input.mp4 -c:v libvpx-vp9 -b:v 1M -pass 1 -f webm /dev/null
ffmpeg -i input.mp4 -c:v libvpx-vp9 -b:v 1M -pass 2 output.webm

# Real-time (one-pass with good quality)
-c:v libvpx-vp9 -b:v 1M -minrate 1M -maxrate 1M -deadline realtime
```

## NVENC (NVIDIA Hardware Encoding)

GPU-accelerated H.264/HEVC encoding on NVIDIA GPUs (Pascal+).

```bash
# H.264 NVENC
ffmpeg -i input.mp4 -c:v h264_nvenc -b:v 5M -preset p2 output.mp4

# HEVC NVENC
ffmpeg -i input.mp4 -c:v hevc_nvenc -b:v 5M -preset p2 output.mp4

# Presets (fast to slow): p1, p2, p3, p4, p5, p6, p7, p_lossless, p_lossless_slow, p_lossless_slower
# Quality presets: llhq, llhq_slow, hq, hq_slow, hdq, hdq_slow, bq, bq_slow
```

### NVENC Options

```bash
# CBR mode (for streaming)
-c:v h264_nvenc -b:v 6M -maxrate 6M -minrate 6M

# VBR mode
-c:v h264_nvenc -b:v 6M -maxrate 8M

# 10-bit (Turing+)
-c:v hevc_nvenc -pix_fmt p010le

# Two-pass (Ampere+)
-c:v h264_nvenc -b:v 5M -temporal-aq 1 -lookahead 20
```

## VAAPI (Intel/AMD Hardware)

Linux hardware acceleration via VAAPI.

```bash
# H.264 VAAPI encoding
ffmpeg -hwaccel vaapi -hwaccel_device /dev/dri/renderD128 -hwaccel_output_format vaapi \
  -i input.mp4 -c:v h264_vaapi -b:v 5M -vf 'format=nv12,hwupload' output.mp4

# HEVC VAAPI
ffmpeg -hwaccel vaapi -hwaccel_device /dev/dri/renderD128 -hwaccel_output_format vaapi \
  -i input.mp4 -c:v hevc_vaapi -b:v 5M -vf 'format=nv12,hwupload' output.mp4

# Rate control
-c:v h264_vaapi -cq 22                    # Constant quality
-c:v h264_vaapi -b:v 5M -maxrate 5M       # CBR
```

## QSV (Intel Quick Sync Video)

Intel integrated GPU encoding (Linux via VAAPI, Windows via DXVA/D3D11).

```bash
# H.264 QSV
ffmpeg -i input.mp4 -c:v h264_qsv -b:v 5M -preset medium output.mp4

# HEVC QSV
ffmpeg -i input.mp4 -c:v hevc_qsv -b:v 5M output.mp4

# Rate control
-c:v h264_qsv -global_quality 23          # Quality-based
-c:v h264_qsv -b:v 5M -maxrate 5M         # CBR

# Presets: veryfast, faster, fast, medium, slow, slower, veryslow
```

## Common Encoding Patterns

### YouTube upload (H.264, high quality)

```bash
ffmpeg -i input.mp4 -c:v libx264 -crf 18 -preset slow \
  -c:a libopus -b:a 128k -pix_fmt yuv420p output.mp4
```

### Web delivery (AV1, small size)

```bash
ffmpeg -i input.mp4 -c:v libsvtav1 -crf 30 -preset 9 \
  -c:a libopus -b:a 96k output.webm
```

### Maximum compatibility (H.264 Baseline)

```bash
ffmpeg -i input.mp4 -c:v libx264 -crf 23 -profile:v baseline -level 3.0 \
  -pix_fmt yuv420p -c:a aac -ar 44100 -ac 2 output.mp4
```

### HDR to SDR conversion

```bash
ffmpeg -i hdr_input.mp4 -c:v libx264 -crf 23 \
  -vf 'zscale=t=linear:npl=100,format=yuv444p,zscale=m=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:r=tv,format=yuv420p' \
  output.mp4
```
