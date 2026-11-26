# Models

Models for enrichment steps (picture classification, picture description, table detection, code/formula recognition, VLMs) must be present at runtime. The standard container image includes only default models; missing models raise runtime errors — Docling Serve does not download them automatically.

Models load from the directory in `DOCLING_SERVE_ARTIFACTS_PATH`; keep that path consistent between download and runtime. With multiple workers or reload, set it via env var, not CLI.

## Making extra models available

### 1. Auto-download at startup (dev only)

Clear the artifacts path so Docling downloads what it needs:

```sh
podman run -d -p 5001:5001 --name docling-serve \
  -e DOCLING_SERVE_ARTIFACTS_PATH="" \
  -e DOCLING_SERVE_ENABLE_UI=true \
  quay.io/docling-project/docling-serve
```

Not recommended for production (startup time, network dependency).

### 2. Custom image with pre-downloaded models

```Dockerfile
FROM quay.io/docling-project/docling-serve
RUN docling-tools models download smolvlm
```

### 3. Entrypoint override to download before startup

```sh
podman run -p 5001:5001 -e DOCLING_SERVE_ENABLE_UI=true \
  quay.io/docling-project/docling-serve \
  -- sh -c 'exec docling-tools models download smolvlm && exec docling-serve run'
```

### 4. Mount a volume with pre-downloaded models (recommended)

```sh
docling-tools models download --all -o models

podman run -p 5001:5001 \
  -v $(pwd)/models:/opt/app-root/src/models \
  -e DOCLING_SERVE_ARTIFACTS_PATH="/opt/app-root/src/models" \
  -e DOCLING_SERVE_ENABLE_UI=true \
  quay.io/docling-project/docling-serve
```

## Kubernetes / OpenShift pattern

Use a PVC for model storage, a Job to download models once, and mount the volume in the deployment:

1. **PVC** — e.g. `docling-model-cache-pvc`, `ReadWriteOnce`, 10 Gi (set `storageClassName` if not using the default).
2. **Download Job** — container runs `docling-tools models download --output-dir=/modelcache [models...]` (or `--all`) with the PVC mounted at `/modelcache`; `restartPolicy: Never`.
3. **Deployment** — set `DOCLING_SERVE_ARTIFACTS_PATH=/modelcache` and mount the same PVC at that path.

The value of `DOCLING_SERVE_ARTIFACTS_PATH` must match the mount path exactly.

## Notes

- A missing model is a runtime error; verify `DOCLING_SERVE_ARTIFACTS_PATH` points at the populated directory.
- For production/cluster deployments, prefer persistent storage plus a dedicated download job over in-container downloads.
