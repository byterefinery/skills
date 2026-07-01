# Common Workflows

## GIF Creation

Two-pass palette method for quality GIFs (direct encoding produces poor color):

```bash
# Pass 1: generate palette
ffmpeg -i input.mp4 -ss 0 -t 5 -vf \
  "fps=15,scale=480:-1:flags=lanczos,palettegen" palette.png

# Pass 2: apply palette
ffmpeg -i input.mp4 -i palette.png -ss 0 -t 5 -filter_complex \
  "fps=15,scale=480:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=5" \
  output.gif

# With transparency (reserve last palette entry)
ffmpeg -i input.mp4 -vf "fps=15,scale=480:-1:flags=lanczos,palettegen=reserve_transparent=1" palette.png
ffmpeg -i input.mp4 -i palette.png -filter_complex \
  "fps=15,scale=480:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:diff_mode=expression" \
  output.gif

# Optimize with gifsicle (if available)
gifsicle -O3 output.gif > optimized.gif
```

## Subtitle Workflows

### Burn subtitles (hardcode)

```bash
# SRT subtitles
ffmpeg -i input.mp4 -vf "subtitles=subs.srt" output.mp4

# ASS/SSA styled subtitles
ffmpeg -i input.mp4 -vf "subtitles=subs.ass:fontsdir=/path/to/fonts" output.mp4

# With forced subtitles only
ffmpeg -i input.mp4 -vf "subtitles=subs.ass:force_style='Bold=0,BackColor=&HAA000000'" output.mp4
```

### Add subtitles to container

```bash
# MP4 (mov_text)
ffmpeg -i input.mp4 -i subs.srt -c copy -c:s mov_text -map 0 -map 1 output.mp4

# MKV (SRT)
ffmpeg -i input.mp4 -i subs.srt -c copy -c:s srt -map 0 -map 1 output.mkv

# With language tag
ffmpeg -i input.mp4 -i subs.srt -c copy -c:s srt -map 0 -map 1 \
  -metadata:s:s:0 language=eng output.mkv
```

### Convert subtitle format

```bash
# SRT to VTT
ffmpeg -i input.srt -c:s webvtt output.vtt

# ASS to SRT (loses styling)
ffmpeg -i input.ass -c:s srt output.srt

# Extract from video
ffmpeg -i input.mkv -map 0:s:0 -c copy output.srt
```

## Trimming

### Fast trim (streamcopy, keyframe-limited)

```bash
# Cut between keyframes (fast, no re-encoding)
ffmpeg -ss 00:01:00 -to 00:02:00 -i input.mp4 -c copy -avoid_negative_ts 1 output.mp4
```

### Precise trim (re-encode, frame-accurate)

```bash
# Frame-accurate cut (re-encodes)
ffmpeg -i input.mp4 -ss 00:01:00 -to 00:02:00 -c:v libx264 -crf 23 -c:a aac output.mp4

# With adjusted timestamps
ffmpeg -i input.mp4 -vf "trim=start=60:end=120,setpts=PTS-PTS_START" \
  -af "atrim=start=60:end=120,asetpts=PTS-PTS_START" \
  -c:v libx264 -crf 23 -c:a aac output.mp4
```

## Thumbnail Generation

### Single thumbnail at specific time

```bash
ffmpeg -i input.mp4 -ss 00:01:30 -vf "thumbnail=50:filter=mp" -frames:v 1 thumbnail.jpg
```

### Multiple thumbnails

```bash
# One frame per minute
ffmpeg -i input.mp4 -vf "fps=1/60,thumbnail=50,format=yuv420p" -frames:v 10 thumb_%03d.jpg

# Evenly spaced thumbnails
ffmpeg -i input.mp4 -vf "fps=1/30,thumbnail=300,format=yuv420p" thumb_%03d.jpg
```

### Contact sheet

```bash
# Generate thumbnails then tile
ffmpeg -i input.mp4 -vf "fps=1/10,thumbnail=60,format=yuv420p[t];[t]tile=5x2" contact_sheet.png
```

## Two-Pass Encoding

For strict bitrate targets (not needed for CRF mode):

```bash
# Pass 1
ffmpeg -i input.mp4 -c:v libx264 -b:v 5000k -pass 1 -f null /dev/null

# Pass 2
ffmpeg -i input.mp4 -c:v libx264 -b:v 5000k -pass 2 -c:a aac -b:a 128k output.mp4

# With maxrate and bufsize
ffmpeg -i input.mp4 -c:v libx264 -b:v 5000k -maxrate 6000k -bufsize 12000k -pass 1 -f null /dev/null
ffmpeg -i input.mp4 -c:v libx264 -b:v 5000k -maxrate 6000k -bufsize 12000k -pass 2 output.mp4
```

## HDR to SDR Conversion

```bash
# HDR (PQ/HLG) to SDR with tone mapping
ffmpeg -i hdr_input.mp4 -c:v libx264 -crf 23 \
  -vf "zscale=t=linear:npl=100,format=yuv444p,zscale=m=bt709,\
  tonemap=tonemap=hable:desat=0,zscale=t=bt709:r=tv,format=yuv420p" \
  output.mp4

# Alternative with libplacebo (if available)
ffmpeg -i hdr_input.mp4 -c:v libx264 -crf 23 \
  -vf "hwupload,tonemap_libplacebo=tonemap=hable:primaries=bt709:transfer=bt709:format=yuv420p,\
  hwdownload,format=yuv420p" \
  output.mp4
```

## Batch Processing

```bash
# Process all files in directory
for f in *.mkv; do
  ffmpeg -i "$f" -c:v libx264 -crf 23 -c:a aac -b:a 128k \
    -movflags +faststart "${f%.mkv}.mp4"
done

# With progress tracking
for f in *.mkv; do
  echo "Processing: $f"
  ffmpeg -y -i "$f" -c:v libx264 -crf 23 -c:a copy \
    -movflags +faststart "${f%.mkv}.mp4" && echo "Done: $f" || echo "Failed: $f"
done
```

## Video Merging

### Same codec (streamcopy)

```bash
# Using concat demuxer
# Create file list.txt:
#   file 'video1.mp4'
#   file 'video2.mp4'
#   file 'video3.mp4'
ffmpeg -f concat -safe 0 -i list.txt -c copy output.mp4
```

### Different codecs (re-encode)

```bash
# Using concat filter
ffmpeg -i a.mp4 -i b.mp4 -i c.mp4 -filter_complex \
  "[0:v][0:a][1:v][1:a][2:v][2:a]concat=n=3:v=1:a=1[outv][outa]" \
  -map "[outv]" -map "[outa]" -c:v libx264 -crf 23 -c:a aac output.mp4
```

### With crossfade transitions

```bash
ffmpeg -i a.mp4 -i b.mp4 -filter_complex \
  "[0:v]trim=0:5,setpts=PTS-PTS_START[a];\
   [1:v]trim=0:5,setpts=PTS-PTS_START[b];\
   [a][b]xfade=transition=fade:duration=0.5:offset=4.5[outv];\
   [0:a]atrim=0:5,asetpts=PTS-PTS_START[ac];\
   [1:a]atrim=0:5,asetpts=PTS-PTS_START[bc];\
   [ac][bc]acrossfade=d=0.5[outa]" \
  -map "[outv]" -map "[outa]" output.mp4
```

## Audio Extraction and Mixing

### Extract audio tracks

```bash
# First audio track
ffmpeg -i input.mkv -map 0:a:0 -c:a copy track1.aac

# All audio tracks
ffmpeg -i input.mkv -map 0:a -c:a copy -f segment track_%d.aac
```

### Mix multiple audio files

```bash
# Simple mix
ffmpeg -i a.mp3 -i b.mp3 -filter_complex "[0:a][1:a]amix=inputs=2:duration=shortest" \
  -c:a libmp3lame -b:a 192k mixed.mp3

# With volume adjustment
ffmpeg -i a.mp3 -i b.mp3 -filter_complex \
  "[0:a]volume=1.0[a];[1:a]volume=0.5[b];[a][b]amix=inputs=2" \
  -c:a libmp3lame mixed.mp3
```

## Speed Change

```bash
# 2x speed (video + audio)
ffmpeg -i input.mp4 -filter_complex \
  "[0:v]setpts=0.5*PTS[v];[0:a]atempo=2.0[a]" \
  -map "[v]" -map "[a]" -c:v libx264 -crf 23 -c:a aac output.mp4

# 0.5x speed
ffmpeg -i input.mp4 -filter_complex \
  "[0:v]setpts=2.0*PTS[v];[0:a]atempo=0.5[a]" \
  -map "[v]" -map "[a]" output.mp4

# Variable speed (accelerate over time)
ffmpeg -i input.mp4 -filter_complex \
  "[0:v]setpts=0.5*PTS[v];[0:a]atempo=1.5,atempo=1.333[a]" \
  -map "[v]" -map "[a]" output.mp4
```

## Rotation and Orientation

```bash
# Fix rotated video (remove rotation metadata, actually rotate)
ffmpeg -i input.mp4 -vf "transpose=1" -c:a copy output.mp4

# Common transpose values:
# 0 = 90° CCW and vertical flip
# 1 = 90° CW
# 2 = 90° CCW
# 3 = 90° CW and vertical flip

# Combine for 180°
ffmpeg -i input.mp4 -vf "transpose=1,transpose=1" -c:a copy output.mp4

# Arbitrary rotation
ffmpeg -i input.mp4 -vf "rotate=PI/4" -c:a copy output.mp4
```

## Watermarking

```bash
# Static watermark (PNG with transparency)
ffmpeg -i input.mp4 -i watermark.png -filter_complex \
  "[1:v]scale=200:-1[wm];[0:v][wm]overlay=W-w-10:10:format=auto" \
  -c:a copy output.mp4

# Animated watermark (with fade)
ffmpeg -i input.mp4 -i watermark.png -filter_complex \
  "[1:v]scale=200:-1,fade=t=in:st=0:d=1,fade=t=out:st=59:d=1[wm];\
   [0:v][wm]overlay=W-w-10:10:format=auto" \
  -c:a copy output.mp4

# Text watermark
ffmpeg -i input.mp4 -vf \
  "drawtext=text='© 2024 My Channel':fontfile=DejaVuSans.ttf:fontsize=36:\
  fontcolor=white@0.5:bordercolor=black:borderw=2:x=(w-tw)/2:y=h-th-20" \
  -c:a copy output.mp4
```

## Picture-in-Picture

```bash
ffmpeg -i main.mp4 -i pip.mp4 -filter_complex \
  "[1:v]scale=320:240[pip];[0:v][pip]overlay=W-w-20:20" \
  -c:a copy output.mp4

# PiP that appears at specific time
ffmpeg -i main.mp4 -i pip.mp4 -filter_complex \
  "[1:v]trim=start=5:end=10,setpts=PTS-PTS_START,scale=320:240[pip];\
   [0:v][pip]overlay=W-w-20:20:enable='between(t,5,10)'" \
  -c:a copy output.mp4
```

## Splitting

```bash
# Split into segments (every 60 seconds)
ffmpeg -i input.mp4 -c copy -f segment -segment_time 60 output_%03d.mp4

# Split at keyframes
ffmpeg -i input.mp4 -c copy -f segment -segment_time 60 -segment_list playlist.txt output_%03d.ts

# Split into chapters
ffmpeg -i input.mp4 -f segment -segment_time 300 -c:v libx264 -crf 23 -c:a aac part_%03d.mp4
```

## Quality Comparison

```bash
# Generate quality comparison (side by side)
ffmpeg -i original.mp4 -i encoded.mp4 -filter_complex \
  "[0:v]scale=640:360[orig];[1:v]scale=640:360[enc];\
   [orig][enc]hstack=inputs=2" \
  -c:v libx264 -crf 23 comparison.mp4
```
