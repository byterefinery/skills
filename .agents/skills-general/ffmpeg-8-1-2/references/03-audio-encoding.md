# Audio Encoding

## AAC (Advanced Audio Coding)

Default audio codec for MP4/MKV. Built-in `aac` encoder or optional `libfdk_aac`.

### Built-in AAC Encoder

```bash
# Basic AAC encoding
ffmpeg -i input.mp4 -c:a aac -b:a 128k output.mp4

# High quality
ffmpeg -i input.mp4 -c:a aac -b:a 256k -movflags +faststart output.mp4

# Sample rate and channels
ffmpeg -i input.mp4 -c:a aac -b:a 128k -ar 48000 -ac 2 output.mp4
```

### AAC Encoder Options

```bash
# Bitrate (recommended)
-c:a aac -b:a 128k           # Stereo music
-c:a aac -b:a 192k           # High quality stereo
-c:a aac -b:a 320k           # Maximum AAC

# Sample rate
-c:a aac -ar 48000            # Standard for video
-c:a aac -ar 44100            # CD quality

# Channels
-c:a aac -ac 2                # Stereo
-c:a aac -ac 6                # 5.1 surround

# AAC specific options
-c:a aac -aac_crf 1.5         # Quality factor (0-4, lower=better)
-c:a aac -aac_is 8            # ISO mode (8=default, more compatible)
-c:a aac -strict experimental # Enable experimental features
```

### libfdk_aac (if available)

Generally higher quality than built-in AAC at same bitrate.

```bash
# VBR mode
-c:a libfdk_aac -vbr 3        # VBR 1-5 (1=highest quality)

# CBR mode
-c:a libfdk_aac -b:a 128k

# Profile
-c:a libfdk_aac -profile:a aac_he_v2  # For low bitrates
```

## Opus

Modern codec, excellent quality at all bitrates. Ideal for WebM, streaming, voice.

```bash
# Basic Opus encoding
ffmpeg -i input.mp4 -c:a libopus -b:a 96k output.webm

# Voice (low bitrate)
ffmpeg -i input.mp4 -c:a libopus -b:a 32k -vbr off output.webm

# Music (high quality)
ffmpeg -i input.mp4 -c:a libopus -b:a 128k output.webm

# Application mode
-c:a libopus -application audio      # General audio (default)
-c:a libopus -application voice      # Voice/telephony (lower latency)
-c:a libopus -application lowdelay   # Low latency
```

### Opus Options

```bash
# Bitrate
-c:a libopus -b:a 64k              # Good voice quality
-c:a libopus -b:a 96k              # Good music quality
-c:a libopus -b:a 128k             # High quality
-c:a libopus -b:a 160k             # Near-transparent

# VBR modes
-c:a libopus -vbr on               # VBR (default)
-c:a libopus -vbr off              # CBR
-c:a libopus -vbr constrained      # CVBR

# Frame size (latency vs efficiency)
-c:a libopus -frame_duration 20    # 20ms (default, good balance)
-c:a libopus -frame_duration 60    # 60ms (better compression, higher latency)

# Stereo coupling
-c:a libopus -cutoff 0             # Full range (default)
-c:a libopus -cutoff 8000          # Limit to 8kHz (voice)
```

## MP3 (libmp3lame)

Requires `--enable-libmp3lame`. Maximum compatibility.

```bash
# Basic MP3 encoding
ffmpeg -i input.mp4 -c:a libmp3lame -b:a 192k output.mp3

# VBR (recommended)
ffmpeg -i input.mp4 -c:a libmp3lame -q:a 2 output.mp3

# VBR quality: 0 (best) to 9 (worst). Default: 2.
# q:a 0 ≈ 245kbps, q:a 2 ≈ 175kbps, q:a 9 ≈ 64kbps
```

### MP3 Options

```bash
# CBR
-c:a libmp3lame -b:a 128k
-c:a libmp3lame -b:a 192k
-c:a libmp3lame -b:a 320k

# VBR with preset
-c:a libmp3lame -q:a 0             # Highest quality
-c:a libmp3lame -q:a 2             # Good quality (default)
-c:a libmp3lame -q:a 5             # Medium quality

# Joint stereo
-c:a libmp3lame -compression_level 10  # 0-10 (10=slowest, best quality)
```

## FLAC (Lossless)

```bash
# Basic FLAC encoding
ffmpeg -i input.wav -c:a flac output.flac

# Compression levels (speed vs size)
-c:a flac -compression_level 0     # Fastest, largest
-c:a flac -compression_level 5     # Default
-c:a flac -compression_level 12    # Slowest, smallest
```

## Audio Processing

### Resampling

```bash
# Change sample rate
ffmpeg -i input.mp4 -ar 48000 output.mp4

# With specific resample filter
ffmpeg -i input.mp4 -af "aresample=48000:dither_method=rectangular" output.mp4
```

### Channel Layout

```bash
# Stereo to mono
ffmpeg -i input.mp4 -ac 1 output.mp4

# Mono to stereo (duplicate)
ffmpeg -i input.mp4 -af "pan=stereo|c0=c0|c1=c0" output.mp4

# 5.1 to stereo (downmix)
ffmpeg -i input.mp4 -ac 2 output.mp4

# Stereo to 5.1 (upmix — not ideal, just adds silence)
ffmpeg -i input.mp4 -ac 6 -af "pan=5.1|FL=0.5*FL+0.5*FR|FR=0.5*FL+0.5*FR|FC=0.5*FL+0.5*FR|LFE=0|BL=0|BR=0" output.mp4
```

### Pan Filter

```bash
# Custom pan layout
-af "pan=stereo|c0=FL|c1=FR"
-af "pan=mono|c0=0.5*FL+0.5*FR"
-af "pan=5.1|c0=FL|c1=FR|c2=FC|c3=LFE|c4=BL|c5=BR"
```

### Volume

```bash
# Simple volume adjustment
-af "volume=1.5"           # 50% louder
-af "volume=0.5"           # 50% quieter
-af "volume=3dB"           # +3dB

# Auto-normalize to peak
-af "alimiter=limit=1:attack=1:release=10"
```

## Audio Extraction and Conversion

```bash
# Extract audio from video
ffmpeg -i input.mp4 -vn -c:a copy output.aac
ffmpeg -i input.mp4 -vn -c:a libopus output.opus

# Convert audio format
ffmpeg -i input.flac -c:a libopus -b:a 128k output.opus
ffmpeg -i input.wav -c:a libmp3lame -q:a 2 output.mp3

# Convert sample rate
ffmpeg -i input.wav -ar 44100 -ac 2 -c:a pcm_s16le output.wav

# Trim audio
ffmpeg -i input.mp3 -ss 00:01:00 -to 00:03:00 -c copy output.mp3
```

## Common Patterns

### Podcast (Opus, voice-optimized)

```bash
ffmpeg -i input.wav -c:a libopus -b:a 32k -application voice \
  -af "loudnorm=I=-16:TP=-1.5:LRA=6" podcast.opus
```

### Music archive (FLAC lossless)

```bash
ffmpeg -i input.wav -c:a flac -compression_level 8 archive.flac
```

### Web audio (AAC, broad compatibility)

```bash
ffmpeg -i input.wav -c:a aac -b:a 128k -ar 44100 -ac 2 music.m4a
```

### Ringtone (short MP3)

```bash
ffmpeg -i input.mp3 -ss 0:30 -t 30 -c:a libmp3lame -b:a 64k ringtone.mp3
```
