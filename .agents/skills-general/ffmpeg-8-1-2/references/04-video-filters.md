# Video Filters

FFmpeg has 500+ video filters. This reference covers the most commonly used ones.

## Filtergraph Syntax

### Simple Filtergraph (`-vf` / `-filter:v`)

Single input, single output, applied to one stream:

```bash
ffmpeg -i input.mp4 -vf "scale=1280:720,fps=30" output.mp4
```

### Complex Filtergraph (`-filter_complex`)

Multiple inputs/outputs. Use labels `[name]` for stream references:

```bash
ffmpeg -i bg.mp4 -i fg.mp4 -filter_complex \
  "[0:v][1:v]overlay=10:10[out]" \
  -map "[out]" output.mp4
```

### Label Conventions

- `[0:v]` — video stream from first input
- `[0:a]` — audio stream from first input
- `[0:v:1]` — second video stream from first input
- `[out]` — custom label for filter output
- Unlabeled outputs auto-map to first output file

## scale

Resize video. Most fundamental filter.

```bash
# Exact dimensions
-vf "scale=1280:720"

# Maintain aspect ratio (use -1 for auto)
-vf "scale=1280:-1"
-vf "scale=-1:720"

# Expression-based
-vf "scale=trunc(iw*0.5/2)*2:trunc(ih*0.5/2)*2"

# Maintain aspect ratio, divisible by 2
-vf "scale=iw/2:-2"

# Max dimensions (fit within)
-vf "scale=min(1280,iw):min(720,ih)"

# Force even dimensions (required by many encoders)
-vf "scale=trunc(iw/2)*2:trunc(ih/2)*2"

# With scaling algorithm
-vf "scale=1280:720:flags=lanczos"
# flags: fast_bilinear, bilinear, bicubic, nearest, area, bicublin, gauss, sinc, lanczos, spline
```

## fps

Change frame rate.

```bash
# Fixed frame rate
-vf "fps=30"
-vf "fps=24000/1001"    # 23.976 fps
-vf "fps=60"

# Round mode
-vf "fps=30:round=init"  # Default: round to nearest
-vf "fps=30:round=down"  # Drop frames
-vf "fps=30:round=up"    # Duplicate frames
```

## concat

Join video segments end-to-end. All segments must have same codec, resolution, and frame rate.

```bash
# Using concat filter (re-encodes)
ffmpeg -i a.mp4 -i b.mp4 -i c.mp4 -filter_complex \
  "[0:v][0:a][1:v][1:a][2:v][2:a]concat=n=3:v=1:a=1[outv][outa]" \
  -map "[outv]" -map "[outa]" output.mp4

# Using concat demuxer (streamcopy, fastest)
# Create file list.txt:
#   file 'a.mp4'
#   file 'b.mp4'
#   file 'c.mp4'
ffmpeg -f concat -safe 0 -i list.txt -c copy output.mp4

# Unsafe mode (allow different formats)
-filter_complex "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1:unsafe=1[v][a]"
```

## overlay

Place one video on top of another.

```bash
# Fixed position
ffmpeg -i bg.mp4 -i logo.png -filter_complex \
  "[0:v][1:v]overlay=10:10" output.mp4

# Bottom-right corner
-filter_complex "[0:v][1:v]overlay=W-w+10:H-h-10"
# W, H = background dimensions; w, h = overlay dimensions

# Centered
-filter_complex "[0:v][1:v]overlay=(W-w)/2:(H-h)/2"

# With transparency (PNG)
-filter_complex "[0:v][1:v]overlay=10:10:format=auto"

# Time-range overlay (show from 5s to 10s)
-filter_complex "[1:v]trim=start=5:end=10,setpts=PTS-PTS_START[logo];[0:v][logo]overlay=10:10"
```

## crop

Crop a region from the video.

```bash
# Crop from center
-vf "crop=640:480"              # Center crop to 640x480
-vf "crop=640:480:100:50"      # Crop 640x480 from position (100, 50)

# Crop with expressions
-vf "crop=iw*0.8:ih*0.8:(iw-iw*0.8)/2:(ih-ih*0.8)/2"

# Auto-detect crop area (remove black bars)
-vf "cropdetect"               # Run to find values, then use crop with detected values
-vf "crop=1280:680:0:40"       # Apply detected crop
```

## trim

Trim video to a time range.

```bash
# By start and duration
-vf "trim=start=5:duration=10,setpts=PTS-PTS_START"

# By start and end
-vf "trim=start=5:end=15,setpts=PTS-PTS_START"

# Always pair with setpts to reset timestamps
```

## drawtext

Render text on video.

```bash
# Basic text
-vf "drawtext=text='Hello World':fontfile=/path/to/font.ttf:fontsize=48:fontcolor=white:x=10:y=10"

# Centered text with shadow
-vf "drawtext=text='Title':fontfile=DejaVuSans.ttf:fontsize=64:fontcolor=white:\
bordercolor=black:borderw=2:x=(w-text_w)/2:y=(h-text_h)/2"

# Timestamp
-vf "drawtext=fontsize=36:fontcolor=white:timecode='00\:00\:00\:00':\
r=24:x=(w-tw)/2:y=h-th-10:box=1:boxcolor=0x00000000@0.5"

# Dynamic text from metadata
-vf "drawtext=text='%{metadata\:title}':fontsize=24:fontcolor=white:x=10:y=10"

# Key options
# text=        Text to render (escape with \ or use textfile=)
# textfile=    Path to file containing text
# fontfile=    Path to font file
# fontsize=    Font size in pixels
# fontcolor=   Text color (name or #RRGGBB or 0xRRGGBBAA)
# x=, y=       Position expressions
# box=1        Draw background box
# boxcolor=    Box color
# shadowx=, shadowy=  Text shadow offset
# alpha=       Text opacity (0-1)
```

## hstack / vstack

Stack videos horizontally or vertically.

```bash
# Side by side (same height required)
ffmpeg -i left.mp4 -i right.mp4 -filter_complex \
  "[0:v]scale=640:360[l];[1:v]scale=640:360[r];[l][r]hstack=inputs=2" output.mp4

# One on top of another (same width required)
ffmpeg -i top.mp4 -i bottom.mp4 -filter_complex \
  "[0:v]scale=640:360[t];[1:v]scale=640:360[b];[t][b]vstack=inputs=2" output.mp4

# Multiple inputs
-filter_complex "[0:v][1:v][2:v][3:v]hstack=inputs=4"
```

## transpose / rotate

Rotate and flip video.

```bash
# Transpose (90° rotations)
-vf "transpose=1"              # Clockwise 90°
-vf "transpose=2"              # Counter-clockwise 90°
-vf "transpose=1,transpose=1"  # 180°

# Arbitrary rotation
-vf "rotate=PI/4"              # 45° rotation
-vf "rotate=PI/2*mod(t,2)"     # Oscillating rotation

# Flip
-vf "hflip"                    # Horizontal flip
-vf "vflip"                    # Vertical flip
```

## eq / curves / colorbalance

Color adjustment.

```bash
# eq — brightness, contrast, saturation, gamma
-vf "eq=brightness=0.1:contrast=1.2:saturation=1.5"
-vf "eq=brightness=-0.05:contrast=1.1:saturation=0.8:gamma=1.2"

# curves — RGB curves (like Photoshop)
-vf "curves=rgb_in='0/255 128/140 255/255':rgb_out='0/255 128/128 255/255'"

# colorbalance — shadows, midtones, highlights
-vf "colorbalance=shad_r=0.8:mid_g=1.1:high_b=0.9"

# hue — hue rotation
-vf "hue=s=0"                  # Desaturate (grayscale)
-vf "hue=h=90"                 # Rotate hue by 90°
```

## format / colorspace

Pixel format and color space conversion.

```bash
# Force pixel format
-vf "format=yuv420p"
-vf "format=nv12"              # For hardware encoding

# Color space conversion (HDR to SDR)
-vf "zscale=t=linear:npl=100,format=yuv444p,zscale=m=bt709,\
tonemap=tonemap=hable:desat=0,zscale=t=bt709:r=tv,format=yuv420p"

# Rec.709 to Rec.601
-vf "colorspace=bt709:alt_transfer=iec61966:all_range=1:\
ows=ntsc:ost=470bg:range=tv:ofs=bt601:ot=601:all_range=0"
```

## palettegen / paletteuse

Create high-quality GIFs using a two-pass palette approach.

```bash
# Pass 1: generate palette
ffmpeg -i input.mp4 -vf "fps=15,scale=480:-1:flags=lanczos,palettegen" palette.png

# Pass 2: apply palette
ffmpeg -i input.mp4 -i palette.png -filter_complex \
  "fps=15,scale=480:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=5" \
  output.gif

# With transparency
ffmpeg -i input.mp4 -vf "fps=15,scale=480:-1:flags=lanczos,palettegen=reserve_transparent=1" palette.png
ffmpeg -i input.mp4 -i palette.png -filter_complex \
  "fps=15,scale=480:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:diff_mode=expression" \
  output.gif
```

## select

Select specific frames.

```bash
# Extract frames at specific rate (for thumbnails)
-vf "select='eq(on\,0)',showinfo"

# Extract every 300th frame
-vf "select='not(mod(n\,300))'"

# Extract frame at specific time
-vf "select='gte(t\,10)*lte(t\,10.01)'"
```

## Other Useful Filters

```bash
# deband (remove color banding)
-vf "deband=range=16:iter=3"

# gradfun (gradual debanding)
-vf "gradfun=radius=12:strength=1.0"

# unsharp (sharpen or blur)
-vf "unsharp=5:5:1.0:5:5:0.0"      # Sharpen
-vf "unsharp=7:7:1.0:7:7:1.0"      # Blur

# gblur (Gaussian blur)
-vf "gblur=sigma=2"

# yadif (deinterlace)
-vf "yadif=0:0:0"

# fieldorder (change field order)
-vf "fieldorder=tff"               # Top field first
-vf "fieldorder=bff"               # Bottom field first

# setpts (adjust video timestamps)
-vf "setpts=2.0*PTS"              # Slow down to 50%
-vf "setpts=0.5*PTS"              # Speed up to 200%

# copy (pass through, useful in filter graphs)
-vf "copy"

# null (pass through unchanged)
-vf "null"

# split (duplicate stream for multiple outputs)
-filter_complex "[0:v]split=2[v1][v2]"

# drawbox (draw a rectangle)
-vf "drawbox=x=10:y=10:w=200:h=100:color=red@0.5:t=fill"

# fifo (buffer for variable-rate filters)
-vf "fifo"

# loop (repeat frames)
-vf "loop=loop=100:size=300"       # Repeat 100 times, 300 frames

# movie (load external video as filter input)
-filter_complex "movie=overlay.png[ov];[0:v][ov]overlay=10:10"

# amovie (load external audio as filter input)
-filter_complex "amovie=bgm.mp3[bg];[0:a][bg]amix=duration=shortest"
```

## Filtergraph Patterns

### Picture-in-picture

```bash
ffmpeg -i main.mp4 -i pip.mp4 -filter_complex \
  "[1:v]scale=320:240[pip];[0:v][pip]overlay=W-w-10:10" \
  -c:a copy output.mp4
```

### Watermark with fade

```bash
ffmpeg -i input.mp4 -i watermark.png -filter_complex \
  "[1:v]fade=t=in:st=0:d=1,fade=t=out:st=9:d=1[wm];\
   [0:v][wm]overlay=10:10:format=auto" \
  output.mp4
```

### Multi-segment with transitions

```bash
ffmpeg -i a.mp4 -i b.mp4 -filter_complex \
  "[0:v]trim=0:5,setpts=PTS-PTS_START[a];\
   [1:v]trim=0:5,setpts=PTS-PTS_START[b];\
   [a][b]xfade=transition=fade:duration=1:offset=4.5[out]" \
  -map "[out]" output.mp4
```

### Speed change with audio pitch

```bash
# 2x speed, adjust audio tempo
ffmpeg -i input.mp4 -filter_complex \
  "[0:v]setpts=0.5*PTS[v];[0:a]atempo=2.0[a]" \
  -map "[v]" -map "[a]" output.mp4
```
