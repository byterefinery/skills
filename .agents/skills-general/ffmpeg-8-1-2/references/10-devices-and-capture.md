# Devices and Capture

## Video Capture

### v4l2 (Linux — Webcams, Capture Cards)

```bash
# List available devices
ffmpeg -f v4l2 -list_devices 1 -i /dev/null

# Capture from webcam
ffmpeg -f v4l2 -i /dev/video0 -c:v libx264 -crf 23 output.mp4

# With format and resolution
ffmpeg -f v4l2 -video_size 1920x1080 -framerate 30 -i /dev/video0 \
  -c:v libx264 -crf 23 output.mp4

# Check supported formats
ffmpeg -f v4l2 -list_formats all -i /dev/video0

# With input format
ffmpeg -f v4l2 -pixel_format yuv420p -video_size 1920x1080 -framerate 30 \
  -input_format mjpeg -i /dev/video0 -c:v libx264 output.mp4

# Device options
# -channel N         Input channel
# -standard          TV standard (ntsc, pal)
# -input_index N     Input index
# -input_format      Pixel format
```

### x11grab (Linux — Screen Capture)

```bash
# Capture entire screen
ffmpeg -f x11grab -video_size 1920x1080 -i :0.0 -c:v libx264 -crf 23 output.mp4

# Capture with offset
ffmpeg -f x11grab -video_size 1920x1080 -i :0.0+100,200 -c:v libx264 output.mp4

# Capture specific window (need xdotool)
WINDOW=$(xdotool search --name "Window Title" | head -1)
X=$(xdotool getwindowgeometry --shell "$WINDOW" | grep X= | cut -d= -f2)
Y=$(xdotool getwindowgeometry --shell "$WINDOW" | grep Y= | cut -d= -f2)
ffmpeg -f x11grab -video_size 1280x720 -i :0.0+$X,$Y -c:v libx264 output.mp4

# With audio (PulseAudio)
ffmpeg -f x11grab -video_size 1920x1080 -i :0.0 \
  -f pulse -i default -c:v libx264 -c:a aac output.mp4
```

### gdigrab (Windows — Screen Capture)

```bash
# Capture entire screen
ffmpeg -f gdigrab -i desktop -c:v libx264 -crf 23 output.mp4

# Capture with offset and size
ffmpeg -f gdigrab -offset_x 0 -offset_y 0 -video_size 1920x1080 -i desktop \
  -c:v libx264 output.mp4

# Capture at specific framerate
ffmpeg -f gdigrab -framerate 30 -i desktop -c:v libx264 output.mp4

# Capture specific window
ffmpeg -f gdigrab -i title=Window\ Title -c:v libx264 output.mp4
```

### avfoundation (macOS — Screen and Camera)

```bash
# List devices
ffmpeg -f avfoundation -list_devices 1 -i ""

# Capture from camera
ffmpeg -f avfoundation -i "FaceTime Camera:0" -c:v libx264 output.mp4

# Screen capture
ffmpeg -f avfoundation -i ":0" -c:v libx264 output.mp4

# Camera + microphone
ffmpeg -f avfoundation -i "FaceTime Camera:Built-in Microphone" \
  -c:v libx264 -c:a aac output.mp4

# With quality settings
ffmpeg -f avfoundation -video_size 1920x1080 -framerate 30 -i "0:0" \
  -c:v libx264 output.mp4
```

### dshow (Windows — DirectShow Devices)

```bash
# List devices
ffmpeg -list_options true -f dshow -i dummy

# Capture from webcam
ffmpeg -f dshow -i video="Camera Name" -c:v libx264 output.mp4

# Camera + audio
ffmpeg -f dshow -i video="Camera Name":audio="Microphone Name" \
  -c:v libx264 -c:a aac output.mp4

# With pixel format and resolution
ffmpeg -f dshow -video_size 1920x1080 -pixel_format yuv420p \
  -i video="Camera Name" -c:v libx264 output.mp4

# Device options
# -video_size WxH    Resolution
# -framerate FPS     Frame rate
# -pixel_format FMT  Pixel format
# -sample_rate Hz    Audio sample rate
# -sample_fmt FMT    Audio sample format
# -channel_layout L  Audio channel layout
# -channels N        Audio channel count
```

## Audio Capture

### ALSA (Linux)

```bash
# List devices
arecord -l
ffmpeg -f alsa -list_devices 1 -i /dev/null

# Capture from default device
ffmpeg -f alsa -i default -c:a aac output.aac

# Capture from specific device
ffmpeg -f alsa -i hw:1,0 -c:a aac output.aac

# With sample rate and channels
ffmpeg -f alsa -ar 48000 -ac 2 -i hw:1,0 -c:a aac output.aac
```

### PulseAudio (Linux)

```bash
# List sources
pactl list sources

# Capture default source
ffmpeg -f pulse -i default -c:a aac output.aac

# Capture specific source
ffmpeg -f pulse -i "alsa_input.pci-0000_00_1f.3.analog-stereo" \
  -c:a aac output.aac

# Monitor (listen to what's playing)
ffmpeg -f pulse -i "default.monitor" -c:a aac output.aac
```

### PipeWire (Linux — modern replacement for PulseAudio)

```bash
# Same interface as PulseAudio
ffmpeg -f pulse -i default -c:a aac output.aac

# Or use ALSA interface
ffmpeg -f alsa -i default -c:a aac output.aac
```

### JACK (Linux — Professional Audio)

```bash
# List connections
jack_lsp

# Capture from JACK
ffmpeg -f jack -i jack -c:a aac output.aac
```

### OpenAL (Cross-platform)

```bash
# List devices
ffmpeg -f openal -list_devices 1 -i /dev/null

# Capture
ffmpeg -f openal -i "Default" -c:a aac output.aac
```

## Screen Recording Patterns

### Full screen + audio (Linux)

```bash
ffmpeg -f x11grab -video_size 1920x1080 -framerate 30 -i :0.0 \
  -f pulse -i default \
  -c:v libx264 -crf 23 -c:a aac -b:a 128k \
  -movflags +faststart output.mp4
```

### Full screen + audio (macOS)

```bash
ffmpeg -f avfoundation -i ":0" \
  -f avfoundation -i ":1" \
  -c:v libx264 -crf 23 -c:a aac \
  -movflags +faststart output.mp4
```

### Full screen + audio (Windows)

```bash
ffmpeg -f gdigrab -framerate 30 -i desktop \
  -f dshow -i audio="Microphone Name" \
  -c:v libx264 -crf 23 -c:a aac \
  -movflags +faststart output.mp4
```

### Webcam recording

```bash
# Linux
ffmpeg -f v4l2 -i /dev/video0 -f pulse -i default \
  -c:v libx264 -crf 23 -c:a aac output.mp4

# macOS
ffmpeg -f avfoundation -i "FaceTime Camera:Built-in Microphone" \
  -c:v libx264 -crf 23 output.mp4

# Windows
ffmpeg -f dshow -i video="Camera":audio="Microphone" \
  -c:v libx264 -crf 23 output.mp4
```

### Live streaming from camera

```bash
# Webcam to RTMP
ffmpeg -f v4l2 -input_format mjpeg -video_size 1280x720 -framerate 30 \
  -i /dev/video0 \
  -f pulse -i default \
  -c:v libx264 -preset veryfast -tune zerolatency -b:v 2500k \
  -c:a aac -b:a 128k -ar 48000 \
  -f flv "rtmp://server/app/streamkey"
```

## Network Capture

### HTTP Live Stream

```bash
# Record HTTP stream
ffmpeg -i "http://stream.server/video.m3u8" -c copy output.ts

# With timeout
ffmpeg -timeout 3600 -i "http://stream.server/video.m3u8" -c copy output.ts
```

### RTSP Stream

```bash
# Record RTSP stream
ffmpeg -i "rtsp://user:pass@ip:554/stream" -c copy output.mkv

# With TCP transport (more reliable)
ffmpeg -rtsp_transport tcp -i "rtsp://user:pass@ip:554/stream" -c copy output.mkv

# With UDP (lower latency)
ffmpeg -rtsp_transport udp -i "rtsp://user:pass@ip:554/stream" -c copy output.mkv
```

## lavfi (Libavfilter as Input)

Generate test content without external files.

```bash
# Test pattern
ffmpeg -f lavfi -i testsrc=size=1920x1080:rate=30 -c:v libx264 -frames:v 300 output.mp4

# Color bar
ffmpeg -f lavfi -i color=c=blue:s=1920x1080:d=10 -c:v libx264 output.mp4

# Sine wave tone
ffmpeg -f lavfi -i "aevalsrc=sin(440*2*PI*t):s=48000:d=5" -c:a aac tone.aac

# Noise
ffmpeg -f lavfi -i "anoisesrc=s=black:d=5:s=48000" -c:a aac noise.aac

# Multiple test sources
ffmpeg -f lavfi -i "testsrc=size=640x480:rate=30,color=c=red:size=640x480:rate=30" \
  -map 0:v -map 1:v -c:v libx264 output.mp4
```

## Device Options Reference

### v4l2 Options

| Option | Description |
|--------|-------------|
| `-video_size WxH` | Frame size |
| `-framerate FPS` | Frame rate |
| `-pixel_format FMT` | Pixel format |
| `-input_format FMT` | Input format (mjpeg, yuv420p, etc.) |
| `-channel N` | Input channel |
| `-standard STD` | TV standard (ntsc, pal, secam) |
| `-input_index N` | Input index |
| `-decimate_file 1` | Drop duplicate frames |

### x11grab Options

| Option | Description |
|--------|-------------|
| `-video_size WxH` | Resolution |
| `-framerate FPS` | Frame rate |
| `-i :DISPLAY+X,Y` | Display and offset |
| `-draw_mouse 0/1` | Show/hide cursor (default: 1) |
| `-follow_mouse [center\|geometry]` | Follow mouse cursor |

### gdigrab Options

| Option | Description |
|--------|-------------|
| `-framerate FPS` | Frame rate |
| `-offset_x N` | X offset |
| `-offset_y N` | Y offset |
| `-video_size WxH` | Resolution |
| `-i desktop` | Capture desktop |
| `-i title=NAME` | Capture window by title |
