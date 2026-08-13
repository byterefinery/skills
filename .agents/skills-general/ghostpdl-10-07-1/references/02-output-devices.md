# Output Devices

## Device Categories

Ghostscript devices fall into these categories: raster image writers, vector/document writers, printer drivers, and special-purpose devices.

## Raster Image Devices

### PNG

| Device | Description |
|--------|-------------|
| `png16m` | 24-bit RGB color PNG |
| `png16malpha` | 32-bit RGBA PNG (with alpha) |
| `pngalpha` | 32-bit RGBA PNG (alternative) |
| `png256` | 8-bit palette PNG (256 colors) |
| `png16` | 4-bit palette PNG (16 colors) |
| `pnggray` | 8-bit grayscale PNG |
| `pngmonod` | 1-bit monochrome PNG (dithered) |
| `pngmono` | 1-bit monochrome PNG |

```bash
gs -dBATCH -dNOPAUSE -sDEVICE=png16m -r300 -sOutputFile=page_%03d.png input.pdf
```

### JPEG

| Device | Description |
|--------|-------------|
| `jpeg` | Full-color JPEG |
| `jpeggray` | Grayscale JPEG |

JPEG parameters (via `-c` dict or device params):
- `JPEGQ=N` — Quality (1-100, default 75)
- `DCTEncode` — DCT encoding method

```bash
gs -dBATCH -dNOPAUSE -sDEVICE=jpeg -r150 -sOutputFile=page.jpg input.pdf
```

### TIFF

| Device | Description |
|--------|-------------|
| `tiff24nc` | 24-bit RGB TIFF, no compression |
| `tiff32nc` | 32-bit RGBA TIFF, no compression |
| `tiff24n` | 24-bit RGB TIFF, no compression (legacy) |
| `tiff32n` | 32-bit RGBA TIFF, no compression (legacy) |
| `tiffgray` | 8-bit grayscale TIFF |
| `tiff12nc` | 12-bit RGB TIFF, no compression |
| `tiff12n` | 12-bit RGB TIFF, no compression (legacy) |
| `tiff16nc` | 16-bit RGB TIFF, no compression |
| `tiff16n` | 16-bit RGB TIFF, no compression (legacy) |
| `tiffg4` | Group 4 CCITT fax TIFF (1-bit) |
| `tiffg3` | Group 3 CCITT fax TIFF (1-bit) |
| `tiffg32d` | Group 3 2D CCITT fax TIFF |
| `tiffpack` | Packbits compressed TIFF |
| `tiffl2` | LZW compressed TIFF |
| `tiffcrd` | Packbits TIFF with color reduction |
| `tiffcrle` | RLE TIFF with color reduction |
| `tiffjpeg` | JPEG-compressed TIFF |

### BMP

| Device | Description |
|--------|-------------|
| `bmp16m` | 24-bit RGB BMP |
| `bmp256` | 8-bit palette BMP |
| `bmp16` | 4-bit palette BMP |
| `bmpgray` | 8-bit grayscale BMP |
| `bmpmono` | 1-bit monochrome BMP |
| `bmpsep1` | 1-bit separated BMP |
| `bmpsep8` | 8-bit separated BMP |
| `bmpsep16` | 4-bit separated BMP |
| `bmpsep16m` | 24-bit separated BMP |
| `bmpa16m` | 24-bit BMP with alpha |
| `bmpgray` | 8-bit grayscale BMP |

### Other Image Formats

| Device | Description |
|--------|-------------|
| `pcx16m` | 24-bit PCX |
| `pcx256` | 8-bit palette PCX |
| `pcx16` | 4-bit palette PCX |
| `pcxgray` | 8-bit grayscale PCX |
| `pcxmono` | 1-bit monochrome PCX |
| `psd` | Adobe Photoshop PSD |
| `psd2` | PSD version 2 (with alpha support) |
| `pam` | Netpbm PAM (portable anymap) |
| `ppmraw` | Raw PPM (P6) |
| `ppm` | ASCII PPM (P3) |
| `pgm` | PGM (grayscale) |
| `pgn` | PGM (grayscale, alternative) |
| `pbmraw` | Raw PBM (P4) |
| `pbm` | ASCII PBM (P1) |
| `tga256` | 8-bit Targa |
| `tga16m` | 24-bit Targa |
| `tga16malpha` | 32-bit Targa with alpha |
| `sgi` | SGI RGB image |
| `miff` | MIFF (MEF Image File Format) |
| `sunras` | Sun Rasterfile |
| `x11bmp` | X11 bitmap |
| `pxlmono` | PXL monochrome |
| `pxlcolor` | PXL color |
| `jetplot` | JetPlot pen plotter |
| `cchart` | Color chart generator |

## Vector/Document Devices

### PDF

| Device | Description |
|--------|-------------|
| `pdfwrite` | PDF writer (converts PS/PDF/images to PDF) |

`pdfwrite` is the most feature-rich device. It supports:
- PDF 1.0 through 2.0 output (via `-dCompatibilityLevel`)
- Font embedding and subsetting
- Image compression (JPEG, Flate, JBIG2, JPEG 2000)
- Color management and ICC profiles
- Transparency and blend modes
- Optional content groups (OCGs)
- PDF/X, PDF/A output (with proper settings)
- N-up imposition
- Booklet and saddle-stitch modes
- Linearization (web-optimized PDF)

```bash
gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
   -dCompatibilityLevel=1.7 \
   -dPDFSETTINGS=/prepress \
   -sOutputFile=output.pdf input.ps
```

### PostScript

| Device | Description |
|--------|-------------|
| `ps2write` | PostScript Level 2 writer |
| `ps3write` | PostScript Level 3 writer |
| `eps2write` | EPS writer (Level 2) |
| `eps3write` | EPS writer (Level 3) |
| `ps2ascii` | ASCII PostScript (encoded) |

```bash
# PDF to PostScript Level 2
gs -dBATCH -dNOPAUSE -sDEVICE=ps2write -sOutputFile=out.ps input.pdf

# PDF to PostScript Level 3
gs -dBATCH -dNOPAUSE -sDEVICE=ps3write -sOutputFile=out.ps input.pdf

# PS to EPS
gs -dBATCH -dNOPAUSE -sDEVICE=eps2write -sOutputFile=out.eps input.ps
```

## Printer Devices

### CUPS

| Device | Description |
|--------|-------------|
| `cups` | CUPS raster driver (generates CUPS-raster format) |
| `cupsated` | CUPS for AT&T devices |
| `cupsdaver` | CUPS for Davex devices |
| `cupsdsaver` | CUPS for DSaver devices |

CUPS device generates output suitable for CUPS backend processing. Requires CUPS library at build time.

```bash
gs -sDEVICE=cups -sOutputFile=- -dBATCH -dNOPAUSE input.pdf | lp -d printer
```

### HP LaserJet

| Device | Description |
|--------|-------------|
| `ljet4` | HP LaserJet 4 |
| `ljet3` | HP LaserJet 3 |
| `ljet2p` | HP LaserJet 2 Plus |
| `ljet2` | HP LaserJet 2 |
| `lj550` | HP LaserJet 550 |
| `lj550n` | HP LaserJet 550 (no color) |
| `lj550color` | HP LaserJet 550 color |
| `ljpcl` | HP LaserJet PCL |
| `ljsolid` | HP LaserJet solid formatting |
| `lj4dith` | HP LaserJet 4 dithered |
| `hl750` | HP LaserJet 750 |
| `hl7xgd2` | HP LaserJet 7x (GD2) |
| `hl1250` | HP LaserJet 1250 |

### Other Printers

| Device | Description |
|--------|-------------|
| `epson` | Epson FX-80 |
| `epson102` | Epson FX-1020 |
| `epsonc` | Epson color |
| `cdj1600` | Kodak ColorQ 1600 |
| `cdj330` | Kodak ColorQ 330 |
| `cdj350` | Kodak ColorQ 350 |
| `cdj395` | Kodak ColorQ 395 |
| `cdj550` | Kodak ColorQ 550 |
| `cdj550_300` | Kodak ColorQ 550 (300 dpi) |
| `bj10v` | Brother HL-1070 |
| `bj10vhigh` | Brother HL-1070 (high res) |
| `bj200` | Brother HL-2040 |
| `bjc800` | Brother Color 800 |
| `bjc880` | Brother Color 880 |
| `djet500` | Brother DCP-5690EN |
| `dx` | IBM DX |
| `r4081` | OKI PagePro 12/16/18 |
| `r4693` | OKI PagePro 12/16/18 (4693) |
| `min1200w` | Minolta PagePro 1200/1200WT |
| `min1200h` | Minolta PagePro 1200/1200WT (high) |
| `min1500` | Minolta PagePro 1500 |
| `bjc600` | Brother Color 600 |
| `bjc700` | Brother Color 700 |
| `bjc700hj` | Brother Color 700 (high) |
| `bjc700h` | Brother Color 700 (high) |
| `bjc700v` | Brother Color 700 (v) |
| `bjc800` | Brother Color 800 |
| `cxmono` | Canon LBP-SX |
| `cxcolor` | Canon LBP-SX color |
| `lbp8` | Canon LBP8 |
| `lbp6` | Canon LBP6 |
| `lbp5` | Canon LBP5 |
| `lbp4` | Canon LBP4 |
| `lbp250` | Canon LBP250 |
| `lbp300` | Canon LBP300 |
| `lbp500` | Canon LBP500 |

## Special Devices

| Device | Description |
|--------|-------------|
| `bbox` | Calculate bounding box (EPS analysis) |
| `nullpage` | Discard all output (validation) |
| `test` | Test device (no output) |
| `textonly` | Extract text as PostScript comments |
| `ink_cov` | Ink coverage analysis |
| `inkcov` | Ink coverage (alternative) |
| `bit` | 1-bit monochrome output |
| `bitcpy` | 1-bit copy |
| `bitrgb` | 24-bit RGB (1-bit per channel) |
| `bitrgb16` | 48-bit RGB (2-bit per channel) |
| `bitrgb256` | 24-bit RGB (8-bit per channel) |
| `plan9rgb` | Plan 9 RGB |
| `ppam` | Netpbm PAM (planar) |
| `pgm` | PGM (grayscale) |
| `pgmgray` | PGM (grayscale, explicit) |
| `pgn` | PGM (alternative) |
| `tiffb4` | 4-bit TIFF |
| `tiffb8` | 8-bit TIFF |
| `faxthumbley` | Humbley fax format |
| `setdev` | Device setter (for testing) |
| `x11alpha` | X11 display with alpha |
| `xrgb` | X11 RGB display |
| `x11bg` | X11 with background |
| `x11c16` | X11 16-color |
| `x11c256` | X11 256-color |
| `x11c4` | X11 4-color |
| `x11color` | X11 color |
| `x11_mono` | X11 monochrome |

## OCR Devices

Requires build with Tesseract and Leptonica.

| Device | Description |
|--------|-------------|
| `ocrps` | OCR with PostScript text overlay |
| `ocrqpdf` | OCR with PDF text overlay (quicker) |
| `ocrhocr` | OCR with hOCR HTML output |
| `ocrpdf` | OCR with full PDF re-rendering |

Parameters:
- `-sOCRLanguage=eng` — Tesseract language (default: `eng`)
- `-dOCREngine=N` — Engine mode (0=default, 1=LSTM, 2=legacy, 3=both)

```bash
gs -dBATCH -dNOPAUSE -sDEVICE=ocrps \
   -sOCRLanguage=eng+deu \
   -sOutputFile=searchable.pdf scanned.pdf
```

## Device Parameters

Devices accept parameters via `-c` with dictionaries or command-line `-d` flags:

```bash
# Via command line
gs -dNOPAUSE -dBATCH -sDEVICE=png16m -r300 -g48006600 -sOutputFile=out.png input.pdf

# Via PostScript dictionary
gs -sDEVICE=pdfwrite -c "<<
  /AntiImageHeightThreshold 1500
  /ColorACSImageDict << /DownsampleType /Bicubic >>
  /ColorImageDict << /DownsampleType /Bicubic >>
>> setdistillerparams" -f input.ps -sOutputFile=out.pdf
```

Common device parameters:
- `-g<width>x<height>` — Output dimensions in pixels
- `-r<DPI>` — Resolution
- `-dDEVICEWIDTHPOINTS=N` — Width in points
- `-dDEVICEHEIGHTPOINTS=N` — Height in points
- `-dDEVICEWIDTH=M` — Width in device units
- `-dDEVICEHEIGHT=M` — Height in device units
- `-dPagium=N` — Page mode for some devices

## Listing Available Devices

```bash
# From command line
gs -h | grep -A 200 "Available devices:"

# From within Ghostscript
devicenames ==

# List a specific device's parameters
</devicename> finddevice ==
```
