# Formats and Protocols

## Common Container Formats

| Extension | Format | Typical Codecs | Notes |
|-----------|--------|---------------|-------|
| `.mp4` | mov,mp4,m4a,3gp | H.264, H.265, AAC, Opus | Most compatible |
| `.mkv` | matroska | Any codec | Flexible, no restrictions |
| `.webm` | webm | VP8/VP9, AV1, Opus | Web standard |
| `.avi` | avi | H.264, MP3, AAC | Legacy, limited features |
| `.mov` | mov | H.264, AAC, ProRes | Apple ecosystem |
| `.flv` | flv | H.264, AAC, MP3 | Flash/legacy streaming |
| `.ts` | mpegts | H.264, AAC | Broadcast/streaming |
| `.wav` | wav | PCM | Uncompressed audio |
| `.ogg` | ogg | Opus, Vorbis | Open format |
| `.m3u8` | hls | H.264, AAC | HLS playlist |
| `.gif` | gif | GIF | Animated images |
| `.mp3` | mp3 | MP3 | Audio only |
| `.aac` | adts | AAC | Audio only |
| `.srt` | srt | text | Subtitles |
| `.ass` | ass | text | Styled subtitles |
| `.vtt` | webvtt | text | Web subtitles |

## Force Format

```bash
# Force output format
ffmpeg -i input.mkv -f mp4 output.mp4

# Force input format (when auto-detection fails)
ffmpeg -f mpegts -i input.ts output.mp4

# Force raw format
ffmpeg -f rawvideo -pix_fmt yuv420p -s 1920x1080 -r 30 -i input.yuv output.mp4
```

## MP4/MOV Options

```bash
# Fast start (web optimization — moov atom at beginning)
-f mp4 -movflags +faststart

# Fragmented MP4 (for streaming)
-f mp4 -movflags +frag_keyframe+empty_moov+default_base_moof

# Disable smart cropping
-f mp4 -movflags +disable_chpl

# Compatible with older players
-f mp4 -movflags +faststart -movflags +skip_to_sidx
```

## Matroska Options

```bash
# Basic MKV
-f matroska

# With chapters
-f matroska -chapters_input 0

# With attachments (fonts)
-f matroska -attach font.ttf
```

## Image Sequences

```bash
# Video to images
ffmpeg -i input.mp4 -vf "fps=1" frame_%04d.png

# Images to video
ffmpeg -f image2 -i frame_%04d.png -c:v libx264 -r 30 output.mp4

# With pattern_type
ffmpeg -f image2 -pattern_type glob -i '*.jpg' -c:v libx264 output.mp4

# Specific image formats
ffmpeg -i input.mp4 -vf "fps=1/60" -q:v 2 frame_%04d.jpg     # JPEG
ffmpeg -i input.mp4 -vf "fps=1/60" frame_%04d.png             # PNG
ffmpeg -i input.mp4 -vf "fps=1/60" -compression_level 9 frame_%04d.webp  # WebP
```

## HLS (HTTP Live Streaming)

```bash
# Basic HLS
ffmpeg -i input.mp4 -c:v libx264 -c:a aac -hls_time 10 \
  -hls_list_size 0 -hls_segment_filename 'seg_%03d.ts' playlist.m3u8

# Multi-bitrate HLS
ffmpeg -i input.mp4 \
  -c:v libx264 -b:v:0 2500k -s:v:0 1280x720 -b:a:0 128k \
  -c:v libx264 -b:v:1 1000k -s:v:1 854x480 -b:a:1 96k \
  -c:v libx264 -b:v:2 500k -s:v:2 640x360 -b:a:2 64k \
  -hls_time 6 -hls_list_size 0 -hls_variant \
    "STREAM-INF:BANDWIDTH=2688000,RESOLUTION=1280x720:/path/0.m3u8,\
     STREAM-INF:BANDWIDTH=1104000,RESOLUTION=854x480:/path/1.m3u8,\
     STREAM-INF:BANDWIDTH=608000,RESOLUTION=640x360:/path/2.m3u8" \
  -f hls master.m3u8
```

## DASH (Dynamic Adaptive Streaming)

```bash
# Multi-bitrate DASH
ffmpeg -i input.mp4 \
  -c:v libx264 -b:v:0 2500k -s:v:0 1280x720 \
  -c:v libx264 -b:v:1 1000k -s:v:1 854x480 \
  -c:a aac -b:a 128k \
  -f dash output.mpd
```

## Protocols

### File Protocol

```bash
# Local file (default)
ffmpeg -i /path/to/input.mp4 output.mp4

# Absolute path with spaces
ffmpeg -i "/path/to/my file.mp4" output.mp4
```

### Pipe Protocol

```bash
# Read from pipe
cat input.mp4 | ffmpeg -i pipe:0 output.mp4

# Write to pipe
ffmpeg -i input.mp4 -f mp4 pipe:1 | cat > output.mp4

# Named pipe (FIFO)
mkfifo /tmp/video.fifo
ffmpeg -i input.mp4 -f mp4 /tmp/video.fifo &
cat /tmp/video.fifo > output.mp4
```

### HTTP/HTTPS

```bash
# Download and process
ffmpeg -i "http://example.com/video.mp4" output.mp4

# With authentication
ffmpeg -i "http://user:pass@example.com/video.mp4" output.mp4

# With headers
ffmpeg -http_header "Authorization: Bearer TOKEN" -i "https://api.example.com/video" output.mp4

# User agent
ffmpeg -user_agent "Mozilla/5.0" -i "https://example.com/video.mp4" output.mp4
```

### RTMP (Real-Time Messaging Protocol)

```bash
# Stream to RTMP server
ffmpeg -re -i input.mp4 -c:v libx264 -preset veryfast -tune zerolatency \
  -c:a aac -b:a 128k -f flv "rtmp://server/app/streamkey"

# Stream with bitrate control
ffmpeg -re -i input.mp4 -c:v libx264 -b:v 2500k -maxrate 2500k \
  -bufsize 5000k -c:a aac -b:a 128k -f flv "rtmp://server/app/streamkey"

# Read RTMP stream
ffmpeg -i "rtmp://server/app/streamkey" -c copy output.mkv
```

### FTP

```bash
# Upload via FTP
ffmpeg -i input.mp4 "ftp://user:pass@server/path/output.mp4"

# Download via FTP
ffmpeg -i "ftp://user:pass@server/path/input.mp4" output.mp4
```

### Concat Protocol

```bash
# Concatenate files of same format without re-encoding
ffmpeg -i "concat:input1.mp4|input2.mp4|input3.mp4" -c copy output.mp4

# With file:// prefix for absolute paths
ffmpeg -i "concat:file:///path/a.mp4|file:///path/b.mp4" -c copy output.mp4
```

### Crypto Protocol (Encrypted Transport)

```bash
# Encrypt stream during transfer
ffmpeg -i input.mp4 -f mp4 "crypto:aes-128:secretkey:/path/output.mp4"
```

### MD5 Protocol (Hash Output)

```bash
# Hash output without writing file
ffmpeg -i input.mp4 -f rawvideo -c:v rawvideo md5:
```

## Subtitle Formats

```bash
# Burn subtitles (hardcode)
ffmpeg -i input.mp4 -vf "subtitles=subs.srt" output.mp4

# With ASS/SSA styled subtitles
ffmpeg -i input.mp4 -vf "subtitles=subs.ass" output.mp4

# Convert subtitle format
ffmpeg -i input.srt -c:s webvtt output.vtt

# Extract subtitles
ffmpeg -i input.mkv -map 0:s:0 -c copy output.srt

# Add subtitles to container
ffmpeg -i input.mp4 -i subs.srt -c copy -c:s mov_text -map 0 -map 1 output.mp4
```

## Common Format-Specific Patterns

### Web-optimized MP4

```bash
ffmpeg -i input.mkv -c:v libx264 -crf 23 -preset medium \
  -c:a aac -b:a 128k -movflags +faststart -pix_fmt yuv420p output.mp4
```

### YouTube-ready file

```bash
ffmpeg -i input.mkv -c:v libx264 -crf 18 -preset slow \
  -c:a libopus -b:a 128k -pix_fmt yuv420p output.mp4
```

### Broadcast TS

```bash
ffmpeg -i input.mp4 -c:v h264 -b:v 8M -maxrate 8M -bufsize 16M \
  -g 48 -keyint_min 48 -c:a aac -b:a 256k -ar 48000 \
  -f mpegts output.ts
```
