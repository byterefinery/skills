# ffprobe

ffprobe inspects media files and outputs stream/container metadata in human- or machine-readable formats.

## Basic Usage

```bash
# Default output (human-readable, shows errors + stream info)
ffprobe input.mp4

# Quiet mode (suppress errors, show only requested data)
ffprobe -v quiet input.mp4

# Show format and stream info
ffprobe -v quiet -show_format -show_streams input.mp4

# Show only stream info
ffprobe -v quiet -show_streams input.mp4

# Show only format info
ffprobe -v quiet -show_format input.mp4
```

## Output Formats

### JSON (Recommended for Scripting)

```bash
ffprobe -v quiet -print_format json -show_format -show_streams input.mp4
```

Output structure:
```json
{
  "streams": [
    {
      "index": 0,
      "codec_name": "h264",
      "codec_type": "video",
      "width": 1920,
      "height": 1080,
      "r_frame_rate": "30000/1001",
      "duration": "120.500000",
      "bits_per_raw_sample": "8",
      "tags": { "language": "eng" }
    },
    {
      "index": 1,
      "codec_name": "aac",
      "codec_type": "audio",
      "sample_rate": "48000",
      "channels": 2,
      "channel_layout": "stereo"
    }
  ],
  "format": {
    "filename": "input.mp4",
    "format_name": "mov,mp4,m4a,3gp",
    "duration": "120.500000",
    "size": "52428800",
    "bit_rate": "3481600",
    "tags": { "encoder": "Lavf58.29.100" }
  }
}
```

### Compact (key=value)

```bash
ffprobe -v quiet -of compact -show_entries stream=codec_name,width,height,duration input.mp4
```

Output:
```
index=0;codec_name=h264;width=1920;height=1080;duration=120.500000
index=1;codec_name=aac;width=0;height=0;duration=N/A
```

### Flat (XML-like key-value)

```bash
ffprobe -v quiet -of flat -show_entries stream=codec_name input.mp4
```

### CSV

```bash
ffprobe -v quiet -of csv=p=0 -show_entries stream=codec_name,width,height input.mp4
```

Output:
```
h264,1920,1080
aac,0,0
```

## Extracting Specific Values

### Duration

```bash
# From format
ffprobe -v quiet -show_entries format=duration -of csv=p=0 input.mp4

# From stream (may differ slightly)
ffprobe -v quiet -show_entries stream=duration -of csv=p=0 input.mp4

# Human-readable
ffprobe -v quiet -show_entries format=duration -of default=noprint_wrappers=1 input.mp4
```

### Resolution

```bash
# Video dimensions
ffprobe -v quiet -select_streams v:0 -show_entries stream=width,height -of csv=p=0 input.mp4

# With label
ffprobe -v quiet -select_streams v:0 -show_entries stream=width,height -of default=noprint_wrappers=1 input.mp4
```

### Frame Rate

```bash
# Nominal frame rate
ffprobe -v quiet -select_streams v:0 -show_entries stream=r_frame_rate -of csv=p=0 input.mp4

# Average frame rate
ffprobe -v quiet -select_streams v:0 -show_entries stream=avg_frame_rate -of csv=p=0 input.mp4
```

### Codec Info

```bash
# Video codec
ffprobe -v quiet -select_streams v:0 -show_entries stream=codec_name,codec_type -of csv=p=0 input.mp4

# Audio codec
ffprobe -v quiet -select_streams a:0 -show_entries stream=codec_name,sample_rate,channels -of csv=p=0 input.mp4
```

### Pixel Format

```bash
ffprobe -v quiet -select_streams v:0 -show_entries stream=pix_fmt -of csv=p=0 input.mp4
```

### Bitrate

```bash
# Overall bitrate
ffprobe -v quiet -show_entries format=bit_rate -of csv=p=0 input.mp4

# Per-stream bitrate
ffprobe -v quiet -show_entries stream=bit_rate -of csv=p=0 input.mp4
```

### Stream Count

```bash
# Total streams
ffprobe -v quiet -show_entries format=nb_streams -of csv=p=0 input.mp4

# Video streams only
ffprobe -v quiet -select_streams v -show_entries stream=codec_name -of csv=p=0 input.mp4 | wc -l
```

## Selecting Streams

```bash
# Video streams only
-select_streams v

# Audio streams only
-select_streams a

# First video stream
-select_streams v:0

# Second audio stream
-select_streams a:1

# Subtitle streams
-select_streams s

# By codec
-select_streams codec:h264
```

## Show Entries Syntax

```bash
# Format entries
-show_entries format=duration,size,bit_rate,format_name

# Stream entries
-show_entries stream=index,codec_name,codec_type,width,height,duration,r_frame_rate

# Multiple show_entries
-show_entries format=duration -show_entries stream=codec_name

# All entries (no filter)
-show_format -show_streams
```

## Common Fields

### Video Stream Fields

| Field | Description |
|-------|-------------|
| `codec_name` | Codec (h264, hevc, vp9, av1) |
| `codec_type` | Stream type (video) |
| `width`, `height` | Resolution |
| `r_frame_rate` | Nominal frame rate |
| `avg_frame_rate` | Average frame rate |
| `pix_fmt` | Pixel format |
| `duration` | Duration in seconds |
| `bit_rate` | Bitrate |
| `nb_frames` | Frame count |
| `profile` | Codec profile |
| `level` | Codec level |
| `color_range` | tv, pc |
| `color_space` | Color space |
| `color_transfer` | Transfer characteristic |
| `color_primaries` | Color primaries |
| `side_data_list` | Rotation, HDR metadata |

### Audio Stream Fields

| Field | Description |
|-------|-------------|
| `codec_name` | Codec (aac, opus, mp3) |
| `sample_rate` | Sample rate in Hz |
| `channels` | Channel count |
| `channel_layout` | Layout (stereo, 5.1) |
| `bits_per_sample` | Bit depth |
| `duration` | Duration in seconds |
| `bit_rate` | Bitrate |

## Practical Patterns

### Check if file is valid

```bash
ffprobe -v error -show_entries format=duration -of csv=p=0 input.mp4 >/dev/null 2>&1 && echo "valid" || echo "invalid"
```

### Get video info one-liner

```bash
ffprobe -v quiet -select_streams v:0 \
  -show_entries stream=width,height,r_frame_rate,codec_name,pix_fmt \
  -of csv=p=0:s=x input.mp4
# Output: 1920x1080x30000/1001xh264xyuv420p
```

### JSON parsing with jq

```bash
# Get all video resolutions
ffprobe -v quiet -print_format json -show_streams input.mp4 | \
  jq '.streams[] | select(.codec_type=="video") | {width, height, codec_name}'

# Get duration in seconds
ffprobe -v quiet -print_format json -show_format input.mp4 | \
  jq '.format.duration'

# Get audio sample rate
ffprobe -v quiet -print_format json -show_streams input.mp4 | \
  jq '.streams[] | select(.codec_type=="audio") | .sample_rate'

# Check for HDR
ffprobe -v quiet -print_format json -show_streams input.mp4 | \
  jq '.streams[] | select(.codec_type=="video") | .color_transfer'
```

### Loop over files

```bash
for f in *.mp4; do
  duration=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$f")
  resolution=$(ffprobe -v quiet -select_streams v:0 -show_entries stream=width,height -of csv=p=0 "$f")
  echo "$f: ${resolution}, ${duration}s"
done
```

### Check rotation

```bash
ffprobe -v quiet -print_format json -show_streams input.mp4 | \
  jq '.streams[] | select(.codec_type=="video") | .side_data_list[]? | select(.rotation)'
```

## Listing Capabilities

```bash
# List decoders
ffmpeg -decoders

# List encoders
ffmpeg -encoders

# List demuxers
ffmpeg -demuxers

# List muxers
ffmpeg -muxers

# List filters
ffmpeg -filters

# List protocols
ffmpeg -protocols

# List pixel formats
ffmpeg -pix_fmts

# List sample formats
ffmpeg -sample_fmts

# List color spaces
ffmpeg -colors

# List hwaccels
ffmpeg -hwaccels

# Get help on specific item
ffmpeg -help decoder=h264
ffmpeg -help encoder=libx264
ffmpeg -help filter=scale
```
