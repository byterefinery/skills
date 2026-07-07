# Audio & FFmpeg

## audio

Converts and compresses audio files to web-compatible formats.

### Import

```ts
import { audio } from '@assetpack/core/ffmpeg';
```

### Usage

```ts
audio()  // Default options

audio({
    inputs: ['.mp3', '.ogg', '.wav'],
    outputs: [
        {
            formats: ['.mp3'],
            recompress: false,
            options: {
                audioBitrate: 96,
                audioChannels: 1,
                audioFrequency: 48000,
            },
        },
        {
            formats: ['.ogg'],
            recompress: false,
            options: {
                audioBitrate: 32,
                audioChannels: 1,
                audioFrequency: 22050,
            },
        },
    ],
});
```

### Default Options

```ts
{
    inputs: ['.mp3', '.ogg', '.wav'],
    outputs: [
        {
            formats: ['.mp3'],
            recompress: false,
            options: {
                audioBitrate: 96,
                audioChannels: 1,
                audioFrequency: 48000,
            },
        },
        {
            formats: ['.ogg'],
            recompress: false,
            options: {
                audioBitrate: 32,
                audioChannels: 1,
                audioFrequency: 22050,
            },
        },
    ],
}
```

### Behavior

- Processes `.mp3`, `.ogg`, `.wav` files by default
- Outputs both `.mp3` and `.ogg` variants
- `recompress: false` skips conversion if input format matches output format
- Mono output by default (1 channel)

### Example

```
Input:  music.wav
Output: music.mp3   (96kbps, mono, 48kHz)
        music.ogg   (32kbps, mono, 22050Hz)
```

---

## ffmpeg

General-purpose FFmpeg conversion pipe. Supports any format conversion.

### Import

```ts
import { ffmpeg } from '@assetpack/core/ffmpeg';
```

### Usage

```ts
ffmpeg({
    inputs: ['.mp4', '.webm'],
    outputs: [
        {
            formats: ['.mp4'],
            recompress: true,
            options: {
                videoCodec: 'libx264',
                audioCodec: 'aac',
                videoBitrate: 1000,
                audioBitrate: 128,
                fps: 30,
            },
        },
    ],
});
```

### Options

```ts
interface FfmpegOptions {
    name?: string;
    inputs: string[];                           // Input extensions
    outputs: {
        formats: string[];                      // Output extensions
        recompress: boolean;                    // Re-encode even if format matches
        options: Partial<FfmpegCommands>;       // FFmpeg command options
    }[];
}
```

### Available FFmpeg Options

Input: `inputFormat`, `inputFPS`, `native`, `seekInput`, `loop`
Audio: `noAudio`, `audioCodec`, `audioBitrate`, `audioChannels`, `audioFrequency`, `audioQuality`
Video: `noVideo`, `videoCodec`, `videoBitrate`, `fps`, `frames`
Video size: `size`, `aspect`, `autopad`, `keepDAR`
Output: `seek`, `duration`, `format`, `flvmeta`

### Behavior

- Processes files matching any extension in `inputs`
- Each `outputs` entry creates one output file
- If `recompress` is false and input format matches output, file is copied instead of re-encoded
- FFmpeg options are passed directly to fluent-ffmpeg command methods
