# Data Pipeline

## GluonTS Integration

Uni2TS relies on GluonTS for dataset handling and inference. GluonTS provides:
- Dataset formats (`PandasDataset`, `ListDataset`)
- Train/test splitting with `split()` and `generate_instances()`
- Rolling window evaluation via `TFTInstanceSplitter`
- `PyTorchPredictor` wrapper for batched inference

### Creating Datasets from Pandas

```python
from gluonts.dataset.pandas import PandasDataset

# Wide format: columns = series, index = timestamps
df = pd.read_csv("data.csv", index_col=0, parse_dates=True)
ds = PandasDataset(dict(df))

# Access dataset metadata
ds.num_feat_dynamic_real      # number of dynamic real features
ds.num_past_feat_dynamic_real # number of past-only dynamic real features
```

### Train/Test Split

```python
from gluonts.dataset.split import split

# Split at offset (last N steps as test)
train, test_template = split(ds, offset=-100)

# Generate rolling window instances
test_data = test_template.generate_instances(
    prediction_length=20,
    windows=5,           # number of evaluation windows
    distance=20,         # steps between windows (20 = non-overlapping)
)

# Access inputs and labels
test_data.input   # iterable of input entries
test_data.label   # iterable of label entries
```

## Uni2TS Transforms

The `uni2ts.transform` module provides composable transformations for the pre-training and fine-tuning pipelines. Transforms are chained via `Chain`.

### Core Transforms

| Transform | Purpose |
|---|---|
| `Patchify` | Split sequences into patches |
| `PatchCrop` / `EvalCrop` / `FinetunePatchCrop` | Select patches for training/evaluation |
| `MaskedPrediction` / `EvalMaskedPrediction` | Mask patches for pre-training objective |
| `AddObservedMask` | Create binary mask for observed values |
| `AddSampleIndex` | Add sample (series) indices |
| `AddTimeIndex` | Add temporal position indices |
| `AddVariateIndex` | Add variate (dimension) indices |
| `PackFields` / `FlatPackFields` | Pack multi-field data for batched processing |
| `PackCollection` / `FlatPackCollection` | Pack collections of time series |
| `Pad` / `EvalPad` / `PadFreq` | Pad sequences to uniform length |
| `ImputeTimeSeries` | Impute missing values |
| `SampleDimension` | Sample dimensions for multivariate series |
| `Transpose` | Transpose array dimensions |

### Imputation Strategies

- `DummyValueImputation` — fill NaN with a constant
- `LastValueImputation` — forward-fill with last observed value
- `CausalMeanImputation` — fill with running mean (used in Moirai-2.0 `predict()`)

## Data Builders

The `uni2ts.data.builder` module converts raw data into HuggingFace datasets compatible with Uni2TS.

### Simple Data Builder

```bash
# Wide format (columns = series)
python -m uni2ts.data.builder.simple <name> <path.csv> --dataset_type wide

# Long format (item_id column)
python -m uni2ts.data.builder.simple <name> <path.csv> --dataset_type long

# Multivariate wide (all columns = one multivariate series)
python -m uni2ts.data.builder.simple <name> <path.csv> --dataset_type wide_multivariate
```

Options:
- `--date_offset 'YYYY-MM-DD HH:MM:SS'` — split by datetime (train = before offset)
- `--offset <int>` — split by row count
- `--normalize` — standardize using training set mean/std
- `--freq <str>` — specify frequency (e.g., `H`, `D`, `W`)

The builder saves data as HuggingFace datasets in `CUSTOM_DATA_PATH` (set in `.env`). Validation split is saved as `<name>_eval`.

### LOTSA Data Builder

For pre-training, use the LOTSA (Large-scale Open Time Series Archive) dataset:

```bash
huggingface-cli download Salesforce/lotsa_data --repo-type=dataset --local-dir /path/to/lotsa
echo "LOTSA_V1_PATH=/path/to/lotsa" >> .env
```

LOTSA contains diverse time series from multiple domains (weather, energy, traffic, etc.) for general pre-training.

## Dataset Classes

### TimeSeriesDataset

Core dataset class wrapping an `Indexer` and `Transformation`:

```python
from uni2ts.data.dataset import TimeSeriesDataset
from uni2ts.common.sampler import SampleTimeSeriesType

dataset = TimeSeriesDataset(
    indexer=indexer,
    transform=transform_chain,
    sample_time_series=SampleTimeSeriesType.UNIFORM,  # or PROPORTIONAL, NONE
    dataset_weight=1.0,
)
```

### FinetuneDataset / EvalDataset

Specialized datasets for fine-tuning and evaluation with appropriate cropping and masking transforms.

### SampleTimeSeriesType

Controls how series are sampled from the dataset:
- `NONE` — sequential access by index
- `UNIFORM` — each series has equal probability
- `PROPORTIONAL` — probability proportional to series length

## Data Loaders

The `uni2ts.data.loader` module provides custom PyTorch dataloaders:

### Collate Functions

- `PadCollate` — pads uneven sequences to uniform batch length
- Custom `pad_func_map` for per-field padding strategies

### DataLoader

```python
from uni2ts.data.loader import DataLoader

loader = DataLoader(
    dataset=dataset,
    batch_size=32,
    shuffle=True,
    num_batches_per_epoch=None,  # fixed number of batches
)
```

## Indexers

Indexers provide efficient access to time series data:

- `HuggingFaceDatasetIndexer` — reads from HuggingFace datasets
- Supports `get_uniform_probabilities()` and `get_proportional_probabilities()` for weighted sampling

## Environment Variables

Set in `.env` file at the repo root:

| Variable | Purpose |
|---|---|
| `CUSTOM_DATA_PATH` | Output directory for processed datasets |
| `LOTSA_V1_PATH` | Path to LOTSA pre-training data |
| `LSF_PATH` | Path to TSLib LSF benchmark data |
