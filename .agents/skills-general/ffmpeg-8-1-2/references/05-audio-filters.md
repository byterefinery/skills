# Audio Filters

## loudnorm (EBU R128 Loudness Normalization)

Industry-standard loudness normalization. Supports single-pass (live) and double-pass (file) modes.

### Double-Pass (Recommended for Files)

```bash
# Pass 1: measure loudness
ffmpeg -i input.mp4 -af "loudnorm=I=-24:TP=-2:LRA=7:print_format=json" -f null /dev/null
# Copy the measured values from output

# Pass 2: apply normalization
ffmpeg -i input.mp4 -af "loudnorm=I=-24:TP=-2:LRA=7:\
measured_I=-26.3:measured_LRA=8.1:measured_TP=-1.2:\
measured_thresh=-36.5:offset=0.5:linear=true:print_format=summary" \
  -c:v copy output.mp4
```

### Single-Pass (Live/Streaming)

```bash
# Dynamic normalization (good enough for most cases)
ffmpeg -i input.mp4 -af "loudnorm=I=-24:TP=-2:LRA=7:linear=false" output.mp4
```

### Parameters

| Parameter | Description | Default | Range |
|-----------|-------------|---------|-------|
| `I` | Integrated loudness target | -24.0 | -70 to -5 LUFS |
| `TP` | True peak limit | -2.0 | -9 to 0 dBTP |
| `LRA` | Loudness range target | 7.0 | 1 to 50 LKFS |
| `linear` | Linear mode (no dynamics) | true | true/false |
| `dual_mono` | Treat mono as dual-mono | false | true/false |

### Platform Targets

| Platform | I (LUFS) | TP (dBTP) | LRA |
|----------|----------|-----------|-----|
| YouTube | -14 | -2 | — |
| Spotify | -14 | -1 | — |
| Netflix | -27 | -2 | — |
| EBU R128 (TV) | -23 or -24 | -1 or -2 | 5-7 |
| Podcasts | -16 | -1.5 | 6 |
| Apple Podcasts | -16 | -1 | — |

## volume

Adjust audio volume.

```bash
# Fixed gain
-af "volume=1.5"               # 50% louder
-af "volume=0.5"               # 50% quieter
-af "volume=3dB"               # +3dB

# Expression-based (dynamic)
-af "volume='if(lt(t,5), 0.5, 1)'"  # Start quiet, ramp to normal

# Fade in/out
-af "afade=t=in:st=0:d=2"      # Fade in over 2 seconds
-af "afade=t=out:st=8:d=2"     # Fade out starting at 8s
```

## aresample

Change sample rate.

```bash
# Simple resample
-af "aresample=48000"

# With options
-af "aresample=48000:first_ts=0:clip=1"

# Or use -ar (simpler)
-ar 48000
```

## atempo

Change playback speed without affecting pitch.

```bash
# Speed up
-af "atempo=1.5"               # 1.5x speed
-af "atempo=2.0"               # 2x speed

# Slow down
-af "atempo=0.5"               # 0.5x speed
-af "atempo=0.75"              # 0.75x speed

# Range: 0.5 to 2.0 per filter. Chain for extreme values:
-af "atempo=2.0,atempo=2.0"    # 4x speed
-af "atempo=0.5,atempo=0.5"    # 0.25x speed
```

## pan

Change channel layout.

```bash
# Stereo to mono
-af "pan=mono|c0=0.5*FL+0.5*FR"

# Mono to stereo
-af "pan=stereo|c0=c0|c1=c0"

# Left channel only
-af "pan=stereo|c0=FL|c1=FL"

# Custom 5.1 layout
-af "pan=5.1|FL=0.5*FL+0.5*FR|FR=0.5*FL+0.5*FR|FC=0.5*FL+0.5*FR|LFE=0|BL=0|BR=0"

# Center channel extraction
-af "pan=mono|c0=FC"
```

## amix

Mix multiple audio streams into one.

```bash
# Mix two audio tracks
-filter_complex "[0:a][1:a]amix=inputs=2:duration=longest"

# Mix with normalization
-filter_complex "[0:a][1:a]amix=inputs=2:duration=shortest:dropout_transition=2"

# Parameters
# inputs=N        Number of input streams
# duration        longest, shortest, or first
# dropout_transition  Seconds for fade when a stream ends (0-10)
```

## amerge

Combine audio streams side-by-side (increases channel count).

```bash
# Merge stereo + mono = 3-channel
-filter_complex "[0:a][1:a]amerge=inputs=2"

# Merge two stereo = 4-channel
-filter_complex "[0:a][1:a]amerge=inputs=2[out]"
```

## equalizer / superequalizer / anequalizer

Frequency equalization.

```bash
# Simple peaking EQ (single band)
-af "equalizer=f=1000:width_type=h:width=1.0:g=6"
# f= center frequency, width_type=h/hb/q, width= bandwidth, g= gain in dB

# Multiple bands (chain)
-af "equalizer=f=315:width_type=h:width=1.0:g=3,\
equalizer=f=1000:width_type=h:width=1.0:g=-2,\
equalizer=f=4000:width_type=h:width=1.0:g=4"

# superequalizer (15-band graphic EQ)
-af "superequalizer=b1_g=3:b2_g=2:b3_g=0:b4_g=-1:b5_g=2"

# anequalizer (multi-band parametric)
-af "anequalizer=g1=0:g2=3:g3=0:g4=-2:g5=0:g6=0:g7=1"
```

## acompressor

Dynamic range compression.

```bash
-af "acompressor=attack=200:release=1000:threshold=0.09:\
ratio=9:output_gain=10:attack_curve=2:release_curve=2:knee=1"
```

## alimiter

Prevent clipping.

```bash
-af "alimiter=limit=1:attack=1:release=10"
```

## dynaudnorm

Dynamic audio normalization.

```bash
-af "dynaudnorm=f=300:gmax=20:gain=0.5:sdetect=1"
```

## Compand

Compression/expansion with multiple bands.

```bash
-af "compand=0.3:0.3:-42/-60/-30/-30/-20/-20/-7/-7:6:points=0/-40|-1/-40|-4/-40|-100/-100:100:0:60"
```

## Audio Noise Reduction

```bash
# anlmdn — spectral noise reduction
-af "anlmdn nsf=0.1"

# arnndn — neural network denoiser (requires trained model)
-af "arnndn=model=voice"

# afftdn — FFT noise reduction
-af "afftdn=nf=-25:tpr=40"

# highpass/lowpass — remove frequency ranges
-af "highpass=f=100"            # Remove frequencies below 100Hz
-af "lowpass=f=8000"            # Remove frequencies above 8kHz
```

## Audio Sources

```bash
# Generate silence
-af "apad=whole_packets=1"

# Generate tone
-af "aevalsrc=sin(440*PI*2*t):s=48000"

# Noise
-af "anoisesrc=s=10000"
```

## Common Patterns

### Podcast mastering chain

```bash
-af "highpass=f=80,lowpass=f=12000,\
acompressor=attack=200:release=1000:threshold=0.09:ratio=4:output_gain=8,\
loudnorm=I=-16:TP=-1.5:LRA=6"
```

### Voice cleanup

```bash
-af "highpass=f=100,lowpass=f=8000,\
anlmdn nsf=0.1,\
acompressor=attack=200:release=1000:threshold=0.09:ratio=4,\
volume=1.5"
```

### Music loudness for streaming

```bash
# YouTube target
-af "loudnorm=I=-14:TP=-2:LRA=7:print_format=summary"

# Spotify target
-af "loudnorm=I=-14:TP=-1:LRA=7:print_format=summary"
```

### Speed change with pitch correction

```bash
# 1.5x speed, maintain pitch
-af "atempo=1.5"

# Combine with video speed change
ffmpeg -i input.mp4 -filter_complex \
  "[0:v]setpts=PTS/1.5[v];[0:a]atempo=1.5[a]" \
  -map "[v]" -map "[a]" output.mp4
```

### Audio trim and crossfade

```bash
-filter_complex \
  "[0:a]atrim=0:10,asetpts=PTS-PTS_START[a1];\
   [0:a]atrim=10:20,asetpts=PTS-PTS_START[a2];\
   [a1][a2]acrossfade=d=1[out]"
```

### Audio normalization (peak)

```bash
# Normalize to peak -1dB
-af "alimiter=limit=-1dB:attack=1:release=10"
```
