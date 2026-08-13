# Building from Source

## Prerequisites

### Build Tools

| Platform | Requirements |
|----------|-------------|
| Linux/macOS | GCC or Clang, GNU make, autoconf (git only) |
| Windows | MSVC (Visual Studio 2015+), nmake |
| BSD | GCC or Clang, GNU make, autoconf |

### Optional Dependencies

| Library | Purpose | Configure Flag |
|---------|---------|----------------|
| Tesseract + Leptonica | OCR devices | `--with-tesseract` / `--without-tesseract` |
| CUPS | CUPS printer drivers | `--enable-cups` / `--disable-cups` |
| Fontconfig | System font discovery | `--enable-fontconfig` / `--disable-fontconfig |
| libpaper | Paper size defaults | `--with-libpaper` |
| libtiff | TIFF support | bundled by default |
| libjpeg | JPEG support | bundled by default |
| zlib | Compression | bundled by default |
| libpng | PNG support | bundled by default |
| OpenJPEG | JPEG 2000 support | `--enable-openjpeg` / `--disable-openjpeg` |
| FreeType | Font rendering | bundled by default |
| brotli | Brotli compression | bundled by default |
| expat | XML parsing (XPS) | bundled by default |
| lcms2 | Color management | bundled (modified) |

## Unix/Linux/macOS Build

### From Release Tarball

```bash
tar xzf ghostpdl-10.07.1.tar.gz
cd ghostpdl-10.07.1

./configure
make
sudo make install
```

### From Git Checkout

```bash
git clone https://github.com/ArtifexSoftware/ghostpdl.git
cd ghostpdl
git checkout ghostpdl-10.07.1

# Generate configure script (not needed for tarballs)
./autogen.sh

./configure
make
sudo make install
```

### Configure Options

```bash
# Full build with everything
./configure \
  --enable-cups \
  --enable-fontconfig \
  --enable-openjpeg \
  --enable-threading \
  --with-tesseract \
  --with-tessdata=/usr/share/tesseract-ocr/4.00/tessdata

# Minimal build (GS only, no PCL/XPS)
./configure \
  --with-gs=gs \
  --without-pcl \
  --without-xps \
  --disable-cups \
  --disable-fontconfig

# Shared library
./configure --enable-shared
make so

# Custom prefix
./configure --prefix=/opt/ghostscript
make
make install

# Custom executable names
./configure --with-gs=mygs --with-pcl=mygpcl --with-xps=mygxps --with-pdf=mygpdf --with-gpdl=mygpdl

# Disable specific features
./configure \
  --disable-cups \
  --disable-openjpeg \
  --disable-fontconfig \
  --disable-dbus \
  --without-tesseract \
  --without-urf

# Select specific drivers
./configure --with-drivers="png16m pdfwrite jpeg tiff24nc"

# Sanitizer builds (debugging)
./configure --with-sanitizer=address
make

# Threading support
./configure --enable-threading
make
```

### Make Targets

| Target | Description |
|--------|-------------|
| `make` | Build all executables |
| `make so` | Build shared library (`libgs.so`) |
| `make sodebug` | Build shared library (debug) |
| `make clean` | Clean build artifacts |
| `make install` | Install to prefix |
| `make uninstall` | Uninstall |
| `make check` | Run tests |
| `make pdf` | Build PDF interpreter only |
| `make pcl` | Build PCL interpreter only |
| `make xps` | Build XPS interpreter only |

### Installation Paths

```bash
# Default prefix: /usr/local
# Binaries: /usr/local/bin/gs, /usr/local/bin/gpdf, ...
# Libraries: /usr/local/lib/libgs.so
# Resources: /usr/local/share/ghostscript/10.07.1/
# Man pages: /usr/local/man/man1/

# Custom prefix
./configure --prefix=/opt/ghostscript
# Binaries: /opt/ghostscript/bin/
# Resources: /opt/ghostscript/share/ghostscript/10.07.1/
```

## Windows Build

### Visual Studio

```cmd
# Open Developer Command Prompt
cd ghostpdl

# Generate makefiles (if from git)
autogen.sh  # needs autoconf/make from MSYS2 or similar

# Build with nmake
nmake -f win32.mak

# Or use Visual Studio solution
devenv.com windows/GhostPDL.sln /Build Release
```

### MSYS2 / MinGW

```bash
# Install build tools
pacman -S gcc make autoconf libtool

# Build
./autogen.sh
./configure
make
make install
```

## macOS Build

```bash
# Using Homebrew
brew install ghostscript

# From source
./autogen.sh
./configure
make
sudo make install

# Shared library
./configure --enable-shared
make so
```

## Build Components

### Selective Interpreter Build

```bash
# Ghostscript only
./configure --with-gs=gs --without-pcl --without-xps --without-pdf --without-gpdl

# Ghostscript + PCL
./configure --with-gs=gs --with-pcl=pcl6 --without-xps

# All interpreters (default)
./configure
```

### Selective Driver Build

```bash
# Only specific output devices
./configure --with-drivers="png16m pdfwrite jpeg tiff24nc bmp16m"

# All drivers (default)
./configure --with-drivers=ALL

# List available driver groups
./configure --help | grep drivers
```

## Shared Library

### Building

```bash
./configure --enable-shared
make so
```

### Linking

```bash
# Unix
gcc -o myapp myapp.c -L/path/to/gs/lib -lgs -lpthread -lm

# Set library path at runtime
export LD_LIBRARY_PATH=/path/to/gs/lib:$LD_LIBRARY_PATH

# Or use rpath
gcc -o myapp myapp.c -L/path/to/gs/lib -lgs -Wl,-rpath,/path/to/gs/lib
```

### Resource Files

The shared library needs access to Ghostscript resource files at runtime:

```bash
# Set resource path
export GS_LIB=/path/to/gs/share/ghostscript/10.07.1

# Or install to standard location
sudo make install
```

## Debugging

```bash
# Debug build
./configure --enable-debug
make debug

# With sanitizers
./configure --with-sanitizer=address
make

# With extra debug flags
GS_DEBUG=-d1024 gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite -sOutputFile=out.pdf input.ps
```

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `GS_LIB` | Resource file search path |
| `GS_LIB64` | 64-bit resource path |
| `GS_FONTPATH` | Font search path |
| `GS_DEVICE` | Default output device |
| `GSCOLORDEVICE` | Default color device |
| `GS_DLL` | DLL path (Windows) |
| `LD_LIBRARY_PATH` | Shared library path (Unix) |

## Common Build Errors

| Error | Fix |
|-------|-----|
| `autoconf not found` | Install autoconf: `apt install autoconf` or `brew install autoconf` |
| `C++ compiler needed for OCR` | Install g++ or use `--without-tesseract` |
| `threading disabled, tesseract needs it` | Use `--enable-threading` or `--without-tesseract` |
| `libtiff not found` | Use bundled: ensure `--without-system-libtiff` |
| `Fontconfig not found` | Install libfontconfig-dev or use `--disable-fontconfig` |
| `CUPS not found` | Install libcups2-dev or use `--disable-cups` |
| `X11 headers not found` | Install libx11-dev or disable X11 devices |

## Cross-Compilation

```bash
# ARM cross-compile
./configure \
  --host=arm-linux-gnueabihf \
  --prefix=/opt/arm-gs \
  --without-x \
  --disable-cups \
  --disable-fontconfig

make
make install
```
