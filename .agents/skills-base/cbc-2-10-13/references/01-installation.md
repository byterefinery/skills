# Installation and Building

## Package Managers

### Linux (Debian/Ubuntu)
```bash
sudo apt-get install coinor-cbc coinor-libcbc-dev
```

### Linux (Fedora/RHEL/CentOS)
```bash
sudo dnf install coin-or-Cbc coin-or-Cbc-devel
```

### Arch Linux
```bash
sudo pacman -S coin-or-cbc
```

### macOS (Homebrew)
```bash
brew tap coin-or-tools/coinor
brew install coin-or-tools/coinor/cbc
```

### Conda (cross-platform)
```bash
conda install coin-or-cbc
```

### Docker
```bash
docker pull coinor/coin-or-optimization-suite
```

## Building from Source

### Using coinbrew (recommended)

```bash
wget https://raw.githubusercontent.com/coin-or/coinbrew/master/coinbrew
chmod u+x coinbrew
./coinbrew fetch Cbc@2.10.13
./coinbrew build Cbc
```

coinbrew automatically fetches all dependencies (CoinUtils, Osi, Clp, Cgl).

### Manual build (autotools)

Prerequisites: CoinUtils 2.11+, Osi 0.108+, Clp 1.17+, Cgl 0.60+, pkg-config.

```bash
./configure -C
make
make test
make install
```

Configure flags of interest:
- `--enable-debug` — debug build
- `--disable-cbc-parallel` — disable multi-threading (enabled by default if pthread found)
- `--enable-gnu-packages` — enable readline for interactive shell
- `--with-*-cflags` / `--with-*-lflags` — specify dependency paths

### pkg-config

After installation, use pkg-config to find headers and libraries:

```bash
pkg-config --cflags coin-or-Cbc
pkg-config --libs coin-or-Cbc

# Compile
g++ -o prog prog.cpp $(pkg-config --cflags --libs coin-or-Cbc coin-or-OsiClp coin-or-Clp coin-or-CoinUtils)
```

Headers install to `$prefix/include/coin-or/`.

### Visual Studio

Project files are in `Cbc/MSVisualStudio/` for v9, v10, v14, and v17. Open the solution file and build. For parallel support on Windows, define `CBC_THREAD` and link against pthreads-win32.

## Dependencies

### Required
- **CoinUtils** — COIN-OR utilities (vectors, matrices)
- **Osi** — Open Solver Interface (abstract solver interface)
- **Clp** — COIN-OR Linear Programming solver (LP relaxation solver)
- **Cgl** — COIN-OR Cut Generation Library (cut generators)

### Recommended
- BLAS/LAPACK — faster LP solves
- GNU Readline/History — interactive CLI shell

### Optional
- ASL (Ampl Solver Library) — AMPL/GMPL interface
- GLPK — alternative LP solver backend
- Metis — graph partitioning for symmetry detection
- MUMPS — sparse direct solver for LP
- nauty — symmetry detection
