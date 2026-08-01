# Building from Source — ONNX Runtime 1.28.0

## Prerequisites

- **Python 3.8+** (3.10+ recommended)
- **CMake 3.24+**
- **C++17 compiler** — GCC 11+, Clang 14+, MSVC 14.40+
- **Git** with submodule support

## Quick Build (Linux)

```bash
git clone --branch v1.28.0 --depth 1 https://github.com/microsoft/onnxruntime.git
cd onnxruntime
git submodule update --init --recursive

# CPU-only, with Python bindings
./build.sh --config Release --build_shared_lib --enable_pybind --build_wheel

# CUDA + Python
./build.sh --config Release --use_cuda --enable_pybind --build_wheel \
    --cuda_version 12.4 --cuda_home /usr/local/cuda

# With specific targets
./build.sh --config Release --build --parallel --target onnxruntime
```

## Build Script

Entry point: `./build.sh` (Linux/macOS) or `./build.bat` (Windows), which delegates to `tools/ci_build/build.py`.

```bash
./build.sh [options]

# Phases (default: --update --build --test for native, --update --build for cross)
--update          # Update submodules, run CMake
--build           # Compile
--clean           # Clean build
--test            # Run unit tests
--parallel [N]    # Parallel jobs (0 = auto, default: 1)

# Core
--build_dir <path>           # Build directory (required)
--config Debug|Release|RelWithDebInfo|MinSizeRel  # Build config(s)
--build_shared_lib           # Build shared library
--enable_lto                 # Link Time Optimization
--use_cache                  # Use ccache
--cmake_path cmake           # CMake executable path
--cmake_generator <name>     # CMake generator
--use_vcpkg                  # Use vcpkg for dependencies
--skip_submodule_sync        # Skip git submodule update
--skip_pip_install           # Skip pip install
```

## Platform-Specific Builds

### Linux

```bash
./build.sh --config Release --build_shared_lib

# Cross-compile to ARM64
./build.sh --config Release --arm64

# Cross-compile to RISC-V 64
./build.sh --config Release --rv64 \
    --riscv_toolchain_root /opt/riscv \
    --riscv_qemu_path /opt/riscv/bin/qemu-riscv64
```

### macOS

```bash
./build.sh --config Release --build_shared_lib --osx_arch arm64

# macOS framework
./build.sh --config Release --build_apple_framework --macos MacOSX
```

### Windows

```bash
build.bat --config Release --build_shared_lib

# Cross-compile ARM64
build.bat --config Release --arm64

# Static MSVC runtime
build.bat --config Release --enable_msvc_static_runtime
```

### Android

```bash
./build.sh --config Release --android \
    --android_abi arm64-v8a \
    --android_api 27 \
    --android_sdk_path $ANDROID_HOME \
    --android_ndk_path $ANDROID_NDK_HOME \
    --android_cpp_shared
```

### iOS

```bash
./build.sh --config Release --ios \
    --osx_arch arm64 \
    --apple_deploy_target 13.0 \
    --build_apple_framework
```

### WebAssembly

```bash
./build.sh --config Release --build_wasm \
    --emsdk_version 4.0.23 \
    --enable_wasm_simd \
    --enable_wasm_threads \
    --enable_wasm_jspi \
    --enable_wasm_profiling
```

## Execution Provider Builds

### CUDA

```bash
./build.sh --config Release --use_cuda \
    --cuda_version 12.4 \
    --cuda_home /usr/local/cuda \
    --cudnn_home /usr/local/cuda \
    --enable_nvtx_profile \
    --enable_cuda_profiling \
    --nvcc_threads 8
```

### TensorRT

```bash
./build.sh --config Release --use_tensorrt \
    --tensorrt_home /usr \
    --use_tensorrt_oss_parser
```

### OpenVINO

```bash
./build.sh --config Release --use_openvino CPU
# or GPU, NPU, HETERO:GPU,CPU, MULTI:GPU,CPU, AUTO:GPU,CPU
```

### CoreML

```bash
./build.sh --config Release --use_coreml
```

### DirectML (Windows)

```bash
build.bat --config Release --use_dml
```

### CANN (Huawei Ascend)

```bash
./build.sh --config Release --use_cann --cann_home /path/to/cann
```

### MIGraphX (AMD)

```bash
./build.sh --config Release --use_migraphx --migraphx_home /opt/rocm
```

### QNN (Qualcomm)

```bash
./build.sh --config Release --use_qnn shared_lib --qnn_home /path/to/qnn
```

### ACL (ARM)

```bash
./build.sh --config Release --use_acl \
    --acl_home /path/to/acl \
    --acl_libs /path/to/acl/libs
```

### XNNPACK

```bash
./build.sh --config Release --use_xnnpack
```

### WebGPU

```bash
./build.sh --config Release --use_webgpu static_lib
```

### NNAPI (Android)

```bash
./build.sh --config Release --use_nnapi --nnapi_min_api 27
```

### DNNL (oneDNN)

```bash
./build.sh --config Release --use_dnnl
```

## Language Bindings

```bash
# Python
--enable_pybind --build_wheel
--wheel_name_suffix nightly

# C#
--build_csharp          # CI
--build_nuget           # Local

# Java
--build_java

# Node.js
--build_nodejs

# Objective-C
--build_objc
```

## Size Reduction

### Minimal Build

```bash
# Minimal build — ORT format only, RTTI disabled
./build.sh --config Release --minimal_build

# With extended features (runtime kernel compilation)
./build.sh --config Release --minimal_build extended

# With custom ops
./build.sh --config Release --minimal_build extended custom_ops
```

### Reduced Operator Set

```bash
# Include only specified operators
./build.sh --config Release \
    --include_ops_by_config ops_config.json \
    --enable_reduced_operator_type_support

# Disable specific features
./build.sh --config Release \
    --disable_contrib_ops \
    --disable_ml_ops \
    --disable_generation_ops \
    --disable_rtti
```

### Disable Data Types

```bash
./build.sh --config Release --disable_types float4 float8 optional sparsetensor string
```

### Client Package Build

Optimized defaults for on-device workloads (thread spinning disabled, etc.):

```bash
./build.sh --config Release --client_package_build
```

## Training Build

```bash
./build.sh --config Release --enable_training \
    --enable_training_apis \
    --enable_training_ops \
    --enable_nccl \
    --nccl_home /path/to/nccl
```

## Debugging

```bash
# Address Sanitizer
./build.sh --config Debug --enable_address_sanitizer

# Memory profiling
./build.sh --config Debug --enable_memory_profile

# Pix capture (Windows, D3D12)
build.bat --config Debug --enable_pix_capture

# Disable warnings as errors
./build.sh --config Debug --compile_no_warning_as_error
```

## Testing

```bash
./build.sh --config Release --test
./build.sh --config Release --test --ctest_timeout 10800 --test_parallel 0
./build.sh --config Release --test --enable_onnx_tests
./build.sh --config Release --test --fuzz_testing
./build.sh --config Release --test --enable_symbolic_shape_infer_tests
./build.sh --config Release --test --build_micro_benchmarks
```

## CMake Direct Build

```bash
mkdir build && cd build
cmake .. \
    -DCMAKE_BUILD_TYPE=Release \
    -DONNX_RUNTIME_BUILD_SHARED_LIB=ON \
    -DUSE_CUDA=ON \
    -DCUDA_HOME=/usr/local/cuda \
    -DCMAKE_TOOLCHAIN_FILE=${VCPKG_INSTALL}/scripts/buildsystems/vcpkg.cmake

cmake --build . --config Release --parallel $(nproc)
ctest --output-on-failure --parallel $(nproc)
```

## Extra CMake Definitions

```bash
./build.sh --config Release \
    --cmake_extra_defines -DMyOption=ON -DAnotherOption=value
```

## MSBuild Extra Options (Windows)

```bash
build.bat --config Release --msbuild_extra_options /p:MyProp=Value
```

## Gotchas

- **Submodules** — always run `git submodule update --init --recursive` after clone; use `--skip_submodule_sync` only if already initialized
- **CUDA version** — auto-detected if `--cuda_version` omitted; specify explicitly for multi-CUDA setups
- **vcpkg** — requires `CMAKE_TOOLCHAIN_FILE` pointing to vcpkg; use `--use_vcpkg` flag
- **Root user** — Linux build refuses to run as root by default; add `--allow_running_as_root`
- **MSVC toolset** — must be >= 14.40; specify with `--msvc_toolset`
- **Wheel naming** — `onnxruntime-gpu` wheels include CUDA EP; plain `onnxruntime` is CPU-only
- **Ninja on Windows** — use `--cmake_generator Ninja` for faster builds
- **OpenMP** — `--use_openmp` enables OpenMP for intra-op parallelism; ORT threadpool always handles inter-op
