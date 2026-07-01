# Stream Selection and Specifiers

## The `-map` Option

`-map` gives explicit control over which input streams go into each output file. Without `-map`, ffmpeg uses automatic selection.

### Syntax

```
-map [-]input_file_index[:stream_specifier][:sync_file_index][:stream_type]
```

### Examples

```bash
# All streams from input 0
ffmpeg -i input.mkv -map 0 output.mkv

# Specific stream by index
ffmpeg -i input.mkv -map 0:2 output.mkv

# All video from input 0, all audio from input 1
ffmpeg -i video.mkv -i audio.mkv -map 0:v -map 1:a output.mkv

# Exclude a stream (prepend -)
ffmpeg -i input.mkv -map 0 -map -0:s output.mkv

# Multiple outputs with different maps
ffmpeg -i input.mkv \
  -map 0:v:0 -c:v libx264 -crf 23 video.mp4 \
  -map 0:a:0 -c:a libopus -b:a 96k audio.opus
```

## Stream Specifiers

Append `:spec` to any per-stream option (`-c`, `-b`, `-f`, `-threads`, etc.).

### Types

| Specifier | Matches |
|-----------|---------|
| `:0`, `:1`, `:2` | Stream by index |
| `:v` | All video streams (includes attached pictures) |
| `:V` | Video streams only (excludes attached pictures/thumbnails) |
| `:a` | All audio streams |
| `:s` | All subtitle streams |
| `:d` | All data streams |
| `:t` | All attachment streams |
| `:v:0` | First video stream |
| `:a:1` | Second audio stream |
| `:u` | Streams with usable configuration (codec + dimensions/rate defined) |
| `:i:PID` | Stream by stream ID (e.g., MPEG-TS PID) |
| `:m:key` | Streams with metadata tag `key` |
| `:m:key=value` | Streams with metadata tag `key` matching `value` |
| `:disp:default` | Streams with default disposition |
| `:p:PROGRAM_ID` | Streams in program with given ID |

### Combining Specifiers

```bash
# Second audio stream
-c:a:1 libopus

# All video streams in program 1
-c:p:1:v libx264

# Video streams with language metadata = eng
-c:v:m:language=eng libx264

# First usable stream
-c:u:0 libx264
```

### Per-Stream Options

Any option that takes a stream specifier:

```bash
# Different bitrates per audio stream
-b:a:0 192k -b:a:1 96k

# Different codecs per video stream
-c:v:0 libx264 -c:v:1 libx265

# Different threads per stream
-threads:v 8 -threads:a 4

# Disable specific stream
-c:a:1 copy -disposition:a:1 0
```

## Automatic Stream Selection

When no `-map` is specified for an output file, ffmpeg selects automatically:

- **Video**: stream with highest resolution
- **Audio**: stream with most channels
- **Subtitles**: first subtitle stream found (type must match muxer's default encoder — text or image)
- **Data/attachments**: never auto-selected; must use `-map`

### Auto-Selection Gotchas

- With multiple inputs, auto-selection picks from **all** inputs, not just one
- If a subtitle encoder is explicitly set (`-c:s`), the first subtitle of any type is selected regardless of compatibility
- Auto-selection skips if complex filtergraph outputs exist (unlabeled filter outputs go to first output)

## Disposition Flags

Control which streams are marked as "default" or have special roles:

```bash
# Make second audio stream the default
ffmpeg -i input.mkv -c copy -disposition:a:1 default -disposition:a:0 0 output.mkv

# Add embedded thumbnail
ffmpeg -i video.mp4 -i cover.jpg -map 0 -map 1 -c copy -c:v:1 png \
  -disposition:v:1 attached_pic output.mp4

# List known disposition flags
ffmpeg -dispositions
```

Common flags: `default`, `dub`, `original`, `comment`, `lyrics`, `karaoke`, `forced`, `hearing_impaired`, `visual_impaired`, `clean_effects`, `attached_pic`, `captions`, `descriptions`, `metadata`, `dependent`, `still_image`.

## Program and Stream Group

```bash
# Create a program (used for DVD/TV-style program groups)
ffmpeg -i input.mkv -program title="Program 1":st=0:st=1 output.mkv

# Map streams from an input program
ffmpeg -i input.ts -map p:100 output.ts
```

## Practical Patterns

### Extract specific track

```bash
# Third audio track only
ffmpeg -i input.mkv -map 0:a:2 -c:a copy output.aac
```

### Merge audio from different sources

```bash
ffmpeg -i video.mkv -i commentary.wav \
  -map 0:v -map 0:a:0 -map 1:a:0 \
  -c:v copy -c:a aac \
  -disposition:a:0 default -disposition:a:1 comment \
  output.mkv
```

### Remove all audio, keep only video

```bash
ffmpeg -i input.mkv -map 0:v -c copy output.mkv
# or simply:
ffmpeg -i input.mkv -an -c copy output.mkv
```

### Select by language

```bash
# Map English audio
ffmpeg -i input.mkv -map 0:a:m:language=eng -c:a copy output.aac
```
