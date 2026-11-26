# Model Management

## Overview

Docling Serve loads ML models from the directory specified by `DOCLING_SERVE_ARTIFACTS_PATH`. The standard container image includes only default models. Additional models (picture classification, picture description, code/formula, VLM) must be pre-downloaded — Docling Serve does not auto-download at runtime.

## Model download CLI

```bash
# List available models
docling-tools models list

# Download specific models
docling-tools models download layout tableformer code_formula picture_classifier smolvlm granite_vision easyocr

# Download all models
docling-tools models download --all -o /models

# Download to specific directory
docling-tools models download --output-dir /opt/models layout tableformer
```

## Approaches

### 1. Auto-download (development only)

Clear the artifacts path to trigger downloads at startup:

```bash
podman run -p 5001:5001 \
  -e DOCLING_SERVE_ARTIFACTS_PATH="" \
  quay.io/docling-project/docling-serve
```

Not recommended for production — increases startup time and depends on network.

### 2. Custom image with pre-downloaded models

```dockerfile
FROM quay.io/docling-project/docling-serve:1.29.0
RUN docling-tools models download smolvlm granite_vision picture_classifier
```

Best for production — models are baked into the image.

### 3. Entrypoint override

```bash
podman run -p 5001:5001 \
  quay.io/docling-project/docling-serve \
  -- sh -c 'exec docling-tools models download smolvlm && exec docling-serve run'
```

Useful when you cannot rebuild the image but want automated model prep.

### 4. Volume mount (recommended for local + production)

```bash
# Download locally
docling-tools models download --all -o models

# Mount into container
podman run -p 5001:5001 \
  -v $(pwd)/models:/models \
  -e DOCLING_SERVE_ARTIFACTS_PATH=/models \
  quay.io/docling-project/docling-serve
```

The `DOCLING_SERVE_ARTIFACTS_PATH` value must match the container mount path exactly.

## Kubernetes PVC pattern

```yaml
# PVC
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: docling-model-cache-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
---
# Download Job
apiVersion: batch/v1
kind: Job
metadata:
  name: docling-model-cache-load
spec:
  template:
    spec:
      containers:
        - name: loader
          image: quay.io/docling-project/docling-serve-cpu:1.29.0
          command:
            - docling-tools
            - models
            - download
            - '--output-dir=/modelcache'
            - 'layout'
            - 'tableformer'
            - 'code_formula'
            - 'picture_classifier'
            - 'smolvlm'
            - 'granite_vision'
            - 'easyocr'
          volumeMounts:
            - name: docling-model-cache
              mountPath: /modelcache
      volumes:
        - name: docling-model-cache
          persistentVolumeClaim:
            claimName: docling-model-cache-pvc
      restartPolicy: Never
---
# Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: docling-serve
spec:
  template:
    spec:
      containers:
        - name: api
          image: quay.io/docling-project/docling-serve-cpu:1.29.0
          env:
            - name: DOCLING_SERVE_ARTIFACTS_PATH
              value: /modelcache
          volumeMounts:
            - name: docling-model-cache
              mountPath: /modelcache
      volumes:
        - name: docling-model-cache
          persistentVolumeClaim:
            claimName: docling-model-cache-pvc
```

## Model cache

Docling Serve caches `DocumentConverter` objects (including loaded models) based on `DOCLING_SERVE_OPTIONS_CACHE_SIZE` (default: 2). This means only 2 distinct model configurations are kept in memory simultaneously.

Clear the cache:

```bash
curl http://localhost:5001/v1/clear/converters
```

## Models by feature

| Feature | Models needed | Included by default |
|---------|---------------|---------------------|
| PDF parsing (docling_parse) | Layout model | Yes |
| Table structure | TableFormer | Yes |
| OCR (easyocr) | EasyOCR models | No |
| OCR (tesserocr) | Tesseract data | No |
| Picture classification | Document figure classifier | No |
| Picture description (local) | VLM model (SmolVLM, Granite) | No |
| Code/formula extraction | Code/formula model | No |
| VLM pipeline | VLM model | No |

## Remote VLM models

For API-based VLM (OpenAI-compatible, Ollama, vLLM), no local model download is needed. Set `DOCLING_SERVE_ENABLE_REMOTE_SERVICES=true` and configure via request options:

```json
{
  "picture_description_preset": "default",
  "picture_description_custom_config": {
    "engine_options": {"engine_type": "api"},
    "model_spec": {
      "name": "custom",
      "default_repo_id": "",
      "revision": "",
      "prompt": "Describe this image.",
      "response_format": "text"
    }
  }
}
```

Or use the API URL directly in the request.

## Troubleshooting

- **Missing model error**: The model is not in the artifacts path. Download it with `docling-tools models download <model_name>`.
- **`DOCLING_SERVE_ARTIFACTS_PATH` mismatch**: The env var must exactly match the mount path inside the container.
- **Slow startup**: Models are loading. Use pre-downloaded models in production.
- **OOM during model load**: Increase memory limits. GPU models need GPU memory, CPU models need RAM.
