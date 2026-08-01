# Deployment

## Overview

Chronos-2 can be deployed for production inference via multiple pathways. The choice depends on infrastructure, latency requirements, and integration needs.

## AutoGluon-Cloud (Recommended)

High-level Python API with real-time, serverless, and batch inference. Pandas DataFrames in, forecasts out. Minimal setup, automatic scaling, pay-per-use billing.

```python
from autogluon.cloud import TimeSeriesFoundationModel

model = TimeSeriesFoundationModel(model_name="chronos-2")

# Batch prediction
forecast_df = model.predict(df, prediction_length=24)

# Deploy & invoke a real-time endpoint
endpoint = model.deploy(instance_type="ml.g5.xlarge")
forecast_df = endpoint.predict(df, prediction_length=24)
```

See the [AutoGluon-Cloud deployment guide](https://auto.gluon.ai/cloud/stable/tutorials/foundation-model-timeseries.html) for serverless endpoints and covariate-aware forecasting.

## SageMaker JumpStart

Production-ready real-time endpoints on CPU or GPU. Full AWS integration with IAM, VPC, and CloudWatch. JSON request/response payloads only; serverless inference and batch prediction require additional setup.

```python
from sagemaker.jumpstart.model import JumpStartModel

model = JumpStartModel(
    model_id="pytorch-forecasting-chronos-2",
    instance_type="ml.g5.2xlarge",
)
predictor = model.deploy()
```

Send time series data as JSON:

```python
payload = {
    "inputs": [
        {"target": [1.0, 2.5, ..., 12.3]},
    ],
    "parameters": {
        "prediction_length": 24,
    },
}
forecast = predictor.predict(payload)["predictions"]
```

See the [SageMaker deployment notebook](https://github.com/amazon-science/chronos-forecasting/blob/main/notebooks/deploy-chronos-to-amazon-sagemaker.ipynb) for full setup.

## Local Serving

Use `amazon/chronos-2` as the default model for all serving setups.

### FastAPI Example

```python
from fastapi import FastAPI
from chronos import Chronos2Pipeline
import torch

app = FastAPI()
pipeline = Chronos2Pipeline.from_pretrained("amazon/chronos-2", device_map="cuda")

@app.post("/predict")
def predict(context: list[float], prediction_length: int = 24):
    forecast = pipeline.predict(
        torch.tensor(context),
        prediction_length=prediction_length,
    )
    return {"predictions": forecast[0].cpu().numpy().tolist()}
```

### Batch Serving with predict_df

For high-throughput batch inference:

```python
pred_df = pipeline.predict_df(
    context_df,
    prediction_length=24,
    batch_size=512,
    quantile_levels=[0.1, 0.5, 0.9],
)
```

## Model Optimization

### Device Placement

```python
# Full GPU
pipeline = Chronos2Pipeline.from_pretrained("amazon/chronos-2", device_map="cuda")

# CPU (slower but no GPU needed)
pipeline = Chronos2Pipeline.from_pretrained("amazon/chronos-2", device_map="cpu")

# Mixed precision
pipeline = Chronos2Pipeline.from_pretrained(
    "amazon/chronos-2",
    device_map="cuda",
    torch_dtype="bfloat16",
)
```

### Model Size Trade-offs

| Model | Parameters | Latency | Memory | Accuracy |
|---|---|---|---|---|
| `chronos-bolt-tiny` | 9M | Fastest | ~40MB | Good |
| `chronos-bolt-mini` | 21M | Fast | ~85MB | Better |
| `chronos-bolt-small` | 48M | Moderate | ~200MB | Good |
| `chronos-bolt-base` | 205M | Slower | ~800MB | Best (Bolt) |
| `chronos-2-small` | 28M | Fast | ~115MB | Good |
| `chronos-2` **(default)** | 120M | Moderate | ~500MB | Best overall |

Default to `amazon/chronos-2` for best accuracy and full feature support. Use Chronos-Bolt only for latency-sensitive applications. Use `autogluon/chronos-2-small` for constrained memory.

### Quantization

The model supports loading with different dtypes:

```python
# Float32 (default, most compatible)
pipeline = Chronos2Pipeline.from_pretrained("amazon/chronos-2", torch_dtype="float32")

# BFloat16 (faster on Ampere+ GPUs, ~2x memory reduction)
pipeline = Chronos2Pipeline.from_pretrained("amazon/chronos-2", torch_dtype="bfloat16")
```

For INT8/INT4 quantization, use HuggingFace `optimum` or `bitsandbytes` with the underlying transformers model.

## S3 Deployment

Load models directly from S3:

```python
pipeline = BaseChronosPipeline.from_pretrained(
    "s3://my-bucket/chronos-2-model/",
    device_map="cuda",
)
```

Requires `pip install 'chronos-forecasting[extras]'` for `boto3`. Models are cached locally on first load.

## Performance Checklist

- Use `device_map="cuda"` and `torch_dtype="bfloat16"` for GPU inference
- Set `batch_size` to maximize GPU utilization without OOM
- For real-time serving, keep the model loaded (not per-request loading)
- Use `predict_df()` with `validate_inputs=False` for production after validating data format once
- For long horizons, accept the autoregressive unrolling warning or tune `max_output_patches`
- Monitor GPU memory with `torch.cuda.memory_allocated()` to tune batch sizes
