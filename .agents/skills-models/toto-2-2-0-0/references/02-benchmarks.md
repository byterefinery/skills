# Benchmarks — BOOM and GIFT-Eval

## GIFT-Eval

[GIFT-Eval](https://huggingface.co/spaces/Salesforce/GIFT-Eval) is a multi-domain time series forecasting benchmark covering diverse datasets.

### Running Evaluation

Use the [official GIFT-Eval notebook](https://github.com/SalesforceAIResearch/gift-eval/blob/main/notebooks/toto_2_0.ipynb) from the Salesforce GIFT-Eval repository. The notebook provides step-by-step instructions for:

1. Setting up the GIFT-Eval environment
2. Loading Toto 2.0 models
3. Running predictions on all benchmark datasets
4. Computing and comparing metrics

### Datasets Covered

GIFT-Eval includes datasets across multiple domains: energy, traffic, healthcare, finance, and more. Toto 2.0 achieves state-of-the-art results across the benchmark without any fine-tuning.

## BOOM (Benchmark of Observability Metrics)

[BOOM](https://huggingface.co/datasets/Datadog/BOOM) is a large-scale, real-world time series dataset designed specifically for evaluating models on observability forecasting tasks.

### Dataset Characteristics

- **Real-world data** — collected from Datadog's monitoring of pre-production environments (no customer data)
- **Covers diverse domains** — infrastructure, networking, databases, security, application-level metrics
- **Heavy-tailed statistics** — reflects the irregularity and structural complexity of production observability data
- **Large scale** — designed to stress-test models on the diversity and unpredictability of operational signals

### Running BOOM Evaluation

1. **BOOM Evaluation Notebook**: [`boom/notebooks/toto.ipynb`](https://github.com/DataDog/toto/tree/v2.0.0/boom/notebooks/toto.ipynb) — example workflow for running Toto 2.0 on BOOM
2. **BOOM README**: [`boom/README.md`](https://github.com/DataDog/toto/tree/v2.0.0/boom/README.md) — detailed instructions and scripts for benchmarking

### Dataset Card

See the full [BOOM dataset card](https://huggingface.co/datasets/Datadog/BOOM) on Hugging Face for preparation details and statistical properties.

## Comparison Notes

- **GIFT-Eval** is the general-purpose benchmark — use it to compare Toto 2.0 against other foundation models (Chronos, LSTM++, etc.)
- **BOOM** is observability-specific — use it when your workload involves monitoring metrics, SLO tracking, or infrastructure forecasting
- Both benchmarks support zero-shot evaluation (no fine-tuning), which is the primary use case for Toto 2.0
