# ImageMagick 7.1.2-26 — APIs

## Table of Contents

- [MagickWand (C API)](#magickwand-c-api)
- [MagickCore (C API)](#magickcore-c-api)
- [Magick++ (C++ API)](#magick-c-c-api)
- [PerlMagick](#perlmagick)
- [Linking and Compilation](#linking-and-compilation)

---

## MagickWand (C API)

High-level C API. Wraps MagickCore with simplified interfaces. Header: `MagickWand/MagickWand.h`.

### Core Types

- `MagickWand` — Image container (like an Image object)
- `DrawingWand` — Drawing/annotation operations
- `PixelWand` — Single pixel color
- `PixelIterator` — Row-by-row pixel access

### Initialization

```c
#include <MagickWand/MagickWand.h>

MagickWandGenesis();           // Initialize library
// ... use API ...
MagickWandTerminus();          // Cleanup
```

### Basic Operations

```c
// Create and read
MagickWand *wand = NewMagickWand();
MagickReadImage(wand, "input.jpg");

// Get info
size_t width = MagickGetImageWidth(wand);
size_t height = MagickGetImageHeight(wand);
size_t channels = MagickGetImageChannels(wand);
double quality = MagickGetImageQuality(wand);

// Resize
MagickResizeImage(wand, 800, 600, LanczosFilter);

// Rotate
MagickRotateImage(wand, pixel_wand, 45.0);

// Write
MagickWriteImage(wand, "output.png");

// Cleanup
wand = DestroyMagickWand(wand);
```

### Drawing

```c
DrawingWand *draw = NewDrawingWand();
PixelWand *fill = NewPixelWand();
PixelInitWand(fill, "red");

DrawSetFillColor(draw, fill);
DrawCircle(draw, 200, 200, 200, 100);

PixelWand *stroke = NewPixelWand();
PixelInitWand(stroke, "blue");
DrawSetStrokeColor(draw, stroke);
DrawSetStrokeWidth(draw, 2);
DrawLine(draw, 50, 50, 300, 300);

MagickDrawImage(wand, draw);

draw = DestroyDrawingWand(draw);
fill = DestroyPixelWand(fill);
stroke = DestroyPixelWand(stroke);
```

### Pixel Access

```c
PixelIterator *iterator = NewPixelIterator(wand);
PixelPacket *pixels;
size_t y;

for (y = 0; y < height; y++) {
    pixels = PixelGetIteratorPixels(iterator, &y);
    if (pixels != (PixelPacket *) NULL) {
        size_t x;
        for (x = 0; x < width; x++) {
            // pixels[x] gives access to pixel at (x, y)
            // Use GetPixelRed(pixels[x]), etc.
        }
        PixelSyncIterator(iterator);  // Write changes back
    }
    iterator = PixelNextIterator(iterator);
}
iterator = DestroyPixelIterator(iterator);
```

### Image Sequence

```c
// Read multiple images
MagickReadImages(wand, "frame*.png");

// Iterate
for (MagickWand *sequence = GetFirstImageWand(wand);
     sequence != (MagickWand *) NULL;
     sequence = GetNextImageWand(wand)) {
    // Process each image
}

// Append
MagickAppendImages(wand, MagickTrue);

// Write multi-frame
MagickWriteImages(wand, "output.gif", MagickTrue);
```

---

## MagickCore (C API)

Low-level C API. Direct access to image internals. Header: `MagickCore/MagickCore.h`.

### Core Types

- `Image` — Single image frame
- `ImageInfo` — Image read/write settings
- `ExceptionInfo` — Error handling
- `PixelPacket` — Individual pixel

### Basic Pattern

```c
#include <MagickCore/MagickCore.h>

MagickCoreGenesis(getenv("HOME"), MagickTrue);

ImageInfo *image_info = CloneImageInfo((ImageInfo *) NULL);
ExceptionInfo *exception = AcquireExceptionInfo();

strcpy(image_info->filename, "input.jpg");
Image *image = ReadImage(image_info, exception);

if (image == (Image *) NULL) {
    // Handle error via exception
}

// Process image...
ResizeImage(image, 800, 600, LanczosFilter);

WriteImage(image_info, image);

image = DestroyImage(image);
image_info = DestroyImageInfo(image_info);
exception = DestroyExceptionInfo(exception);

MagickCoreTerminus();
```

### Quantum Access

```c
// Quantum is the pixel value type (depends on build: Q8, Q16, Q32)
// QuantumRange is the max value (255 for Q8, 65535 for Q16)

Quantum red = GetPixelRed(image, x, y);
Quantum green = GetPixelGreen(image, x, y);
Quantum blue = GetPixelBlue(image, x, y);
Quantum alpha = GetPixelAlpha(image, x, y);

SetPixelRed(image, x, y, new_red);
SetPixelGreen(image, x, y, new_green);
SyncImagePixels(image, exception);
```

---

## Magick++ (C++ API)

C++ object-oriented wrapper. Header: `Magick++.h`.

### Basic Usage

```cpp
#include <Magick++.h>
using namespace Magick;

int main(int argc, char **argv) {
    Magick::InitializeMagick(*argv);

    // Read
    Image image("input.jpg");

    // Get info
    cout << "Size: " << image.columns() << "x" << image.rows() << endl;
    cout << "Type: " << image.type() << endl;

    // Resize
    image.resize("800x600");

    // Rotate
    image.rotate(Degrees(45));

    // Write
    image.write("output.png");

    return 0;
}
```

### Drawing

```cpp
DrawableComposite composite;
DrawableFillColor fill("red");
DrawableStrokeColor stroke("blue");
DrawableStrokeWidth width(2);
DrawableCircle circle(200, 200, 200, 100);
DrawableLine line(50, 50, 300, 300);

image.draw(fill);
image.draw(circle);
image.draw(stroke);
image.draw(width);
image.draw(line);
```

Drawable objects: `DrawableCircle`, `DrawableEllipse`, `DrawableLine`, `DrawablePolygon`, `DrawablePolyline`, `DrawableRectangle`, `DrawableRoundRectangle`, `DrawablePath`, `DrawableText`, `DrawableFillColor`, `DrawableStrokeColor`, `DrawableStrokeWidth`, `DrawableFont`, `DrawableFontSize`, `DrawableGravity`, `DrawableTranslate`, `DrawableRotate`, `DrawableScale`, `DrawableShear`, `DrawableSkewX`, `DrawableSkewY`, `DrawableComposite`, `DrawablePush`, `DrawablePop`.

### Image Sequence

```cpp
// Read sequence
Image images[10];
ReadImages(images, 10, "frame*.png");

// Combine
Image combined;
CombineImages(&combined, images, 10);

// Write animation
WriteImages(images, 10, "animation.gif");
```

---

## PerlMagick

Perl binding (if built with Perl support).

```perl
use Image::Magick;

my $magick = Image::Magick->new;
$magick->Read('input.jpg');
$magick->Resize(geometry => '800x600');
$magick->Write('output.png');
```

---

## Linking and Compilation

### Find Headers and Libraries

```bash
# pkg-config
pkg-config --cflags MagickWand
pkg-config --libs MagickWand

pkg-config --cflags MagickCore
pkg-config --libs MagickCore

pkg-config --cflags Magick++
pkg-config --libs Magick++
```

### Compile Examples

```bash
# C with MagickWand
gcc -o program program.c $(pkg-config --cflags --libs MagickWand)

# C with MagickCore
gcc -o program program.c $(pkg-config --cflags --libs MagickCore)

# C++ with Magick++
g++ -o program program.cpp $(pkg-config --cflags --libs Magick++)
```

### Quantum Depth

The build determines quantum depth:
- Q8: 8-bit per channel (less memory, less precision)
- Q16: 16-bit per channel (default, good balance)
- Q32: 32-bit per channel (maximum precision)

HDRI mode uses floating-point Quantum for out-of-range values.

Check with: `magick -version` (shows Quantum depth and HDRI status).
