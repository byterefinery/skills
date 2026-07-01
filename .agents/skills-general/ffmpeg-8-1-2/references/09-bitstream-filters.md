# Bitstream Filters

Bitstream filters (BSFs) operate on encoded packets without decoding. They are applied with `-bsf:v` (video) or `-bsf:a` (audio).

## Usage

```bash
# Apply to all video streams
-bsf:v filter_name

# Apply to specific stream
-bsf:v:0 filter_name

# Multiple filters (comma-separated)
-bsf:v "filter1=option=val;filter2"
```

## Common Video Bitstream Filters

### h264_mp4toannexb

Convert H.264 from AVCC (MP4) to Annex B format. Required for MPEG-TS output.

```bash
# MP4 to TS (needs this filter)
ffmpeg -i input.mp4 -c copy -bsf:v h264_mp4toannexb output.ts

# Often automatic when muxer detects the need
ffmpeg -i input.mp4 -c copy -f mpegts output.ts
```

### hevc_mp4toannexb

Same as above but for HEVC/H.265.

```bash
ffmpeg -i input.mp4 -c copy -bsf:v hevc_mp4toannexb output.ts
```

### h264_metadata / hevc_metadata

Modify codec parameters in the bitstream without re-encoding.

```bash
# Change frame rate in H.264 bitstream
-bsf:v "h264_metadata=fps=30"

# Set level
-bsf:v "h264_metadata=level=4.2"

# Set profile
-bsf:v "h264_metadata=profile=main"

# Change color properties
-bsf:v "h264_metadata=color_range=1;color_primaries=1;transfer_characteristics=1;matrix_coefficients=1"

# Set HDR metadata (static)
-bsf:v "hevc_metadata=smpte2086_mastering_display_color_volume=G(13250,34500)B(7500,3000)R(64000,33000)WP(31270,32900)L(10000000,1);smpte2086_max_cll=4000;smpte2086_max_fall=1500"

# Change timebase
-bsf:v "h264_metadata=timebase=1/60"
```

### av1_metadata

Modify AV1 bitstream metadata.

```bash
# Set color range
-bsf:v "av1_metadata=color_range=1"

# Set HDR metadata
-bsf:v "av1_metadata=smpte2086_mastering_display_color_volume=..."
```

### extract_extradata

Extract extradata (SPS/PPS) from packets into the stream header. Useful for some players.

```bash
-bsf:v extract_extradata
```

### dump_extra

Insert extradata before every keyframe. Useful for some streaming scenarios.

```bash
-bsf:v dump_extra
```

### remove_extra

Remove extradata from packets.

```bash
-bsf:v remove_extra
```

### chomp

Remove zero-padding from packets.

```bash
-bsf:v chomp
```

### noise

Add noise to the bitstream (for testing robustness).

```bash
-bsf:v "noise=bitrate=1000:error_rate=0.001"
```

### filter_units

Filter out specific NAL unit types.

```bash
# Remove SEI NAL units
-bsf:v "filter_units=remove_types=6"

# NAL unit types: 1=Coded slice, 2=Coded slice A, 3=Coded slice B,
# 4=Coded slice IDR, 5=SEI, 6=SPS, 7=PPS, 8=AUD, 9=End of seq, 10=End of stream
```

## Common Audio Bitstream Filters

### aac_adtstoasc

Convert AAC from ADTS to ASC format. Required when putting AAC into MP4/MOV.

```bash
# ADTS AAC to MP4
ffmpeg -i input.aac -c copy -bsf:a aac_adtstoasc output.mp4
```

### dca_core

Extract core stream from DTS-HD bitstream.

```bash
-bsf:a dca_core
```

### eac3_core

Extract core stream from E-AC-3 (Dolby Digital Plus) bitstream.

```bash
-bsf:a eac3_core
```

### eia608_to_smpte436m

Convert EIA-608 closed captions to SMPTE 436M.

```bash
-bsf:a eia608_to_smpte436m
```

## Subtitle Bitstream Filters

### mov2textsub

Convert MOV text subtitles to text format.

```bash
-bsf:s mov2textsub
```

### pgs_frame_merge

Merge PGS subtitle field pairs into single frames.

```bash
-bsf:s pgs_frame_merge
```

## Practical Patterns

### H.264 to MPEG-TS

```bash
ffmpeg -i input.mp4 -c copy -bsf:v h264_mp4toannexb -f mpegts output.ts
```

### Fix H.264 level for compatibility

```bash
# Force level 3.0 for older devices
ffmpeg -i input.mp4 -c copy -bsf:v "h264_metadata=level=3.0" output.mp4
```

### Add HDR metadata to existing stream

```bash
ffmpeg -i input.mp4 -c copy \
  -bsf:v "hevc_metadata=smpte2086_mastering_display_color_volume=G(13250,34500)B(7500,3000)R(64000,33000)WP(31270,32900)L(10000000,1);smpte2086_max_cll=4000;smpte2086_max_fall=1500" \
  output.mp4
```

### Convert AAC for MP4

```bash
ffmpeg -i input.aac -c copy -bsf:a aac_adtstoasc -f mp4 output.mp4
```

### Remove padding for smaller files

```bash
ffmpeg -i input.mp4 -c copy -bsf:v chomp output.mp4
```

### Extract SPS/PPS for RTSP

```bash
ffmpeg -i input.mp4 -c copy -bsf:v extract_extradata -f rtp rtp://server:port
```

## Listing Bitstream Filters

```bash
# List all BSFs
ffmpeg -bsfs

# Get help on specific BSF
ffmpeg -help bsf=h264_metadata
```

## Gotchas

- **BSFs only work on encoded data**: you cannot apply a BSF to a stream that is being decoded or encoded. Use `-c copy` for streamcopy.
- **Order matters**: when multiple BSFs are applied, they run in the order specified.
- **Not all muxers need explicit BSFs**: ffmpeg often auto-applies `h264_mp4toannexb` when muxing H.264 to MPEG-TS. Explicit specification ensures it happens.
- **Metadata BSFs may not persist**: some players ignore bitstream metadata. For reliable HDR/color metadata, re-encode or use proper container metadata.
