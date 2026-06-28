# 04 — Deployment

## AutoGluon-Cloud (Recommended)

AutoGluon-Cloud provides the simplest deployment path with a high-level Python API. Pass pandas DataFrames in, get forecasts out. Supports real-time, serverless, and batch inference.

### Installation

```bash
pip install "autogluon.cloud>=0.5.0"
```

### Batch Prediction

```python
from autogluon.cloud import TimeSeriesFoundationModel

model = TimeSeriesFoundationModel(model_name="chronos-2")
forecast_df = model.predict(df, prediction_length=24)
```

### Real-Time Endpoint

```python
endpoint = model.deploy(instance_type="ml.g5.xlarge")
forecast_df = endpoint.predict(df, prediction_length=24)
```

### Serverless Endpoint

```python
endpoint = model.deploy(
    strategy="serverless",
    max_payload=10,        # MB
    memory_size=4096,      # MB
    timeout=60,            # seconds
)
forecast_df = endpoint.predict(df, prediction_length=24)
```

### Batch Inference

```python
job = model.run_batch(
    input_path="s3://bucket/input/",
    output_path="s3://bucket/output/",
    instance_type="ml.g5.xlarge",
    instance_count=2,
    prediction_length=24,
)
job.wait()
```

### Covariate-Aware Cloud Forecasting

```python
forecast_df = model.predict(
    df,
    prediction_length=24,
    future_df=future_covariates,
)
```

## SageMaker JumpStart

JumpStart provides fine-grained control over deployment configuration. Uses JSON request/response payloads.

### Installation

```bash
pip install -U 'sagemaker<3'
```

### Deploy Endpoint

```python
from sagemaker.jumpstart.model import JumpStartModel

model = JumpStartModel(
    model_id="pytorch-forecasting-chronos-2",
    instance_type="ml.g5.2xlarge",
)
predictor = model.deploy()
```

### Invoke Endpoint

```python
payload = {
    "inputs": [
        {"target": [1.0, 2.5, 3.7, ..., 12.3]}
    ],
    "parameters": {
        "prediction_length": 24,
    }
}
forecast = predictor.predict(payload)["predictions"]
```

### Batch with JumpStart

Batch prediction requires additional setup beyond the basic endpoint. Use AutoGluon-Cloud for simpler batch workflows.

### Instance Types

| Instance | GPU | VRAM | When to use |
|---|---|---|---|
| `ml.g5.xlarge` | 1x T4 | 16 GB | Cost-effective, single-user |
| `ml.g5.2xlarge` | 1x T4 | 16 GB | Default recommendation |
| `ml.g5.4xlarge` | 1x T4 | 16 GB | Higher throughput |
| `ml.g5.12xlarge` | 4x T4 | 64 GB | Large batch sizes |

## Local Deployment

### FastAPI Example

```python
from fastapi import FastAPI
from chronos import Chronos2Pipeline
import pandas as pd

app = FastAPI()
pipeline = Chronos2Pipeline.from_pretrained("amazon/chronos-2", device_map="cuda")

@app.post("/predict")
def predict(context: dict):
    df = pd.DataFrame(context["data"])
    pred_df = pipeline.predict_df(df, prediction_length=context.get("horizon", 24))
    return pred_df.to_dict(orient="records")
```

### Docker

```dockerfile
FROM pytorch/pytorch:2.5.1-cuda12.4-cudnn9-runtime

RUN pip install "chronos-forecasting>=2.0" pandas pyarrow

COPY app.py /app/app.py
WORKDIR /app

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Performance Considerations

- **Batch size**: ~100 is optimal for cross-learning. Larger batches improve throughput but may reduce cross-learning accuracy
- **GPU memory**: Chronos-2 fits comfortably on a single T4 (16 GB). Use larger instances for bigger batch sizes
- **CPU inference**: Supported but significantly slower. Use GPU for production workloads
- **Model loading**: First inference is slower due to model loading. Consider keeping endpoints warm
- **Quantized models**: INT8/INT4 versions are available on HuggingFace for reduced memory footprint
