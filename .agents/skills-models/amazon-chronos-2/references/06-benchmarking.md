# 06 — Benchmarking

## Running Benchmarks with fev

[fev](https://github.com/amazon-science/fev) is the Forecasting Evaluation framework used by Chronos for benchmarking.

```python
import fev

pipeline = Chronos2Pipeline.from_pretrained("amazon/chronos-2", device_map="cuda")
task = fev.get_task("m4_hourly")

predictions, inference_time = pipeline.predict_fev(task, batch_size=256)
```

### Available Tasks

```python
# M4 tasks
task = fev.get_task("m4_hourly")
task = fev.get_task("m4_daily")
task = fev.get_task("m4_weekly")
task = fev.get_task("m4_monthly")
task = fev.get_task("m4_quarterly")
task = fev.get_task("m4_yearly")

# Monash tasks
task = fev.get_task("monash_tourism_monthly")
task = fev.get_task("monash_weather")
task = fev.get_task("monash_traffic")
```

### Benchmarking with Fine-Tuning

Fine-tune on the first evaluation window before forecasting:

```python
predictions, inference_time = pipeline.predict_fev(
    task,
    batch_size=256,
    finetune_kwargs={
        "finetune_mode": "full",
        "num_steps": 500,
        "learning_rate": 1e-6,
    },
)
```

### Evaluating Results

```python
from fev.metrics import crps, mase, smape

# Compute metrics
crps_score = crps(predictions, task.test_data)
mase_score = mase(predictions, task.test_data, task.train_data)
smape_score = smape(predictions, task.test_data)
```

### Performance Tips

- Use `batch_size=256` for optimal throughput on A10G-class GPUs
- Set `device_map="cuda"` — CPU benchmarking is significantly slower
- For quick sanity checks, use smaller tasks like `m4_hourly` before running full benchmarks
