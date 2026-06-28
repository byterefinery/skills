# Installation Guide

## Quick Install

```bash
pip install autogluon
```

Installs all three modules (tabular, multimodal, timeseries). Python 3.10–3.13. Linux, macOS, Windows.

## Module-Specific Install

```bash
pip install autogluon.tabular      # TabularPredictor only
pip install autogluon.timeseries   # TimeSeriesPredictor only
pip install autogluon.multimodal   # MultiModalPredictor only
```

## Tabular Optional Dependencies

```bash
# Full tabular install (all model backends)
pip install autogluon.tabular[all]

# Specific backends
pip install autogluon.tabular[lightgbm,catboost,xgboost,fastai,ray]

# Foundation models (for extreme_quality preset)
pip install autogluon.tabular[tabarena]    # TabICL, TabPFNv2, TabDPT

# Individual foundation models
pip install autogluon.tabular[tabicl]      # TabICL
pip install autogluon.tabular[tabpfn]      # TabPFNv2
pip install autogluon.tabular[realmlp]     # RealMLP

# KNN speedup (25x faster, CPU only, not ARM-compatible)
pip install autogluon.tabular[all,skex]

# Interpretable models
pip install autogluon.tabular[interpret]   # EBM models
pip install autogluon.tabular[imodels]     # Interpretable ML (experimental)

# ONNX export
pip install autogluon.tabular[skl2onnx]
```

## uv Install

```bash
# CPU
python -m uv pip install autogluon

# GPU
python -m uv pip install autogluon --extra-index-url https://download.pytorch.org/whl/cu121
```

## Conda Install

```bash
conda install -c conda-forge autogluon
```

## GPU Install

```bash
# pip + PyTorch CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install autogluon

# Or use the GPU-specific install
pip install autogluon --extra-index-url https://download.pytorch.org/whl/cu121
```

## macOS Notes

- Apple Silicon (M1/M2/M3): use conda for best compatibility
- No GPU acceleration for multimodal on Mac — CPU only
- Install libomp: `brew install libomp` (may be needed for LightGBM)

## Windows Notes

- Full install works on Windows with CPU
- GPU support requires WSL2 or native PyTorch CUDA build
- Object detection (`mmdet`) has limited Windows support; use WSL2

## Nightly Builds

```bash
pip install --pre autogluon
```

## From Source

```bash
git clone --recursive https://github.com/autogluon/autogluon.git
cd autogluon
./full_install.sh

# Or install a specific submodule
pip install -e tabular/[lightgbm,catboost]
```

## Kaggle

```python
!pip install -U autogluon > /dev/null
# Restart runtime after install
```

For competitions without internet, use packaged AutoGluon artifacts from the Kaggle dataset repository.

## SageMaker

AutoGluon comes pre-installed in Amazon SageMaker Distribution images. No additional installation needed in SageMaker Studio notebooks.

## Verifying Installation

```python
import autogluon.tabular as tabular
import autogluon.timeseries as timeseries
import autogluon.multimodal as multimodal

print(tabular.__version__)
print(timeseries.__version__)
print(multimodal.__version__)
```
